<?php
declare(strict_types=1);
require_once __DIR__ . '/cloud_control.php';

function stc_position_event_id(string $positionId, string $eventType): string {
    return 'posevt-' . substr(hash('sha256', $positionId . '|' . $eventType . '|' . microtime(true) . '|' . bin2hex(random_bytes(8))), 0, 40);
}

function stc_position_id(): string {
    return 'pos-' . substr(hash('sha256', microtime(true) . '|' . bin2hex(random_bytes(16))), 0, 40);
}

function stc_num(mixed $value, string $field, bool $allowZero = false): float {
    if (!is_int($value) && !is_float($value)) {
        stc_json(['ok' => false, 'error' => 'invalid_numeric', 'field' => $field], 400);
    }
    $n = (float)$value;
    if (!is_finite($n) || ($allowZero ? $n < 0 : $n <= 0)) {
        stc_json(['ok' => false, 'error' => 'invalid_numeric', 'field' => $field], 400);
    }
    return $n;
}

function stc_position_side(mixed $value): string {
    $side = strtoupper(trim((string)$value));
    if (!in_array($side, ['LONG', 'SHORT'], true)) {
        stc_json(['ok' => false, 'error' => 'invalid_side'], 400);
    }
    return $side;
}

function stc_price_value_usd(string $competitionId, string $symbol, float $referencePrice): float {
    if ($competitionId === 'amp-futures-sep-2026') {
        $map = [
            'CME_MINI:MES1!' => 5.0,
            'CME_MINI:MNQ1!' => 2.0,
            'CBOT_MINI:MYM1!' => 0.5,
            'CME_MINI:M2K1!' => 5.0,
            'NYMEX:MCL1!' => 100.0,
            'NYMEX:MNG1!' => 1000.0,
            'COMEX_MINI:MGC1!' => 10.0,
            'COMEX_MINI:SIL1!' => 1000.0,
            'CME_MINI:M6E1!' => 12500.0,
            'CME_MINI:M6B1!' => 6250.0,
            'CME_MINI:MJY1!' => 1250000.0,
            'CME_MINI:M6A1!' => 10000.0,
            'CME:MBT1!' => 0.1,
            'CME:MET1!' => 0.1,
            'CBOT:ZN1!' => 1000.0,
            'CBOT:ZB1!' => 1000.0,
        ];
        if (!array_key_exists($symbol, $map)) {
            throw new RuntimeException('amp_contract_value_unverified');
        }
        return $map[$symbol];
    }

    if ($competitionId === 'capital-africa-sep-2026') {
        if ($symbol === 'CAPITALCOM:USDZAR') {
            if ($referencePrice <= 0) {
                throw new RuntimeException('invalid_reference_price');
            }
            return 1.0 / $referencePrice;
        }
        return 1.0;
    }

    throw new RuntimeException('unknown_competition');
}

function stc_position_public(array $row): array {
    return [
        'position_id' => (string)$row['position_id'],
        'competition_id' => (string)$row['competition_id'],
        'symbol' => (string)$row['symbol'],
        'side' => (string)$row['side'],
        'origin' => (string)$row['origin'],
        'initial_quantity' => (float)$row['initial_quantity'],
        'quantity' => (float)$row['quantity'],
        'entry_price' => (float)$row['entry_price'],
        'initial_stop' => (float)$row['initial_stop'],
        'current_stop' => (float)$row['current_stop'],
        'target1' => (float)$row['target1'],
        'target2' => (float)$row['target2'],
        'source_plan_id' => $row['source_plan_id'],
        'source_signal_id' => $row['source_signal_id'],
        'status' => (string)$row['status'],
        'opened_at_utc' => $row['opened_at_utc'],
        'closed_at_utc' => $row['closed_at_utc'],
        'exit_price' => $row['exit_price'] === null ? null : (float)$row['exit_price'],
        'realized_pnl_usd' => (float)$row['realized_pnl_usd'],
        'note' => $row['note'],
        'updated_at_utc' => $row['updated_at_utc'],
    ];
}

function stc_position_row(PDO $pdo, string $positionId, bool $forUpdate = false): ?array {
    $sql = 'SELECT * FROM stc_positions WHERE position_id = ? LIMIT 1';
    if ($forUpdate) {
        $sql .= ' FOR UPDATE';
    }
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$positionId]);
    $row = $stmt->fetch();
    return $row === false ? null : $row;
}

