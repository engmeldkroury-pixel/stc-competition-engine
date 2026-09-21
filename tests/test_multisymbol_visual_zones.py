from pathlib import Path

PINE = Path(__file__).resolve().parents[1] / "tradingview" / "STC_MULTI_FEED.pine"


def test_visual_version_and_overlay():
    text = PINE.read_text(encoding="utf-8")
    assert 'indicator("STC Capital Multi Feed v0.5 Visual Zones", overlay=true' in text


def test_visual_engine_has_multi_factor_analysis():
    text = PINE.read_text(encoding="utf-8")
    for token in (
        "ta.ema(close, 200)",
        "ta.rsi(close, 14)",
        "ta.macd(close, 12, 26, 9)",
        "ta.dmi(14, 14)",
        "ta.stdev(close, 20)",
        "ta.highest(high, structureLen)",
        "ta.lowest(low, structureLen)",
        "volumeRatioV",
        "timeframe.from_seconds",
        "request.security(syminfo.tickerid, higherTf",
    ):
        assert token in text


def test_visual_engine_draws_dynamic_zones_and_levels():
    text = PINE.read_text(encoding="utf-8")
    for title in (
        '"Entry zone low"',
        '"Entry zone high"',
        '"Invalidation / Stop"',
        '"Exit zone start / TP1"',
        '"Exit zone end / TP2"',
        '"Dynamic resistance"',
        '"Dynamic support"',
    ):
        assert title in text
    assert 'fill(pEntryLow, pEntryHigh' in text
    assert 'fill(pTarget1, pTarget2' in text


def test_visual_zones_follow_chart_timeframe_but_feed_contract_stays_fixed_input():
    text = PINE.read_text(encoding="utf-8")
    assert 'feedTf = input.timeframe("15", "Production feed timeframe"' in text
    assert 'timeframe.period' in text
    assert 'higherTf = timeframe.from_seconds' in text
    assert '"timeframe":"' in text


def test_visual_layer_does_not_place_orders_or_change_approval_contract():
    text = PINE.read_text(encoding="utf-8")
    assert "strategy.entry" not in text
    assert "strategy.exit" not in text
    assert "strategy.order" not in text
    assert "approved" not in text
    assert "alert(buildMessage(symbol, d), alert.freq_all)" in text


def test_fire_control_fix_is_preserved():
    text = PINE.read_text(encoding="utf-8")
    assert "varip array<int> lastSentTimes" in text
