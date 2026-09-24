<?php
declare(strict_types=1);
require_once __DIR__ . '/portfolio_control.php';
require_once __DIR__ . '/macro_control.php';

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
    $latestSignalContext = null;
    $lossCooldown = null;
    $positionSizing = null;
    $executionTicket = null;

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
        if (!stc_signal_quality_gate_eligible($signal)) {
            $reasons[] = 'quality_gate_not_passed';
        }

        $lockedPlan = $decision['locked_trade_plan'] ?? null;
        if (!is_array($lockedPlan)
            || ($lockedPlan['levels_locked'] ?? false) !== true
            || ($lockedPlan['execution'] ?? '') !== 'manual_only') {
            $reasons[] = 'locked_plan_unavailable';
        }

        $openStmt = $pdo->prepare(
            "SELECT COALESCE(SUM(quantity), 0) FROM stc_positions "
            . "WHERE competition_id = ? AND symbol = ? AND status = 'OPEN'"
        );
        $openStmt->execute([$competitionId, $symbol]);
        if ((float)$openStmt->fetchColumn() > 1e-12) {
            $reasons[] = 'existing_open_position';
        }

        $direction = strtoupper(trim((string)($signal['recommendation'] ?? 'WAIT')));
        $decisionTimeframeMinutes = 15;
        if (is_array($lockedPlan)) {
            $rawTimeframe = trim((string)($lockedPlan['decision_timeframe'] ?? '15'));
            if (preg_match('/^\d+$/', $rawTimeframe) === 1) {
                $decisionTimeframeMinutes = max(1, (int)$rawTimeframe);
            }
        }
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $lossCooldown = stc_recent_same_direction_loss_cooldown(
            $pdo,
            $competitionId,
            $symbol,
            $direction,
            $now,
            $decisionTimeframeMinutes
        );
        if (($lossCooldown['active'] ?? false) === true) {
            $reasons[] = 'same_direction_loss_cooldown';
        }

        $validUntil = stc_parse_utc((string)($envelope['valid_until'] ?? ''));
        if ($validUntil === null || $now >= $validUntil) {
            $reasons[] = 'signal_expired';
        }
        $latestSignalContext = stc_latest_signal_context($pdo, $competitionId, $symbol);
        if ($latestSignalContext === null) {
            $reasons[] = 'latest_signal_unavailable';
        } elseif ((string)$latestSignalContext['event_id'] !== (string)$signalRow['event_id']) {
            $compatibility = stc_locked_plan_latest_signal_compatibility(
                $signal,
                (array)$latestSignalContext['signal']
            );
            $latestSignalContext['compatibility_with_locked_plan'] = $compatibility;
            if (($compatibility['compatible'] ?? false) !== true) {
                $reasons[] = 'newer_signal_not_aligned';
            }
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

            $checkedPrice = $checked['evidence']['quote_price'] ?? null;
            if ($checkedPrice !== null && is_array($lockedPlan)) {
                try {
                    $positionSizing = stc_current_position_sizing_for_plan(
                        $pdo,
                        $competitionId,
                        $symbol,
                        (float)$checkedPrice,
                        (float)$lockedPlan['initial_stop']
                    );
                    if (($positionSizing['allowed_by_position_limit'] ?? false) !== true
                        || ($positionSizing['allowed_by_risk_policy'] ?? false) !== true
                        || (float)($positionSizing['proposed_quantity'] ?? 0.0) <= 0.0) {
                        $reasons[] = 'risk_capacity_unavailable';
                    } else {
                        $orderInstruction = stc_entry_order_instruction(
                            (string)$lockedPlan['direction'],
                            (float)$checkedPrice,
                            (float)$lockedPlan['entry_min'],
                            (float)$lockedPlan['entry_max']
                        );
                        $executionTicket = [
                            'ticket_version' => 'stc-execution-ticket-v1',
                            'competition_id' => $competitionId,
                            'symbol' => $symbol,
                            'direction' => (string)$lockedPlan['direction'],
                            'approved_quote_price' => (float)$checkedPrice,
                            'entry_min' => (float)$lockedPlan['entry_min'],
                            'entry_max' => (float)$lockedPlan['entry_max'],
                            'initial_stop' => (float)$lockedPlan['initial_stop'],
                            'final_take_profit' => (float)$lockedPlan['target2'],
                            'max_quantity' => (float)$positionSizing['proposed_quantity'],
                            'risk_amount_usd' => (float)$positionSizing['risk_amount_usd'],
                            'risk_budget_usd' => (float)$positionSizing['risk_budget_usd'],
                            'risk_fraction' => (float)$positionSizing['risk_fraction'],
                            'order_instruction' => $orderInstruction,
                            'do_not_exceed_quantity' => true,
                            'smaller_quantity_allowed' => true,
                            'manual_execution_only' => true,
                            'freshness_seconds' => 60,
                        ];
                    }
                } catch (Throwable $e) {
                    $reasons[] = 'risk_capacity_unavailable';
                }
            }

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
                        'loss_cooldown' => $lossCooldown,
                        'position_sizing' => $positionSizing,
                        'execution_ticket' => $executionTicket,
                    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
                    'owner',
                ]);
            }
        }
        $reasons = array_values(array_unique($reasons));
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
        'latest_signal_context' => $latestSignalContext,
        'loss_cooldown' => $lossCooldown,
        'position_sizing' => $positionSizing,
        'execution_ticket' => $status === 'approved' ? $executionTicket : null,
        'execution' => 'manual_only',
    ], $status === 'blocked' ? 409 : 200);
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    stc_json(['ok' => false, 'error' => 'approval_failed'], 409);
}
