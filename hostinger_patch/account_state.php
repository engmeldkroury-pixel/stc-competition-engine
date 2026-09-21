<?php
declare(strict_types=1);
require __DIR__ . '/portfolio_control.php';

stc_require_owner_auth($config);
$pdo = stc_pdo($config);
$method = strtoupper((string)($_SERVER['REQUEST_METHOD'] ?? 'GET'));

function stc_account_state_rows(PDO $pdo): array {
    $rows = [];
    $stmt = $pdo->query(
        'SELECT competition_id, equity_usd, risk_fraction, source, version, updated_at_utc '
        . 'FROM stc_account_state ORDER BY competition_id'
    );
    while (($row = $stmt->fetch()) !== false) {
        $rows[] = [
            'competition_id' => (string)$row['competition_id'],
            'equity_usd' => (float)$row['equity_usd'],
            'risk_fraction' => (float)$row['risk_fraction'],
            'source' => (string)$row['source'],
            'version' => (int)$row['version'],
            'updated_at_utc' => $row['updated_at_utc'],
        ];
    }
    return $rows;
}

if ($method === 'GET') {
    stc_json([
        'ok' => true,
        'accounts' => stc_account_state_rows($pdo),
        'note' => 'Equity is owner-maintained because STC has no broker-account read access.',
    ]);
}

if ($method !== 'POST') {
    stc_json(['ok' => false, 'error' => 'method_not_allowed'], 405);
}

$body = stc_json_body();
$competitionId = trim((string)($body['competition_id'] ?? ''));
if (!in_array($competitionId, ['capital-africa-sep-2026', 'amp-futures-sep-2026'], true)) {
    stc_json(['ok' => false, 'error' => 'invalid_competition_id'], 400);
}
$equity = stc_num($body['equity_usd'] ?? null, 'equity_usd');
$riskFraction = $body['risk_fraction'] ?? null;
if (!is_int($riskFraction) && !is_float($riskFraction)) {
    stc_json(['ok' => false, 'error' => 'invalid_risk_fraction'], 400);
}
$riskFraction = (float)$riskFraction;
if (!is_finite($riskFraction) || $riskFraction <= 0 || $riskFraction > 0.02) {
    stc_json(['ok' => false, 'error' => 'risk_fraction_out_of_range'], 400);
}

$stmt = $pdo->prepare(
    'UPDATE stc_account_state SET equity_usd = ?, risk_fraction = ?, source = ?, version = version + 1 '
    . 'WHERE competition_id = ?'
);
$stmt->execute([$equity, $riskFraction, 'owner_manual', $competitionId]);
if ($stmt->rowCount() < 1) {
    stc_json(['ok' => false, 'error' => 'account_state_missing'], 409);
}

stc_json([
    'ok' => true,
    'accounts' => stc_account_state_rows($pdo),
    'note' => 'Account state updated manually. No broker action was taken.',
]);
