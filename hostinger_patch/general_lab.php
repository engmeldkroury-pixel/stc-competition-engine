<?php
declare(strict_types=1);

require __DIR__ . '/cloud_control.php';

$role = stc_require_operator_auth($config);
$pdo = stc_pdo($config);
$method = strtoupper((string)($_SERVER['REQUEST_METHOD'] ?? 'GET'));

const STC_GENERAL_LAB_WAITING_SYMBOL = 'WAITING_FOR_SYMBOL_RESOLUTION';
const STC_GENERAL_LAB_WAITING_HISTORY = 'WAITING_FOR_EXACT_HISTORY';
const STC_GENERAL_LAB_RUNNING = 'RUNNING';
const STC_GENERAL_LAB_EVALUATED = 'EVALUATED';
const STC_GENERAL_LAB_FAILED = 'FAILED';
const STC_GENERAL_LAB_CANCELLED = 'CANCELLED';

function stc_general_lab_statuses(): array {
    return [
        STC_GENERAL_LAB_WAITING_SYMBOL,
        STC_GENERAL_LAB_WAITING_HISTORY,
        STC_GENERAL_LAB_RUNNING,
        STC_GENERAL_LAB_EVALUATED,
        STC_GENERAL_LAB_FAILED,
        STC_GENERAL_LAB_CANCELLED,
    ];
}

function stc_general_lab_require_role(string $role, array $allowed): void {
    if (!in_array($role, $allowed, true)) {
        stc_json(['ok' => false, 'error' => 'forbidden'], 403);
    }
}

function stc_general_lab_symbol(mixed $value, string $field = 'symbol'): string {
    $symbol = trim((string)$value);
    if ($symbol === '' || strlen($symbol) > 128 || preg_match('/[\x00-\x1F\x7F]/', $symbol) === 1) {
        stc_json(['ok' => false, 'error' => 'invalid_symbol', 'field' => $field], 400);
    }
    return strtoupper($symbol);
}

function stc_general_lab_request_id(string $symbol): string {
    return 'lab-' . substr(hash('sha256', $symbol . '|' . microtime(true) . '|' . bin2hex(random_bytes(12))), 0, 40);
}

function stc_general_lab_event_id(string $requestId, string $eventType): string {
    return 'labevt-' . substr(hash('sha256', $requestId . '|' . $eventType . '|' . microtime(true) . '|' . bin2hex(random_bytes(8))), 0, 40);
}

function stc_general_lab_event(
    PDO $pdo,
    string $requestId,
    string $eventType,
    string $statusAfter,
    string $actor,
    ?array $detail = null
): void {
    $stmt = $pdo->prepare(
        'INSERT INTO stc_general_lab_request_events '
        . '(event_id, request_id, event_type, status_after, actor, detail_json) '
        . 'VALUES (?, ?, ?, ?, ?, ?)'
    );
    $stmt->execute([
        stc_general_lab_event_id($requestId, $eventType),
        $requestId,
        $eventType,
        $statusAfter,
        $actor,
        $detail === null ? null : json_encode($detail, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
    ]);
}

function stc_general_lab_row(PDO $pdo, string $requestId, bool $forUpdate = false): ?array {
    $sql = 'SELECT * FROM stc_general_lab_requests WHERE request_id = ?';
    if ($forUpdate) {
        $sql .= ' FOR UPDATE';
    }
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$requestId]);
    $row = $stmt->fetch();
    return $row === false ? null : $row;
}

function stc_general_lab_public(array $row): array {
    $result = null;
    if (($row['result_json'] ?? null) !== null && (string)$row['result_json'] !== '') {
        $decoded = json_decode((string)$row['result_json'], true);
        if (is_array($decoded)) {
            $result = $decoded;
        }
    }
    return [
        'request_id' => (string)$row['request_id'],
        'requested_symbol' => (string)$row['requested_symbol'],
        'resolved_symbol' => $row['resolved_symbol'] === null ? null : (string)$row['resolved_symbol'],
        'status' => (string)$row['status'],
        'requested_by' => (string)$row['requested_by'],
        'requested_at_utc' => (string)$row['requested_at_utc'],
        'claimed_at_utc' => $row['claimed_at_utc'],
        'completed_at_utc' => $row['completed_at_utc'],
        'updated_at_utc' => (string)$row['updated_at_utc'],
        'note' => $row['note'],
        'result' => $result,
        'execution' => 'research_only',
        'live_authority' => false,
    ];
}

