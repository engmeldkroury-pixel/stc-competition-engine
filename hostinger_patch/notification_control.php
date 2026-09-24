<?php
declare(strict_types=1);
require_once __DIR__ . '/portfolio_control.php';

function stc_notification_id(string $eventKey): string {
    return 'notify-' . substr(hash('sha256', $eventKey), 0, 40);
}

function stc_notification_config_status(array $config): array {
    $bot = trim((string)($config['telegram_bot_token'] ?? ''));
    $chat = trim((string)($config['telegram_chat_id'] ?? ''));
    $email = trim((string)($config['notification_email'] ?? ''));
    $from = trim((string)($config['notification_from_email'] ?? ''));
    return [
        'telegram_configured' => $bot !== '' && $chat !== ''
            && $bot !== 'CHANGE_ME_TELEGRAM_BOT_TOKEN'
            && $chat !== 'CHANGE_ME_TELEGRAM_CHAT_ID',
        'email_configured' => filter_var($email, FILTER_VALIDATE_EMAIL) !== false
            && filter_var($from, FILTER_VALIDATE_EMAIL) !== false,
    ];
}

function stc_record_delivery(
    PDO $pdo,
    string $notificationId,
    string $channel,
    string $status,
    ?int $httpCode = null,
    ?string $error = null
): void {
    $stmt = $pdo->prepare(
        'INSERT INTO stc_notification_deliveries '
        . '(notification_id, channel, status, http_code, error_text) VALUES (?, ?, ?, ?, ?)'
    );
    $stmt->execute([
        $notificationId,
        $channel,
        $status,
        $httpCode,
        $error === null ? null : substr($error, 0, 512),
    ]);
}

function stc_delivery_already_sent(PDO $pdo, string $notificationId, string $channel): bool {
    $stmt = $pdo->prepare(
        "SELECT 1 FROM stc_notification_deliveries "
        . "WHERE notification_id = ? AND channel = ? AND status = 'sent' LIMIT 1"
    );
    $stmt->execute([$notificationId, $channel]);
    return $stmt->fetchColumn() !== false;
}

function stc_send_telegram(array $config, string $title, string $body): array {
    $token = trim((string)($config['telegram_bot_token'] ?? ''));
    $chatId = trim((string)($config['telegram_chat_id'] ?? ''));
    if ($token === '' || $chatId === '') {
        return ['attempted' => false, 'ok' => false, 'http_code' => null, 'error' => 'telegram_not_configured'];
    }
    if (!function_exists('curl_init')) {
        return ['attempted' => false, 'ok' => false, 'http_code' => null, 'error' => 'curl_unavailable'];
    }

    $url = 'https://api.telegram.org/bot' . rawurlencode($token) . '/sendMessage';
    $payload = http_build_query([
        'chat_id' => $chatId,
        'text' => $title . "\n\n" . $body,
        'disable_web_page_preview' => 'true',
    ], '', '&', PHP_QUERY_RFC3986);

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT_MS => 1500,
        CURLOPT_TIMEOUT_MS => 3500,
        CURLOPT_NOSIGNAL => true,
    ]);
    $response = curl_exec($ch);
    $errno = curl_errno($ch);
    $error = $errno ? curl_error($ch) : null;
    $http = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);

    $ok = $errno === 0 && $http >= 200 && $http < 300;
    if (!$ok && $error === null && is_string($response)) {
        $decoded = json_decode($response, true);
        $error = is_array($decoded) ? (string)($decoded['description'] ?? 'telegram_delivery_failed') : 'telegram_delivery_failed';
    }
    return [
        'attempted' => true,
        'ok' => $ok,
        'http_code' => $http > 0 ? $http : null,
        'error' => $error,
    ];
}

