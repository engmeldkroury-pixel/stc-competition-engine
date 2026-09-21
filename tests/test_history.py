from datetime import datetime, timedelta, timezone

import pytest

from app.history import build_historical_regime
from app.models import Bar


def _bars(start: float, step: float, count: int = 300) -> list[Bar]:
    t0 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    bars = []
    price = start
    for i in range(count):
        price = price + step
        bars.append(
            Bar(
                timestamp=t0 + timedelta(days=i),
                open=price - step * 0.25,
                high=price + abs(step) + 1.0,
                low=price - abs(step) - 1.0,
                close=price,
                volume=1000.0 + i,
            )
        )
    return bars


def test_historical_regime_requires_one_year_depth():
    with pytest.raises(ValueError):
        build_historical_regime("CAPITALCOM:XAUUSD", _bars(100.0, 1.0, count=200))


def test_rising_one_year_history_is_bullish():
    r = build_historical_regime("CAPITALCOM:XAUUSD", _bars(100.0, 1.0, count=300))
    assert r.bars_used == 300
    assert r.regime == "bullish"
    assert r.regime_score > 0.5
    assert r.momentum_252 > 0
    assert r.high_252 > r.low_252


def test_falling_one_year_history_is_bearish():
    r = build_historical_regime("CAPITALCOM:XAUUSD", _bars(500.0, -0.8, count=300))
    assert r.regime == "bearish"
    assert r.regime_score < -0.5
    assert r.momentum_252 < 0
