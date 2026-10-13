from pathlib import Path

SOURCE = Path("hostinger_patch/notification_control.php").read_text(encoding="utf-8")


def test_owner_stc_email_is_unconditionally_disabled():
    assert "'email_configured' => false" in SOURCE
    assert "email_disabled_by_owner" in SOURCE
    assert "@mail(" not in SOURCE


def test_expired_competition_filter_is_applied_before_any_delivery():
    start = SOURCE.index("function stc_dispatch_notification(")
    body = SOURCE[start:SOURCE.index("function stc_account_state_for(", start)]
    assert body.index("stc_notification_suppression_reason($event)") < body.index("stc_send_telegram(")
    assert "competition_ended" in SOURCE
    assert "stc_competition_rule_summary($competitionId)" in SOURCE


def test_suppression_applies_to_new_signals_and_outstanding_old_positions():
    assert "['competition_id' => $competitionId, 'event_type' => 'SIGNAL']" in SOURCE
    assert "'event_type' => 'POSITION_MANAGEMENT'" in SOURCE
    assert "continue; // Keep position in the ledger" in SOURCE


def test_future_contests_are_not_globally_muted():
    assert "['amp-futures-sep-2026', 'capital-africa-sep-2026']" in SOURCE
    assert "return null; // Future competitions and the independent Spot lab keep their own policies." in SOURCE


def test_non_actionable_heartbeat_is_disabled():
    assert "routine_heartbeat_disabled" in SOURCE
    heartbeat = SOURCE.index("function stc_maybe_notify_system_heartbeat(")
    assert "return null;" in SOURCE[heartbeat:heartbeat + 210]
