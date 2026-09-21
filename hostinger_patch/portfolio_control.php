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
            'action' => 'PROTECT',
            'urgency' => 'normal',
            'r_multiple' => $r,
            'unrealized_pnl_usd' => $unrealized,
            'thesis_degraded' => false,
            'suggested_stop' => $protective,
            'suggested_partial_fraction' => null,
            'reasons' => ['management_checkpoint_reached', 'single_take_profit_mode_keep_full_quantity_and_protect'],
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


function stc_max_open_position(string $competitionId, string $symbol): ?float {
    $capital = [
        'CAPITALCOM:BTCUSD' => 0.5,
        'CAPITALCOM:ETHUSD' => 15.0,
        'CAPITALCOM:DOGEUSD' => 500000.0,
        'CAPITALCOM:EURUSD' => 800000.0,
        'CAPITALCOM:AUDUSD' => 1200000.0,
        'CAPITALCOM:USDZAR' => 800000.0,
        'CAPITALCOM:XAUUSD' => 75.0,
        'CAPITALCOM:XAGUSD' => 5000.0,
        'CAPITALCOM:SPX500' => 40.0,
        'CAPITALCOM:NAS100' => 10.0,
    ];
    if ($competitionId === 'capital-africa-sep-2026') {
        return array_key_exists($symbol, $capital) ? $capital[$symbol] : null;
    }
    if ($competitionId === 'amp-futures-sep-2026') {
        $amp = [
            'CME_MINI:MES1!' => 500.0,
            'CME_MINI:MNQ1!' => 500.0,
            'CBOT_MINI:MYM1!' => 500.0,
            'CME_MINI:M2K1!' => 500.0,
            'NYMEX:MCL1!' => 100.0,
            'NYMEX:MNG1!' => 10.0,
            'COMEX_MINI:MGC1!' => 100.0,
            'COMEX_MINI:SIL1!' => 10.0,
            'CME_MINI:M6E1!' => 25.0,
            'CME_MINI:M6B1!' => 10.0,
            'CME_MINI:MJY1!' => 5.0,
            'CME_MINI:M6A1!' => 25.0,
            'CME:MBT1!' => 25.0,
            'CME:MET1!' => 25.0,
            'CBOT:ZN1!' => 100.0,
            'CBOT:ZB1!' => 100.0,
        ];
        return array_key_exists($symbol, $amp) ? $amp[$symbol] : null;
    }
    return null;
}

function stc_competition_min_trading_days(string $competitionId): int {
    if ($competitionId === 'capital-africa-sep-2026') {
        return 3;
    }
    if ($competitionId === 'amp-futures-sep-2026') {
        return 5;
    }
    throw new RuntimeException('unknown_competition');
}

