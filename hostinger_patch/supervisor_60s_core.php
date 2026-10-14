<?php
declare(strict_types=1);

/**
 * Pure, fail-closed state machine for the owner/manual Paper Trading supervisor.
 *
 * WARNING: a recent 15-minute bar is NOT a verified live quote; neither a
 * recorded STC position nor an alert is proof of an actual TradingView fill.
 * This module never sends messages or changes orders/positions.
 */

function stc_supervisor_utc_now(?DateTimeImmutable $now = null): DateTimeImmutable {
    return ($now ?? new DateTimeImmutable('now', new DateTimeZone('UTC')))
        ->setTimezone(new DateTimeZone('UTC'));
}

function stc_supervisor_parse_time(mixed $raw): ?DateTimeImmutable {
    if (!is_string($raw) || trim($raw) === '') {
        return null;
    }
    try {
        $timestamp = new DateTimeImmutable(trim($raw), new DateTimeZone('UTC'));
        return $timestamp->setTimezone(new DateTimeZone('UTC'));
    } catch (Throwable $e) {
        return null;
    }
}

function stc_supervisor_is_reconciliation(string $state): bool {
    return in_array($state, [
        'ENDED_RECONCILIATION',
        'SOURCE_UNVERIFIED',
        'DATA_STALE',
        'CONTEST_UNVERIFIED',
        'POSITION_DATA_INVALID',
        'EXTERNAL_FILL_UNVERIFIED',
    ], true);
}

/**
 * Position state: remain tracked until an actual manual owner ledger update.
 * We deliberately do not tell the owner the position is safe or "HOLD" just
 * because repeated polls find no newer market events.
 */
function stc_supervisor_position_state(
    array $position,
    array $history,
    ?DateTimeImmutable $now = null
): array {
    $now = stc_supervisor_utc_now($now);
    $cid = trim((string)($position['competition_id'] ?? ''));
    $symbol = trim((string)($position['symbol'] ?? ''));
    $id = trim((string)($position['position_id'] ?? ''));
    if ($id === '' || $cid === '' || $symbol === '' || ($position['status'] ?? '') !== 'OPEN') {
        return [
            'state' => 'POSITION_DATA_INVALID', 'reason' => 'invalid_open_position_identity',
            'source_age_seconds' => null, 'source_at_utc' => null,
            'manual_action' => 'RECONCILE',
            'quote_verified' => false, 'external_fill_verified' => false,
        ];
    }

    $suppression = stc_notification_suppression_reason([
        'competition_id' => $cid,
        'event_type' => 'POSITION_MANAGEMENT',
    ], $now);
    if ($suppression !== null) {
        return [
            'state' => $suppression === 'competition_ended'
                ? 'ENDED_RECONCILIATION' : 'CONTEST_UNVERIFIED',
            'reason' => $suppression,
            'source_age_seconds' => null, 'source_at_utc' => null,
            'manual_action' => 'RECONCILE',
            'quote_verified' => false, 'external_fill_verified' => false,
        ];
    }

    $latest = $history === [] ? null : $history[count($history) - 1];
    $source = is_array($latest)
        ? stc_supervisor_parse_time($latest['time'] ?? null) : null;
    if ($source === null) {
        return [
            'state' => 'SOURCE_UNVERIFIED', 'reason' => 'no_verifiable_source_bar',
            'source_age_seconds' => null, 'source_at_utc' => null,
            'manual_action' => 'RECHECK',
            'quote_verified' => false, 'external_fill_verified' => false,
        ];
    }
    $age = $now->getTimestamp() - $source->getTimestamp();
    if ($age < -60 || $age > 1800) {
        return [
            'state' => 'DATA_STALE',
            'reason' => $age < -60 ? 'source_in_future' : 'source_bar_older_than_30_minutes',
            'source_age_seconds' => $age,
            'source_at_utc' => $source->format(DateTimeInterface::ATOM),
            'manual_action' => 'RECHECK',
            'quote_verified' => false, 'external_fill_verified' => false,
        ];
    }
    // The actual TradingView Paper Trading account has NO verified position
    // readback/quote in this process, so advice cannot be an execution order.
    return [
        'state' => 'EXTERNAL_FILL_UNVERIFIED',
        'reason' => 'source_recent_but_no_verified_live_quote_or_paper_fill',
        'source_age_seconds' => $age,
        'source_at_utc' => $source->format(DateTimeInterface::ATOM),
        'manual_action' => 'RECHECK',
        'quote_verified' => false, 'external_fill_verified' => false,
    ];
}

/** Manual signal handling: a delayed alert never extends a plan's original TTL. */
function stc_supervisor_signal_state(
    array $record,
    ?DateTimeImmutable $now = null
): array {
    $now = stc_supervisor_utc_now($now);
    $cid = trim((string)($record['competition_id'] ?? ''));
    $signalId = trim((string)($record['plan_id'] ?? ''));
    if ($cid === '' || $signalId === '') {
        return [
            'state' => 'SIGNAL_DATA_INVALID', 'reason' => 'missing_signal_identity',
            'manual_action' => 'RECHECK', 'valid_until_utc' => null,
        ];
    }
    $suppression = stc_notification_suppression_reason([
        'competition_id' => $cid,
        'event_type' => 'SIGNAL',
    ], $now);
    if ($suppression !== null) {
        return [
            'state' => $suppression === 'competition_ended'
                ? 'EXPIRED_SIGNAL' : 'CONTEST_UNVERIFIED',
            'reason' => $suppression, 'manual_action' => 'NO_ENTRY',
            'valid_until_utc' => null,
        ];
    }
    $valid = stc_supervisor_parse_time($record['valid_until'] ?? null);
    if ($valid === null || (string)($record['valid_until'] ?? '') === '') {
        return [
            'state' => 'SIGNAL_TTL_UNVERIFIED',
            'reason' => 'missing_or_invalid_server_locked_plan_expiry',
            'manual_action' => 'NO_ENTRY', 'valid_until_utc' => null,
        ];
    }
    if ($now >= $valid) {
        return [
            'state' => 'EXPIRED_SIGNAL',
            'reason' => 'locked_trade_plan_expired',
            'manual_action' => 'NO_ENTRY',
            'valid_until_utc' => $valid->format(DateTimeInterface::ATOM),
        ];
    }
    if (($record['owner_recorded_open'] ?? false) === true) {
        return [
            'state' => 'OWNER_RECORDED_OPEN',
            'reason' => 'owner_ledger_open_requires_separate_position_watch',
            'manual_action' => 'NO_DUPLICATE_ENTRY',
            'valid_until_utc' => $valid->format(DateTimeInterface::ATOM),
        ];
    }
    return [
        'state' => 'PENDING_MANUAL_CONFIRMATION',
        'reason' => 'quote_and_external_execution_reconfirmation_required',
        'manual_action' => 'REVALIDATE_LIVE_PRICE_AND_ACCOUNT',
        'valid_until_utc' => $valid->format(DateTimeInterface::ATOM),
    ];
}
