
from datetime import datetime, timedelta, timezone

import pytest

from app.historical_features import extract_feature_snapshot
from app.indicator_catalog import feature_count
from app.models import Bar


UTC = timezone.utc


def _bars(*, count: int = 320, slope: float = 0.25, volume_step: float = 2.0) -> list[Bar]:
    t0 = datetime(2025, 1, 1, tzinfo=UTC)
    out: list[Bar] = []
    price = 100.0
    for i in range(count):
        wiggle = 0.15 if i % 4 in (0, 1) else -0.10
        price = max(2.0, price + slope + wiggle)
        open_price = price - slope * 0.35
        high = max(price, open_price) + 0.8
        low = min(price, open_price) - 0.8
        out.append(
            Bar(
                timestamp=t0 + timedelta(minutes=15 * i),
                open=open_price,
                high=high,
                low=low,
                close=price,
                volume=1000.0 + volume_step * i,
            )
        )
    return out


def test_full_catalog_is_materialized_without_future_data():
    bars = _bars()
    snap = extract_feature_snapshot("TEST:UP", "15", bars)
    assert len(snap.values) == feature_count()
    assert len(snap.observations) == feature_count()
    assert snap.timestamp == bars[-1].timestamp
    assert all(-1.0 <= value <= 1.0 for value in snap.values.values())


def test_rising_market_has_positive_trend_evidence():
    snap = extract_feature_snapshot("TEST:UP", "15", _bars(slope=0.35))
    assert snap.values["ema_9_20_50_100_200_alignment"] > 0.5
    assert snap.values["linear_regression_slope"] > 0
    assert snap.values["market_structure_trend"] >= 0
    assert snap.values["relative_strength_rank"] >= 0


def test_falling_market_has_negative_trend_evidence():
    snap = extract_feature_snapshot("TEST:DOWN", "15", _bars(slope=-0.22))
    assert snap.values["ema_9_20_50_100_200_alignment"] < -0.5
    assert snap.values["linear_regression_slope"] < 0
    assert snap.values["relative_strength_rank"] <= 0


def test_feature_pipeline_requires_long_enough_confirmed_history():
    with pytest.raises(ValueError):
        extract_feature_snapshot("TEST:SHORT", "15", _bars(count=200))
