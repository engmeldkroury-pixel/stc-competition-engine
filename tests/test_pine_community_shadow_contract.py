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


def test_production_feeds_emit_frozen_component_payloads_without_extra_security_calls():
    files = {
        "tradingview/STC_CAPITAL_MTF_FEED_A.pine": ("trendilo",),
        "tradingview/STC_CAPITAL_MTF_FEED_B.pine": ("supertrend_kivanc", "range_filter_guikroth"),
        "tradingview/STC_AMP_MTF_FEED_B.pine": ("ssl_hybrid",),
        "tradingview/STC_AMP_MTF_FEED_C.pine": ("alphatrend", "waddah_attar_explosion", "trendilo"),
        "tradingview/STC_AMP_MTF_FEED_D.pine": ("range_filter_guikroth",),
    }
    for path, component_ids in files.items():
        source = Path(path).read_text(encoding="utf-8")
        assert '"community_component_signals"' in source
        assert source.count("request.security") == 5
        assert "barstate.isconfirmed and barstate.isrealtime" in source
        for component_id in component_ids:
            assert component_id in source


def test_frozen_production_component_parameters_match_registry_contract():
    capital_a = Path("tradingview/STC_CAPITAL_MTF_FEED_A.pine").read_text(encoding="utf-8")
    capital_b = Path("tradingview/STC_CAPITAL_MTF_FEED_B.pine").read_text(encoding="utf-8")
    amp_b = Path("tradingview/STC_AMP_MTF_FEED_B.pine").read_text(encoding="utf-8")
    amp_c = Path("tradingview/STC_AMP_MTF_FEED_C.pine").read_text(encoding="utf-8")
    amp_d = Path("tradingview/STC_AMP_MTF_FEED_D.pine").read_text(encoding="utf-8")

    assert "frozenTrendiloEvent(1.25)" in capital_a
    assert "atrPeriod = 14" in capital_b and "multiplier = 3.0" in capital_b
    assert "frozenRangeFilterEvent(2.0)" in capital_b
    assert "baselineLength = 100" in amp_b and "sslLength = 20" in amp_b
    assert "period = 20" in amp_c and "coefficient = 1.0" in amp_c
    assert "sensitivity = 100.0" in amp_c and "deadZoneMult = 3.0" in amp_c
    assert "bandMultiplier = 1.25" in amp_c
    assert "rangeMultiplier = 3.0" in amp_d
