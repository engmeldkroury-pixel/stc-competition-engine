<?php
declare(strict_types=1);
require_once __DIR__ . '/_bootstrap.php';

function stc_require_owner_auth(array $config): void {
    $expected = (string)($config['owner_api_token'] ?? '');
    if ($expected === '' || $expected === 'CHANGE_ME_TO_A_DIFFERENT_LONG_RANDOM_SECRET') {
        stc_json(['ok' => false, 'error' => 'owner_api_not_configured'], 503);
    }
    $provided = stc_bearer_token();
    if ($provided === '' || !hash_equals($expected, $provided)) {
        header('WWW-Authenticate: Bearer');
        stc_json(['ok' => false, 'error' => 'unauthorized'], 401);
    }
}

function stc_require_operator_auth(array $config): string {
    $provided = stc_bearer_token();
    if ($provided === '') {
        header('WWW-Authenticate: Bearer');
        stc_json(['ok' => false, 'error' => 'unauthorized'], 401);
    }
    $owner = (string)($config['owner_api_token'] ?? '');
    if ($owner !== '' && $owner !== 'CHANGE_ME_TO_A_DIFFERENT_LONG_RANDOM_SECRET' && hash_equals($owner, $provided)) {
        return 'owner';
    }
    $worker = (string)($config['worker_api_token'] ?? '');
    if ($worker !== '' && $worker !== 'CHANGE_ME_TO_A_LONG_RANDOM_SECRET' && hash_equals($worker, $provided)) {
        return 'worker';
    }
    header('WWW-Authenticate: Bearer');
    stc_json(['ok' => false, 'error' => 'unauthorized'], 401);
}

function stc_bool_input(mixed $value, string $field): bool {
    if (!is_bool($value)) {
        stc_json(['ok' => false, 'error' => 'invalid_boolean', 'field' => $field], 400);
    }
    return $value;
}


function stc_signal_quality_gate_eligible(array $signal): bool {
    if (($signal['quality_gate_passed'] ?? false) !== true) {
        return false;
    }
    $grade = (string)($signal['setup_grade'] ?? '');
    if ($grade === 'A_PLUS') {
        return true;
    }
    return $grade === 'COMPETITION_OPPORTUNITY'
        && (string)($signal['competition_id'] ?? '') === 'capital-africa-sep-2026'
        && ($signal['competition_mode'] ?? false) === true;
}

function stc_provider_of_symbol(string $symbol): string {
    $parts = explode(':', $symbol, 2);
    return count($parts) === 2 ? strtoupper(trim($parts[0])) : '';
}

function stc_runtime_control_row(PDO $pdo, bool $forUpdate = false): array {
    $sql = 'SELECT id, safe_mode, kill_switch, reason, version, updated_at_utc FROM stc_runtime_control WHERE id = 1';
    if ($forUpdate) {
        $sql .= ' FOR UPDATE';
    }
    $row = $pdo->query($sql)->fetch();
    if ($row === false) {
        throw new RuntimeException('runtime_control_missing');
    }
    return [
        'safe_mode' => (bool)$row['safe_mode'],
        'kill_switch' => (bool)$row['kill_switch'],
        'reason' => $row['reason'],
        'version' => (int)$row['version'],
        'updated_at_utc' => $row['updated_at_utc'],
    ];
}

function stc_signal_event(PDO $pdo, string $signalId): ?array {
    $stmt = $pdo->prepare(
        'SELECT id, event_id, status, payload_json, result_json, analysis_completed_at_utc '
        . 'FROM stc_webhook_events '
        . "WHERE status = 'ingested' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.signal.signal_id')) = ? "
        . 'ORDER BY id DESC LIMIT 1'
    );
    $stmt->execute([$signalId]);
    $row = $stmt->fetch();
    if ($row === false) {
        return null;
    }
    $payload = json_decode((string)$row['payload_json'], true);
    $result = json_decode((string)$row['result_json'], true);
    if (!is_array($payload) || !is_array($result)) {
        return null;
    }
    $row['payload'] = $payload;
    $row['result'] = $result;
    return $row;
}