function stc_competition_progress(PDO $pdo, string $competitionId): array {
    $requiredDays = stc_competition_min_trading_days($competitionId);

    $stmt = $pdo->prepare(
        "SELECT COUNT(*) AS total_entries, "
        . "COALESCE(SUM(status = 'OPEN'), 0) AS open_positions, "
        . "COALESCE(SUM(status = 'CLOSED'), 0) AS closed_positions, "
        . "COALESCE(SUM(realized_pnl_usd), 0) AS realized_pnl_usd "
        . "FROM stc_positions WHERE competition_id = ?"
    );
    $stmt->execute([$competitionId]);
    $row = $stmt->fetch() ?: [];

    $daysStmt = $pdo->prepare(
        "SELECT trade_date FROM ("
        . "SELECT DATE(opened_at_utc) AS trade_date FROM stc_positions WHERE competition_id = ? "
        . "UNION "
        . "SELECT DATE(e.created_at_utc) AS trade_date "
        . "FROM stc_position_events e "
        . "JOIN stc_positions p ON p.position_id = e.position_id "
        . "WHERE p.competition_id = ? AND e.event_type IN ('PARTIAL', 'CLOSE')"
        . ") q WHERE trade_date IS NOT NULL ORDER BY trade_date"
    );
    $daysStmt->execute([$competitionId, $competitionId]);
    $dates = [];
    while (($d = $daysStmt->fetchColumn()) !== false) {
        $dates[] = (string)$d;
    }

    $qualifyingDays = count($dates);
    $daysRemaining = max(0, $requiredDays - $qualifyingDays);

    $actionStmt = $pdo->prepare(
        "SELECT COUNT(*) FROM stc_position_events e "
        . "JOIN stc_positions p ON p.position_id = e.position_id "
        . "WHERE p.competition_id = ? AND e.event_type IN ('OPEN', 'PARTIAL', 'CLOSE')"
    );
    $actionStmt->execute([$competitionId]);
    $positionActions = (int)$actionStmt->fetchColumn();

    return [
        'competition_id' => $competitionId,
        'qualifying_trading_days' => $qualifyingDays,
        'required_trading_days' => $requiredDays,
        'days_remaining' => $daysRemaining,
        'eligible_by_days' => $daysRemaining === 0,
        'qualifying_dates_utc' => $dates,
        'total_entries' => (int)($row['total_entries'] ?? 0),
        'open_positions' => (int)($row['open_positions'] ?? 0),
        'closed_positions' => (int)($row['closed_positions'] ?? 0),
        'position_actions' => $positionActions,
        'realized_pnl_usd' => (float)($row['realized_pnl_usd'] ?? 0.0),
        'scoring_basis' => 'realized_pnl_closed_positions',
        'qualification_rule' => 'UTC day counts when an action results in opening or closing a position',
    ];
}

function stc_risk_cluster(string $symbol): string {
    $map = [
        'CAPITALCOM:BTCUSD' => 'crypto',
        'CAPITALCOM:ETHUSD' => 'crypto',
        'CAPITALCOM:DOGEUSD' => 'crypto',
        'CAPITALCOM:EURUSD' => 'fx_usd',
        'CAPITALCOM:AUDUSD' => 'fx_usd',
        'CAPITALCOM:USDZAR' => 'fx_usd',
        'CAPITALCOM:XAUUSD' => 'metals',
        'CAPITALCOM:XAGUSD' => 'metals',
        'CAPITALCOM:SPX500' => 'equity_indices',
        'CAPITALCOM:NAS100' => 'equity_indices',
        'CME_MINI:MES1!' => 'equity_indices',
        'CME_MINI:MNQ1!' => 'equity_indices',
        'CBOT_MINI:MYM1!' => 'equity_indices',
        'CME_MINI:M2K1!' => 'equity_indices',
        'NYMEX:MCL1!' => 'energy',
        'NYMEX:MNG1!' => 'energy',
        'COMEX_MINI:MGC1!' => 'metals',
        'COMEX_MINI:SIL1!' => 'metals',
        'CME_MINI:M6E1!' => 'fx_usd',
        'CME_MINI:M6B1!' => 'fx_usd',
        'CME_MINI:MJY1!' => 'fx_usd',
        'CME_MINI:M6A1!' => 'fx_usd',
        'CME:MBT1!' => 'crypto',
        'CME:MET1!' => 'crypto',
        'CBOT:ZN1!' => 'rates',
        'CBOT:ZB1!' => 'rates',
    ];
    return (string)($map[$symbol] ?? 'other');
}

function stc_commission_rate(string $competitionId): float {
    if ($competitionId === 'capital-africa-sep-2026') {
        return 0.0001;
    }
    if ($competitionId === 'amp-futures-sep-2026') {
        return 0.0;
    }
    throw new RuntimeException('unknown_competition');
}

