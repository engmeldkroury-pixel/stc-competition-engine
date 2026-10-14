<?php
declare(strict_types=1);

/**
 * STC 60s host-side, CLI-ONLY read-only market/ledger observation.
 *
 * Invocation: php supervisor_60s.php --dry-run | --tick
 * --dry-run: only SELECTs; no writes
 * --tick: append durable audit receipts, no notifications or broker actions.
 * Actual 60-second schedule must be configured and proven separately.
 */

if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
require_once __DIR__ . '/notification_control.php';
require_once __DIR__ . '/supervisor_60s_core.php';

$mode = $argv[1] ?? '';
if (!in_array($mode, ['--dry-run', '--tick'], true)) {
    fwrite(STDERR, "usage: php supervisor_60s.php --dry-run|--tick\n");
    exit(2);
}

function stc_supervisor_watch_key(string $kind, string $ref): string {
    return hash('sha256', 'stc-supervisor-v1:' . $kind . ':' . $ref);
}

function stc_supervisor_read_watches(PDO $pdo, DateTimeImmutable $now): array {
    $watches = [];
    // Bounded state lookup prevents re-writing already terminal plan receipts.
    // A completed position's ledger remains stored separately.
    $priorRows = $pdo->query(
        "SELECT watch_key, state FROM stc_supervisor_watches "
        . "WHERE watch_type = 'POSITION' OR "
        . "(watch_type = 'SIGNAL' AND last_checked_utc >= "
        . "UTC_TIMESTAMP() - INTERVAL 1 DAY) "
        . "ORDER BY last_checked_utc DESC LIMIT 2501"
    )->fetchAll(PDO::FETCH_ASSOC);
    if (count($priorRows) > 2500) {
        throw new RuntimeException('watch_state_capacity_exceeded');
    }
    $priorStates = [];
    foreach ($priorRows as $priorRow) {
        $priorStates[(string)$priorRow['watch_key']] = (string)$priorRow['state'];
    }
    $positions = $pdo->query(
        "SELECT position_id, competition_id, symbol, status, current_stop, "
        . "opened_at_utc, source_plan_id FROM stc_positions "
        . "WHERE status = 'OPEN' ORDER BY id ASC LIMIT 501"
    )->fetchAll(PDO::FETCH_ASSOC);
    if (count($positions) > 500) {
        throw new RuntimeException('open_position_limit_exceeded');
    }
    $openPlans = [];
    foreach ($positions as $position) {
        $sourcePlan = trim((string)($position['source_plan_id'] ?? ''));
        if ($sourcePlan !== '') {
            $openPlans[$sourcePlan] = true;
        }
        $cid = (string)$position['competition_id'];
        $symbol = (string)$position['symbol'];
        // Expired/unregistered contests need only reconciliation, not 200
        // extra signal lookups every minute. No old-contest market polling.
        $isEligible = stc_notification_suppression_reason([
            'competition_id' => $cid, 'event_type' => 'POSITION_MANAGEMENT',
        ], $now) === null;
        $history = $isEligible
            ? stc_recent_signal_states($pdo, $cid, $symbol, 200)
            : [];
        $state = stc_supervisor_position_state($position, $history, $now);
        $ref = (string)$position['position_id'];
        $key = stc_supervisor_watch_key('POSITION', $ref);
        if ($state['state'] === 'ENDED_RECONCILIATION'
            && ($priorStates[$key] ?? '') === 'ENDED_RECONCILIATION') {
            // The owner can still reconcile via the durable OPEN position
            // ledger. Avoid pointless repeated 60-second archived receipts.
            continue;
        }
        $watches[$key] = [
            'watch_key' => $key, 'watch_type' => 'POSITION',
            'competition_id' => $cid, 'symbol' => $symbol, 'source_ref' => $ref,
            'state' => $state['state'], 'reason' => $state['reason'],
            'source_age_seconds' => $state['source_age_seconds'],
            'last_source_time_utc' => $state['source_at_utc'],
            'quote_verified' => false, 'external_fill_verified' => false,
            'manual_action' => $state['manual_action'], 'valid_until_utc' => null,
        ];
    }

    // All recent ingested locked plans are observed independently of the browser.
    // Restrict to 24h and explicitly expose a batching error rather than
    // pretending we examined more watches than capacity allows.
    $stmt = $pdo->query(
        "SELECT payload_json, result_json FROM stc_webhook_events "
        . "WHERE status = 'ingested' "
        . "AND analysis_completed_at_utc >= UTC_TIMESTAMP() - INTERVAL 2 HOUR "
        . "ORDER BY id DESC LIMIT 2001"
    );
    $recent = $stmt->fetchAll(PDO::FETCH_ASSOC);
    if (count($recent) > 2000) {
        throw new RuntimeException('signal_batch_limit_exceeded');
    }
    foreach ($recent as $row) {
        $payload = json_decode((string)($row['payload_json'] ?? ''), true);
        $result = json_decode((string)($row['result_json'] ?? ''), true);
        if (!is_array($payload) || !is_array($result)) {
            continue;
        }
        $decision = $result['decision'] ?? null;
        $plan = is_array($decision) ? ($decision['locked_trade_plan'] ?? null) : null;
        if (!is_array($plan)) {
            continue;
        }
        $cid = trim((string)($payload['competition_id'] ?? ''));
        $symbol = trim((string)($payload['symbol'] ?? ''));
        $planId = trim((string)($plan['plan_id'] ?? ''));
        if ($cid === '' || $symbol === '' || $planId === '') {
            continue;
        }
        $key = stc_supervisor_watch_key('SIGNAL', $cid . '|' . $planId);
        if (isset($watches[$key])) {
            continue;
        }
        $status = stc_supervisor_signal_state([
            'competition_id' => $cid,
            'plan_id' => $planId,
            'valid_until' => $plan['valid_until'] ?? null,
            'owner_recorded_open' => isset($openPlans[$planId]),
        ], $now);
        $previousState = $priorStates[$key] ?? null;
        if ($previousState !== null && in_array($previousState, [
            'EXPIRED_SIGNAL', 'OWNER_RECORDED_OPEN',
            'SIGNAL_TTL_UNVERIFIED', 'CONTEST_UNVERIFIED',
            'SIGNAL_DATA_INVALID',
        ], true)) {
            continue; // Already terminal: no resurrection or minute replay.
        }
        if ($status['state'] !== 'PENDING_MANUAL_CONFIRMATION'
            && $previousState === $status['state']) {
            continue; // Write terminal transition once, then stop polling.
        }
        $watches[$key] = [
            'watch_key' => $key, 'watch_type' => 'SIGNAL',
            'competition_id' => $cid, 'symbol' => $symbol, 'source_ref' => $planId,
            'state' => $status['state'], 'reason' => $status['reason'],
            'source_age_seconds' => null, 'last_source_time_utc' => null,
            'quote_verified' => false, 'external_fill_verified' => false,
            'manual_action' => $status['manual_action'],
            'valid_until_utc' => $status['valid_until_utc'],
        ];
    }

    // Resume existing nonterminal watches that no longer appear in the last
    // 24h source window; closure only from the owner-reported ledger.
    $tracked = $pdo->query(
        "SELECT watch_key, watch_type, competition_id, symbol, source_ref, state, "
        . "last_valid_until_utc FROM stc_supervisor_watches "
        . "WHERE state IN ('PENDING_MANUAL_CONFIRMATION', 'EXTERNAL_FILL_UNVERIFIED', "
        . "'DATA_STALE', 'SOURCE_UNVERIFIED') "
        . "OR (watch_type = 'POSITION' AND state = 'ENDED_RECONCILIATION' "
        . "AND last_checked_utc <= UTC_TIMESTAMP() - INTERVAL 1 HOUR) "
        . "ORDER BY last_checked_utc ASC LIMIT 501"
    )->fetchAll(PDO::FETCH_ASSOC);
    if (count($tracked) > 500) {
        throw new RuntimeException('persisted_watch_limit_exceeded');
    }
    $positionProbe = $pdo->prepare(
        "SELECT status FROM stc_positions WHERE position_id = ? LIMIT 1"
    );
    foreach ($tracked as $old) {
        $key = (string)$old['watch_key'];
        if (isset($watches[$key])) {
            continue;
        }
        $type = (string)$old['watch_type'];
        $ref = (string)$old['source_ref'];
        $state = 'SOURCE_UNVERIFIED';
        $reason = 'watch_missing_from_current_ingested_event_window';
        $manualAction = 'RECONCILE';
        if ($type === 'POSITION') {
            $positionProbe->execute([$ref]);
            $found = $positionProbe->fetchColumn();
            if ($found !== false && (string)$found !== 'OPEN') {
                $state = 'OWNER_RECORDED_CLOSED';
                $reason = 'position_ledger_status_not_open_requires_external_reconciliation';
            } elseif (stc_notification_suppression_reason([
                'competition_id' => (string)$old['competition_id'],
                'event_type' => 'POSITION_MANAGEMENT',
            ], $now) !== null) {
                $state = 'ENDED_RECONCILIATION';
                $reason = 'ended_or_unregistered_contest_unresolved_ledger';
            }
        } elseif ($type === 'SIGNAL') {
            $expiry = stc_supervisor_parse_time($old['last_valid_until_utc'] ?? null);
            if ($expiry !== null && $now >= $expiry) {
                $state = 'EXPIRED_SIGNAL';
                $reason = 'persisted_signal_ttl_elapsed';
                $manualAction = 'NO_ENTRY';
            }
        }
        $watches[$key] = [
            'watch_key' => $key, 'watch_type' => $type,
            'competition_id' => (string)$old['competition_id'],
            'symbol' => (string)$old['symbol'], 'source_ref' => $ref,
            'state' => $state, 'reason' => $reason,
            'source_age_seconds' => null, 'last_source_time_utc' => null,
            'quote_verified' => false, 'external_fill_verified' => false,
            'manual_action' => $manualAction,
            'valid_until_utc' => $old['last_valid_until_utc'] ?? null,
        ];
    }
    return array_values($watches);
}

