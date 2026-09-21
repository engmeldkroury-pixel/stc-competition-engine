from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "hostinger_patch"


def test_hostinger_patch_files_present():
    for name in ("cloud_control.php", "runtime_control.php", "approval.php", "operator_snapshot.php", "operator.php", "migrations/001_cloud_approval.sql"):
        assert (PATCH / name).exists()


def test_migration_is_fail_closed_and_additive():
    sql = (PATCH / "migrations" / "001_cloud_approval.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS stc_runtime_control" in sql
    assert "CREATE TABLE IF NOT EXISTS stc_execution_evidence" in sql
    assert "CREATE TABLE IF NOT EXISTS stc_signal_approvals" in sql
    assert "VALUES (1, 1, 1, 'Initial fail-closed cloud control', 1)" in sql
    assert "DROP TABLE" not in sql.upper()
    assert "DELETE FROM" not in sql.upper()
    assert "ALTER TABLE stc_webhook_events" not in sql


def test_patch_requires_separate_owner_auth_and_stays_manual_only():
    control = (PATCH / "cloud_control.php").read_text(encoding="utf-8")
    approval = (PATCH / "approval.php").read_text(encoding="utf-8")
    runtime = (PATCH / "runtime_control.php").read_text(encoding="utf-8")
    assert "owner_api_token" in control
    assert "stc_require_owner_auth($config);" in approval
    assert "stc_require_owner_auth($config);" in runtime
    assert "'execution' => 'manual_only'" in approval
    assert "stc_trigger_processor" not in approval
    assert "curl_" not in approval


def test_patch_validates_receipt_and_fresh_confirmation():
    control = (PATCH / "cloud_control.php").read_text(encoding="utf-8")
    assert "stc_validate_signal_receipt" in control
    assert "evidence_stale" in control
    assert "price_outside_envelope" in control
    assert "market_not_open" in control
    assert "safe_mode" in (PATCH / "runtime_control.php").read_text(encoding="utf-8")
    assert "kill_switch" in (PATCH / "runtime_control.php").read_text(encoding="utf-8")


def test_owner_console_is_human_initiated_and_has_no_order_execution():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "stc_require_owner_auth($config);" in snapshot
    assert "'automatic_execution_available' => false" in snapshot
    assert "'execution' => 'manual_only'" in snapshot
    assert "approval.php" in ui
    assert "runtime_control.php" in ui
    assert "This page never places an order." in ui
    assert "confirm(" in ui
    combined = snapshot + ui
    for forbidden in ("place_order", "submit_order", "broker_order", "strategy.entry"):
        assert forbidden not in combined


def test_owner_console_requires_fresh_manual_confirmation_for_approval():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "approvalFresh" in snapshot
    assert "$age >= 0 && $age <= 60" in snapshot
    assert "observed_at_utc:new Date().toISOString()" in ui
    assert "quote_price:price" in ui
    assert "market_status:'open'" in ui


def test_owner_console_auto_refresh_and_actionable_browser_notifications():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "setInterval(()=>{secondsToRefresh=30;refresh()},30000)" in ui
    assert "Notification.requestPermission()" in ui
    assert "STC NEW LOCKED TRADE PLAN" in ui
    assert "LONG" in ui and "SHORT" in ui
    assert "WAIT" in ui
    assert "Decision timeframe" in ui
    assert "Historical context" in ui


def test_owner_snapshot_covers_both_competitions_without_mixing_symbol_identity():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "capital-africa-sep-2026" in snapshot
    assert "amp-futures-sep-2026" in snapshot
    assert "$seenKey = $competitionId . '|' . $symbol;" in snapshot
    assert "'competition_id' => $competitionId" in snapshot
    assert "AMP Futures" in ui
    assert "Capital.com Africa" in ui


def test_owner_console_has_separate_navigation_for_competitions_general_and_notifications():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    for label in ("Overview", "Capital.com Africa", "AMP Futures", "General Lab", "Notification Center"):
        assert label in ui
    assert 'data-tab="capital"' in ui
    assert 'data-tab="amp"' in ui
    assert 'data-tab="general"' in ui
    assert 'data-tab="notifications"' in ui
    assert "stc_general_lab" in ui
    assert "Separate research/sandbox area" in ui
    assert "does not affect either competition account" in ui
