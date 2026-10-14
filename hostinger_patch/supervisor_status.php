<?php
declare(strict_types=1);
require __DIR__ . '/cloud_control.php';

stc_require_owner_auth($config);
if (strtoupper((string)($_SERVER['REQUEST_METHOD'] ?? 'GET')) !== 'GET') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}
$pdo = stc_pdo($config);
$latest = $pdo->query(
    'SELECT minute_bucket_utc, started_at_utc, completed_at_utc, status, '
    . 'observed_signals, observed_positions, stale_count, reconciliation_count, '
    . 'errors_count FROM stc_supervisor_ticks ORDER BY id DESC LIMIT 1'
)->fetch(PDO::FETCH_ASSOC);

$summary = [];
$stateRows = $pdo->query(
    'SELECT watch_type, state, COUNT(*) AS count FROM stc_supervisor_watches '
    . 'GROUP BY watch_type, state ORDER BY watch_type, state'
)->fetchAll(PDO::FETCH_ASSOC);
foreach ($stateRows as $row) {
    $summary[] = [
        'watch_type' => (string)$row['watch_type'],
        'state' => (string)$row['state'],
        'count' => (int)$row['count'],
    ];
}
$healthy = false;
$lastAge = null;
if (is_array($latest)) {
    $completed = $latest['completed_at_utc'] === null
        ? null
        : new DateTimeImmutable((string)$latest['completed_at_utc'], new DateTimeZone('UTC'));
    if ($completed !== null) {
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $lastAge = $now->getTimestamp() - $completed->getTimestamp();
        $healthy = $latest['status'] === 'SUCCEEDED'
            && $lastAge >= 0 && $lastAge <= 150;
    }
}
stc_json([
    'ok' => true,
    'monitor_health' => $healthy ? 'TICK_RECEIPTS_RECENT' : 'MONITOR_UNHEALTHY_OR_NOT_SCHEDULED',
    'last_success_age_seconds' => $lastAge,
    'last_tick' => $latest === false ? null : $latest,
    'watch_state_counts' => $summary,
    'poll_interval_target_seconds' => 60,
    'poll_interval_proven' => false, // A GET cannot prove continuous scheduling.
    'live_market_quote_connected' => false,
    'external_tradingview_paper_fills_connected' => false,
    'email_enabled' => false,
    'execution' => 'manual_only',
    'automatic_execution_available' => false,
]);