function stc_propose_position_size(
    string $competitionId,
    string $symbol,
    float $equity,
    float $riskFraction,
    float $entryPrice,
    float $stopPrice,
    float $currentOpenQuantity,
    float $portfolioOpenRiskUsd = 0.0,
    float $clusterOpenRiskUsd = 0.0,
    float $portfolioRiskMultiple = 6.0,
    float $clusterRiskMultiple = 3.0
): array {
    if ($equity <= 0 || $entryPrice <= 0 || $stopPrice <= 0 || $riskFraction <= 0 || $riskFraction > 0.02) {
        throw new RuntimeException('invalid_sizing_input');
    }
    if ($portfolioOpenRiskUsd < 0 || $clusterOpenRiskUsd < 0 || $portfolioRiskMultiple < 1 || $clusterRiskMultiple < 1) {
        throw new RuntimeException('invalid_portfolio_risk_input');
    }
    $maxPosition = stc_max_open_position($competitionId, $symbol);
    if ($maxPosition === null) {
        throw new RuntimeException('symbol_not_allowed');
    }
    $value = stc_price_value_usd($competitionId, $symbol, $entryPrice);
    $stopRisk = abs($entryPrice - $stopPrice) * $value;
    if ($stopRisk <= 0) {
        throw new RuntimeException('invalid_stop_distance');
    }
    $commission = 2.0 * $entryPrice * $value * stc_commission_rate($competitionId);
    $totalRisk = $stopRisk + $commission;

    $configuredBudget = $equity * $riskFraction;
    $portfolioCap = $equity * $riskFraction * $portfolioRiskMultiple;
    $clusterCap = $equity * $riskFraction * $clusterRiskMultiple;
    $remainingPortfolio = max(0.0, $portfolioCap - $portfolioOpenRiskUsd);
    $remainingCluster = max(0.0, $clusterCap - $clusterOpenRiskUsd);
    $budget = min($configuredBudget, $remainingPortfolio, $remainingCluster);
    $limitedBy = [];
    if ($remainingPortfolio + 1e-12 < $configuredBudget) {
        $limitedBy[] = 'portfolio_risk_capacity';
    }
    if ($remainingCluster + 1e-12 < $configuredBudget) {
        $limitedBy[] = 'correlation_cluster_capacity';
    }

    $raw = $budget / $totalRisk;
    $room = max(0.0, $maxPosition - $currentOpenQuantity);

    if ($competitionId === 'amp-futures-sep-2026') {
        $qty = floor(min($raw, $room) + 1e-12);
        $integerContracts = true;
    } else {
        $qty = floor(min($raw, $room) * 1000000.0) / 1000000.0;
        $integerContracts = false;
    }

    $riskAmount = $qty * $totalRisk;
    $portfolioAfter = $portfolioOpenRiskUsd + $riskAmount;
    $clusterAfter = $clusterOpenRiskUsd + $riskAmount;
    $positionLimitAllowed = $qty > 0
        && ($currentOpenQuantity + $qty) <= $maxPosition + 1e-12;
    $riskPolicyAllowed = $qty > 0
        && $portfolioAfter <= $portfolioCap + 1e-9
        && $clusterAfter <= $clusterCap + 1e-9;

    return [
        'equity_usd' => $equity,
        'risk_fraction' => $riskFraction,
        'risk_budget_usd' => $budget,
        'entry_price' => $entryPrice,
        'stop_price' => $stopPrice,
        'price_value_usd_per_price_unit' => $value,
        'stop_risk_usd_per_unit' => $stopRisk,
        'estimated_round_trip_commission_usd_per_unit' => $commission,
        'proposed_quantity' => $qty,
        'max_position' => $maxPosition,
        'current_open_quantity' => $currentOpenQuantity,
        'projected_open_quantity' => $currentOpenQuantity + $qty,
        'risk_amount_usd' => $riskAmount,
        'risk_cluster' => stc_risk_cluster($symbol),
        'portfolio_risk_cap_usd' => $portfolioCap,
        'cluster_risk_cap_usd' => $clusterCap,
        'portfolio_risk_before_usd' => $portfolioOpenRiskUsd,
        'cluster_risk_before_usd' => $clusterOpenRiskUsd,
        'portfolio_risk_after_usd' => $portfolioAfter,
        'cluster_risk_after_usd' => $clusterAfter,
        'risk_budget_limited_by' => $limitedBy,
        'quantity_is_integer_contracts' => $integerContracts,
        'allowed_by_position_limit' => $positionLimitAllowed,
        'allowed_by_risk_policy' => $riskPolicyAllowed,
        'provisional_risk_setting' => true,
        'note' => 'STC sizing proposal only. Portfolio and correlation-cluster caps are STC risk controls, not official competition limits. Human approval and manual order entry required.',
    ];
}


