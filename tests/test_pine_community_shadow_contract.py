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


def test_community_pine_candidate_covers_frozen_amp_profiles():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
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