function stc_send_email(array $config, string $title, string $body): array {
    $to = trim((string)($config['notification_email'] ?? ''));
    $from = trim((string)($config['notification_from_email'] ?? ''));
    if (filter_var($to, FILTER_VALIDATE_EMAIL) === false || filter_var($from, FILTER_VALIDATE_EMAIL) === false) {
        return ['attempted' => false, 'ok' => false, 'http_code' => null, 'error' => 'email_not_configured'];
    }
    $headers = [
        'From: STC <' . $from . '>',
        'Reply-To: ' . $from,
        'Content-Type: text/plain; charset=UTF-8',
        'X-Mailer: STC-Competition-Engine',
    ];
    $ok = @mail($to, $title, $body, implode("\r\n", $headers));
    return [
        'attempted' => true,
        'ok' => $ok,
        'http_code' => null,
        'error' => $ok ? null : 'mail_function_failed',
    ];
}

function stc_dispatch_notification(PDO $pdo, array $config, array $event): array {
    $eventKey = (string)$event['event_key'];
    $notificationId = stc_notification_id($eventKey);
    $stmt = $pdo->prepare(
        'INSERT IGNORE INTO stc_notification_events '
        . '(notification_id, event_key, event_type, competition_id, symbol, position_id, severity, title, body_text) '
        . 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    $stmt->execute([
        $notificationId,
        $eventKey,
        (string)$event['event_type'],
        $event['competition_id'] ?? null,
        $event['symbol'] ?? null,
        $event['position_id'] ?? null,
        $event['severity'] ?? 'normal',
        (string)$event['title'],
        (string)$event['body'],
    ]);

    $configStatus = stc_notification_config_status($config);
    $results = [];
    $deliveredAny = false;

    if ($configStatus['telegram_configured']) {
        if (stc_delivery_already_sent($pdo, $notificationId, 'telegram')) {
            $results['telegram'] = ['attempted' => false, 'ok' => true, 'status' => 'already_sent'];
            $deliveredAny = true;
        } else {
            $result = stc_send_telegram($config, (string)$event['title'], (string)$event['body']);
            stc_record_delivery(
                $pdo,
                $notificationId,
                'telegram',
                $result['ok'] ? 'sent' : 'failed',
                $result['http_code'],
                $result['error']
            );
            $results['telegram'] = $result;
            $deliveredAny = $deliveredAny || $result['ok'];
        }
    }

    if ($configStatus['email_configured']) {
        if (stc_delivery_already_sent($pdo, $notificationId, 'email')) {
            $results['email'] = ['attempted' => false, 'ok' => true, 'status' => 'already_sent'];
            $deliveredAny = true;
        } else {
            $result = stc_send_email($config, (string)$event['title'], (string)$event['body']);
            stc_record_delivery(
                $pdo,
                $notificationId,
                'email',
                $result['ok'] ? 'sent' : 'failed',
                null,
                $result['error']
            );
            $results['email'] = $result;
            $deliveredAny = $deliveredAny || $result['ok'];
        }
    }

    return [
        'notification_id' => $notificationId,
        'event_key' => $eventKey,
        'new_event' => $stmt->rowCount() === 1,
        'delivered_any' => $deliveredAny,
        'channels' => $results,
        'config' => $configStatus,
    ];
}

function stc_account_state_for(PDO $pdo, string $competitionId): ?array {
    $stmt = $pdo->prepare(
        'SELECT competition_id, equity_usd, risk_fraction, source, version, updated_at_utc '
        . 'FROM stc_account_state WHERE competition_id = ? LIMIT 1'
    );
    $stmt->execute([$competitionId]);
    $row = $stmt->fetch();
    return $row === false ? null : $row;
}

function stc_notify_signal_event(PDO $pdo, array $config, string $eventId): array {
    $stmt = $pdo->prepare(
        'SELECT payload_json, result_json FROM stc_webhook_events '
        . "WHERE event_id = ? AND status = 'ingested' LIMIT 1"
    );
    $stmt->execute([$eventId]);
    $row = $stmt->fetch();
    if ($row === false) {
        return ['ok' => false, 'skipped' => true, 'reason' => 'event_not_ingested'];
    }
    $payload = json_decode((string)$row['payload_json'], true);
    $result = json_decode((string)$row['result_json'], true);
    $decision = is_array($result) ? ($result['decision'] ?? null) : null;
    $signal = is_array($decision) ? ($decision['signal'] ?? null) : null;
    $plan = is_array($decision) ? ($decision['locked_trade_plan'] ?? null) : null;
    if (!is_array($payload) || !is_array($signal) || !is_array($plan)) {
        return ['ok' => true, 'skipped' => true, 'reason' => 'no_locked_plan'];
    }
    $direction = (string)($signal['recommendation'] ?? 'WAIT');
    if (!in_array($direction, ['LONG', 'SHORT'], true)) {
        return ['ok' => true, 'skipped' => true, 'reason' => 'wait_signal'];
    }
    $setupGrade = (string)($signal['setup_grade'] ?? '');
    if (!stc_signal_quality_gate_eligible($signal)) {
        return ['ok' => true, 'skipped' => true, 'reason' => 'quality_gate_not_passed'];
    }

    $validUntil = stc_parse_utc((string)($plan['valid_until'] ?? ''));
    $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
    if ($validUntil === null || $now >= $validUntil) {
        return ['ok' => true, 'skipped' => true, 'reason' => 'expired_plan'];
    }
    $minutesLeft = max(1, (int)ceil(($validUntil->getTimestamp() - $now->getTimestamp()) / 60));

    $competitionId = (string)$payload['competition_id'];
    $symbol = (string)$payload['symbol'];
    $account = stc_account_state_for($pdo, $competitionId);
    $sizingText = 'Quantity: update account state / sizing before manual entry.';
    if (is_array($account)) {
        $openStmt = $pdo->prepare(
            "SELECT COALESCE(SUM(quantity), 0) FROM stc_positions "
            . "WHERE status = 'OPEN' AND competition_id = ? AND symbol = ?"
        );
        $openStmt->execute([$competitionId, $symbol]);
        $openQty = (float)$openStmt->fetchColumn();
        try {
            $sizing = stc_propose_position_size(
                $competitionId,
                $symbol,
                (float)$account['equity_usd'],
                (float)$account['risk_fraction'],
                (float)$plan['entry_mid'],
                (float)$plan['initial_stop'],
                $openQty
            );
            $riskPct = ((float)$account['equity_usd']) > 0
                ? ((float)$sizing['risk_amount_usd'] / (float)$account['equity_usd']) * 100.0
                : 0.0;
            $sizingText = 'Quantity: ' . rtrim(rtrim(number_format((float)$sizing['proposed_quantity'], 6, '.', ''), '0'), '.')
                . ' | Risk: $' . number_format((float)$sizing['risk_amount_usd'], 2, '.', '')
                . ' (' . number_format($riskPct, 3, '.', '') . '%)'
                . ' | Official max: ' . rtrim(rtrim(number_format((float)$sizing['max_position'], 6, '.', ''), '0'), '.');
        } catch (Throwable $e) {
            $sizingText = 'Sizing blocked: ' . $e->getMessage();
        }
    }

    $order = stc_entry_order_instruction(
        $direction,
        (float)($payload['close'] ?? 0.0),
        (float)$plan['entry_min'],
        (float)$plan['entry_max']
    );
    $orderText = trim(((string)($order['side'] ?? '')) . ' ' . (string)($order['order_type'] ?? 'ENTRY'));
    if (($order['trigger_price'] ?? null) !== null) {
        $orderText .= ' | trigger ' . $order['trigger_price'];
    }
    if (($order['limit_price'] ?? null) !== null) {
        $orderText .= ' | limit ' . $order['limit_price'];
    }

    $label = $competitionId === 'amp-futures-sep-2026' ? 'AMP Futures' : 'Capital.com Africa';
    $title = 'STC NEW PLAN • ' . $label . ' • ' . $direction;
    $qualityScore = isset($signal['setup_quality_score']) ? (int)$signal['setup_quality_score'] : null;
    $tf = is_array($signal['timeframe_confirmation'] ?? null) ? $signal['timeframe_confirmation'] : [];
    $tfParts = [];
    foreach ([
        ['15m', 'entry_score'],
        ['1H', '1h_score'],
        ['2H', '2h_score'],
        ['4H', '4h_score'],
        ['1D', '1d_score'],
        ['1M', '1m_score'],
    ] as $tfDef) {
        [$tfLabel, $tfKey] = $tfDef;
        if (array_key_exists($tfKey, $tf) && $tf[$tfKey] !== null) {
            $value = (float)$tf[$tfKey];
            $tfParts[] = $tfLabel . ' ' . ($value >= 0 ? '+' : '') . number_format($value, 2, '.', '');
        } else {
            $tfParts[] = $tfLabel . ' -';
        }
    }
    $probability = is_array($signal['empirical_win_probability'] ?? null) ? $signal['empirical_win_probability'] : [];
    $family = is_array($signal['live_family_evidence'] ?? null) ? $signal['live_family_evidence'] : [];
    $familyText = 'UNAVAILABLE';
    if ($family !== []) {
        $familyText = (isset($family['score']) ? number_format((float)$family['score'], 2, '.', '') : '-')
            . ' | agreement ' . number_format((float)($family['agreement_ratio'] ?? 0.0) * 100.0, 0, '.', '') . '%'
            . ' | aligned ' . (int)($family['aligned_families'] ?? 0) . '/9'
            . ' | conflicts ' . (int)($family['conflicting_families'] ?? 0);
    }
    $probabilityText = 'NOT CALIBRATED';
    if (isset($probability['estimated_probability']) && is_numeric($probability['estimated_probability'])) {
        $probabilityText = number_format((float)$probability['estimated_probability'] * 100.0, 1, '.', '')
            . '% • n=' . (int)($probability['sample_size'] ?? 0);
    }
    $research = is_array($signal['research_calibration'] ?? null) ? $signal['research_calibration'] : [];
    $researchText = 'NO MATCHING LIVE-TIMEFRAME CALIBRATION';
    $featureText = 'NONE';
    if (($research['status'] ?? '') === 'AVAILABLE_INFORMATIONAL' || isset($research['strategy_id'])) {
        $researchText = (string)($research['strategy_id'] ?? '-')
            . ' @ ' . (string)($research['timeframe'] ?? '-')
            . ' | robust ' . number_format((float)($research['robust_score'] ?? 0.0), 2, '.', '');
        $weights = is_array($research['feature_weights'] ?? null) ? $research['feature_weights'] : [];
        arsort($weights, SORT_NUMERIC);
        $top = [];
        foreach (array_slice($weights, 0, 5, true) as $feature => $weight) {
            $top[] = $feature . ' ' . number_format((float)$weight * 100.0, 1, '.', '') . '%';
        }
        if ($top !== []) {
            $featureText = implode(' | ', $top);
        }
    }
    $body = implode("\n", [
        $symbol,
        'STATUS: ACTIVE • ' . $minutesLeft . ' min left',
        'Order: ' . $orderText,
        'Entry zone: ' . $plan['entry_min'] . ' - ' . $plan['entry_max'],
        'Stop: ' . $plan['initial_stop'],
        'Management checkpoint (no partial TP): ' . $plan['target1'],
        'Final take profit: ' . $plan['target2'],
        $sizingText,
        'Setup grade: ' . $setupGrade . ' (quality gate passed)',
        'Setup quality: ' . ($qualityScore === null ? '-' : $qualityScore . '/100'),
        'Empirical win probability: ' . $probabilityText,
        'Research strategy: ' . $researchText,
        'Top validated features: ' . $featureText,
        'MTF: ' . implode(' | ', $tfParts),
        'Evidence families: ' . $familyText,
        'Signal score: ' . number_format((float)($signal['composite_score'] ?? 0.0), 2, '.', ''),
        'Single-TP mode: place only the final take-profit; STC uses the checkpoint for protection logic.',
        'Reconfirm the live price before approval.',
        'Manual approval + manual order entry only.',
    ]);

    return [
        'ok' => true,
        'skipped' => false,
        'dispatch' => stc_dispatch_notification($pdo, $config, [
            'event_key' => 'plan:' . (string)$plan['plan_id'],
            'event_type' => 'NEW_LOCKED_PLAN',
            'competition_id' => $competitionId,
            'symbol' => $symbol,
            'position_id' => null,
            'severity' => 'high',
            'title' => $title,
            'body' => $body,
        ]),
    ];
}

function stc_state_hash(PDO $pdo, string $stateKey): ?string {
    $stmt = $pdo->prepare('SELECT state_hash FROM stc_notification_state WHERE state_key = ?');
    $stmt->execute([$stateKey]);
    $value = $stmt->fetchColumn();
    return $value === false ? null : (string)$value;
}

function stc_set_state_hash(PDO $pdo, string $stateKey, string $hash): void {
    $stmt = $pdo->prepare(
        'INSERT INTO stc_notification_state (state_key, state_hash) VALUES (?, ?) '
        . 'ON DUPLICATE KEY UPDATE state_hash = VALUES(state_hash), updated_at_utc = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$stateKey, $hash]);
}

function stc_notify_portfolio(PDO $pdo, array $config): array {
    $notifications = [];
    $stmt = $pdo->query("SELECT * FROM stc_positions WHERE status = 'OPEN' ORDER BY id ASC");
    while (($position = $stmt->fetch()) !== false) {
        $history = stc_recent_signal_states(
            $pdo,
            (string)$position['competition_id'],
            (string)$position['symbol'],
            3
        );
        $advice = stc_supervise_position($position, $history);
        if (($advice['action'] ?? 'HOLD') === 'HOLD') {
            continue;
        }
        $stateKey = 'position:' . (string)$position['position_id'] . ':management';
        $fingerprint = hash('sha256', json_encode([
            'action' => $advice['action'],
            'suggested_stop' => $advice['suggested_stop'] === null ? null : round((float)$advice['suggested_stop'], 8),
            'partial' => $advice['suggested_partial_fraction'],
            'reasons' => $advice['reasons'],
        ], JSON_UNESCAPED_SLASHES));
        if (stc_state_hash($pdo, $stateKey) === $fingerprint) {
            continue;
        }

        $title = 'STC POSITION • ' . (string)$advice['action'] . ' • ' . (string)$position['symbol'];
        $bodyLines = [
            'Competition: ' . (string)$position['competition_id'],
            'Position: ' . (string)$position['side'] . ' x ' . (string)$position['quantity'],
            'R multiple: ' . ($advice['r_multiple'] === null ? '-' : number_format((float)$advice['r_multiple'], 2, '.', '')),
            'Unrealized P/L: ' . ($advice['unrealized_pnl_usd'] === null ? '-' : '$' . number_format((float)$advice['unrealized_pnl_usd'], 2, '.', '')),
        ];
        if ($advice['suggested_stop'] !== null) {
            $bodyLines[] = 'Suggested stop: ' . (string)$advice['suggested_stop'];
        }
        if ($advice['suggested_partial_fraction'] !== null) {
            $bodyLines[] = 'Suggested partial: ' . number_format((float)$advice['suggested_partial_fraction'] * 100, 0) . '%';
        }
        $bodyLines[] = 'Reason: ' . implode(', ', $advice['reasons']);
        $bodyLines[] = 'Take action manually in the competition platform, then record it in STC.';

        $dispatch = stc_dispatch_notification($pdo, $config, [
            'event_key' => 'position:' . (string)$position['position_id'] . ':' . $fingerprint,
            'event_type' => 'POSITION_MANAGEMENT',
            'competition_id' => (string)$position['competition_id'],
            'symbol' => (string)$position['symbol'],
            'position_id' => (string)$position['position_id'],
            'severity' => ($advice['action'] === 'EXIT_NOW' ? 'critical' : 'high'),
            'title' => $title,
            'body' => implode("\n", $bodyLines),
        ]);
        $notifications[] = $dispatch;
        if ($dispatch['delivered_any']) {
            stc_set_state_hash($pdo, $stateKey, $fingerprint);
        }
    }
    return ['ok' => true, 'notifications' => $notifications];
}