function stc_plan_event(PDO $pdo, string $planId): ?array {
    $stmt = $pdo->prepare(
        'SELECT event_id, payload_json, result_json FROM stc_webhook_events '
        . "WHERE status = 'ingested' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.locked_trade_plan.plan_id')) = ? "
        . 'ORDER BY id DESC LIMIT 1'
    );
    $stmt->execute([$planId]);
    $row = $stmt->fetch();
    if ($row === false) {
        return null;
    }
    $payload = json_decode((string)$row['payload_json'], true);
    $result = json_decode((string)$row['result_json'], true);
    if (!is_array($payload) || !is_array($result)) {
        return null;
    }
    return ['row' => $row, 'payload' => $payload, 'result' => $result];
}

function stc_validate_stc_plan_position(PDO $pdo, array $body): array {
    $planId = trim((string)($body['source_plan_id'] ?? ''));
    if ($planId === '') {
        stc_json(['ok' => false, 'error' => 'source_plan_required'], 400);
    }
    $event = stc_plan_event($pdo, $planId);
    if ($event === null) {
        stc_json(['ok' => false, 'error' => 'source_plan_not_found'], 404);
    }
    $decision = $event['result']['decision'] ?? null;
    $plan = is_array($decision) ? ($decision['locked_trade_plan'] ?? null) : null;
    $signal = is_array($decision) ? ($decision['signal'] ?? null) : null;
    if (!is_array($plan) || !is_array($signal)) {
        stc_json(['ok' => false, 'error' => 'source_plan_invalid'], 409);
    }

    $competitionId = (string)($body['competition_id'] ?? '');
    $symbol = (string)($body['symbol'] ?? '');
    $side = stc_position_side($body['side'] ?? null);
    if ((string)($plan['competition_id'] ?? '') !== $competitionId
        || (string)($plan['symbol'] ?? '') !== $symbol
        || (string)($plan['direction'] ?? '') !== $side) {
        stc_json(['ok' => false, 'error' => 'source_plan_target_mismatch'], 409);
    }

    $signalId = (string)($signal['signal_id'] ?? '');
    $stmt = $pdo->prepare(
        'SELECT decision, decided_at_utc FROM stc_signal_approvals '
        . 'WHERE signal_id = ? ORDER BY id DESC LIMIT 1'
    );
    $stmt->execute([$signalId]);
    $approval = $stmt->fetch();
    if ($approval === false || (string)$approval['decision'] !== 'approved') {
        stc_json(['ok' => false, 'error' => 'approved_signal_required'], 409);
    }

    return ['plan' => $plan, 'signal_id' => $signalId];
}

function stc_recent_signal_states(PDO $pdo, string $competitionId, string $symbol, int $limit = 3): array {
    $limit = max(1, min($limit, 5));
    $stmt = $pdo->prepare(
        'SELECT payload_json, result_json FROM stc_webhook_events '
        . "WHERE status = 'ingested' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.competition_id')) = ? "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.symbol')) = ? "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.action')) = 'signal_created' "
        . 'ORDER BY id DESC LIMIT ' . $limit
    );
    $stmt->execute([$competitionId, $symbol]);
    $items = [];
    while (($row = $stmt->fetch()) !== false) {
        $payload = json_decode((string)$row['payload_json'], true);
        $result = json_decode((string)$row['result_json'], true);
        $signal = is_array($result) ? ($result['decision']['signal'] ?? null) : null;
        if (!is_array($payload) || !is_array($signal)) {
            continue;
        }
        $items[] = [
            'time' => (string)($payload['time'] ?? ''),
            'close' => (float)($payload['close'] ?? 0),
            'recommendation' => (string)($signal['recommendation'] ?? 'WAIT'),
            'composite_score' => (float)($signal['composite_score'] ?? 0),
        ];
    }
    return array_reverse($items);
}