function stc_validate_signal_receipt(array $row, array $payload, array $result, string $signalId): bool {
    $receipt = $result['receipt'] ?? null;
    $decision = $result['decision'] ?? null;
    if (!is_array($receipt) || !is_array($decision)) {
        return false;
    }
    $hash = (string)($receipt['payload_sha256'] ?? '');
    return (string)($result['event_id'] ?? '') === (string)($row['event_id'] ?? '')
        && (string)($receipt['event_id'] ?? '') === (string)($row['event_id'] ?? '')
        && preg_match('/^[0-9a-f]{64}$/', $hash) === 1
        && (string)($receipt['competition_id'] ?? '') === (string)($payload['competition_id'] ?? '')
        && (string)($receipt['symbol'] ?? '') === (string)($payload['symbol'] ?? '')
        && (string)($receipt['event_time'] ?? '') === (string)($payload['time'] ?? '')
        && (string)($receipt['status'] ?? '') === (string)($result['status'] ?? '')
        && (string)($receipt['action'] ?? '') === (string)($decision['action'] ?? '')
        && (string)($receipt['signal_id'] ?? '') === $signalId
        && (string)($receipt['execution'] ?? '') === 'manual_only';
}

function stc_latest_signal_event_id(PDO $pdo, string $competitionId, string $symbol): ?string {
    $stmt = $pdo->prepare(
        'SELECT event_id FROM stc_webhook_events '
        . "WHERE status = 'ingested' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.decision.action')) = 'signal_created' "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.competition_id')) = ? "
        . "AND JSON_UNQUOTE(JSON_EXTRACT(payload_json, '$.symbol')) = ? "
        . 'ORDER BY id DESC LIMIT 1'
    );
    $stmt->execute([$competitionId, $symbol]);
    $row = $stmt->fetch();
    return $row === false ? null : (string)$row['event_id'];
}

function stc_parse_utc(string $value): ?DateTimeImmutable {
    try {
        $dt = new DateTimeImmutable($value);
        if (preg_match('/(?:Z|[+-]\d{2}:?\d{2})$/', $value) !== 1) {
            return null;
        }
        return $dt->setTimezone(new DateTimeZone('UTC'));
    } catch (Throwable $e) {
        return null;
    }
}

function stc_validate_owner_confirmation(array $confirmation, array $envelope, string $competitionId, string $symbol): array {
    $reasons = [];
    $observedRaw = trim((string)($confirmation['observed_at_utc'] ?? ''));
    $observed = stc_parse_utc($observedRaw);
    $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
    if ($observed === null) {
        $reasons[] = 'invalid_observed_at';
    } else {
        $age = $now->getTimestamp() - $observed->getTimestamp();
        if ($age < -5) {
            $reasons[] = 'evidence_from_future';
        } elseif ($age > 60) {
            $reasons[] = 'evidence_stale';
        }
    }
    $price = $confirmation['quote_price'] ?? null;
    if (!is_int($price) && !is_float($price)) {
        $reasons[] = 'invalid_quote_price';
        $price = null;
    } else {
        $price = (float)$price;
        if (!is_finite($price) || $price <= 0) {
            $reasons[] = 'invalid_quote_price';
            $price = null;
        }
    }
    if (($confirmation['market_status'] ?? null) !== 'open') {
        $reasons[] = 'market_not_open';
    }
    $min = (float)($envelope['entry_min'] ?? 0.0);
    $max = (float)($envelope['entry_max'] ?? 0.0);
    if ($price !== null && ($price < $min || $price > $max)) {
        $reasons[] = 'price_outside_envelope';
    }
    return [
        'valid' => $reasons === [],
        'reasons' => $reasons,
        'evidence' => [
            'source' => 'owner_platform_confirmation',
            'competition_id' => $competitionId,
            'symbol' => $symbol,
            'provider' => stc_provider_of_symbol($symbol),
            'observed_at_utc' => $observed === null ? null : $observed->format('Y-m-d H:i:s'),
            'quote_price' => $price,
            'market_status' => (string)($confirmation['market_status'] ?? 'unknown'),
        ],
    ];
}
