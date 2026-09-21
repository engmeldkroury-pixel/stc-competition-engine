<?php
declare(strict_types=1);
require __DIR__ . '/cloud_control.php';

stc_require_owner_auth($config);
$pdo = stc_pdo($config);

try {
    $runtime = stc_runtime_control_row($pdo);
    $stmt = $pdo->prepare(
        'SELECT id, event_id, payload_json, result_json, analysis_completed_at_utc '
        . 'FROM stc_webhook_events '
        . "WHERE status = 'ingested' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.competition_id')) = ? "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.action')) = 'signal_created' "
        . 'ORDER BY id DESC LIMIT 100'
    );
    $stmt->execute(['capital-africa-sep-2026']);

    $cards = [];
    $seen = [];
    $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));

    while (($row = $stmt->fetch()) !== false) {
        $payload = json_decode((string)$row['payload_json'], true);
        $result = json_decode((string)$row['result_json'], true);
        if (!is_array($payload) || !is_array($result)) {
            continue;
        }

        $decision = $result['decision'] ?? null;
        $signal = is_array($decision) ? ($decision['signal'] ?? null) : null;
        $envelope = is_array($decision) ? ($decision['approval_envelope'] ?? null) : null;
        if (!is_array($decision) || !is_array($signal) || !is_array($envelope)) {
            continue;
        }

        $symbol = (string)($payload['symbol'] ?? '');
        $signalId = (string)($signal['signal_id'] ?? '');
        if ($symbol === '' || $signalId === '' || isset($seen[$symbol])) {
            continue;
        }
        if (!stc_validate_signal_receipt($row, $payload, $result, $signalId)) {
            continue;
        }
        $seen[$symbol] = true;

        $approvalStmt = $pdo->prepare(
            'SELECT approval_id, decision, quote_evidence_id, runtime_control_version, '
            . 'reason_json, note, decided_at_utc '
            . 'FROM stc_signal_approvals WHERE signal_id = ? ORDER BY id DESC LIMIT 1'
        );
        $approvalStmt->execute([$signalId]);
        $approval = $approvalStmt->fetch() ?: null;
        if (is_array($approval)) {
            $approval['reasons'] = json_decode((string)($approval['reason_json'] ?? '[]'), true) ?: [];
            unset($approval['reason_json']);
        }

        $validUntil = stc_parse_utc((string)($envelope['valid_until'] ?? ''));
        $approvalFresh = false;
        if (is_array($approval) && ($approval['decision'] ?? '') === 'approved') {
            try {
                $decided = new DateTimeImmutable((string)$approval['decided_at_utc'], new DateTimeZone('UTC'));
                $age = $now->getTimestamp() - $decided->setTimezone(new DateTimeZone('UTC'))->getTimestamp();
                $approvalFresh = $age >= 0 && $age <= 60;
            } catch (Throwable $e) {
                $approvalFresh = false;
            }
        }

        $recommendation = (string)($signal['recommendation'] ?? 'WAIT');
        $lockedPlan = $decision['locked_trade_plan'] ?? null;
        $planValid = is_array($lockedPlan)
            && ($lockedPlan['levels_locked'] ?? false) === true
            && ($lockedPlan['execution'] ?? '') === 'manual_only';

        $manualReady = !$runtime['safe_mode']
            && !$runtime['kill_switch']
            && in_array($recommendation, ['LONG', 'SHORT'], true)
            && $planValid
            && $approvalFresh
            && $validUntil !== null
            && $now < $validUntil;

        $cards[] = [
            'event_id' => (string)$row['event_id'],
            'signal_id' => $signalId,
            'symbol' => $symbol,
            'source_time' => (string)($payload['time'] ?? ''),
            'recommendation' => $recommendation,
            'composite_score' => (float)($signal['composite_score'] ?? 0.0),
            'confidence' => (float)($signal['confidence'] ?? 0.0),
            'reasons' => is_array($signal['reasons'] ?? null) ? $signal['reasons'] : [],
            'envelope' => $envelope,
            'locked_trade_plan' => $planValid ? $lockedPlan : null,
            'approval' => $approval,
            'manual_execution_ready' => $manualReady,
            'execution' => 'manual_only',
        ];
        if (count($cards) >= 10) {
            break;
        }
    }

    stc_json([
        'ok' => true,
        'scope' => 'owner_console_read_only_snapshot',
        'observed_at_utc' => $now->format(DateTimeInterface::ATOM),
        'runtime_control' => $runtime,
        'cards' => $cards,
        'execution' => 'manual_only',
        'automatic_execution_available' => false,
    ]);
} catch (Throwable $e) {
    stc_json(['ok' => false, 'error' => 'operator_snapshot_unavailable'], 503);
}
