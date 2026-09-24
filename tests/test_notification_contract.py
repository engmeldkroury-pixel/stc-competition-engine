from pathlib import Path


def test_competition_opportunity_grade_is_notification_eligible():
    source = Path("hostinger_patch/notification_control.php").read_text(encoding="utf-8")
    assert "'A_PLUS', 'COMPETITION_OPPORTUNITY'" in source
    assert "'Setup grade: ' . $setupGrade . ' (quality gate passed)'" in source
    assert "high_conviction_gate_not_passed" not in source
