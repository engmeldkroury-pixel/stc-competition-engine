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


def test_production_mtf_feeds_emit_exact_component_shadow_without_live_authority():
    capital_a = Path("tradingview/STC_CAPITAL_MTF_FEED_A.pine").read_text(encoding="utf-8")
    capital_b = Path("tradingview/STC_CAPITAL_MTF_FEED_B.pine").read_text(encoding="utf-8")
    amp_b = Path("tradingview/STC_AMP_MTF_FEED_B.pine").read_text(encoding="utf-8")
    amp_c = Path("tradingview/STC_AMP_MTF_FEED_C.pine").read_text(encoding="utf-8")
    amp_d = Path("tradingview/STC_AMP_MTF_FEED_D.pine").read_text(encoding="utf-8")

    for source in (capital_a, capital_b, amp_b, amp_c, amp_d):
        assert "Component Shadow" in source
        assert '"community_component_signals":' in source
        assert "SHADOW evidence only" in source
        assert "strategy.entry" not in source

    # Capital frozen/profile-ready exact components.
    assert 'componentEvent("CAPITALCOM:ETHUSD", "ssl_hybrid", 60, 15' in capital_a
    assert '"ssl_hybrid":' in capital_a
    assert 'componentEvent("CAPITALCOM:DOGEUSD", "range_filter", 100, 0, 0, 3.0' in capital_a
    assert '"range_filter_guikroth":' in capital_a
    assert 'componentEvent("CAPITALCOM:DOGEUSD", "schaff", 12, 26, 50, 0.5' in capital_a
    assert '"schaff_trend_cycle":' in capital_a
    assert 'componentEvent("CAPITALCOM:EURUSD", "trendilo", 1, 50, 0, 0.85, 6.0, 1.0)' in capital_a
    assert '"trendilo":' in capital_a
    assert 'componentEvent("CAPITALCOM:NAS100", "halftrend", 5' in capital_b
    assert '"halftrend_everget":' in capital_b

    # AMP exact final-frozen survivors that already have causal Pine parity adapters.
    assert 'componentEvent("NYMEX:MCL1!", "ssl_hybrid", 100, 20' in amp_b
    assert '"ssl_hybrid":' in amp_b
    assert 'componentEvent("CME_MINI:MJY1!", "trendilo", 1, 50, 0, 0.85, 6.0, 1.25)' in amp_c
    assert '"trendilo":' in amp_c
    assert 'componentEvent("CBOT:ZB1!", "range_filter", 100, 0, 0, 3.0' in amp_d
    assert '"range_filter_guikroth":' in amp_d


def test_component_shadow_payload_keeps_non_profile_symbols_empty():
    capital_a = Path("tradingview/STC_CAPITAL_MTF_FEED_A.pine").read_text(encoding="utf-8")
    capital_b = Path("tradingview/STC_CAPITAL_MTF_FEED_B.pine").read_text(encoding="utf-8")
    amp_b = Path("tradingview/STC_AMP_MTF_FEED_B.pine").read_text(encoding="utf-8")
    amp_c = Path("tradingview/STC_AMP_MTF_FEED_C.pine").read_text(encoding="utf-8")
    amp_d = Path("tradingview/STC_AMP_MTF_FEED_D.pine").read_text(encoding="utf-8")

    for token in ("btcCommunity = \"\"", "audCommunity = \"\""):
        assert token in capital_a
    for token in ("zarCommunity = \"\"", "xauCommunity = \"\"", "xagCommunity = \"\"", "spxCommunity = \"\""):
        assert token in capital_b
    for token in ("mngCommunity = \"\"", "mgcCommunity = \"\"", "silCommunity = \"\""):
        assert token in amp_b
    for token in ("m6eCommunity = \"\"", "m6bCommunity = \"\"", "m6aCommunity = \"\""):
        assert token in amp_c
    for token in ("mbtCommunity = \"\"", "metCommunity = \"\"", "znCommunity = \"\""):
        assert token in amp_d
