<?php
declare(strict_types=1);
require_once __DIR__ . '/cloud_control.php';

function stc_macro_currencies_for_symbol(string $symbol): array {
    $map = [
        'CAPITALCOM:BTCUSD' => ['USD'],
        'CAPITALCOM:ETHUSD' => ['USD'],
        'CAPITALCOM:DOGEUSD' => ['USD'],
        'CAPITALCOM:EURUSD' => ['EUR', 'USD'],
        'CAPITALCOM:AUDUSD' => ['AUD', 'USD'],
        'CAPITALCOM:USDZAR' => ['USD', 'ZAR'],
        'CAPITALCOM:XAUUSD' => ['USD'],
        'CAPITALCOM:XAGUSD' => ['USD'],
        'CAPITALCOM:SPX500' => ['USD'],
        'CAPITALCOM:NAS100' => ['USD'],
        'CME_MINI:MES1!' => ['USD'],
        'CME_MINI:MNQ1!' => ['USD'],
        'CBOT_MINI:MYM1!' => ['USD'],
        'CME_MINI:M2K1!' => ['USD'],
        'NYMEX:MCL1!' => ['USD'],
        'NYMEX:MNG1!' => ['USD'],
        'COMEX_MINI:MGC1!' => ['USD'],
        'COMEX_MINI:SIL1!' => ['USD'],
        'CME_MINI:M6E1!' => ['EUR', 'USD'],
        'CME_MINI:M6B1!' => ['GBP', 'USD'],
        'CME_MINI:MJY1!' => ['JPY', 'USD'],
        'CME_MINI:M6A1!' => ['AUD', 'USD'],
        'CME:MBT1!' => ['USD'],
        'CME:MET1!' => ['USD'],
        'CBOT:ZN1!' => ['USD'],
        'CBOT:ZB1!' => ['USD'],
    ];
    return $map[$symbol] ?? ['USD'];
}

function stc_macro_calendar_fetch(array $config): array {
    $enabled = (bool)($config['macro_calendar_enabled'] ?? true);
    if (!$enabled) {
        return ['ok' => false, 'disabled' => true, 'events' => [], 'error' => 'macro_calendar_disabled'];
    }

    $url = trim((string)($config['macro_calendar_url'] ?? 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'));
    if (!preg_match('#^https://#i', $url)) {
        return ['ok' => false, 'disabled' => false, 'events' => [], 'error' => 'macro_calendar_url_invalid'];
    }

    $cacheSeconds = max(60, min((int)($config['macro_calendar_cache_seconds'] ?? 600), 3600));
    $cachePath = sys_get_temp_dir() . '/stc_macro_calendar_cache.json';
    $cached = null;
    if (is_file($cachePath)) {
        $age = time() - (int)filemtime($cachePath);
        if ($age >= 0 && $age <= $cacheSeconds) {
            $raw = @file_get_contents($cachePath);
            $decoded = is_string($raw) ? json_decode($raw, true) : null;
            if (is_array($decoded) && isset($decoded['events']) && is_array($decoded['events'])) {
                $decoded['cache_age_seconds'] = $age;
                $decoded['from_cache'] = true;
                return $decoded;
            }
        }
    }

    $timeoutMs = max(500, min((int)($config['macro_calendar_timeout_ms'] ?? 1800), 4000));
    $body = false;
    $http = null;
    $error = null;

    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => ['Accept: application/json', 'User-Agent: STC-Competition-Engine/1.0'],
            CURLOPT_CONNECTTIMEOUT_MS => min(1000, $timeoutMs),
            CURLOPT_TIMEOUT_MS => $timeoutMs,
            CURLOPT_NOSIGNAL => true,
            CURLOPT_FOLLOWLOCATION => false,
        ]);
        $body = curl_exec($ch);
        $errno = curl_errno($ch);
        if ($errno !== 0) {
            $error = curl_error($ch);
        }
        $http = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        curl_close($ch);
    } else {
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'header' => "Accept: application/json\r\nUser-Agent: STC-Competition-Engine/1.0\r\nConnection: close",
                'timeout' => $timeoutMs / 1000.0,
                'ignore_errors' => true,
            ],
        ]);
        $body = @file_get_contents($url, false, $context);
        $headers = $http_response_header ?? [];
        foreach ($headers as $line) {
            if (preg_match('#^HTTP/\\S+\\s+(\\d{3})#', $line, $m) === 1) {
                $http = (int)$m[1];
                break;
            }
        }
        if ($body === false) {
            $error = 'macro_calendar_request_failed';
        }
    }

    if (!is_string($body) || $body === '' || $http === null || $http < 200 || $http >= 300) {
        return [
            'ok' => false,
            'disabled' => false,
            'events' => [],
            'http_code' => $http,
            'error' => $error ?? 'macro_calendar_http_failure',
        ];
    }

    $rows = json_decode($body, true);
    if (!is_array($rows)) {
        return ['ok' => false, 'disabled' => false, 'events' => [], 'http_code' => $http, 'error' => 'macro_calendar_invalid_json'];
    }

    $events = [];
    foreach ($rows as $row) {
        if (!is_array($row)) {
            continue;
        }
        $title = trim((string)($row['title'] ?? ''));
        $currency = strtoupper(trim((string)($row['country'] ?? '')));
        $dateRaw = trim((string)($row['date'] ?? ''));
        $impact = ucfirst(strtolower(trim((string)($row['impact'] ?? ''))));
        if ($title === '' || $currency === '' || $dateRaw === '' || $impact === '') {
            continue;
        }
        try {
            $date = new DateTimeImmutable($dateRaw);
            $dateUtc = $date->setTimezone(new DateTimeZone('UTC'));
        } catch (Throwable $e) {
            continue;
        }
        $events[] = [
            'title' => $title,
            'currency' => $currency,
            'time_utc' => $dateUtc->format(DateTimeInterface::ATOM),
            'impact' => $impact,
            'forecast' => trim((string)($row['forecast'] ?? '')),
            'previous' => trim((string)($row['previous'] ?? '')),
        ];
    }

    if ($events === []) {
        return ['ok' => false, 'disabled' => false, 'events' => [], 'http_code' => $http, 'error' => 'macro_calendar_empty'];
    }

    $result = [
        'ok' => true,
        'disabled' => false,
        'events' => $events,
        'source' => $url,
        'fetched_at_utc' => gmdate(DateTimeInterface::ATOM),
        'cache_age_seconds' => 0,
        'from_cache' => false,
    ];
    @file_put_contents($cachePath, json_encode($result, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);
    return $result;
}

