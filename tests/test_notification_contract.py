from pathlib import Path


def test_competition_opportunity_grade_is_notification_eligible():
    notify = Path("hostinger_patch/notification_control.php").read_text(encoding="utf-8")
    cloud = Path("hostinger_patch/cloud_control.php").read_text(encoding="utf-8")
    assert "stc_signal_quality_gate_eligible($signal)" in notify
    assert "A_PLUS" in cloud
    assert "COMPETITION_OPPORTUNITY" in cloud
    assert "capital-africa-sep-2026" in cloud
    assert "'Setup grade: ' . $setupGrade . ' (quality gate passed)'" in notify
    assert "high_conviction_gate_not_passed" not in notify


def test_notification_uses_fail_safe_max_quantity_language_and_blocks_duplicate_or_cooldown_entries():
    notify = Path("hostinger_patch/notification_control.php").read_text(encoding="utf-8")
    assert "MAX STC QUANTITY:" in notify
    assert "DO NOT EXCEED; smaller is allowed" in notify
    assert "Official max:" not in notify
    assert "Never use profile max, trade value, margin, leverage, or % balance as quantity." in notify
    assert "This notification is NOT an execution approval." in notify
    assert "'reason' => 'existing_open_position'" in notify
    assert "'reason' => 'same_direction_loss_cooldown'" in notify
    assert "stc_recent_same_direction_loss_cooldown(" in notify