if ($method === 'GET') {
    $where = [];
    $params = [];

    $status = strtoupper(trim((string)($_GET['status'] ?? '')));
    if ($status !== '') {
        if (!in_array($status, stc_general_lab_statuses(), true)) {
            stc_json(['ok' => false, 'error' => 'invalid_status'], 400);
        }
        $where[] = 'status = ?';
        $params[] = $status;
    }

    $symbol = trim((string)($_GET['symbol'] ?? ''));
    if ($symbol !== '') {
        $symbol = stc_general_lab_symbol($symbol);
        $where[] = '(requested_symbol = ? OR resolved_symbol = ?)';
        $params[] = $symbol;
        $params[] = $symbol;
    }

    $limit = (int)($_GET['limit'] ?? 100);
    $limit = max(1, min($limit, 200));

    $sql = 'SELECT * FROM stc_general_lab_requests';
    if ($where !== []) {
        $sql .= ' WHERE ' . implode(' AND ', $where);
    }
    $sql .= ' ORDER BY updated_at_utc DESC, id DESC LIMIT ' . $limit;
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);

    $rows = [];
    while (($row = $stmt->fetch()) !== false) {
        $rows[] = stc_general_lab_public($row);
    }

    stc_json([
        'ok' => true,
        'requests' => $rows,
        'count' => count($rows),
        'execution' => 'research_only',
        'live_authority' => false,
        'data_source_policy' => 'exact_provider_history_required_no_silent_substitution',
    ]);
}

if ($method !== 'POST') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}

$body = stc_json_body();
$action = strtoupper(trim((string)($body['action'] ?? '')));