function stc_macro_risk_context(
    array $config,
    string $symbol,
    ?DateTimeImmutable $now = null,
    ?array $preloadedCalendar = null
): array {
    $now = $now ?? new DateTimeImmutable('now', new DateTimeZone('UTC'));
    $now = $now->setTimezone(new DateTimeZone('UTC'));
    $beforeMinutes = max(0, min((int)($config['macro_blackout_before_minutes'] ?? 45), 180));
    $afterMinutes = max(0, min((int)($config['macro_blackout_after_minutes'] ?? 30), 180));
    $failClosed = (bool)($config['macro_calendar_fail_closed'] ?? true);
    $currencies = stc_macro_currencies_for_symbol($symbol);
    $calendar = $preloadedCalendar ?? stc_macro_calendar_fetch($config);

    if (($calendar['ok'] ?? false) !== true) {
        return [
            'status' => ($calendar['disabled'] ?? false) ? 'disabled' : 'unavailable',
            'block_new_approval' => $failClosed && !($calendar['disabled'] ?? false),
            'relevant_currencies' => $currencies,
            'blackout_before_minutes' => $beforeMinutes,
            'blackout_after_minutes' => $afterMinutes,
            'nearby_high_impact' => [],
            'next_high_impact' => null,
            'source' => $calendar['source'] ?? ($config['macro_calendar_url'] ?? 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'),
            'error' => $calendar['error'] ?? 'macro_calendar_unavailable',
            'fail_closed' => $failClosed,
        ];
    }

    $nearby = [];
    $next = null;
    foreach ($calendar['events'] as $event) {
        if (!in_array((string)$event['currency'], $currencies, true) || (string)$event['impact'] !== 'High') {
            continue;
        }
        try {
            $eventTime = new DateTimeImmutable((string)$event['time_utc']);
            $eventTime = $eventTime->setTimezone(new DateTimeZone('UTC'));
        } catch (Throwable $e) {
            continue;
        }
        $deltaSeconds = $eventTime->getTimestamp() - $now->getTimestamp();
        $deltaMinutes = $deltaSeconds / 60.0;
        $decorated = $event;
        $decorated['minutes_from_now'] = $deltaMinutes;

        if ($deltaMinutes >= -$afterMinutes && $deltaMinutes <= $beforeMinutes) {
            $nearby[] = $decorated;
        }
        if ($deltaMinutes >= 0 && ($next === null || $deltaMinutes < (float)$next['minutes_from_now'])) {
            $next = $decorated;
        }
    }

    usort($nearby, static fn(array $a, array $b): int => abs((float)$a['minutes_from_now']) <=> abs((float)$b['minutes_from_now']));
    return [
        'status' => $nearby === [] ? 'safe' : 'blackout',
        'block_new_approval' => $nearby !== [],
        'relevant_currencies' => $currencies,
        'blackout_before_minutes' => $beforeMinutes,
        'blackout_after_minutes' => $afterMinutes,
        'nearby_high_impact' => $nearby,
        'next_high_impact' => $next,
        'source' => $calendar['source'] ?? null,
        'fetched_at_utc' => $calendar['fetched_at_utc'] ?? null,
        'cache_age_seconds' => $calendar['cache_age_seconds'] ?? null,
        'fail_closed' => $failClosed,
    ];
}
