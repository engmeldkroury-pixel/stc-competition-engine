<?php
/** CLI-only, consistent read-only snapshot. Never install as an HTTP endpoint. */
declare(strict_types=1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit(2); }
ini_set('display_errors', '0');
ini_set('log_errors', '0');
set_time_limit(90);

function stc_r8_select(array $value, array $keys): array {
    return array_intersect_key($value, array_fill_keys($keys, true));
}
function stc_r8_project(array $row): array {
    $payload = json_decode((string)$row['payload_json'], true, 512, JSON_THROW_ON_ERROR);
    $result = json_decode((string)$row['result_json'], true, 512, JSON_THROW_ON_ERROR);
    if (!is_array($payload) || !is_array($result)) { throw new RuntimeException('invalid_source'); }
    $decision = $result['decision'] ?? [];
    $out = stc_r8_select($result, ['event_id', 'status', 'receipt']);
    $out['decision'] = stc_r8_select($decision, ['action', 'execution', 'research_outcome_seed']);
    $out['decision']['signal'] = stc_r8_select($decision['signal'] ?? [], [
        'competition_id', 'symbol', 'signal_id', 'recommendation', 'pre_gate_recommendation',
        'quality_gate_failures', 'gate_diagnostics',
    ]);
    $out['decision']['approval_envelope'] = stc_r8_select($decision['approval_envelope'] ?? [], [
        'competition_id', 'symbol', 'issued_at', 'valid_until', 'entry_min', 'entry_max', 'reference_price',
    ]);
    // Preserve the complete original payload for independent receipt-hash validation.
    // Do not export IPs, raw request headers, account/position tables or configuration.
    return ['event_id'=>$row['event_id'], 'status'=>$row['status'], 'payload'=>$payload, 'result'=>$out];
}

if (getenv('STC_R8_PROJECTION_TEST') === '1') {
    try { echo json_encode(stc_r8_project(json_decode(stream_get_contents(STDIN), true, 512, JSON_THROW_ON_ERROR)), JSON_THROW_ON_ERROR | JSON_PRESERVE_ZERO_FRACTION); exit(0); }
    catch (Throwable $e) { fwrite(STDERR, 'projection_failed'); exit(2); }
}

$pdo = null;
try {
    $target = (string)($argv[1] ?? '');
    if (!preg_match('#^/home/[A-Za-z0-9_-]+/domains/stc\.feama\.site/public_html$#D', $target) || realpath($target) !== $target) {
        throw new RuntimeException('invalid_target');
    }
    require_once $target . '/cloud_control.php';
    $pdo = stc_pdo($config);
    $pdo->exec('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ');
    $pdo->exec('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY');
    $where = "status = 'ingested' AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.competition_id')) IN ('capital-africa-sep-2026', 'amp-futures-sep-2026') AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.action')) = 'signal_created'";
    $meta = $pdo->query('SELECT COUNT(*) AS matching_rows, MAX(id) AS max_id FROM stc_webhook_events WHERE ' . $where)->fetch(PDO::FETCH_ASSOC);
    $engine = $pdo->query("SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stc_webhook_events'")->fetchColumn();
    if (strtoupper((string)$engine) !== 'INNODB') { throw new RuntimeException('snapshot_engine_not_verified'); }
    $stmt = $pdo->query('SELECT id, event_id, status, payload_json, result_json FROM stc_webhook_events WHERE ' . $where . ' ORDER BY id DESC LIMIT 5000');
    $events = []; $excluded = 0; $firstId = null;
    while (($row = $stmt->fetch(PDO::FETCH_ASSOC)) !== false) {
        $firstId = (int)$row['id'];
        try { $events[] = stc_r8_project($row); }
        catch (Throwable $e) { $excluded++; }
    }
    $pdo->exec('ROLLBACK');
    echo json_encode(['ok'=>true, 'events'=>$events, 'source_snapshot'=>[
        'source'=>'SSH_CLI_READ_ONLY_MYSQL_SNAPSHOT', 'matching_rows'=>(int)$meta['matching_rows'],
        'max_id'=>(int)$meta['max_id'], 'min_selected_id'=>$firstId, 'row_limit'=>5000,
        'selected_rows'=>count($events), 'projection_failures'=>$excluded,
        'truncated'=>(int)$meta['matching_rows'] > 5000,
        'captured_at'=>gmdate('Y-m-d\TH:i:s\Z'), 'database_writes'=>false,
        'scope'=>'bounded_latest_signals_not_complete_market_or_execution_history',
    ]], JSON_THROW_ON_ERROR | JSON_PRESERVE_ZERO_FRACTION);
} catch (Throwable $e) {
    if ($pdo instanceof PDO && $pdo->inTransaction()) { $pdo->rollBack(); }
    // Never print exception messages, paths or credential-bearing connection details.
    fwrite(STDERR, 'STC read-only history export failed: ' . get_class($e) . "\n");
    exit(2);
}
