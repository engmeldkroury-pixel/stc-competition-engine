from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "hostinger_patch"


def test_hostinger_patch_files_present():
    for name in ("cloud_control.php", "runtime_control.php", "approval.php", "migrations/001_cloud_approval.sql"):
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
