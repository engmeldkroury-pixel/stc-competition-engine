
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



from app.research_dataset import (
    research_timeframe_bundle,
    resample_daily_to_monthly,
    resample_hourly_to_two_hour,
)


def test_hourly_to_two_hour_resample_uses_only_complete_even_utc_buckets():
    t0 = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    bars = [
        Bar(
            timestamp=t0 + timedelta(hours=i),
            open=100 + i,
            high=101 + i,
            low=99 + i,
            close=100.5 + i,
            volume=10 + i,
        )
        for i in range(6)
    ]
    out = resample_hourly_to_two_hour(bars)
    assert len(out) == 3
    assert [b.timestamp.hour for b in out] == [0, 2, 4]
    assert out[0].open == bars[0].open
    assert out[0].close == bars[1].close
    assert out[0].high == max(bars[0].high, bars[1].high)
    assert out[0].volume == bars[0].volume + bars[1].volume


def test_hourly_resample_drops_partial_or_gapped_bucket_instead_of_inventing_bar():
    t0 = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    bars = [
        Bar(timestamp=t0, open=1, high=2, low=0.5, close=1.5, volume=10),
        Bar(timestamp=t0 + timedelta(hours=2), open=2, high=3, low=1.5, close=2.5, volume=10),
        Bar(timestamp=t0 + timedelta(hours=3), open=2.5, high=3.5, low=2, close=3, volume=10),
    ]
    out = resample_hourly_to_two_hour(bars)
    assert len(out) == 1
    assert out[0].timestamp.hour == 2


def test_daily_to_monthly_resample_preserves_ohlcv_semantics():
    t0 = datetime(2026, 1, 30, tzinfo=UTC)
    bars = [
        Bar(timestamp=t0, open=10, high=12, low=9, close=11, volume=100),
        Bar(timestamp=t0 + timedelta(days=1), open=11, high=13, low=10, close=12, volume=110),
        Bar(timestamp=datetime(2026, 2, 2, tzinfo=UTC), open=12, high=15, low=11, close=14, volume=120),
    ]
    out = resample_daily_to_monthly(bars)
    assert len(out) == 2
    assert out[0].open == 10
    assert out[0].close == 12
    assert out[0].high == 13
    assert out[0].low == 9
    assert out[0].volume == 210
    assert out[1].timestamp.month == 2


def test_standard_research_bundle_exposes_requested_multitimeframe_context():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    bars15 = [
        Bar(timestamp=base + timedelta(minutes=15 * i), open=1, high=2, low=0.5, close=1.5, volume=1)
        for i in range(8)
    ]
    bars1h = [
        Bar(timestamp=base + timedelta(hours=i), open=1, high=2, low=0.5, close=1.5, volume=1)
        for i in range(8)
    ]
    bars4h = [
        Bar(timestamp=base + timedelta(hours=4 * i), open=1, high=2, low=0.5, close=1.5, volume=1)
        for i in range(4)
    ]
    bars1d = [
        Bar(timestamp=base + timedelta(days=i), open=1, high=2, low=0.5, close=1.5, volume=1)
        for i in range(40)
    ]
    bundle = research_timeframe_bundle(
        bars_15m=bars15,
        bars_1h=bars1h,
        bars_4h=bars4h,
        bars_1d=bars1d,
    )
    assert set(bundle) == {"15", "60", "120", "240", "1D", "1M"}
    assert len(bundle["120"]) == 3
    assert len(bundle["15"]) == 7
    assert len(bundle["60"]) == 7



def test_optional_native_5m_and_30m_are_added_without_resampling():
    base = datetime(2026, 1, 1, tzinfo=UTC)
    def bars(step_minutes, count):
        return [
            Bar(
                timestamp=base + timedelta(minutes=step_minutes * i),
                open=1,
                high=2,
                low=0.5,
                close=1.5,
                volume=1,
            )
            for i in range(count)
        ]

    bundle = research_timeframe_bundle(
        bars_5m=bars(5, 12),
        bars_15m=bars(15, 8),
        bars_30m=bars(30, 10),
        bars_1h=bars(60, 8),
        bars_4h=bars(240, 4),
        bars_1d=bars(1440, 40),
    )
    assert {"5", "30"}.issubset(bundle)
    assert len(bundle["5"]) == 11
    assert len(bundle["30"]) == 9
    assert bundle["5"][0].timestamp == base
    assert bundle["30"][1].timestamp == base + timedelta(minutes=30)
