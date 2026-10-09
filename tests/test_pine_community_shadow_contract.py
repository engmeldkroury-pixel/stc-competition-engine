from pathlib import Path


def test_community_pine_parity_candidate_is_research_only_and_uses_frozen_parameters():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")

    assert 'indicator("STC Community Shadow Parity Candidate v0.1"' in source
    assert "NO live-trading authority" in source
    assert "alert(" not in source
    assert "strategy.entry" not in source

    # EURUSD Trendilo frozen research parameters.
    assert "lookback = 50" in source
    assert "almaOffset = 0.85" in source
    assert "almaSigma = 6.0" in source
    assert "bandMultiplier = 1.0" in source

    # ETHUSD SSL Hybrid.
    assert "baselineLength = 60" in source
    assert "sslLength = 15" in source

    # DOGEUSD Range Filter + Schaff.
    assert "samplingPeriod = 100" in source
    assert "rangeMultiplier = 3.0" in source
    assert "cycleLength = 12" in source
    assert "fastLength = 26" in source
    assert "slowLength = 50" in source
    assert "alpha = 0.5" in source

    # NAS100 HalfTrend.
    assert "amplitude = 5" in source


def test_community_pine_candidate_exposes_each_component_event_separately_for_parity():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
    for label in (
        "Trendilo event",
        "SSL Hybrid event",
        "Range Filter event",
        "Schaff event",
        "HalfTrend event",
    ):
        assert label in source


def test_amp_pine_candidate_covers_frozen_amp_profiles():
    source = Path("tradingview/STC_AMP_COMMUNITY_SHADOW_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
    for symbol in ("NYMEX:MCL1!", "CME_MINI:MJY1!", "CBOT:ZB1!"):
        assert symbol in source

    # MCL frozen SSL Hybrid parameters.
    assert "baselineLength = 100" in source
    assert "sslLength = 20" in source

    # MJY MULTITF_CONFIRMED Trendilo parameters.
    assert "bandMultiplier = 1.25" in source
    assert "MJY Trendilo event" in source

    # ZB frozen Range Filter reuses the causal 100 / 3.0 profile.
    assert "ZB Range Filter event" in source
    assert "samplingPeriod = 100" in source
    assert "rangeMultiplier = 3.0" in source

    assert "MCL SSL Hybrid event" in source


def test_amp_mtf_feeds_emit_only_their_frozen_shadow_component_payloads():
    feed_b = Path("tradingview/STC_AMP_MTF_FEED_B.pine").read_text(encoding="utf-8")
    feed_c = Path("tradingview/STC_AMP_MTF_FEED_C.pine").read_text(encoding="utf-8")
    feed_d = Path("tradingview/STC_AMP_MTF_FEED_D.pine").read_text(encoding="utf-8")

    assert '"community_component_signals":{"ssl_hybrid":' in feed_b
    assert 'symbol == "NYMEX:MCL1!"' in feed_b
    assert "ta.ema(close, 100)" in feed_b
    assert "ta.ema(high, 20)" in feed_b
    assert "ta.ema(low, 20)" in feed_b

    assert '"community_component_signals":{"trendilo":' in feed_c
    assert 'symbol == "CME_MINI:MJY1!"' in feed_c
    assert "ta.alma(trendiloPch, 50, 0.85, 6.0)" in feed_c
    assert "trendiloRms = 1.25 *" in feed_c

    assert '"community_component_signals":{"range_filter_guikroth":' in feed_d
    assert 'symbol == "CBOT:ZB1!"' in feed_d
    assert "ta.ema(rfChange, 100)" in feed_d
    assert "rfSecond = ta.ema(rfFirst, 199)" in feed_d
    assert "rfSmoothRange = rfSecond * 3.0" in feed_d

    for source in (feed_b, feed_c, feed_d):
        assert "communitySignal" in source
        assert "strategy.entry" not in source
