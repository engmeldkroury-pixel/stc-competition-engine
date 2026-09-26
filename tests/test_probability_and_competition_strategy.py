from datetime import datetime, timezone

from app.competition_strategy import competition_pace
from app.probability import estimate_win_probability


UTC = timezone.utc


def test_win_probability_is_not_displayed_as_calibrated_with_small_sample():
    r = estimate_win_probability(8, 2, min_samples=50)
    assert r.status == "INSUFFICIENT_DATA"
    assert r.sample_size == 10
    assert r.observed_win_rate == 0.8
    assert r.estimated_win_probability is None
    assert r.confidence_low is not None
    assert r.confidence_high is not None


def test_win_probability_is_calibrated_only_after_minimum_sample():
    r = estimate_win_probability(45, 15, min_samples=50)
    assert r.status == "CALIBRATED"
    assert r.sample_size == 60
    assert r.estimated_win_probability == 0.75
    assert r.confidence_low < r.estimated_win_probability < r.confidence_high


def test_competition_pace_keeps_shared_competition_floor_when_catching_up():
    r = competition_pace(
        "amp-futures-sep-2026",
        now_utc=datetime(2026, 9, 25, 12, 0, tzinfo=UTC),
        qualifying_days_done=5,
        realized_pnl=-500,
        current_rank=120,
        prize_cutoff_rank=20,
    )
    assert r.phase == "CATCH_UP"
    assert r.scan_mode == "BROADEN_UNIVERSE_KEEP_QUALITY"
    assert r.quality_floor == "COMPETITION_OPPORTUNITY_84"
    assert r.size_band == "NORMAL_TO_UPPER_ALLOWED"


def test_competition_pace_protects_late_prize_zone_score():
    r = competition_pace(
        "capital-africa-sep-2026",
        now_utc=datetime(2026, 10, 1, 8, 0, tzinfo=UTC),
        qualifying_days_done=3,
        realized_pnl=1200,
        current_rank=7,
        prize_cutoff_rank=10,
    )
    assert r.phase == "PROTECT_SCORE"
    assert r.size_band == "LOW"
    assert r.quality_floor == "COMPETITION_OPPORTUNITY_84"