function stc_supervise_position(array $position, array $history): array {
    if ($history === []) {
        return [
            'action' => 'HOLD',
            'urgency' => 'normal',
            'r_multiple' => null,
            'unrealized_pnl_usd' => null,
            'thesis_degraded' => false,
            'suggested_stop' => (float)$position['current_stop'],
            'suggested_partial_fraction' => null,
            'reasons' => ['no_fresh_signal_history'],
        ];
    }

    $latest = $history[count($history) - 1];
    $price = (float)$latest['close'];
    $side = (string)$position['side'];
    $entry = (float)$position['entry_price'];
    $initialStop = (float)$position['initial_stop'];
    $currentStop = (float)$position['current_stop'];
    $target1 = (float)$position['target1'];
    $target2 = (float)$position['target2'];
    $quantity = (float)$position['quantity'];
    $riskPrice = abs($entry - $initialStop);
    if ($riskPrice <= 0 || $price <= 0) {
        throw new RuntimeException('position_risk_invalid');
    }

    $sign = $side === 'LONG' ? 1.0 : -1.0;
    $pnlPrice = ($price - $entry) * $sign;
    $r = $pnlPrice / $riskPrice;
    try {
        $value = stc_price_value_usd((string)$position['competition_id'], (string)$position['symbol'], $entry);
        $unrealized = $pnlPrice * $quantity * $value;
    } catch (Throwable $e) {
        $unrealized = null;
    }

    $stopHit = $side === 'LONG' ? $price <= $currentStop : $price >= $currentStop;
    $target2Hit = $side === 'LONG' ? $price >= $target2 : $price <= $target2;
    $target1Hit = $side === 'LONG' ? $price >= $target1 : $price <= $target1;

    $opposite = $side === 'LONG' ? 'SHORT' : 'LONG';
    $recent = array_slice($history, -2);
    $oppositeConfirmed = count($recent) === 2;
    foreach ($recent as $item) {
        $score = (float)$item['composite_score'];
        if ((string)$item['recommendation'] !== $opposite) {
            $oppositeConfirmed = false;
            break;
        }
        if ($side === 'LONG' && $score > -0.55) {
            $oppositeConfirmed = false;
            break;
        }
        if ($side === 'SHORT' && $score < 0.55) {
            $oppositeConfirmed = false;
            break;
        }
    }

    if ($stopHit) {
        return [
            'action' => 'EXIT_NOW',
            'urgency' => 'critical',
            'r_multiple' => $r,
            'unrealized_pnl_usd' => $unrealized,
            'thesis_degraded' => true,
            'suggested_stop' => null,
            'suggested_partial_fraction' => null,
            'reasons' => ['current_price_breached_active_stop'],
        ];
    }

    if ($target2Hit) {
        return [
            'action' => 'EXIT_NOW',
            'urgency' => 'high',
            'r_multiple' => $r,
            'unrealized_pnl_usd' => $unrealized,
            'thesis_degraded' => false,
            'suggested_stop' => null,
            'suggested_partial_fraction' => null,
            'reasons' => ['target2_reached', 'protect_realized_competition_score'],
        ];
    }

    if ($oppositeConfirmed) {
        return [
            'action' => 'EXIT_NOW',
            'urgency' => 'high',
            'r_multiple' => $r,
            'unrealized_pnl_usd' => $unrealized,
            'thesis_degraded' => true,
            'suggested_stop' => null,
            'suggested_partial_fraction' => null,
            'reasons' => ['two_closed_bars_confirmed_strong_opposite_signal'],
        ];
    }

    if ($target1Hit) {
        $protective = $side === 'LONG' ? max($currentStop, $entry) : min($currentStop, $entry);
        return [
            'action' => 'PARTIAL_TAKE_PROFIT',
            'urgency' => 'normal',
            'r_multiple' => $r,
            'unrealized_pnl_usd' => $unrealized,
            'thesis_degraded' => false,
            'suggested_stop' => $protective,
            'suggested_partial_fraction' => 0.5,
            'reasons' => ['target1_reached', 'reduce_risk_and_protect_remainder'],
        ];
    }

    if ($r >= 1.0) {
        $lockR = $r < 1.5 ? 0.25 : 0.50;
        $suggested = $side === 'LONG'
            ? max($currentStop, $entry + $riskPrice * $lockR)
            : min($currentStop, $entry - $riskPrice * $lockR);
        return [
            'action' => 'PROTECT',
            'urgency' => 'normal',
            'r_multiple' => $r,
            'unrealized_pnl_usd' => $unrealized,
            'thesis_degraded' => false,
            'suggested_stop' => $suggested,
            'suggested_partial_fraction' => null,
            'reasons' => ['position_at_least_one_r_in_profit', 'tighten_protection_without_forced_rotation'],
        ];
    }

    return [
        'action' => 'HOLD',
        'urgency' => 'normal',
        'r_multiple' => $r,
        'unrealized_pnl_usd' => $unrealized,
        'thesis_degraded' => false,
        'suggested_stop' => $currentStop,
        'suggested_partial_fraction' => null,
        'reasons' => ['original_thesis_not_invalidated', 'no_confirmed_exit_condition'],
    ];
}
