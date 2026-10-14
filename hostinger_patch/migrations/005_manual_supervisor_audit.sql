-- STC 60-second manual-trade supervisor: additive read-only observation receipts.
-- No order routing, notification delivery, broker API, or mail integration.
-- Preserve historic trades; NEVER delete/close a ledger position automatically.
CREATE TABLE IF NOT EXISTS stc_supervisor_ticks (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    minute_bucket_utc DATETIME NOT NULL UNIQUE,
    started_at_utc DATETIME NOT NULL,
    completed_at_utc DATETIME NULL,
    status VARCHAR(24) NOT NULL DEFAULT 'STARTED',
    observed_signals INT UNSIGNED NOT NULL DEFAULT 0,
    observed_positions INT UNSIGNED NOT NULL DEFAULT 0,
    stale_count INT UNSIGNED NOT NULL DEFAULT 0,
    reconciliation_count INT UNSIGNED NOT NULL DEFAULT 0,
    errors_count INT UNSIGNED NOT NULL DEFAULT 0,
    detail VARCHAR(255) NULL,
    INDEX idx_stc_supervisor_health (status, completed_at_utc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_supervisor_watches (
    watch_key CHAR(64) NOT NULL PRIMARY KEY,
    watch_type VARCHAR(16) NOT NULL,
    competition_id VARCHAR(128) NOT NULL,
    symbol VARCHAR(128) NOT NULL,
    source_ref VARCHAR(128) NOT NULL,
    state VARCHAR(48) NOT NULL,
    last_source_time_utc DATETIME NULL,
    last_verified_quote_utc DATETIME NULL,
    external_fill_verified TINYINT(1) NOT NULL DEFAULT 0,
    last_valid_until_utc DATETIME NULL,
    last_checked_utc DATETIME NOT NULL,
    first_seen_utc DATETIME NOT NULL,
    state_changed_utc DATETIME NOT NULL,
    INDEX idx_stc_supervisor_watches_state (watch_type, state, last_checked_utc),
    INDEX idx_stc_supervisor_competition (competition_id, state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_supervisor_watch_receipts (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tick_id BIGINT UNSIGNED NOT NULL,
    watch_key CHAR(64) NOT NULL,
    watch_type VARCHAR(16) NOT NULL,
    competition_id VARCHAR(128) NOT NULL,
    state VARCHAR(48) NOT NULL,
    observed_at_utc DATETIME NOT NULL,
    source_age_seconds INT NULL,
    quote_verified TINYINT(1) NOT NULL DEFAULT 0,
    external_fill_verified TINYINT(1) NOT NULL DEFAULT 0,
    suggested_manual_action VARCHAR(32) NOT NULL DEFAULT 'RECHECK',
    reason VARCHAR(128) NOT NULL,
    detail_json TEXT NULL,
    UNIQUE KEY uniq_stc_supervisor_receipt (tick_id, watch_key),
    INDEX idx_stc_supervisor_watch_history (watch_key, id),
    CONSTRAINT fk_stc_supervisor_tick FOREIGN KEY (tick_id)
      REFERENCES stc_supervisor_ticks(id) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
