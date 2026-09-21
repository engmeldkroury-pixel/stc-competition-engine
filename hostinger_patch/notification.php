<?php
declare(strict_types=1);
require __DIR__ . '/notification_control.php';

$actor = stc_require_operator_auth($config);
$pdo = stc_pdo($config);
$method = strtoupper((string)($_SERVER['REQUEST_METHOD'] ?? 'GET'));

if ($method === 'GET') {
    if ($actor !== 'owner') {
        stc_json(['ok' => false, 'error' => 'owner_required'], 403);
    }
    $events = [];
    $stmt = $pdo->query(
        'SELECT notification_id, event_key, event_type, competition_id, symbol, position_id, '
        . 'severity, title, body_text, created_at_utc '
        . 'FROM stc_notification_events ORDER BY id DESC LIMIT 50'
    );
    while (($row = $stmt->fetch()) !== false) {
        $events[] = $row;
    }

    $deliveries = [];
    $d = $pdo->query(
        'SELECT notification_id, channel, status, http_code, error_text, attempted_at_utc '
        . 'FROM stc_notification_deliveries ORDER BY id DESC LIMIT 100'
    );
    while (($row = $d->fetch()) !== false) {
        $deliveries[] = $row;
    }

    stc_json([
        'ok' => true,
        'config' => stc_notification_config_status($config),
        'events' => $events,
        'deliveries' => $deliveries,
    ]);
}

if ($method !== 'POST') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}

$body = stc_json_body();
$action = strtolower(trim((string)($body['action'] ?? '')));

if ($action === 'signal') {
    $eventId = trim((string)($body['event_id'] ?? ''));
    if ($eventId === '') {
        stc_json(['ok' => false, 'error' => 'event_id_required'], 400);
    }
    stc_json(stc_notify_signal_event($pdo, $config, $eventId));
}

if ($action === 'portfolio') {
    stc_json(stc_notify_portfolio($pdo, $config));
}

if ($action === 'test') {
    if ($actor !== 'owner') {
        stc_json(['ok' => false, 'error' => 'owner_required'], 403);
    }
    $suffix = gmdate('YmdHis');
    $dispatch = stc_dispatch_notification($pdo, $config, [
        'event_key' => 'test:' . $suffix,
        'event_type' => 'OWNER_TEST',
        'competition_id' => null,
        'symbol' => null,
        'position_id' => null,
        'severity' => 'normal',
        'title' => 'STC notification test',
        'body' => 'If you received this message, the configured STC mobile/email notification channel is working.',
    ]);
    stc_json(['ok' => true, 'dispatch' => $dispatch]);
}

stc_json(['ok' => false, 'error' => 'unsupported_action'], 400);
