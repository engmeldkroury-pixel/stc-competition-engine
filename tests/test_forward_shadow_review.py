import math

import pytest

from app.forward_shadow_review import ValuedForwardTrade, review_forward_trades


def rows(values, days=6):
    out = []
    for i, value in enumerate(values):
        day = 20 + (i % days)
        out.append(ValuedForwardTrade(
            source_open_utc=f"2026-09-{day:02d}T12:00:00Z",
            net_r=value,
            record_sha256=f"sha-{i}",
        ))
    return out


def test_empty_and_small_samples_are_collecting():
    assert review_forward_trades([]).state == "COLLECTING"
    assert review_forward_trades(rows([0.5] * 11)).state == "COLLECTING"


def test_negative_forward_sample_is_reject_or_research():
    report = review_forward_trades(rows([-1.0, 0.2] * 6))
    assert report.state == "REJECT_OR_RESEARCH"
    assert report.automatic_live_promotion is False


def test_early_positive_does_not_auto_promote():
    report = review_forward_trades(rows([0.8, -0.4] * 8))
    assert report.state == "EARLY_POSITIVE"
    assert report.automatic_live_promotion is False


def test_strong_diverse_sample_can_only_become_eligible_for_review():
    values = [1.2, 0.8, -0.3, 1.0, 0.6, -0.2] * 8
    report = review_forward_trades(rows(values, days=6))
    assert report.state == "ELIGIBLE_FOR_REVIEW"
    assert report.n == 48
    assert report.distinct_utc_days == 6
    assert report.mean_r > 0.10
    assert report.profit_factor > 1.20
    assert report.lower_80_mean_r > 0
    assert report.automatic_live_promotion is False


def test_one_day_profit_concentration_blocks_review_eligibility():
    values = [-0.1] * 29 + [20.0]
    data = []
    for i, value in enumerate(values):
        day = "2026-09-28" if i == 29 else f"2026-09-{23 + (i % 5):02d}"
        data.append(ValuedForwardTrade(
            source_open_utc=day + "T12:00:00Z",
            net_r=value,
            record_sha256=f"x-{i}",
        ))
    report = review_forward_trades(data)
    assert report.state != "ELIGIBLE_FOR_REVIEW"
    assert "positive_result_too_day_concentrated" in report.reasons


def test_duplicate_or_nonfinite_records_fail_closed():
    duplicate = ValuedForwardTrade("2026-09-28T12:00:00Z", 1.0, "same")
    with pytest.raises(ValueError, match="duplicate_forward_record"):
        review_forward_trades([duplicate, duplicate])
    with pytest.raises(ValueError, match="finite_net_r"):
        review_forward_trades([ValuedForwardTrade("2026-09-28T12:00:00Z", math.nan, "nan")])
