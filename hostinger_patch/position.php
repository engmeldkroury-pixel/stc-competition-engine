<?php
declare(strict_types=1);
require __DIR__ . '/portfolio_control.php';

stc_require_owner_auth($config);
$pdo = stc_pdo($config);
$method = strtoupper((string)($_SERVER['REQUEST_METHOD'] ?? 'GET'));

if ($method === 'GET') {
    $status = strtoupper(trim((string)($_GET['status'] ?? 'OPEN')));
    if (!in_array($status, ['OPEN', 'CLOSED', 'ALL'], true)) {
        stc_json(['ok' => false, 'error' => 'invalid_status'], 400);
    }
    $competitionId = trim((string)($_GET['competition_id'] ?? ''));

    $where = [];
    $params = [];
    if ($status !== 'ALL') {
        $where[] = 'status = ?';
        $params[] = $status;
    }
    if ($competitionId !== '') {
        $where[] = 'competition_id = ?';
        $params[] = $competitionId;
    }

    $sql = 'SELECT * FROM stc_positions';
    if ($where !== []) {
        $sql .= ' WHERE ' . implode(' AND ', $where);
    }
    $sql .= ' ORDER BY updated_at_utc DESC, id DESC LIMIT 200';

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $positions = [];
    while (($row = $stmt->fetch()) !== false) {
        $positions[] = stc_position_public($row);
    }
    stc_json([
        'ok' => true,
        'positions' => $positions,
        'execution' => 'manual_only',
        'automatic_execution_available' => false,
    ]);
}

if ($method !== 'POST') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}

$body = stc_json_body();
$action = strtoupper(trim((string)($body['action'] ?? '')));

