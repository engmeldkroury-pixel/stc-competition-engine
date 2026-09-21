-- STC durable manual position ledger + portfolio supervisor state.
-- Additive migration only. No broker/order execution.

CREATE TABLE IF NOT EXISTS stc_positions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    position_id VARCHAR(128) NOT NULL UNIQUE,
    competition_id VARCHAR(128) NOT NULL,
    symbol VARCHAR(128) NOT NULL,
    side VARCHAR(8) NOT NULL,
    origin VARCHAR(32) NOT NULL DEFAULT 'stc_plan',
    initial_quantity DECIMAL(24,8) NOT NULL,
    quantity DECIMAL(24,8) NOT NULL,
    entry_price DECIMAL(24,10) NOT NULL,
    initial_stop DECIMAL(24,10) NOT NULL,
    current_stop DECIMAL(24,10) NOT NULL,
    target1 DECIMAL(24,10) NOT NULL,
    target2 DECIMAL(24,10) NOT NULL,
    source_plan_id VARCHAR(128) NULL,
    source_signal_id VARCHAR(128) NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'OPEN',
    opened_at_utc DATETIME NOT NULL,
    closed_at_utc DATETIME NULL,
    exit_price DECIMAL(24,10) NULL,
    realized_pnl_usd DECIMAL(24,8) NOT NULL DEFAULT 0,
    note VARCHAR(512) NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stc_positions_open (status, competition_id, symbol),
    INDEX idx_stc_positions_plan (source_plan_id),
    INDEX idx_stc_positions_signal (source_signal_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_position_events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(128) NOT NULL UNIQUE,
    position_id VARCHAR(128) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    quantity_delta DECIMAL(24,8) NULL,
    price DECIMAL(24,10) NULL,
    realized_pnl_delta_usd DECIMAL(24,8) NOT NULL DEFAULT 0,
    stop_after DECIMAL(24,10) NULL,
    note VARCHAR(512) NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stc_position_events_position (position_id, id),
    CONSTRAINT fk_stc_position_events_position
      FOREIGN KEY (position_id) REFERENCES stc_positions(position_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS stc_account_state (
    competition_id VARCHAR(128) NOT NULL PRIMARY KEY,
    equity_usd DECIMAL(24,8) NOT NULL,
    risk_fraction DECIMAL(10,8) NOT NULL DEFAULT 0.00500000,
    source VARCHAR(32) NOT NULL DEFAULT 'owner_manual',
    version BIGINT UNSIGNED NOT NULL DEFAULT 1,
    updated_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO stc_account_state (competition_id, equity_usd, risk_fraction, source, version)
VALUES
    ('capital-africa-sep-2026', 100000.00, 0.00500000, 'initial_profile_seed', 1),
    ('amp-futures-sep-2026', 250000.00, 0.00500000, 'initial_profile_seed', 1)
ON DUPLICATE KEY UPDATE competition_id = competition_id;
