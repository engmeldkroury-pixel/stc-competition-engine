from datetime import datetime, timedelta, timezone

from app.analysis import analyze
from app.models import Bar


def make_bars(n=80, slope=1.0):
    base = datetime(2026, 9, 1, tzinfo=timezone.utc)
    out = []
    for i in range(n):
        close = 100 + slope * i + (0.2 if i % 2 == 0 else -0.2)
        out.append(
            Bar(
                timestamp=base + timedelta(minutes=i),
                open=close - 0.2,
                high=close + 0.5,
                low=close - 0.5,
                close=close,
                volume=1000 + i,
            )
        )
    return out


def test_bullish_series_scores_positive():
    r = analyze("TEST", make_bars(slope=0.5))
    assert r.technical_score > 0
    assert r.regime == "bullish"


def test_bearish_series_scores_negative():
    r = analyze("TEST", make_bars(slope=-0.5))
    assert r.technical_score < 0
    assert r.regime == "bearish"
