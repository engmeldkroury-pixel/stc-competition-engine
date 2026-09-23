-- STC General Lab durable research request queue.
-- Additive only. No broker execution and no competition account mutation.

CREATE TABLE IF NOT EXISTS stc_general_lab_requests (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(128) NOT NULL UNIQUE,
    requested_symbol VARCHAR(128) NOT NULL,
    resolved_symbol VARCHAR(128) NULL,
    status VARCHAR(64) NOT NULL,
    requested_by VARCHAR(32) NOT NULL DEFAULT 'owner',
    requested_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at_utc DATETIME NULL,
    completed_at_utc DATETIME NULL,
    updated_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    result_json LONGTEXT NULL,
    note VARCHAR(1024) NULL,
    INDEX idx_stc_general_lab_status (status, updated_at_utc),
    INDEX idx_stc_general_lab_symbol (requested_symbol, updated_at_utc),
    INDEX idx_stc_general_lab_resolved_symbol (resolved_symbol, updated_at_utc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_general_lab_request_events (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(128) NOT NULL UNIQUE,
    request_id VARCHAR(128) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    status_after VARCHAR(64) NOT NULL,
    actor VARCHAR(32) NOT NULL,
    detail_json TEXT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stc_general_lab_event_request (request_id, created_at_utc),
    CONSTRAINT fk_stc_general_lab_event_request
      FOREIGN KEY (request_id) REFERENCES stc_general_lab_requests(request_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