try {
    if ($action === 'REQUEST') {
        stc_general_lab_require_role($role, ['owner']);
        $symbol = stc_general_lab_symbol($body['symbol'] ?? '');
        $force = ($body['force'] ?? false) === true;

        if (!$force) {
            $stmt = $pdo->prepare(
                'SELECT * FROM stc_general_lab_requests '
                . 'WHERE requested_symbol = ? '
                . 'ORDER BY updated_at_utc DESC, id DESC LIMIT 1'
            );
            $stmt->execute([$symbol]);
            $existing = $stmt->fetch();
            if ($existing !== false && in_array((string)$existing['status'], [
                STC_GENERAL_LAB_WAITING_SYMBOL,
                STC_GENERAL_LAB_WAITING_HISTORY,
                STC_GENERAL_LAB_RUNNING,
                STC_GENERAL_LAB_EVALUATED,
            ], true)) {
                stc_json([
                    'ok' => true,
                    'created' => false,
                    'request' => stc_general_lab_public($existing),
                    'execution' => 'research_only',
                    'live_authority' => false,
                ]);
            }
        }

        $requestId = stc_general_lab_request_id($symbol);
        $status = strpos($symbol, ':') === false
            ? STC_GENERAL_LAB_WAITING_SYMBOL
            : STC_GENERAL_LAB_WAITING_HISTORY;
        $note = $status === STC_GENERAL_LAB_WAITING_SYMBOL
            ? 'Provider-qualified TradingView symbol must be resolved by an authorized data worker.'
            : 'Waiting for exact-provider TradingView history. No substitute provider is allowed.';

        $pdo->beginTransaction();
        $stmt = $pdo->prepare(
            'INSERT INTO stc_general_lab_requests '
            . '(request_id, requested_symbol, status, requested_by, note) '
            . "VALUES (?, ?, ?, 'owner', ?)"
        );
        $stmt->execute([$requestId, $symbol, $status, $note]);
        stc_general_lab_event($pdo, $requestId, 'REQUESTED', $status, 'owner', [
            'requested_symbol' => $symbol,
            'data_source_policy' => 'exact_provider_history_required_no_silent_substitution',
        ]);
        $pdo->commit();

        stc_json([
            'ok' => true,
            'created' => true,
            'request' => stc_general_lab_public(stc_general_lab_row($pdo, $requestId) ?? []),
            'execution' => 'research_only',
            'live_authority' => false,
        ], 201);
    }

    if ($action === 'CLAIM') {
        stc_general_lab_require_role($role, ['worker', 'owner']);
        $requestId = trim((string)($body['request_id'] ?? ''));
        if ($requestId === '') {
            stc_json(['ok' => false, 'error' => 'request_id_required'], 400);
        }
        $resolved = trim((string)($body['resolved_symbol'] ?? ''));
        $resolved = $resolved === '' ? null : stc_general_lab_symbol($resolved, 'resolved_symbol');

        $pdo->beginTransaction();
        $row = stc_general_lab_row($pdo, $requestId, true);
        if ($row === null) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'request_not_found'], 404);
        }
        if (!in_array((string)$row['status'], [STC_GENERAL_LAB_WAITING_SYMBOL, STC_GENERAL_LAB_WAITING_HISTORY, STC_GENERAL_LAB_FAILED], true)) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'request_not_claimable', 'status' => $row['status']], 409);
        }
        $effectiveResolved = $resolved ?? ($row['resolved_symbol'] === null ? null : (string)$row['resolved_symbol']);
        if ($effectiveResolved === null && strpos((string)$row['requested_symbol'], ':') !== false) {
            $effectiveResolved = (string)$row['requested_symbol'];
        }
        $stmt = $pdo->prepare(
            "UPDATE stc_general_lab_requests SET status = ?, resolved_symbol = ?, claimed_at_utc = UTC_TIMESTAMP(), "
            . "completed_at_utc = NULL, result_json = NULL, note = ? WHERE request_id = ?"
        );
        $stmt->execute([
            STC_GENERAL_LAB_RUNNING,
            $effectiveResolved,
            'Authorized research worker claimed request. Exact-provider history is required before evaluation.',
            $requestId,
        ]);
        stc_general_lab_event($pdo, $requestId, 'CLAIMED', STC_GENERAL_LAB_RUNNING, $role, [
            'resolved_symbol' => $effectiveResolved,
        ]);
        $pdo->commit();

        stc_json([
            'ok' => true,
            'request' => stc_general_lab_public(stc_general_lab_row($pdo, $requestId) ?? []),
            'execution' => 'research_only',
            'live_authority' => false,
        ]);
    }

    if ($action === 'COMPLETE') {
        stc_general_lab_require_role($role, ['worker', 'owner']);
        $requestId = trim((string)($body['request_id'] ?? ''));
        $result = $body['result'] ?? null;
        if ($requestId === '' || !is_array($result)) {
            stc_json(['ok' => false, 'error' => 'request_id_and_result_required'], 400);
        }
        $resolved = trim((string)($body['resolved_symbol'] ?? ''));
        $resolved = $resolved === '' ? null : stc_general_lab_symbol($resolved, 'resolved_symbol');

        $result['general_lab'] = true;
        $result['execution'] = 'research_only';
        $result['live_authority'] = false;
        $result['promotion_required'] = true;
        $resultJson = json_encode($result, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        if ($resultJson === false) {
            stc_json(['ok' => false, 'error' => 'result_json_encode_failed'], 400);
        }

        $pdo->beginTransaction();
        $row = stc_general_lab_row($pdo, $requestId, true);
        if ($row === null) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'request_not_found'], 404);
        }
        if ((string)$row['status'] !== STC_GENERAL_LAB_RUNNING) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'request_not_running', 'status' => $row['status']], 409);
        }
        $effectiveResolved = $resolved
            ?? ($row['resolved_symbol'] === null ? null : (string)$row['resolved_symbol'])
            ?? (string)$row['requested_symbol'];
        $stmt = $pdo->prepare(
            'UPDATE stc_general_lab_requests SET status = ?, resolved_symbol = ?, completed_at_utc = UTC_TIMESTAMP(), '
            . 'result_json = ?, note = ? WHERE request_id = ?'
        );
        $stmt->execute([
            STC_GENERAL_LAB_EVALUATED,
            $effectiveResolved,
            $resultJson,
            'Research evaluation completed. Result remains research-only and requires explicit promotion.',
            $requestId,
        ]);
        stc_general_lab_event($pdo, $requestId, 'COMPLETED', STC_GENERAL_LAB_EVALUATED, $role, [
            'resolved_symbol' => $effectiveResolved,
            'live_authority' => false,
        ]);
        $pdo->commit();

        stc_json([
            'ok' => true,
            'request' => stc_general_lab_public(stc_general_lab_row($pdo, $requestId) ?? []),
            'execution' => 'research_only',
            'live_authority' => false,
        ]);
    }

    if ($action === 'FAIL') {
        stc_general_lab_require_role($role, ['worker', 'owner']);
        $requestId = trim((string)($body['request_id'] ?? ''));
        if ($requestId === '') {
            stc_json(['ok' => false, 'error' => 'request_id_required'], 400);
        }
        $note = trim((string)($body['note'] ?? 'Research worker reported failure.'));
        $note = substr($note, 0, 1024);

        $pdo->beginTransaction();
        $row = stc_general_lab_row($pdo, $requestId, true);
        if ($row === null) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'request_not_found'], 404);
        }
        if ((string)$row['status'] === STC_GENERAL_LAB_EVALUATED) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'evaluated_request_immutable'], 409);
        }
        $stmt = $pdo->prepare(
            'UPDATE stc_general_lab_requests SET status = ?, completed_at_utc = UTC_TIMESTAMP(), note = ? WHERE request_id = ?'
        );
        $stmt->execute([STC_GENERAL_LAB_FAILED, $note, $requestId]);
        stc_general_lab_event($pdo, $requestId, 'FAILED', STC_GENERAL_LAB_FAILED, $role, ['note' => $note]);
        $pdo->commit();

        stc_json([
            'ok' => true,
            'request' => stc_general_lab_public(stc_general_lab_row($pdo, $requestId) ?? []),
            'execution' => 'research_only',
            'live_authority' => false,
        ]);
    }

    if ($action === 'CANCEL') {
        stc_general_lab_require_role($role, ['owner']);
        $requestId = trim((string)($body['request_id'] ?? ''));
        if ($requestId === '') {
            stc_json(['ok' => false, 'error' => 'request_id_required'], 400);
        }
        $pdo->beginTransaction();
        $row = stc_general_lab_row($pdo, $requestId, true);
        if ($row === null) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'request_not_found'], 404);
        }
        if ((string)$row['status'] === STC_GENERAL_LAB_EVALUATED) {
            $pdo->rollBack();
            stc_json(['ok' => false, 'error' => 'evaluated_request_immutable'], 409);
        }
        $stmt = $pdo->prepare(
            'UPDATE stc_general_lab_requests SET status = ?, completed_at_utc = UTC_TIMESTAMP(), note = ? WHERE request_id = ?'
        );
        $stmt->execute([
            STC_GENERAL_LAB_CANCELLED,
            'Cancelled by owner. No research or broker action will be performed.',
            $requestId,
        ]);
        stc_general_lab_event($pdo, $requestId, 'CANCELLED', STC_GENERAL_LAB_CANCELLED, 'owner');
        $pdo->commit();

        stc_json([
            'ok' => true,
            'request' => stc_general_lab_public(stc_general_lab_row($pdo, $requestId) ?? []),
            'execution' => 'research_only',
            'live_authority' => false,
        ]);
    }

    stc_json(['ok' => false, 'error' => 'unsupported_action'], 400);
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    stc_json(['ok' => false, 'error' => 'general_lab_request_failed'], 503);
}
