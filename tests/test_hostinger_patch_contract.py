from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "hostinger_patch"


def test_hostinger_patch_files_present():
    for name in ("cloud_control.php", "runtime_control.php", "approval.php", "operator_snapshot.php", "operator.php", "portfolio_control.php", "position.php", "account_state.php", "notification_control.php", "notification.php", "macro_control.php", "migrations/001_cloud_approval.sql", "migrations/002_portfolio_supervisor.sql", "migrations/003_notifications.sql"):
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
    assert "STC NEW ACTIVE TRADE PLAN" in ui
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


def test_portfolio_migration_is_additive_and_manual_only():
    sql = (PATCH / "migrations" / "002_portfolio_supervisor.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS stc_positions" in sql
    assert "CREATE TABLE IF NOT EXISTS stc_position_events" in sql
    assert "CREATE TABLE IF NOT EXISTS stc_account_state" in sql
    assert "initial_profile_seed" in sql
    assert "DROP TABLE" not in sql.upper()
    assert "DELETE FROM" not in sql.upper()
    assert "ALTER TABLE stc_webhook_events" not in sql


def test_position_ledger_never_places_orders_and_requires_owner_auth():
    position = (PATCH / "position.php").read_text(encoding="utf-8")
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    account = (PATCH / "account_state.php").read_text(encoding="utf-8")
    for text in (position, account):
        assert "stc_require_owner_auth($config);" in text
    combined = position + control + account
    for forbidden in ("place_order", "submit_order", "broker_order", "strategy.entry"):
        assert forbidden not in combined
    assert "manual_only" in position
    assert "Owner confirmed manual competition fill" in position
    assert "stop_risk_widening_blocked" in position


def test_portfolio_supervisor_has_anti_churn_and_manual_management_actions():
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "two_closed_bars_confirmed_strong_opposite_signal" in control
    for action in ("HOLD", "PROTECT", "EXIT_NOW"):
        assert action in control
    assert "PARTIAL_TAKE_PROFIT" not in control
    assert "rotation_candidates" in snapshot
    assert "score_advantage" in snapshot
    assert "current_thesis_degraded_and_new_locked_plan_materially_stronger" in snapshot
    assert "After manual fill: record open position" in ui
    assert "After manual stop change: record" in ui
    assert "Partial take-profit is disabled in single-TP mode" in ui
    assert "After manual close: record" in ui


def test_console_exposes_owner_synced_equity_and_provisional_sizing():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    account = (PATCH / "account_state.php").read_text(encoding="utf-8")
    assert "stc_account_state" in snapshot
    assert "position_sizing" in snapshot
    assert "provisional_risk_setting" in (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    assert "Owner-synced equity" in ui
    assert "STC risk budget / trade" in ui
    assert "risk_fraction_out_of_range" in account


def test_filtered_signal_cards_keep_actions_bound_to_authoritative_snapshot_index():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "all.indexOf(c)" in ui
    assert "approveCard(" in ui


def test_notification_migration_is_additive_and_auditable():
    sql = (PATCH / "migrations" / "003_notifications.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS stc_notification_events" in sql
    assert "CREATE TABLE IF NOT EXISTS stc_notification_deliveries" in sql
    assert "CREATE TABLE IF NOT EXISTS stc_notification_state" in sql
    assert "event_key VARCHAR(255) NOT NULL UNIQUE" in sql
    assert "DROP TABLE" not in sql.upper()
    assert "DELETE FROM" not in sql.upper()


def test_notification_endpoint_is_actionable_only_and_has_no_order_execution():
    endpoint = (PATCH / "notification.php").read_text(encoding="utf-8")
    control = (PATCH / "notification_control.php").read_text(encoding="utf-8")
    combined = endpoint + control
    assert "stc_require_operator_auth($config)" in endpoint
    assert "NEW_LOCKED_PLAN" in control
    assert "POSITION_MANAGEMENT" in control
    assert "wait_signal" in control
    assert "Manual approval + manual order entry only." in control
    for forbidden in ("place_order", "submit_order", "broker_order", "strategy.entry"):
        assert forbidden not in combined


def test_notification_secrets_are_config_only_and_never_committed_as_values():
    control = (PATCH / "notification_control.php").read_text(encoding="utf-8")
    assert "telegram_bot_token" in control
    assert "telegram_chat_id" in control
    assert "notification_email" in control
    assert "CHANGE_ME_TELEGRAM_BOT_TOKEN" in control
    assert "api.telegram.org/bot" in control
    # Token is read from private config and appended at runtime, not hardcoded.
    assert "123456789:" not in control


def test_owner_console_exposes_server_notification_status_and_test():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "Telegram mobile" in ui
    assert "Email backup" in ui
    assert "Send notification test" in ui
    assert "refreshNotificationStatus()" in ui
    assert "action:'test'" in ui
    assert "Raw 15-minute feed bars do not generate user notifications." in ui



def test_owner_console_embedded_javascript_is_syntax_valid_and_has_no_trailing_corruption():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert ui.count("</html>") == 1
    assert ui.rstrip().endswith("</html>")
    assert "function accountHtml(account,competitionId)" in ui
    assert "function renderOverview(cards)" in ui
    assert "function renderPositions(target,positions)" in ui
    assert "allowed_by_risk_policy" in ui
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not available for JavaScript syntax validation")
    script = ui.split("<script>", 1)[1].split("</script>", 1)[0]
    result = subprocess.run(
        [node, "--check"],
        input=script,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_snapshot_exposes_correlation_cluster_risk_and_expired_plan_cancellation():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    assert "stc_risk_cluster" in control
    assert "portfolio_risk_cap_usd" in control
    assert "cluster_risk_cap_usd" in control
    assert "allowed_by_risk_policy" in control
    assert "correlation_cluster_capacity" in control
    assert "CANCEL_PENDING_PLAN" in snapshot
    assert "deterministic_asset_risk_groups_not_statistical_correlation" in snapshot



def test_macro_calendar_gate_is_fail_closed_for_new_approvals_and_audited():
    macro = (PATCH / "macro_control.php").read_text(encoding="utf-8")
    approval = (PATCH / "approval.php").read_text(encoding="utf-8")
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "https://nfs.faireconomy.media/ff_calendar_thisweek.json" in macro
    assert "macro_calendar_fail_closed" in macro
    assert "macro_blackout_before_minutes" in macro
    assert "macro_blackout_after_minutes" in macro
    assert "High" in macro
    assert "macro_high_impact_blackout" in approval
    assert "macro_calendar_unavailable_fail_closed" in approval
    assert "'macro_context' => $macroContext" in approval
    assert "'macro_context' => $macroContext" in snapshot
    assert "macro_calendar_status" in snapshot
    assert "Macro event risk" in ui
    assert "New approval blocked by macro-risk gate." in ui


def test_hostinger_php_patch_files_are_syntax_valid_when_php_is_available():
    php = shutil.which("php")
    if php is None:
        pytest.skip("php is not available for syntax validation")
    names = [
        "approval.php",
        "cloud_control.php",
        "portfolio_control.php",
        "operator_snapshot.php",
        "operator.php",
        "position.php",
        "account_state.php",
        "notification_control.php",
        "notification.php",
        "macro_control.php",
    ]
    for name in names:
        result = subprocess.run(
            [php, "-l", str(PATCH / name)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, f"{name}: {result.stdout}\n{result.stderr}"



def test_snapshot_exposes_only_explicit_opportunity_lifecycle_and_order_instruction_fields():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    assert "'opportunity_active' => $opportunityActive" in snapshot
    assert "'expires_in_seconds' => $expiresInSeconds" in snapshot
    assert "'order_instruction' => $orderInstruction" in snapshot
    assert "'source_close_time' =>" in snapshot
    assert "stc_entry_order_instruction" in control
    for order_type in ("BUY_LIMIT", "BUY_STOP_LIMIT", "SELL_LIMIT", "SELL_STOP_LIMIT", "MARKET"):
        assert order_type in control


def test_owner_console_hides_expired_opportunities_and_formats_readable_local_time():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "function isOpportunityActive(c)" in ui
    assert "function formatLocalTime(value)" in ui
    assert "function formatCountdown(seconds)" in ui
    assert "data-valid-until" in ui
    assert "ACTIVE NOW" in ui
    assert "Expired opportunities are removed automatically" in ui
    assert "const actionable=cards.filter(c=>isOpportunityActive(c));" in ui
    assert "c.recommendation==='WAIT'||isOpportunityActive(c)" in ui
    assert "updateLiveCountdowns()" in ui
    assert "source_close_time||c.source_time" in ui


def test_owner_console_recalculates_manual_order_type_from_live_price_entry():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "function deriveOrderInstruction(c,price)" in ui
    assert "BUY LIMIT" in ui
    assert "BUY STOP-LIMIT" in ui
    assert "SELL LIMIT" in ui
    assert "SELL STOP-LIMIT" in ui
    assert "LIVE PRICE CHECK" in ui
    assert 'oninput="updateOrderHint(' in ui


def test_browser_notifications_do_not_suppress_active_plan_on_first_load():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "stc_seen_signal_plans" in ui
    assert "persistSeenSet('stc_seen_signal_plans'" in ui
    assert "STC NEW ACTIVE TRADE PLAN" in ui
    assert "if(!initializedSignals)" not in ui
    assert "if(snapshot)maybeNotify(snapshot.cards||[])" in ui


def test_server_notification_skips_expired_plan_and_includes_order_type_and_time_left():
    control = (PATCH / "notification_control.php").read_text(encoding="utf-8")
    assert "'reason' => 'expired_plan'" in control
    assert "stc_entry_order_instruction(" in control
    assert "'STATUS: ACTIVE • ' . $minutesLeft . ' min left'" in control
    assert "'Order: ' . $orderText" in control
    assert "'Reconfirm the live price before approval.'" in control


def test_php_derives_confirmed_bar_close_from_feed_timeframe():
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    assert "function stc_feed_bar_close_utc" in control
    assert "preg_match('/^\\d+$/'" in control
    assert "$opened->modify('+' . $seconds . ' seconds')" in control

def test_executed_positions_persist_and_block_replacement_opportunities():
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "$hasOpenPosition = (float)($openQty[$seenKey] ?? 0.0) > 0.0;" in snapshot
    assert "&& !$hasOpenPosition" in snapshot
    assert "'has_open_position' => $hasOpenPosition" in snapshot
    assert "'entry_blocked_reason' => $hasOpenPosition ? 'existing_open_position_managed_by_portfolio_supervisor'" in snapshot
    assert "$pendingPlanAction = 'MANAGE_EXISTING_POSITION';" in snapshot
    assert "c.has_open_position" in ui
    assert "EXECUTED • TRACKING" in ui
    assert "New signals are used to manage that position, not to create a replacement trade." in ui


def test_owner_console_can_backfill_existing_manual_positions_for_supervision():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "Record an existing manual position" in ui
    assert "function recordExistingPosition(competitionId)" in ui
    assert "origin:'manual_external'" in ui
    assert "ALREADY OPEN in the competition platform" in ui
    assert "no order will be sent" in ui
    assert "Latest market check" in ui
    assert "What to do now" in ui

def test_single_take_profit_mode_is_owner_visible_and_no_partial_tp_is_suggested():
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    notify = (PATCH / "notification_control.php").read_text(encoding="utf-8")
    assert "single_take_profit_mode_keep_full_quantity_and_protect" in control
    assert "'action' => 'PROTECT'" in control
    assert "'suggested_partial_fraction' => null" in control
    assert "Management checkpoint" in ui
    assert "Final take profit" in ui
    assert "Single-TP mode" in ui
    assert "Final take profit" in notify
    assert "no partial TP" in notify


def test_competition_progress_is_exposed_with_qualification_days_and_trade_counts():
    control = (PATCH / "portfolio_control.php").read_text(encoding="utf-8")
    snapshot = (PATCH / "operator_snapshot.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "function stc_competition_min_trading_days" in control
    assert "function stc_competition_progress" in control
    assert "return 3;" in control
    assert "return 5;" in control
    assert "'competition_progress' => [" in snapshot
    for label in ("Qualifying trading days", "Days remaining", "Trades entered", "Open / closed", "Recorded trade actions", "Realized competition P/L"):
        assert label in ui


def test_sizing_ui_shows_quantity_risk_and_official_position_limit():
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "STC POSITION SIZE" in ui
    assert "Configured risk budget" in ui
    assert "Official max open position" in ui
    assert "Projected open after" in ui
    assert "use this quantity unless the competition platform forces a smaller valid amount" in ui


def test_manual_backfill_preserves_original_competition_day_and_uses_one_final_tp():
    position = (PATCH / "position.php").read_text(encoding="utf-8")
    ui = (PATCH / "operator.php").read_text(encoding="utf-8")
    assert "manual_position_open_time_outside_competition_window" in position
    assert "2026-09-01T08:00:00+00:00" in position
    assert "2026-09-16T08:00:00+00:00" in position
    assert "Original open time if known" in ui
    assert "Final take-profit price (one TP only)" in ui
    assert "const checkpoint=(entry+finalTp)/2;" in ui


def test_mobile_signal_alert_contains_sizing_risk_and_single_tp_ticket():
    notify = (PATCH / "notification_control.php").read_text(encoding="utf-8")
    assert "'Quantity: '" in notify
    assert "' | Risk: $'" in notify
    assert "' | Official max: '" in notify
    assert "'Signal score: '" in notify
    assert "Single-TP mode: place only the final take-profit" in notify