function stc_entry_order_instruction(
    string $direction,
    float $currentPrice,
    float $entryMin,
    float $entryMax
): array {
    $direction = strtoupper(trim($direction));
    if (!in_array($direction, ['LONG', 'SHORT'], true)) {
        return [
            'order_type' => 'NONE',
            'side' => null,
            'status' => 'not_actionable',
            'trigger_price' => null,
            'limit_price' => null,
            'explanation' => 'No actionable LONG/SHORT plan.',
        ];
    }
    if ($currentPrice <= 0 || $entryMin <= 0 || $entryMax <= 0 || $entryMin > $entryMax) {
        throw new RuntimeException('invalid_order_instruction_input');
    }

    $mid = ($entryMin + $entryMax) / 2.0;
    if ($currentPrice >= $entryMin && $currentPrice <= $entryMax) {
        return [
            'order_type' => 'MARKET',
            'side' => $direction === 'LONG' ? 'BUY' : 'SELL',
            'status' => 'inside_entry_zone',
            'trigger_price' => null,
            'limit_price' => null,
            'reference_price' => $currentPrice,
            'explanation' => 'Latest confirmed price is inside the locked entry zone. Reconfirm the live price before manual execution.',
        ];
    }

    if ($direction === 'LONG') {
        if ($currentPrice > $entryMax) {
            return [
                'order_type' => 'BUY_LIMIT',
                'side' => 'BUY',
                'status' => 'wait_pullback',
                'trigger_price' => null,
                'limit_price' => $mid,
                'reference_price' => $currentPrice,
                'explanation' => 'Price is above the entry zone; wait for a pullback into the locked zone.',
            ];
        }
        return [
            'order_type' => 'BUY_STOP_LIMIT',
            'side' => 'BUY',
            'status' => 'wait_breakout_into_zone',
            'trigger_price' => $entryMin,
            'limit_price' => $entryMax,
            'reference_price' => $currentPrice,
            'explanation' => 'Price is below the entry zone; enter only if price rises into the locked zone.',
        ];
    }

    if ($currentPrice < $entryMin) {
        return [
            'order_type' => 'SELL_LIMIT',
            'side' => 'SELL',
            'status' => 'wait_rebound',
            'trigger_price' => null,
            'limit_price' => $mid,
            'reference_price' => $currentPrice,
            'explanation' => 'Price is below the entry zone; wait for a rebound into the locked zone.',
        ];
    }

    return [
        'order_type' => 'SELL_STOP_LIMIT',
        'side' => 'SELL',
        'status' => 'wait_breakdown_into_zone',
        'trigger_price' => $entryMax,
        'limit_price' => $entryMin,
        'reference_price' => $currentPrice,
        'explanation' => 'Price is above the entry zone; enter only if price falls into the locked zone.',
    ];
}


function stc_feed_bar_close_utc(string $timeValue, string $timeframe): ?DateTimeImmutable {
    $opened = stc_parse_utc($timeValue);
    if ($opened === null) {
        return null;
    }
    $tf = strtolower(trim($timeframe));
    $seconds = null;
    if (preg_match('/^\d+$/', $tf) === 1) {
        $seconds = ((int)$tf) * 60;
    } elseif (preg_match('/^(\d+)m$/', $tf, $m) === 1) {
        $seconds = ((int)$m[1]) * 60;
    } elseif (preg_match('/^(\d+)h$/', $tf, $m) === 1) {
        $seconds = ((int)$m[1]) * 3600;
    } elseif ($tf === '1d') {
        $seconds = 86400;
    }
    if ($seconds === null || $seconds <= 0) {
        return $opened;
    }
    return $opened->modify('+' . $seconds . ' seconds');
}
