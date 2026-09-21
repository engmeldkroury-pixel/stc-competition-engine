-- STC actionable notification center.
-- Additive only. Stores de-duplicated notification events and delivery audit.

CREATE TABLE IF NOT EXISTS stc_notification_events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    notification_id VARCHAR(128) NOT NULL UNIQUE,
    event_key VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(64) NOT NULL,
    competition_id VARCHAR(128) NULL,
    symbol VARCHAR(128) NULL,
    position_id VARCHAR(128) NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'normal',
    title VARCHAR(255) NOT NULL,
    body_text TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stc_notification_target (competition_id, symbol, created_at_utc),
    INDEX idx_stc_notification_position (position_id, created_at_utc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_notification_deliveries (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    notification_id VARCHAR(128) NOT NULL,
    channel VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    http_code INT NULL,
    error_text VARCHAR(512) NULL,
    attempted_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stc_notification_delivery (notification_id, channel, attempted_at_utc),
    CONSTRAINT fk_stc_notification_delivery_event
      FOREIGN KEY (notification_id) REFERENCES stc_notification_events(notification_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_notification_state (
    state_key VARCHAR(255) NOT NULL PRIMARY KEY,
    state_hash CHAR(64) NOT NULL,
    updated_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
