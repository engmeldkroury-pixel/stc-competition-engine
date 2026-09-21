<?php
declare(strict_types=1);
require __DIR__ . '/cloud_control.php';

$pdo = stc_pdo($config);

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    stc_require_operator_auth($config);
    try {
        stc_json(['ok' => true, 'runtime_control' => stc_runtime_control_row($pdo)]);
    } catch (Throwable $e) {
        stc_json(['ok' => false, 'error' => 'runtime_control_unavailable'], 503);
    }
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}
stc_require_owner_auth($config);
$data = stc_json_body((int)($config['max_body_bytes'] ?? 65536));
$allowed = ['safe_mode', 'kill_switch', 'reason'];
foreach ($data as $key => $_) {
    if (!in_array((string)$key, $allowed, true)) {
        stc_json(['ok' => false, 'error' => 'unsupported_field', 'field' => (string)$key], 400);
    }
}
if (!array_key_exists('safe_mode', $data) && !array_key_exists('kill_switch', $data) && !array_key_exists('reason', $data)) {
    stc_json(['ok' => false, 'error' => 'no_changes_requested'], 400);
}
$reason = array_key_exists('reason', $data) ? trim((string)$data['reason']) : null;
if ($reason !== null && strlen($reason) > 512) {
    stc_json(['ok' => false, 'error' => 'reason_too_long'], 400);
}

$pdo->beginTransaction();
try {
    $current = stc_runtime_control_row($pdo, true);
    $safe = array_key_exists('safe_mode', $data) ? stc_bool_input($data['safe_mode'], 'safe_mode') : $current['safe_mode'];
    $kill = array_key_exists('kill_switch', $data) ? stc_bool_input($data['kill_switch'], 'kill_switch') : $current['kill_switch'];
    $nextReason = array_key_exists('reason', $data) ? ($reason === '' ? null : $reason) : $current['reason'];
    $stmt = $pdo->prepare(
        'UPDATE stc_runtime_control SET safe_mode = ?, kill_switch = ?, reason = ?, version = version + 1, '
        . 'updated_at_utc = UTC_TIMESTAMP() WHERE id = 1 AND version = ?'
    );
    $stmt->execute([$safe ? 1 : 0, $kill ? 1 : 0, $nextReason, $current['version']]);
    if ($stmt->rowCount() !== 1) {
        throw new RuntimeException('runtime_control_conflict');
    }
    $updated = stc_runtime_control_row($pdo);
    $pdo->commit();
    stc_json(['ok' => true, 'runtime_control' => $updated, 'execution' => 'manual_only']);
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    stc_json(['ok' => false, 'error' => 'runtime_control_update_failed'], 409);
}
