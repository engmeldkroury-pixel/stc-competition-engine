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
