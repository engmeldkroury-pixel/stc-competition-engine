from pathlib import Path

PINE = Path(__file__).resolve().parents[1] / "tradingview" / "STC_MULTI_FEED.pine"


def test_visual_version_and_overlay():
    text = PINE.read_text(encoding="utf-8")
    assert 'indicator("STC Capital Multi Feed v0.7.1 Historical Context", overlay=true' in text


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
    assert 'alert(buildMessage("CAPITALCOM:BTCUSD", btc, btcH), alert.freq_all)' in text


def test_fire_control_fix_is_preserved():
    text = PINE.read_text(encoding="utf-8")
    assert "varip int lastBTC = na" in text
    assert "varip int lastNAS = na" in text


def test_stateful_visual_setup_locks_levels_until_expiry_or_invalidation():
    text = PINE.read_text(encoding="utf-8")
    for token in (
        "var int lockedDir = 0",
        "var int lockedAtBar = na",
        "var float lockedEntryLow = na",
        "var float lockedEntryHigh = na",
        "var float lockedStop = na",
        "var float lockedTarget1 = na",
        "var float lockedTarget2 = na",
        "setupLifetimeBars",
        "lockedExpired",
        "lockedInvalidated",
        "if lockedDir == 0 and setupDir != 0",
    ):
        assert token in text


def test_stateful_visual_levels_are_not_recomputed_while_locked():
    text = PINE.read_text(encoding="utf-8")
    assert "entryLow = lockedDir != 0 ? lockedEntryLow : na" in text
    assert "entryHigh = lockedDir != 0 ? lockedEntryHigh : na" in text
    assert "stopLevel = lockedDir != 0 ? lockedStop : na" in text
    assert "target1 = lockedDir != 0 ? lockedTarget1 : na" in text
    assert "target2 = lockedDir != 0 ? lockedTarget2 : na" in text