function stc_supervisor_write_receipts(
    PDO $pdo,
    array $watches,
    DateTimeImmutable $now
): array {
    $utc = $now->format('Y-m-d H:i:s');
    $bucket = $now->format('Y-m-d H:i:00');
    $pdo->beginTransaction();
    try {
        $insertTick = $pdo->prepare(
            "INSERT IGNORE INTO stc_supervisor_ticks "
            . "(minute_bucket_utc, started_at_utc, status) VALUES (?, ?, 'STARTED')"
        );
        $insertTick->execute([$bucket, $utc]);
        $queryTick = $pdo->prepare(
            "SELECT id, status FROM stc_supervisor_ticks "
            . "WHERE minute_bucket_utc = ? FOR UPDATE"
        );
        $queryTick->execute([$bucket]);
        $tick = $queryTick->fetch(PDO::FETCH_ASSOC);
        if ($tick === false) {
            throw new RuntimeException('supervisor_tick_insert_failed');
        }
        if ($tick['status'] === 'SUCCEEDED') {
            $pdo->commit();
            return ['status' => 'ALREADY_RECORDED', 'minute_bucket' => $bucket];
        }
        $tickId = (int)$tick['id'];
        $upsert = $pdo->prepare(
            'INSERT INTO stc_supervisor_watches '
            . '(watch_key, watch_type, competition_id, symbol, source_ref, state, '
            . 'last_source_time_utc, last_verified_quote_utc, external_fill_verified, '
            . 'last_valid_until_utc, last_checked_utc, first_seen_utc, state_changed_utc) '
            . 'VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 0, ?, ?, ?, ?) '
            . 'ON DUPLICATE KEY UPDATE '
            . 'state_changed_utc = IF(state <> VALUES(state), VALUES(state_changed_utc), state_changed_utc), '
            . 'state=VALUES(state), last_checked_utc=VALUES(last_checked_utc), '
            . 'last_source_time_utc=VALUES(last_source_time_utc), '
            . 'last_valid_until_utc=COALESCE(VALUES(last_valid_until_utc), last_valid_until_utc)'
        );
        $receipt = $pdo->prepare(
            'INSERT IGNORE INTO stc_supervisor_watch_receipts '
            . '(tick_id, watch_key, watch_type, competition_id, state, observed_at_utc, '
            . 'source_age_seconds, quote_verified, external_fill_verified, '
            . 'suggested_manual_action, reason, detail_json) '
            . 'VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)'
        );
        $counts = ['signals' => 0, 'positions' => 0, 'stale' => 0, 'reconciliation' => 0];
        foreach ($watches as $watch) {
            $type = $watch['watch_type'];
            $counts[$type === 'POSITION' ? 'positions' : 'signals']++;
            if (in_array($watch['state'], ['DATA_STALE', 'SOURCE_UNVERIFIED'], true)) {
                $counts['stale']++;
            }
            if (stc_supervisor_is_reconciliation((string)$watch['state'])) {
                $counts['reconciliation']++;
            }
            $source = stc_supervisor_parse_time($watch['last_source_time_utc'] ?? null);
            $expires = stc_supervisor_parse_time($watch['valid_until_utc'] ?? null);
            $upsert->execute([
                $watch['watch_key'], $type, $watch['competition_id'],
                $watch['symbol'], $watch['source_ref'], $watch['state'],
                $source?->format('Y-m-d H:i:s'),
                $expires?->format('Y-m-d H:i:s'),
                $utc, $utc, $utc,
            ]);
            $detail = json_encode([
                'source_timestamp' => $watch['last_source_time_utc'],
                'live_quote_verified' => false,
                'external_paper_fill_verified' => false,
                'manual_only' => true,
            ], JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES);
            $receipt->execute([
                $tickId, $watch['watch_key'], $type, $watch['competition_id'],
                $watch['state'], $utc, $watch['source_age_seconds'],
                $watch['manual_action'], $watch['reason'], $detail,
            ]);
        }
        $update = $pdo->prepare(
            "UPDATE stc_supervisor_ticks SET status='SUCCEEDED', "
            . "completed_at_utc=UTC_TIMESTAMP(), observed_signals=?, "
            . "observed_positions=?, stale_count=?, reconciliation_count=?, "
            . "errors_count=0, detail='READ_ONLY_MANUAL_SUPERVISOR' WHERE id=?"
        );
        $update->execute([
            $counts['signals'], $counts['positions'], $counts['stale'],
            $counts['reconciliation'], $tickId,
        ]);
        // INSERT IGNORE is for replay idempotency only; never silently accept
        // a skipped receipt in a supposedly successful minute.
        $audit = $pdo->prepare(
            'SELECT COUNT(*) FROM stc_supervisor_watch_receipts WHERE tick_id = ?'
        );
        $audit->execute([$tickId]);
        if ((int)$audit->fetchColumn() !== count($watches)) {
            throw new RuntimeException('incomplete_supervisor_tick_receipts');
        }
        $pdo->commit();
        return ['status' => 'RECORDED', 'minute_bucket' => $bucket] + $counts;
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

$pdo = null;
$lockAcquired = false;
try {
    if (!isset($config) || !is_array($config)) {
        throw new RuntimeException('hosting_private_config_unavailable');
    }
    $pdo = stc_pdo($config);
    $now = stc_supervisor_utc_now();
    if ($mode === '--tick') {
        $locked = $pdo->query("SELECT GET_LOCK('stc_supervisor_60s_v1', 0)")->fetchColumn();
        if ((int)$locked !== 1) {
            echo json_encode(['ok' => true, 'status' => 'ALREADY_RUNNING']) . "\n";
            exit(0);
        }
        $lockAcquired = true;
    }
    $watches = stc_supervisor_read_watches($pdo, $now);
    if ($mode === '--dry-run') {
        $counts = [];
        foreach ($watches as $watch) {
            $state = (string)$watch['state'];
            $counts[$state] = ($counts[$state] ?? 0) + 1;
        }
        echo json_encode([
            'ok' => true, 'mode' => 'READ_ONLY_DRY_RUN',
            'watches' => count($watches),
            'states' => $counts,
            'no_messages_sent' => true, 'no_trades_executed' => true,
            'market_quote_feed' => 'NOT_CONNECTED',
            'external_paper_account_readback' => 'NOT_CONNECTED',
        ], JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . "\n";
    } else {
        $report = stc_supervisor_write_receipts($pdo, $watches, $now);
        echo json_encode([
            'ok' => true, 'mode' => 'DURABLE_AUDIT_TICK',
            'no_messages_sent' => true, 'no_trades_executed' => true,
            'live_quote_verified' => false,
        ] + $report, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . "\n";
    }
} catch (Throwable $e) {
    fwrite(STDERR, json_encode([
        'ok' => false, 'status' => 'MONITOR_UNHEALTHY',
        'error_class' => get_class($e),
        'no_messages_sent' => true, 'no_trades_executed' => true,
    ]) . "\n");
    exit(1);
} finally {
    if ($lockAcquired && $pdo instanceof PDO) {
        $pdo->query("SELECT RELEASE_LOCK('stc_supervisor_60s_v1')");
    }
}
