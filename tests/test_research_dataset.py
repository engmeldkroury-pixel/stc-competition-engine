
from datetime import datetime, timedelta, timezone

from app.models import Bar
from app.research_dataset import (
    bars_from_tradingview_ohlcv,
    data_quality_report,
    drop_latest_unconfirmed_bar,
    normalize_confirmed_bars,
)


UTC = timezone.utc


def test_tradingview_ohlcv_parser_and_quality_contract():
    payload = {
        "bars": [
            {"t": 1780000000 + i * 900, "o": 100 + i, "h": 101 + i, "l": 99 + i, "c": 100.5 + i, "v": 1000 + i}
            for i in range(1000)
        ]
    }
    bars = bars_from_tradingview_ohlcv(payload)
    q = data_quality_report("TEST:X", "15m", bars)
    assert len(bars) == 1000
    assert q.quality_ok is True
    assert q.duplicate_timestamps == 0
    assert q.median_spacing_seconds == 900


def test_quality_flags_duplicate_or_short_history():
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    bars = [
        Bar(timestamp=t0, open=1, high=2, low=0.5, close=1.5, volume=1),
        Bar(timestamp=t0, open=1.5, high=2, low=1, close=1.8, volume=1),
    ]
    q = data_quality_report("TEST:X", "15m", bars)
    assert q.quality_ok is False
    assert q.duplicate_timestamps == 1
    assert "insufficient_for_walk_forward_900_bar_minimum" in q.notes


def test_normalize_deduplicates_and_orders_without_filling_gaps():
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    a = Bar(timestamp=t0 + timedelta(minutes=15), open=2, high=3, low=1, close=2.5, volume=1)
    b = Bar(timestamp=t0, open=1, high=2, low=0.5, close=1.5, volume=1)
    c = a.model_copy(update={"close": 2.7, "high": 3.1})
    out = normalize_confirmed_bars([a, b, c])
    assert [x.timestamp for x in out] == [t0, t0 + timedelta(minutes=15)]
    assert out[-1].close == 2.7
    assert len(out) == 2


def test_drop_latest_unconfirmed_bar_is_explicit():
    payload = {
        "bars": [
            {"t": 1780000000 + i * 900, "o": 100, "h": 101, "l": 99, "c": 100, "v": 10}
            for i in range(3)
        ]
    }
    bars = bars_from_tradingview_ohlcv(payload)
    assert len(drop_latest_unconfirmed_bar(bars)) == 2
