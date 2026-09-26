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

    $signalRows = $stmt->fetchAll();
    $latestContextByTarget = [];
    $preferredRowIdByTarget = [];

    foreach ($signalRows as $candidateRow) {
        $candidatePayload = json_decode((string)$candidateRow['payload_json'], true);
        $candidateResult = json_decode((string)$candidateRow['result_json'], true);
        $candidateDecision = is_array($candidateResult) ? ($candidateResult['decision'] ?? null) : null;
        $candidateSignal = is_array($candidateDecision) ? ($candidateDecision['signal'] ?? null) : null;
        $candidateEnvelope = is_array($candidateDecision) ? ($candidateDecision['approval_envelope'] ?? null) : null;
        $candidatePlan = is_array($candidateDecision) ? ($candidateDecision['locked_trade_plan'] ?? null) : null;
        if (!is_array($candidatePayload) || !is_array($candidateResult) || !is_array($candidateDecision)
            || !is_array($candidateSignal) || !is_array($candidateEnvelope)) {
            continue;
        }
        $candidateCompetitionId = (string)($candidatePayload['competition_id'] ?? '');
        $candidateSymbol = (string)($candidatePayload['symbol'] ?? '');
        $candidateSignalId = (string)($candidateSignal['signal_id'] ?? '');
        if ($candidateCompetitionId === '' || $candidateSymbol === '' || $candidateSignalId === '') {
            continue;
        }
        if (!stc_validate_signal_receipt(
            $candidateRow,
            $candidatePayload,
            $candidateResult,
            $candidateSignalId
        )) {
            continue;
        }
        $candidateKey = $candidateCompetitionId . '|' . $candidateSymbol;
        if (!isset($latestContextByTarget[$candidateKey])) {
            $latestContextByTarget[$candidateKey] = [
                'id' => (int)$candidateRow['id'],
                'event_id' => (string)$candidateRow['event_id'],
                'payload' => $candidatePayload,
                'signal' => $candidateSignal,
            ];
        }
        if (isset($preferredRowIdByTarget[$candidateKey])) {
            continue;
        }
        $candidateValidUntil = stc_parse_utc((string)($candidateEnvelope['valid_until'] ?? ''));
        $candidatePlanValid = stc_signal_quality_gate_eligible($candidateSignal)
            && is_array($candidatePlan)
            && ($candidatePlan['levels_locked'] ?? false) === true
            && ($candidatePlan['execution'] ?? '') === 'manual_only'
            && $candidateValidUntil !== null
            && $now < $candidateValidUntil;
        if ($candidatePlanValid) {
            // Preserve the newest still-valid locked plan even when a newer
            // monitor-only bar arrives. This prevents an already presented
            // execution ticket from disappearing before expiry/reconciliation.
            $preferredRowIdByTarget[$candidateKey] = (int)$candidateRow['id'];
        }
    }

    foreach ($latestContextByTarget as $targetKey => $latestContext) {
        if (!isset($preferredRowIdByTarget[$targetKey])) {
            $preferredRowIdByTarget[$targetKey] = (int)$latestContext['id'];
        }
    }

    $cards = [];
    $seen = [];

    foreach ($signalRows as $row) {
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
        if ((int)$row['id'] !== (int)($preferredRowIdByTarget[$seenKey] ?? -1)) {
            continue;
        }
        $seen[$seenKey] = true;

        $latestRawContext = $latestContextByTarget[$seenKey] ?? null;
        $latestSignalContext = null;
        $latestApprovalCompatible = true;
        if (is_array($latestRawContext)) {
            $latestSignal = is_array($latestRawContext['signal'] ?? null)
                ? $latestRawContext['signal']
                : [];
            $compatibility = stc_locked_plan_latest_signal_compatibility($signal, $latestSignal);
            $sameEvent = (string)($latestRawContext['event_id'] ?? '') === (string)$row['event_id'];
            $latestApprovalCompatible = $sameEvent || (($compatibility['compatible'] ?? false) === true);
            $latestPayload = is_array($latestRawContext['payload'] ?? null)
                ? $latestRawContext['payload']
                : [];
            $latestSignalContext = [
                'event_id' => (string)($latestRawContext['event_id'] ?? ''),
                'source_time' => (string)($latestPayload['time'] ?? ''),
                'recommendation' => (string)($latestSignal['recommendation'] ?? 'WAIT'),
                'pre_gate_recommendation' => (string)($latestSignal['pre_gate_recommendation'] ?? ($latestSignal['recommendation'] ?? 'WAIT')),
                'setup_grade' => (string)($latestSignal['setup_grade'] ?? 'MONITOR_ONLY'),
                'setup_quality_score' => isset($latestSignal['setup_quality_score'])
                    ? (int)$latestSignal['setup_quality_score']
                    : null,
                'quality_gate_failures' => is_array($latestSignal['quality_gate_failures'] ?? null)
                    ? $latestSignal['quality_gate_failures']
                    : [],
                'same_event' => $sameEvent,
                'approval_compatible_with_locked_plan' => $latestApprovalCompatible,
                'compatibility' => $compatibility,
            ];
        }

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
            $approval['execution_ticket'] = null;
            $approval['position_sizing_at_approval'] = null;
            $evidenceId = trim((string)($approval['quote_evidence_id'] ?? ''));
            if ($evidenceId !== '') {
                $evidenceStmt = $pdo->prepare(
                    'SELECT details_json FROM stc_execution_evidence WHERE evidence_id = ? LIMIT 1'
                );
                $evidenceStmt->execute([$evidenceId]);
                $detailsRaw = $evidenceStmt->fetchColumn();
                if (is_string($detailsRaw) && $detailsRaw !== '') {
                    $details = json_decode($detailsRaw, true);
                    if (is_array($details)) {
                        if (is_array($details['execution_ticket'] ?? null)) {
                            $approval['execution_ticket'] = $details['execution_ticket'];
                        }
                        if (is_array($details['position_sizing'] ?? null)) {
                            $approval['position_sizing_at_approval'] = $details['position_sizing'];
                        }
                    }
                }
            }
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
        $hasOpenPosition = (float)($openQty[$seenKey] ?? 0.0) > 0.0;
        $macroContext = stc_macro_risk_context($config, $symbol, $now, $macroCalendar);
        $qualityGatePassed = stc_signal_quality_gate_eligible($signal);
        $lockedPlan = $decision['locked_trade_plan'] ?? null;
        $planValid = $qualityGatePassed
            && is_array($lockedPlan)
            && ($lockedPlan['levels_locked'] ?? false) === true
            && ($lockedPlan['execution'] ?? '') === 'manual_only';

        $decisionTimeframeMinutes = 15;
        if (is_array($lockedPlan)) {
            $rawTimeframe = trim((string)($lockedPlan['decision_timeframe'] ?? '15'));
            if (preg_match('/^\d+$/', $rawTimeframe) === 1) {
                $decisionTimeframeMinutes = max(1, (int)$rawTimeframe);
            }
        }
        $lossCooldown = stc_recent_same_direction_loss_cooldown(
            $pdo,
            $competitionId,
            $symbol,
            $recommendation,
            $now,
            $decisionTimeframeMinutes
        );

        $manualReady = !$runtime['safe_mode']
            && !$runtime['kill_switch']
            && in_array($recommendation, ['LONG', 'SHORT'], true)
            && !$hasOpenPosition
            && $planValid
            && $latestApprovalCompatible
            && (($lossCooldown['active'] ?? false) !== true)
            && $approvalFresh
            && $validUntil !== null
            && $now < $validUntil;

        $sizing = null;
        if ($planValid && !$hasOpenPosition && isset($accounts[$competitionId])) {
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
        $opportunityActive = false;
        $expiresInSeconds = null;
        $orderInstruction = null;
        if ($planValid && $validUntil !== null) {
            $expiresInSeconds = $validUntil->getTimestamp() - $now->getTimestamp();
            if ($now >= $validUntil) {
                $pendingPlanAction = 'CANCEL_PENDING_PLAN';
            } elseif ($hasOpenPosition) {
                $pendingPlanAction = 'MANAGE_EXISTING_POSITION';
            } elseif (($lossCooldown['active'] ?? false) === true) {
                $pendingPlanAction = 'WAIT_SAME_DIRECTION_LOSS_COOLDOWN';
            } elseif (in_array($recommendation, ['LONG', 'SHORT'], true)) {
                if ($latestApprovalCompatible) {
                    $opportunityActive = true;
                    try {
                        $orderInstruction = stc_entry_order_instruction(
                            $recommendation,
                            (float)($payload['close'] ?? 0.0),
                            (float)$lockedPlan['entry_min'],
                            (float)$lockedPlan['entry_max']
                        );
                    } catch (Throwable $e) {
                        $orderInstruction = [
                            'order_type' => 'UNKNOWN',
                            'side' => null,
                            'status' => 'instruction_unavailable',
                            'trigger_price' => null,
                            'limit_price' => null,
                            'explanation' => 'Order instruction could not be derived safely.',
                        ];
                    }
                } else {
                    $pendingPlanAction = 'PRESERVE_FOR_RECOVERY';
                }
            }
        }

        $sourceTime = stc_parse_utc((string)($payload['time'] ?? ''));
        $sourceCloseTime = stc_feed_bar_close_utc(
            (string)($payload['time'] ?? ''),
            (string)($payload['timeframe'] ?? '')
        );
        $sourceAgeSeconds = $sourceCloseTime === null
            ? null
            : max(0, $now->getTimestamp() - $sourceCloseTime->getTimestamp());

        $cards[] = [
            'event_id' => (string)$row['event_id'],
            'signal_id' => $signalId,
            'competition_id' => $competitionId,
            'symbol' => $symbol,
            'source_time' => (string)($payload['time'] ?? ''),
            'source_close_time' => $sourceCloseTime === null ? null : $sourceCloseTime->format(DateTimeInterface::ATOM),
            'current_price' => (float)($payload['close'] ?? 0.0),
            'recommendation' => $recommendation,
            'composite_score' => (float)($signal['composite_score'] ?? 0.0),
            'confidence' => (float)($signal['confidence'] ?? 0.0),
            'quality_gate_passed' => $qualityGatePassed,
            'setup_grade' => (string)($signal['setup_grade'] ?? 'MONITOR_ONLY'),
            'setup_quality_score' => isset($signal['setup_quality_score']) ? (int)$signal['setup_quality_score'] : null,
            'setup_quality_label' => (string)($signal['setup_quality_label'] ?? ''),
            'timeframe_confirmation' => is_array($signal['timeframe_confirmation'] ?? null) ? $signal['timeframe_confirmation'] : null,
            'live_family_evidence' => is_array($signal['live_family_evidence'] ?? null) ? $signal['live_family_evidence'] : null,
            'empirical_win_probability' => is_array($signal['empirical_win_probability'] ?? null) ? $signal['empirical_win_probability'] : [
                'status' => 'NOT_ATTACHED_TO_LIVE_SIGNAL',
                'estimated_probability' => null,
                'sample_size' => 0,
            ],
            'research_calibration' => is_array($signal['research_calibration'] ?? null) ? $signal['research_calibration'] : [
                'status' => 'UNAVAILABLE',
            ],
            'pre_gate_recommendation' => (string)($signal['pre_gate_recommendation'] ?? ($signal['recommendation'] ?? 'WAIT')),
            'quality_gate_failures' => is_array($signal['quality_gate_failures'] ?? null) ? $signal['quality_gate_failures'] : [],
            'reasons' => is_array($signal['reasons'] ?? null) ? $signal['reasons'] : [],
            'latest_signal_context' => $latestSignalContext,
            'envelope' => $envelope,
            'locked_trade_plan' => $planValid ? $lockedPlan : null,
            'position_sizing' => $sizing,
            'macro_context' => $macroContext,
            'loss_cooldown' => $lossCooldown,
            'approval' => $approval,
            'manual_execution_ready' => $manualReady,
            'has_open_position' => $hasOpenPosition,
            'open_position_quantity' => (float)($openQty[$seenKey] ?? 0.0),
            'entry_blocked_reason' => $hasOpenPosition ? 'existing_open_position_managed_by_portfolio_supervisor' : null,
            'opportunity_active' => $opportunityActive,
            'expires_in_seconds' => $expiresInSeconds,
            'source_age_seconds' => $sourceAgeSeconds,
            'order_instruction' => $orderInstruction,
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
    $summaryTemplate = [
        'open_positions' => 0,
        'initial_risk_usd' => 0.0,
        'open_unrealized_pnl_usd' => 0.0,
        'open_unrealized_known_positions' => 0,
        'open_unrealized_unknown_positions' => 0,
        'clusters' => [],
    ];
    $summary = [
        'capital-africa-sep-2026' => $summaryTemplate,
        'amp-futures-sep-2026' => $summaryTemplate,
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
            $summary[$cid] = $summaryTemplate;
        }
        $summary[$cid]['open_positions'] += 1;
        $summary[$cid]['initial_risk_usd'] += $risk;
        if (($advice['unrealized_pnl_usd'] ?? null) === null) {
            $summary[$cid]['open_unrealized_unknown_positions'] += 1;
        } else {
            $summary[$cid]['open_unrealized_known_positions'] += 1;
            $summary[$cid]['open_unrealized_pnl_usd'] += (float)$advice['unrealized_pnl_usd'];
        }
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
                    || !is_array($candidate['locked_trade_plan'])
                    || ($candidate['opportunity_active'] ?? false) !== true) {
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

    $closedPositions = [];
    $closedStmt = $pdo->query(
        "SELECT * FROM stc_positions WHERE status = 'CLOSED' "
        . "ORDER BY closed_at_utc DESC, updated_at_utc DESC, id DESC LIMIT 40"
    );
    while (($closedRow = $closedStmt->fetch()) !== false) {
        $closedPositions[] = stc_position_public($closedRow);
    }

    $newAuditBucket = static function (): array {
        return [
            'rows' => 0,
            'directional_rows' => 0,
            'historical_live_passed' => 0,
            'quality_bins' => [
                'gte_78' => 0,
                'gte_84' => 0,
                'gte_90' => 0,
            ],
            'strict_a_plus_proxy' => 0,
            'balanced_competition_proxy' => 0,
            'current_84_structural_proxy' => 0,
            'per_symbol' => [],
        ];
    };

    $gateAudit = [
        'scope' => 'recent_signal_created_rows_from_operator_snapshot_query',
        'rows_examined' => count($signalRows),
        // Legacy Capital-only summary retained for backward compatibility.
        'capital_rows' => 0,
        'capital_directional_rows' => 0,
        'historical_live_passed' => 0,
        'quality_bins' => [
            'gte_78' => 0,
            'gte_84' => 0,
            'gte_90' => 0,
        ],
        'strict_a_plus_proxy' => 0,
        'balanced_competition_proxy' => 0,
        'per_symbol' => [],
        'by_competition' => [
            'capital-africa-sep-2026' => $newAuditBucket(),
            'amp-futures-sep-2026' => $newAuditBucket(),
        ],
        'authority' => 'research_audit_only',
        'note' => 'Proxy counts compare recent stored signal context. They do not create or approve trades.',
        'current_84_structural_proxy_note' => 'Approximates the shared 84 competition gate from stored MTF/family/composite fields; live volatility/liquidity/blended-technical factors are not replayed here.',
    ];

    foreach ($signalRows as $auditRow) {
        $auditPayload = json_decode((string)$auditRow['payload_json'], true);
        $auditResult = json_decode((string)$auditRow['result_json'], true);
        $auditDecision = is_array($auditResult) ? ($auditResult['decision'] ?? null) : null;
        $auditSignal = is_array($auditDecision) ? ($auditDecision['signal'] ?? null) : null;
        if (!is_array($auditPayload) || !is_array($auditSignal)) {
            continue;
        }

        $competitionId = (string)($auditPayload['competition_id'] ?? '');
        if (!isset($gateAudit['by_competition'][$competitionId])) {
            continue;
        }
        $bucket =& $gateAudit['by_competition'][$competitionId];
        $bucket['rows']++;
        if ($competitionId === 'capital-africa-sep-2026') {
            $gateAudit['capital_rows']++;
        }

        $direction = (string)($auditSignal['pre_gate_recommendation']
            ?? $auditSignal['recommendation']
            ?? 'WAIT');
        if (!in_array($direction, ['LONG', 'SHORT'], true)) {
            unset($bucket);
            continue;
        }

        $bucket['directional_rows']++;
        if ($competitionId === 'capital-africa-sep-2026') {
            $gateAudit['capital_directional_rows']++;
        }

        $sign = $direction === 'LONG' ? 1.0 : -1.0;
        $quality = isset($auditSignal['setup_quality_score'])
            ? (int)$auditSignal['setup_quality_score']
            : 0;
        foreach ([78, 84, 90] as $floor) {
            if ($quality >= $floor) {
                $key = 'gte_' . $floor;
                $bucket['quality_bins'][$key]++;
                if ($competitionId === 'capital-africa-sep-2026') {
                    $gateAudit['quality_bins'][$key]++;
                }
            }
        }
        if (($auditSignal['quality_gate_passed'] ?? false) === true) {
            $bucket['historical_live_passed']++;
            if ($competitionId === 'capital-africa-sep-2026') {
                $gateAudit['historical_live_passed']++;
            }
        }

        $tf = is_array($auditSignal['timeframe_confirmation'] ?? null)
            ? $auditSignal['timeframe_confirmation']
            : [];
        $family = is_array($auditSignal['live_family_evidence'] ?? null)
            ? $auditSignal['live_family_evidence']
            : [];

        $aligned = static function ($value, float $sign): ?float {
            return is_numeric($value) ? $sign * (float)$value : null;
        };
        $entry = $aligned($tf['entry_score'] ?? null, $sign);
        $h1 = $aligned($tf['1h_score'] ?? null, $sign);
        $h2 = $aligned($tf['2h_score'] ?? null, $sign);
        $h4 = $aligned($tf['4h_score'] ?? null, $sign);
        $d1 = $aligned($tf['1d_score'] ?? null, $sign);
        $m1 = $aligned($tf['1m_score'] ?? null, $sign);
        $familyScore = $aligned($family['score'] ?? null, $sign);
        $familyAgreement = is_numeric($family['agreement_ratio'] ?? null)
            ? (float)$family['agreement_ratio']
            : null;
        $familyAligned = is_numeric($family['aligned_families'] ?? null)
            ? (int)$family['aligned_families']
            : null;
        $familyConflicts = is_numeric($family['conflicting_families'] ?? null)
            ? (int)$family['conflicting_families']
            : null;
        $composite = $aligned($auditSignal['composite_score'] ?? null, $sign);

        $strictProxy = $quality >= 90
            && $entry !== null && $entry >= 0.75
            && $h1 !== null && $h1 >= 0.70
            && $h2 !== null && $h2 >= 0.65
            && $h4 !== null && $h4 >= 0.65
            && $d1 !== null && $d1 >= 0.55
            && $m1 !== null && $m1 >= 0.55
            && $familyScore !== null && $familyScore >= 0.45
            && $familyAgreement !== null && $familyAgreement >= 0.65
            && $familyAligned !== null && $familyAligned >= 5
            && $familyConflicts !== null && $familyConflicts <= 2;

        $balancedProxy = $quality >= 84
            && $entry !== null && $entry >= 0.65
            && $h1 !== null && $h1 >= 0.60
            && $h2 !== null && $h2 >= 0.50
            && $h4 !== null && $h4 >= 0.50
            && $d1 !== null && $d1 >= 0.00
            && $m1 !== null && $m1 >= 0.00
            && $familyScore !== null && $familyScore >= 0.35
            && $familyAgreement !== null && $familyAgreement >= 0.65
            && $familyAligned !== null && $familyAligned >= 5
            && $familyConflicts !== null && $familyConflicts <= 1;

        $intradayAligned = 0;
        foreach ([$h1, $h2, $h4] as $intradayValue) {
            if ($intradayValue !== null && $intradayValue >= 0.35) {
                $intradayAligned++;
            }
        }
        $current84StructuralProxy = $quality >= 84
            && $entry !== null && $entry >= 0.55
            && $intradayAligned >= 2
            && $d1 !== null && $d1 >= -0.15
            && $m1 !== null && $m1 >= -0.15
            && $familyScore !== null && $familyScore >= 0.25
            && $familyAgreement !== null && $familyAgreement >= 0.55
            && $familyAligned !== null && $familyAligned >= 4
            && $familyConflicts !== null && $familyConflicts <= 3
            && $composite !== null && $composite >= 0.35;

        $symbol = (string)($auditPayload['symbol'] ?? 'UNKNOWN');
        if (!isset($bucket['per_symbol'][$symbol])) {
            $bucket['per_symbol'][$symbol] = [
                'directional_rows' => 0,
                'strict_a_plus_proxy' => 0,
                'balanced_competition_proxy' => 0,
                'current_84_structural_proxy' => 0,
            ];
        }
        $bucket['per_symbol'][$symbol]['directional_rows']++;
        if ($strictProxy) {
            $bucket['strict_a_plus_proxy']++;
            $bucket['per_symbol'][$symbol]['strict_a_plus_proxy']++;
            if ($competitionId === 'capital-africa-sep-2026') {
                $gateAudit['strict_a_plus_proxy']++;
            }
        }
        if ($balancedProxy) {
            $bucket['balanced_competition_proxy']++;
            $bucket['per_symbol'][$symbol]['balanced_competition_proxy']++;
            if ($competitionId === 'capital-africa-sep-2026') {
                $gateAudit['balanced_competition_proxy']++;
            }
        }
        if ($current84StructuralProxy) {
            $bucket['current_84_structural_proxy']++;
            $bucket['per_symbol'][$symbol]['current_84_structural_proxy']++;
        }

        if ($competitionId === 'capital-africa-sep-2026') {
            if (!isset($gateAudit['per_symbol'][$symbol])) {
                $gateAudit['per_symbol'][$symbol] = [
                    'directional_rows' => 0,
                    'strict_a_plus_proxy' => 0,
                    'balanced_competition_proxy' => 0,
                ];
            }
            $gateAudit['per_symbol'][$symbol]['directional_rows']++;
            if ($strictProxy) {
                $gateAudit['per_symbol'][$symbol]['strict_a_plus_proxy']++;
            }
            if ($balancedProxy) {
                $gateAudit['per_symbol'][$symbol]['balanced_competition_proxy']++;
            }
        }
        unset($bucket);
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
        'competition_rules' => [
            'capital-africa-sep-2026' => stc_competition_rule_summary('capital-africa-sep-2026'),
            'amp-futures-sep-2026' => stc_competition_rule_summary('amp-futures-sep-2026'),
        ],
        'competition_progress' => [
            'capital-africa-sep-2026' => stc_competition_progress($pdo, 'capital-africa-sep-2026'),
            'amp-futures-sep-2026' => stc_competition_progress($pdo, 'amp-futures-sep-2026'),
        ],
        'cards' => $cards,
        'competition_gate_audit' => $gateAudit,
        'portfolio' => [
            'positions' => $positions,
            'closed_positions_recent' => $closedPositions,
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
