-- STC durable cloud approval state. Fail-closed defaults; no trade execution.
-- Apply once to the same database used by stc_webhook_events.

CREATE TABLE IF NOT EXISTS stc_runtime_control (
    id TINYINT UNSIGNED NOT NULL PRIMARY KEY,
    safe_mode TINYINT(1) NOT NULL DEFAULT 1,
    kill_switch TINYINT(1) NOT NULL DEFAULT 1,
    reason VARCHAR(512) NULL,
    version BIGINT UNSIGNED NOT NULL DEFAULT 1,
    updated_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO stc_runtime_control (id, safe_mode, kill_switch, reason, version)
VALUES (1, 1, 1, 'Initial fail-closed cloud control', 1)
ON DUPLICATE KEY UPDATE id = id;

CREATE TABLE IF NOT EXISTS stc_execution_evidence (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    evidence_id VARCHAR(128) NOT NULL UNIQUE,
    source VARCHAR(64) NOT NULL,
    competition_id VARCHAR(128) NULL,
    symbol VARCHAR(128) NOT NULL,
    provider VARCHAR(64) NOT NULL,
    observed_at_utc DATETIME NOT NULL,
    quote_price DECIMAL(24,10) NULL,
    market_status VARCHAR(16) NOT NULL DEFAULT 'unknown',
    details_json LONGTEXT NULL,
    recorded_by VARCHAR(32) NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stc_evidence_target (competition_id, symbol, observed_at_utc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stc_signal_approvals (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    approval_id VARCHAR(128) NOT NULL UNIQUE,
    signal_id VARCHAR(128) NOT NULL,
    event_id VARCHAR(512) NOT NULL,
    competition_id VARCHAR(128) NOT NULL,
    symbol VARCHAR(128) NOT NULL,
    decision VARCHAR(16) NOT NULL,
    quote_evidence_id VARCHAR(128) NULL,
    runtime_control_version BIGINT UNSIGNED NOT NULL,
    reason_json LONGTEXT NOT NULL,
    note VARCHAR(512) NULL,
    decided_at_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stc_approval_signal (signal_id, id),
    INDEX idx_stc_approval_target (competition_id, symbol, decided_at_utc),
    CONSTRAINT fk_stc_approval_evidence
      FOREIGN KEY (quote_evidence_id) REFERENCES stc_execution_evidence(evidence_id)
      ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