try {
    if ($action === 'VOID') {
        $positionId = trim((string)($body['position_id'] ?? ''));
        $reason = trim((string)($body['reason'] ?? ''));
        $confirmed = ($body['confirm_void'] ?? false) === true;
        if ($positionId === '' || !$confirmed || strlen($reason) < 8) {
            stc_json([
                'ok' => false,
                'error' => 'void_confirmation_required',
                'detail' => 'Provide position_id, confirm_void=true, and a specific reconciliation reason.',
            ], 400);
        }

        $row = stc_position_row($pdo, $positionId);
        if ((string)$row['status'] !== 'OPEN') {
            stc_json(['ok' => false, 'error' => 'only_open_position_can_be_voided'], 409);
        }
        if ((string)$row['origin'] !== 'manual_external') {
            stc_json([
                'ok' => false,
                'error' => 'void_restricted_to_manual_external',
                'detail' => 'STC-plan positions must be closed through the normal audited close workflow.',
            ], 409);
        }

        $quantity = (float)$row['quantity'];
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $note = trim((string)($row['note'] ?? ''));
        $note = trim(($note !== '' ? $note . ' | ' : '')
            . 'VOIDED ledger-only reconciliation record: ' . substr($reason, 0, 320)
            . '. No broker action. No realized P/L.');

        $pdo->beginTransaction();
        $stmt = $pdo->prepare(
            "UPDATE stc_positions SET status = 'VOID', quantity = 0, closed_at_utc = ?, "
            . "realized_pnl_usd = 0, note = ? WHERE position_id = ? AND status = 'OPEN'"
        );
        $stmt->execute([
            $now->format('Y-m-d H:i:s'),
            $note,
            $positionId,
        ]);
        if ($stmt->rowCount() !== 1) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'position_void_race'], 409);
        }

        $evt = $pdo->prepare(
            'INSERT INTO stc_position_events '
            . '(event_id, position_id, event_type, quantity_delta, price, realized_pnl_delta_usd, note, created_at_utc) '
            . 'VALUES (?, ?, ?, ?, ?, 0, ?, ?)'
        );
        $evt->execute([
            stc_position_event_id($positionId, 'VOID'),
            $positionId,
            'VOID',
            -$quantity,
            (float)$row['entry_price'],
            'Owner-confirmed ledger reconciliation void. No broker action and no realized P/L.',
            $now->format('Y-m-d H:i:s'),
        ]);
        $pdo->commit();

        stc_json([
            'ok' => true,
            'position' => stc_position_public(stc_position_row($pdo, $positionId)),
            'execution' => 'none',
            'automatic_execution_available' => false,
            'note' => 'Ledger record voided for reconciliation only. No broker action occurred.',
        ]);
    }

    if ($action === 'IMPORT_CLOSED') {
        $competitionId = trim((string)($body['competition_id'] ?? ''));
        $symbol = trim((string)($body['symbol'] ?? ''));
        $resolvedTarget = stc_resolve_position_target($competitionId, $symbol);
        if ($resolvedTarget === null) {
            stc_json([
                'ok' => false,
                'error' => 'invalid_position_target',
                'detail' => 'Select a configured competition and use a supported TradingView/provider symbol.',
            ], 400);
        }
        $competitionId = (string)$resolvedTarget['competition_id'];
        $symbol = (string)$resolvedTarget['symbol'];

        $side = stc_position_side($body['side'] ?? null);
        $quantity = stc_num($body['quantity'] ?? null, 'quantity');
        $entryPrice = stc_num($body['entry_price'] ?? null, 'entry_price');
        $exitPrice = stc_num($body['exit_price'] ?? null, 'exit_price');

        $opened = stc_parse_utc(trim((string)($body['opened_at_utc'] ?? '')));
        $closed = stc_parse_utc(trim((string)($body['closed_at_utc'] ?? '')));
        if ($opened === null || $closed === null || $closed < $opened) {
            stc_json(['ok' => false, 'error' => 'invalid_historical_trade_times'], 400);
        }

        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $competitionStart = $competitionId === 'amp-futures-sep-2026'
            ? new DateTimeImmutable('2026-09-01T08:00:00+00:00')
            : new DateTimeImmutable('2026-09-16T08:00:00+00:00');
        if ($opened < $competitionStart || $closed < $competitionStart || $closed > $now) {
            stc_json(['ok' => false, 'error' => 'historical_trade_outside_competition_window'], 400);
        }

        $sign = $side === 'LONG' ? 1.0 : -1.0;
        $value = stc_price_value_usd($competitionId, $symbol, $entryPrice);
        $computedPnl = ($exitPrice - $entryPrice) * $sign * $quantity * $value;
        $realizedPnl = $computedPnl;
        $pnlSource = 'stc_estimate';
        if (array_key_exists('realized_pnl_usd', $body) && $body['realized_pnl_usd'] !== null && $body['realized_pnl_usd'] !== '') {
            if (!is_int($body['realized_pnl_usd']) && !is_float($body['realized_pnl_usd'])) {
                stc_json(['ok' => false, 'error' => 'invalid_realized_pnl_usd'], 400);
            }
            $realizedPnl = (float)$body['realized_pnl_usd'];
            if (!is_finite($realizedPnl)) {
                stc_json(['ok' => false, 'error' => 'invalid_realized_pnl_usd'], 400);
            }
            $pnlSource = 'owner_platform_record';
        }

        $positionId = stc_position_id();
        $note = trim((string)($body['note'] ?? ''));
        $note = trim(($note !== '' ? $note . ' | ' : '')
            . 'Historical closed trade imported by owner; no broker action. P/L source: ' . $pnlSource
            . '. Historical stop/targets unavailable in import and stored as entry-price placeholders.');

        $pdo->beginTransaction();
        $stmt = $pdo->prepare(
            'INSERT INTO stc_positions '
            . '(position_id, competition_id, symbol, side, origin, initial_quantity, quantity, '
            . 'entry_price, initial_stop, current_stop, target1, target2, source_plan_id, source_signal_id, '
            . "status, opened_at_utc, closed_at_utc, exit_price, realized_pnl_usd, note) "
            . "VALUES (?, ?, ?, ?, 'manual_external', ?, 0, ?, ?, ?, ?, ?, NULL, NULL, 'CLOSED', ?, ?, ?, ?, ?)"
        );
        $stmt->execute([
            $positionId,
            $competitionId,
            $symbol,
            $side,
            $quantity,
            $entryPrice,
            $entryPrice,
            $entryPrice,
            $entryPrice,
            $entryPrice,
            $opened->format('Y-m-d H:i:s'),
            $closed->format('Y-m-d H:i:s'),
            $exitPrice,
            $realizedPnl,
            $note,
        ]);

        $evt = $pdo->prepare(
            'INSERT INTO stc_position_events '
            . '(event_id, position_id, event_type, quantity_delta, price, realized_pnl_delta_usd, note, created_at_utc) '
            . 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        );
        $evt->execute([
            stc_position_event_id($positionId, 'OPEN_IMPORT'),
            $positionId,
            'OPEN',
            $quantity,
            $entryPrice,
            0.0,
            'Historical owner-confirmed open import; STC did not place the order.',
            $opened->format('Y-m-d H:i:s'),
        ]);
        $evt->execute([
            stc_position_event_id($positionId, 'CLOSE_IMPORT'),
            $positionId,
            'CLOSE',
            -$quantity,
            $exitPrice,
            $realizedPnl,
            'Historical owner-confirmed close import; STC did not place the order.',
            $closed->format('Y-m-d H:i:s'),
        ]);
        $pdo->commit();

        stc_json([
            'ok' => true,
            'position' => stc_position_public(stc_position_row($pdo, $positionId)),
            'realized_pnl_source' => $pnlSource,
            'execution' => 'manual_only',
            'note' => 'Historical closed trade recorded for competition progress/audit only. No broker order was sent.',
        ], 201);
    }

    if ($action === 'OPEN') {
        $competitionId = trim((string)($body['competition_id'] ?? ''));
        $symbol = trim((string)($body['symbol'] ?? ''));
        $resolvedTarget = stc_resolve_position_target($competitionId, $symbol);
        if ($resolvedTarget === null) {
            stc_json([
                'ok' => false,
                'error' => 'invalid_position_target',
                'detail' => 'Select a configured competition and use a supported TradingView/provider symbol.',
            ], 400);
        }
        $competitionId = (string)$resolvedTarget['competition_id'];
        $symbol = (string)$resolvedTarget['symbol'];
        $side = stc_position_side($body['side'] ?? null);
        $quantity = stc_num($body['quantity'] ?? null, 'quantity');
        $entryPrice = stc_num($body['entry_price'] ?? null, 'entry_price');
        $initialStop = stc_num($body['initial_stop'] ?? null, 'initial_stop');
        $currentStop = array_key_exists('current_stop', $body)
            ? stc_num($body['current_stop'], 'current_stop')
            : $initialStop;
        $target1 = stc_num($body['target1'] ?? null, 'target1');
        $target2 = stc_num($body['target2'] ?? null, 'target2');
        $origin = strtolower(trim((string)($body['origin'] ?? 'stc_plan')));
        if (!in_array($origin, ['stc_plan', 'manual_external'], true)) {
            stc_json(['ok' => false, 'error' => 'invalid_origin'], 400);
        }

        $geometryValid = $side === 'LONG'
            ? ($initialStop < $entryPrice && $target1 > $entryPrice && $target2 > $target1)
            : ($initialStop > $entryPrice && $target1 < $entryPrice && $target2 < $target1);
        if (!$geometryValid) {
            stc_json(['ok' => false, 'error' => 'invalid_position_geometry'], 409);
        }

        $maxPosition = stc_max_open_position($competitionId, $symbol);
        if ($maxPosition === null) {
            stc_json(['ok' => false, 'error' => 'symbol_not_allowed'], 409);
        }
        $qtyStmt = $pdo->prepare(
            "SELECT COALESCE(SUM(quantity), 0) AS qty FROM stc_positions "
            . "WHERE status = 'OPEN' AND competition_id = ? AND symbol = ?"
        );
        $qtyStmt->execute([$competitionId, $symbol]);
        $existingQty = (float)($qtyStmt->fetch()['qty'] ?? 0.0);
        if ($existingQty + $quantity > $maxPosition + 1e-12) {
            stc_json([
                'ok' => false,
                'error' => 'competition_position_limit_exceeded',
                'current_open_quantity' => $existingQty,
                'requested_quantity' => $quantity,
                'max_position' => $maxPosition,
            ], 409);
        }

        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $openedRaw = trim((string)($body['opened_at_utc'] ?? ''));
        $opened = $openedRaw === '' ? $now : stc_parse_utc($openedRaw);
        if ($opened === null) {
            stc_json(['ok' => false, 'error' => 'invalid_opened_at'], 400);
        }

        // The Record Trade recovery form is often used immediately after a
        // manual platform fill. If the owner leaves the field blank, use the
        // Hostinger server time directly. If a browser clock is only slightly
        // ahead, clamp it to server-now instead of rejecting a real fill.
        $futureSkewSeconds = $opened->getTimestamp() - $now->getTimestamp();
        if ($futureSkewSeconds > 300) {
            stc_json([
                'ok' => false,
                'error' => 'opened_at_out_of_range',
                'detail' => 'Open time is more than 5 minutes ahead of the STC server clock.',
                'server_now_utc' => $now->format(DateTimeInterface::ATOM),
            ], 400);
        }
        if ($futureSkewSeconds > 0) {
            $opened = $now;
        }

        $age = $now->getTimestamp() - $opened->getTimestamp();
        if ($origin === 'stc_plan' && $age > 86400) {
            stc_json(['ok' => false, 'error' => 'opened_at_out_of_range'], 400);
        }
        if ($origin === 'manual_external') {
            $competitionStart = $competitionId === 'amp-futures-sep-2026'
                ? new DateTimeImmutable('2026-09-01T08:00:00+00:00')
                : new DateTimeImmutable('2026-09-16T08:00:00+00:00');
            if ($opened < $competitionStart) {
                stc_json([
                    'ok' => false,
                    'error' => 'manual_position_open_time_outside_competition_window',
                    'detail' => 'Open time is before the configured competition start.',
                    'competition_start_utc' => $competitionStart->format(DateTimeInterface::ATOM),
                    'server_now_utc' => $now->format(DateTimeInterface::ATOM),
                ], 400);
            }
        }

        $sourcePlanId = null;
        $sourceSignalId = null;
        if ($origin === 'stc_plan') {
            $validated = stc_validate_stc_plan_position($pdo, $body);
            $plan = $validated['plan'];
            $sourcePlanId = (string)$plan['plan_id'];
            $sourceSignalId = (string)$validated['signal_id'];

            if ($entryPrice < (float)$plan['entry_min'] || $entryPrice > (float)$plan['entry_max']) {
                stc_json(['ok' => false, 'error' => 'executed_entry_outside_locked_plan'], 409);
            }
            if (abs($initialStop - (float)$plan['initial_stop']) > max(1e-9, abs((float)$plan['initial_stop']) * 1e-8)) {
                stc_json(['ok' => false, 'error' => 'initial_stop_must_match_locked_plan'], 409);
            }
            if (abs($target1 - (float)$plan['target1']) > max(1e-9, abs((float)$plan['target1']) * 1e-8)
                || abs($target2 - (float)$plan['target2']) > max(1e-9, abs((float)$plan['target2']) * 1e-8)) {
                stc_json(['ok' => false, 'error' => 'targets_must_match_locked_plan'], 409);
            }

            $currentSizing = stc_current_position_sizing_for_plan(
                $pdo,
                $competitionId,
                $symbol,
                $entryPrice,
                $initialStop
            );
            $approvedTicket = is_array($validated['execution_ticket'] ?? null)
                ? $validated['execution_ticket']
                : null;
            $approvedMaxQuantity = $approvedTicket === null
                ? (float)($currentSizing['proposed_quantity'] ?? 0.0)
                : (float)($approvedTicket['max_quantity'] ?? 0.0);
            $currentMaxQuantity = (float)($currentSizing['proposed_quantity'] ?? 0.0);
            $allowedQuantity = min($approvedMaxQuantity, $currentMaxQuantity);
            $qtyTolerance = max(1e-9, abs($allowedQuantity) * 1e-8);

            if (($currentSizing['allowed_by_position_limit'] ?? false) !== true
                || ($currentSizing['allowed_by_risk_policy'] ?? false) !== true
                || $allowedQuantity <= 0.0) {
                stc_json([
                    'ok' => false,
                    'error' => 'stc_risk_capacity_unavailable_at_fill_record',
                    'approved_max_quantity' => $approvedMaxQuantity,
                    'current_max_quantity' => $currentMaxQuantity,
                    'filled_quantity' => $quantity,
                ], 409);
            }
            if ($quantity > $allowedQuantity + $qtyTolerance) {
                stc_json([
                    'ok' => false,
                    'error' => 'filled_quantity_exceeds_stc_risk_ticket',
                    'filled_quantity' => $quantity,
                    'approved_max_quantity' => $approvedMaxQuantity,
                    'current_max_quantity' => $currentMaxQuantity,
                    'allowed_quantity' => $allowedQuantity,
                    'risk_amount_usd_at_allowed_quantity' => (float)($currentSizing['risk_amount_usd'] ?? 0.0),
                    'risk_budget_usd' => (float)($currentSizing['risk_budget_usd'] ?? 0.0),
                    'detail' => 'Record this as manual_external for supervision if the platform fill already exceeded the STC ticket. Do not label the oversized fill as an STC-compliant plan fill.',
                ], 409);
            }
        }

        $positionId = stc_position_id();
        $eventId = stc_position_event_id($positionId, 'OPEN');

        $pdo->beginTransaction();
        $stmt = $pdo->prepare(
            'INSERT INTO stc_positions '
            . '(position_id, competition_id, symbol, side, origin, initial_quantity, quantity, '
            . 'entry_price, initial_stop, current_stop, target1, target2, source_plan_id, source_signal_id, '
            . "status, opened_at_utc, realized_pnl_usd, note) "
            . "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, 0, ?)"
        );
        $stmt->execute([
            $positionId,
            $competitionId,
            $symbol,
            $side,
            $origin,
            $quantity,
            $quantity,
            $entryPrice,
            $initialStop,
            $currentStop,
            $target1,
            $target2,
            $sourcePlanId,
            $sourceSignalId,
            $opened->format('Y-m-d H:i:s'),
            trim((string)($body['note'] ?? '')) ?: null,
        ]);
        $evt = $pdo->prepare(
            'INSERT INTO stc_position_events '
            . '(event_id, position_id, event_type, quantity_delta, price, stop_after, note) '
            . "VALUES (?, ?, 'OPEN', ?, ?, ?, ?)"
        );
        $evt->execute([
            $eventId,
            $positionId,
            $quantity,
            $entryPrice,
            $currentStop,
            'Owner confirmed manual competition fill; STC did not place the order.',
        ]);
        $pdo->commit();

        $row = stc_position_row($pdo, $positionId);
        stc_json([
            'ok' => true,
            'position' => stc_position_public($row),
            'execution' => 'manual_only',
            'note' => 'Position recorded after owner-confirmed manual fill. No broker order was sent.',
        ], 201);
    }

    if (!in_array($action, ['UPDATE_STOP', 'PARTIAL', 'CLOSE'], true)) {
        stc_json(['ok' => false, 'error' => 'unsupported_action'], 400);
    }

    $positionId = trim((string)($body['position_id'] ?? ''));
    if ($positionId === '') {
        stc_json(['ok' => false, 'error' => 'position_id_required'], 400);
    }

    $pdo->beginTransaction();
    $row = stc_position_row($pdo, $positionId, true);
    if ($row === null) {
        $pdo->rollBack();
        stc_json(['ok' => false, 'error' => 'position_not_found'], 404);
    }
    if ((string)$row['status'] !== 'OPEN') {
        $pdo->rollBack();
        stc_json(['ok' => false, 'error' => 'position_not_open'], 409);
    }

    if ($action === 'UPDATE_STOP') {
        $newStop = stc_num($body['current_stop'] ?? null, 'current_stop');
        $entry = (float)$row['entry_price'];
        $oldStop = (float)$row['current_stop'];
        $side = (string)$row['side'];

        // Never allow risk to be silently widened after the position is recorded.
        $widens = $side === 'LONG' ? $newStop < $oldStop : $newStop > $oldStop;
        if ($widens) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'stop_risk_widening_blocked'], 409);
        }

        $stmt = $pdo->prepare('UPDATE stc_positions SET current_stop = ?, note = COALESCE(?, note) WHERE position_id = ?');
        $note = trim((string)($body['note'] ?? '')) ?: null;
        $stmt->execute([$newStop, $note, $positionId]);
        $evt = $pdo->prepare(
            'INSERT INTO stc_position_events '
            . '(event_id, position_id, event_type, stop_after, note) '
            . "VALUES (?, ?, 'STOP_UPDATE', ?, ?)"
        );
        $evt->execute([stc_position_event_id($positionId, 'STOP_UPDATE'), $positionId, $newStop, $note]);
        $pdo->commit();
        stc_json([
            'ok' => true,
            'position' => stc_position_public(stc_position_row($pdo, $positionId)),
            'execution' => 'manual_only',
        ]);
    }

    $exitPrice = stc_num($body['exit_price'] ?? null, 'exit_price');
    $remaining = (float)$row['quantity'];
    $closeQty = $action === 'CLOSE'
        ? $remaining
        : stc_num($body['quantity_closed'] ?? null, 'quantity_closed');
    if ($closeQty > $remaining + 1e-12) {
        $pdo->rollBack();
        stc_json(['ok' => false, 'error' => 'quantity_closed_exceeds_open_quantity'], 409);
    }

    $entry = (float)$row['entry_price'];
    $side = (string)$row['side'];
    $sign = $side === 'LONG' ? 1.0 : -1.0;
    $value = stc_price_value_usd((string)$row['competition_id'], (string)$row['symbol'], $entry);
    $pnlDelta = ($exitPrice - $entry) * $sign * $closeQty * $value;
    $newQty = max(0.0, $remaining - $closeQty);
    $realizedTotal = (float)$row['realized_pnl_usd'] + $pnlDelta;
    $isClosed = $newQty <= 1e-12;
    $note = trim((string)($body['note'] ?? '')) ?: null;

    $stmt = $pdo->prepare(
        'UPDATE stc_positions SET quantity = ?, realized_pnl_usd = ?, status = ?, '
        . 'closed_at_utc = ?, exit_price = ?, note = COALESCE(?, note) WHERE position_id = ?'
    );
    $stmt->execute([
        $newQty,
        $realizedTotal,
        $isClosed ? 'CLOSED' : 'OPEN',
        $isClosed ? gmdate('Y-m-d H:i:s') : null,
        $isClosed ? $exitPrice : null,
        $note,
        $positionId,
    ]);
    $evt = $pdo->prepare(
        'INSERT INTO stc_position_events '
        . '(event_id, position_id, event_type, quantity_delta, price, realized_pnl_delta_usd, note) '
        . 'VALUES (?, ?, ?, ?, ?, ?, ?)'
    );
    $evt->execute([
        stc_position_event_id($positionId, $action),
        $positionId,
        $isClosed ? 'CLOSE' : 'PARTIAL',
        -$closeQty,
        $exitPrice,
        $pnlDelta,
        $note,
    ]);
    $pdo->commit();

    stc_json([
        'ok' => true,
        'position' => stc_position_public(stc_position_row($pdo, $positionId)),
        'realized_pnl_delta_usd' => $pnlDelta,
        'execution' => 'manual_only',
        'note' => 'Ledger updated after owner-confirmed manual platform action. STC sent no broker order.',
    ]);
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    stc_json(['ok' => false, 'error' => 'position_ledger_update_failed'], 500);
}
