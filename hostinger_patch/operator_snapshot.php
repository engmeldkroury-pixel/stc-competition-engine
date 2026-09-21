<?php
declare(strict_types=1);
require __DIR__ . '/portfolio_control.php';
require_once __DIR__ . '/macro_control.php';

stc_require_owner_auth($config);
$pdo = stc_pdo($config);

try {
    $runtime = stc_runtime_control_row($pdo);
    $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
    $macroCalendar = stc_macro_calendar_fetch($config);

    $accounts = [];
    $accountStmt = $pdo->query(
        'SELECT competition_id, equity_usd, risk_fraction, source, version, updated_at_utc '
        . 'FROM stc_account_state ORDER BY competition_id'
    );
    while (($row = $accountStmt->fetch()) !== false) {
        $accounts[(string)$row['competition_id']] = [
            'competition_id' => (string)$row['competition_id'],
            'equity_usd' => (float)$row['equity_usd'],
            'risk_fraction' => (float)$row['risk_fraction'],
            'source' => (string)$row['source'],
            'version' => (int)$row['version'],
            'updated_at_utc' => $row['updated_at_utc'],
        ];
    }

    $openQty = [];
    $qtyStmt = $pdo->query(
        "SELECT competition_id, symbol, SUM(quantity) AS qty FROM stc_positions "
        . "WHERE status = 'OPEN' GROUP BY competition_id, symbol"
    );
    while (($row = $qtyStmt->fetch()) !== false) {
        $openQty[(string)$row['competition_id'] . '|' . (string)$row['symbol']] = (float)$row['qty'];
    }

    $riskByCompetition = [
        'capital-africa-sep-2026' => 0.0,
        'amp-futures-sep-2026' => 0.0,
    ];
    $riskByCluster = [];
    $riskStmt = $pdo->query(
        "SELECT competition_id, symbol, quantity, entry_price, initial_stop "
        . "FROM stc_positions WHERE status = 'OPEN'"
    );
    while (($row = $riskStmt->fetch()) !== false) {
        $cid = (string)$row['competition_id'];
        $symbol = (string)$row['symbol'];
        try {
            $value = stc_price_value_usd($cid, $symbol, (float)$row['entry_price']);
            $risk = abs((float)$row['entry_price'] - (float)$row['initial_stop'])
                * (float)$row['quantity'] * $value;
        } catch (Throwable $e) {
            $risk = 0.0;
        }
        $riskByCompetition[$cid] = (float)($riskByCompetition[$cid] ?? 0.0) + $risk;
        $clusterKey = $cid . '|' . stc_risk_cluster($symbol);
        $riskByCluster[$clusterKey] = (float)($riskByCluster[$clusterKey] ?? 0.0) + $risk;
    }

    $stmt = $pdo->prepare(
        'SELECT id, event_id, payload_json, result_json, analysis_completed_at_utc '
        . 'FROM stc_webhook_events '
        . "WHERE status = 'ingested' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.competition_id')) IN (?, ?) "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.action')) = 'signal_created' "
        . 'ORDER BY id DESC LIMIT 400'
    );
    $stmt->execute(['capital-africa-sep-2026', 'amp-futures-sep-2026']);

    $cards = [];
    $seen = [];

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

        $competitionId = (string)($payload['competition_id'] ?? '');
        $symbol = (string)($payload['symbol'] ?? '');
        $signalId = (string)($signal['signal_id'] ?? '');
        $seenKey = $competitionId . '|' . $symbol;
        if ($competitionId === '' || $symbol === '' || $signalId === '' || isset($seen[$seenKey])) {
            continue;
        }
        if (!stc_validate_signal_receipt($row, $payload, $result, $signalId)) {
            continue;
        }
        $seen[$seenKey] = true;

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
        $macroContext = stc_macro_risk_context($config, $symbol, $now, $macroCalendar);
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

        $sizing = null;
        if ($planValid && isset($accounts[$competitionId])) {
            try {
                $account = $accounts[$competitionId];
                $sizing = stc_propose_position_size(
                    $competitionId,
                    $symbol,
                    (float)$account['equity_usd'],
                    (float)$account['risk_fraction'],
                    (float)$lockedPlan['entry_mid'],
                    (float)$lockedPlan['initial_stop'],
                    (float)($openQty[$seenKey] ?? 0.0),
                    (float)($riskByCompetition[$competitionId] ?? 0.0),
                    (float)($riskByCluster[$competitionId . '|' . stc_risk_cluster($symbol)] ?? 0.0)
                );
            } catch (Throwable $e) {
                $sizing = [
                    'proposed_quantity' => 0.0,
                    'allowed_by_position_limit' => false,
                    'error' => $e->getMessage(),
                ];
            }
        }

        if ($manualReady && is_array($sizing)) {
            $manualReady = ($sizing['allowed_by_position_limit'] ?? false) === true
                && ($sizing['allowed_by_risk_policy'] ?? false) === true;
        }
        if ($manualReady && ($macroContext['block_new_approval'] ?? false) === true) {
            $manualReady = false;
        }

        $pendingPlanAction = null;
        if ($planValid && $validUntil !== null && $now >= $validUntil) {
            $pendingPlanAction = 'CANCEL_PENDING_PLAN';
        }

        $cards[] = [
            'event_id' => (string)$row['event_id'],
            'signal_id' => $signalId,
            'competition_id' => $competitionId,
            'symbol' => $symbol,
            'source_time' => (string)($payload['time'] ?? ''),
            'current_price' => (float)($payload['close'] ?? 0.0),
            'recommendation' => $recommendation,
            'composite_score' => (float)($signal['composite_score'] ?? 0.0),
            'confidence' => (float)($signal['confidence'] ?? 0.0),
            'reasons' => is_array($signal['reasons'] ?? null) ? $signal['reasons'] : [],
            'envelope' => $envelope,
            'locked_trade_plan' => $planValid ? $lockedPlan : null,
            'position_sizing' => $sizing,
            'macro_context' => $macroContext,
            'approval' => $approval,
            'manual_execution_ready' => $manualReady,
            'pending_plan_action' => $pendingPlanAction,
            'execution' => 'manual_only',
        ];
        if (count($cards) >= 80) {
            break;
        }
    }

    $cardByTarget = [];
    foreach ($cards as $card) {
        $cardByTarget[$card['competition_id'] . '|' . $card['symbol']] = $card;
    }

    $positions = [];
    $summary = [
        'capital-africa-sep-2026' => ['open_positions' => 0, 'initial_risk_usd' => 0.0, 'clusters' => []],
        'amp-futures-sep-2026' => ['open_positions' => 0, 'initial_risk_usd' => 0.0, 'clusters' => []],
    ];
    $rotationCandidates = [];

    $posStmt = $pdo->query(
        "SELECT * FROM stc_positions WHERE status = 'OPEN' ORDER BY opened_at_utc ASC, id ASC"
    );
    while (($positionRow = $posStmt->fetch()) !== false) {
        $public = stc_position_public($positionRow);
        $history = stc_recent_signal_states(
            $pdo,
            (string)$positionRow['competition_id'],
            (string)$positionRow['symbol'],
            3
        );
        $advice = stc_supervise_position($positionRow, $history);
        $public['management'] = $advice;
        $public['latest_signal_history'] = $history;

        try {
            $value = stc_price_value_usd(
                (string)$positionRow['competition_id'],
                (string)$positionRow['symbol'],
                (float)$positionRow['entry_price']
            );
            $risk = abs((float)$positionRow['entry_price'] - (float)$positionRow['initial_stop'])
                * (float)$positionRow['quantity'] * $value;
        } catch (Throwable $e) {
            $risk = 0.0;
        }
        $cid = (string)$positionRow['competition_id'];
        if (!isset($summary[$cid])) {
            $summary[$cid] = ['open_positions' => 0, 'initial_risk_usd' => 0.0, 'clusters' => []];
        }
        $summary[$cid]['open_positions'] += 1;
        $summary[$cid]['initial_risk_usd'] += $risk;
        $cluster = stc_risk_cluster((string)$positionRow['symbol']);
        if (!isset($summary[$cid]['clusters'][$cluster])) {
            $summary[$cid]['clusters'][$cluster] = ['open_positions' => 0, 'initial_risk_usd' => 0.0];
        }
        $summary[$cid]['clusters'][$cluster]['open_positions'] += 1;
        $summary[$cid]['clusters'][$cluster]['initial_risk_usd'] += $risk;

        if (($advice['thesis_degraded'] ?? false) === true) {
            $latestScore = 0.0;
            if ($history !== []) {
                $latest = $history[count($history) - 1];
                $latestScore = (float)$latest['composite_score'];
            }
            $alignment = (string)$positionRow['side'] === 'LONG' ? $latestScore : -$latestScore;
            $baseline = max(0.0, $alignment);
            $best = null;

            foreach ($cards as $candidate) {
                if ($candidate['competition_id'] !== $cid
                    || $candidate['symbol'] === (string)$positionRow['symbol']
                    || !in_array($candidate['recommendation'], ['LONG', 'SHORT'], true)
                    || !is_array($candidate['locked_trade_plan'])) {
                    continue;
                }
                $advantage = abs((float)$candidate['composite_score']) - $baseline;
                if ($advantage < 0.25) {
                    continue;
                }
                if ($best === null || $advantage > $best['score_advantage']) {
                    $best = [
                        'competition_id' => $cid,
                        'from_position_id' => (string)$positionRow['position_id'],
                        'from_symbol' => (string)$positionRow['symbol'],
                        'to_symbol' => (string)$candidate['symbol'],
                        'to_direction' => (string)$candidate['recommendation'],
                        'score_advantage' => $advantage,
                        'to_plan_id' => (string)$candidate['locked_trade_plan']['plan_id'],
                        'reason' => 'current_thesis_degraded_and_new_locked_plan_materially_stronger',
                    ];
                }
            }
            if ($best !== null) {
                $rotationCandidates[] = $best;
                $public['rotation_candidate'] = $best;
            } else {
                $public['rotation_candidate'] = null;
            }
        } else {
            $public['rotation_candidate'] = null;
        }

        $positions[] = $public;
    }

    stc_json([
        'ok' => true,
        'scope' => 'owner_console_dual_competition_portfolio_snapshot',
        'competitions' => ['capital-africa-sep-2026', 'amp-futures-sep-2026'],
        'observed_at_utc' => $now->format(DateTimeInterface::ATOM),
        'runtime_control' => $runtime,
        'macro_calendar_status' => [
            'ok' => ($macroCalendar['ok'] ?? false) === true,
            'error' => $macroCalendar['error'] ?? null,
            'source' => $macroCalendar['source'] ?? ($config['macro_calendar_url'] ?? 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'),
            'fetched_at_utc' => $macroCalendar['fetched_at_utc'] ?? null,
            'cache_age_seconds' => $macroCalendar['cache_age_seconds'] ?? null,
        ],
        'account_states' => array_values($accounts),
        'cards' => $cards,
        'portfolio' => [
            'positions' => $positions,
            'summary' => $summary,
            'risk_policy' => [
                'per_trade_risk_fraction_source' => 'owner_configured',
                'portfolio_cap_multiple_of_trade_risk' => 6.0,
                'correlation_cluster_cap_multiple_of_trade_risk' => 3.0,
                'cluster_model' => 'deterministic_asset_risk_groups_not_statistical_correlation',
                'official_competition_limit' => false,
            ],
            'rotation_candidates' => $rotationCandidates,
            'anti_churn_policy' => 'two_closed_bar_opposite_confirmation_and_material_score_advantage',
        ],
        'execution' => 'manual_only',
        'automatic_execution_available' => false,
    ]);
} catch (Throwable $e) {
    stc_json(['ok' => false, 'error' => 'operator_snapshot_unavailable'], 503);
}
