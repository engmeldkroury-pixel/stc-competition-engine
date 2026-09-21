<?php
declare(strict_types=1);
require __DIR__ . '/macro_control.php';

$pdo = stc_pdo($config);

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    stc_require_operator_auth($config);
    $signalId = trim((string)($_GET['signal_id'] ?? ''));
    if ($signalId === '' || strlen($signalId) > 128) {
        stc_json(['ok' => false, 'error' => 'invalid_signal_id'], 400);
    }
    $signalRow = stc_signal_event($pdo, $signalId);
    if ($signalRow === null) {
        stc_json(['ok' => false, 'error' => 'signal_not_found'], 404);
    }
    $stmt = $pdo->prepare(
        'SELECT approval_id, signal_id, event_id, decision, quote_evidence_id, runtime_control_version, '
        . 'reason_json, note, decided_at_utc FROM stc_signal_approvals WHERE signal_id = ? ORDER BY id DESC LIMIT 1'
    );
    $stmt->execute([$signalId]);
    $approval = $stmt->fetch() ?: null;
    if (is_array($approval) && isset($approval['reason_json'])) {
        $approval['reasons'] = json_decode((string)$approval['reason_json'], true) ?: [];
        unset($approval['reason_json']);
    }
    stc_json([
        'ok' => true,
        'signal_id' => $signalId,
        'approval' => $approval,
        'runtime_control' => stc_runtime_control_row($pdo),
        'execution' => 'manual_only',
    ]);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}
stc_require_owner_auth($config);
$data = stc_json_body((int)($config['max_body_bytes'] ?? 65536));
$signalId = trim((string)($data['signal_id'] ?? ''));
$requested = trim((string)($data['decision'] ?? ''));
$note = trim((string)($data['note'] ?? ''));
if ($signalId === '' || strlen($signalId) > 128 || !in_array($requested, ['approve', 'reject'], true)) {
    stc_json(['ok' => false, 'error' => 'invalid_approval_request'], 400);
}
if (strlen($note) > 512) {
    stc_json(['ok' => false, 'error' => 'note_too_long'], 400);
}

$pdo->beginTransaction();
try {
    $control = stc_runtime_control_row($pdo, true);
    $signalRow = stc_signal_event($pdo, $signalId);
    if ($signalRow === null) {
        $pdo->rollBack();
        stc_json(['ok' => false, 'error' => 'signal_not_found'], 404);
    }
    $result = $signalRow['result'];
    $payload = $signalRow['payload'];
    $decision = $result['decision'] ?? null;
    $signal = is_array($decision) ? ($decision['signal'] ?? null) : null;
    $envelope = is_array($decision) ? ($decision['approval_envelope'] ?? null) : null;
    if (!is_array($decision) || !is_array($signal) || !is_array($envelope)
        || !stc_validate_signal_receipt($signalRow, $payload, $result, $signalId)
        || ($decision['action'] ?? '') !== 'signal_created'
        || ($decision['execution'] ?? '') !== 'manual_approval_required'
        || ($signal['requires_human_approval'] ?? false) !== true
        || ($signal['signal_id'] ?? '') !== $signalId) {
        throw new RuntimeException('invalid_signal_contract');
    }
    $competitionId = (string)($signal['competition_id'] ?? '');
    $symbol = (string)($signal['symbol'] ?? '');
    if ($competitionId === '' || $symbol === '' || ($payload['competition_id'] ?? null) !== $competitionId || ($payload['symbol'] ?? null) !== $symbol) {
        throw new RuntimeException('signal_target_mismatch');
    }

    $approvalId = 'approval-' . bin2hex(random_bytes(16));
    $status = 'rejected';
    $reasons = [];
    $evidenceId = null;
    $macroContext = null;

    if ($requested === 'approve') {
        if ($control['safe_mode']) {
            $reasons[] = 'safe_mode_active';
        }
        if ($control['kill_switch']) {
            $reasons[] = 'kill_switch_active';
        }
        if (($signal['recommendation'] ?? '') === 'WAIT') {
            $reasons[] = 'wait_is_not_an_order';
        }
        $validUntil = stc_parse_utc((string)($envelope['valid_until'] ?? ''));
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        if ($validUntil === null || $now >= $validUntil) {
            $reasons[] = 'signal_expired';
        }
        $latestEventId = stc_latest_signal_event_id($pdo, $competitionId, $symbol);
        if ($latestEventId === null || $latestEventId !== (string)$signalRow['event_id']) {
            $reasons[] = 'newer_signal_exists';
        }

        $macroContext = stc_macro_risk_context($config, $symbol, $now);
        if (($macroContext['block_new_approval'] ?? false) === true) {
            $reasons[] = ($macroContext['status'] ?? '') === 'blackout'
                ? 'macro_high_impact_blackout'
                : 'macro_calendar_unavailable_fail_closed';
        }

        $confirmation = $data['confirmation'] ?? null;
        if (!is_array($confirmation)) {
            $reasons[] = 'owner_confirmation_missing';
        } else {
            $checked = stc_validate_owner_confirmation($confirmation, $envelope, $competitionId, $symbol);
            $reasons = array_values(array_unique(array_merge($reasons, $checked['reasons'])));
            if ($checked['evidence']['observed_at_utc'] !== null) {
                $evidenceId = 'owner-' . bin2hex(random_bytes(16));
                $insertEvidence = $pdo->prepare(
                    'INSERT INTO stc_execution_evidence '
                    . '(evidence_id, source, competition_id, symbol, provider, observed_at_utc, quote_price, market_status, details_json, recorded_by) '
                    . 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                );
                $insertEvidence->execute([
                    $evidenceId,
                    $checked['evidence']['source'],
                    $competitionId,
                    $symbol,
                    $checked['evidence']['provider'],
                    $checked['evidence']['observed_at_utc'],
                    $checked['evidence']['quote_price'],
                    $checked['evidence']['market_status'],
                    json_encode([
                        'attestation' => 'owner_platform_confirmation',
                        'macro_context' => $macroContext,
                    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
                    'owner',
                ]);
            }
        }
        $status = $reasons === [] ? 'approved' : 'blocked';
    } else {
        $reasons[] = 'owner_rejected';
    }

    $insertApproval = $pdo->prepare(
        'INSERT INTO stc_signal_approvals '
        . '(approval_id, signal_id, event_id, competition_id, symbol, decision, quote_evidence_id, runtime_control_version, reason_json, note) '
        . 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    $insertApproval->execute([
        $approvalId,
        $signalId,
        (string)$signalRow['event_id'],
        $competitionId,
        $symbol,
        $status,
        $evidenceId,
        $control['version'],
        json_encode($reasons, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
        $note === '' ? null : $note,
    ]);
    $pdo->commit();
    stc_json([
        'ok' => true,
        'approval_id' => $approvalId,
        'signal_id' => $signalId,
        'decision' => $status,
        'approved' => $status === 'approved',
        'reasons' => $reasons,
        'quote_evidence_id' => $evidenceId,
        'runtime_control_version' => $control['version'],
        'macro_context' => $macroContext,
        'execution' => 'manual_only',
    ], $status === 'blocked' ? 409 : 200);
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    stc_json(['ok' => false, 'error' => 'approval_failed'], 409);
}
