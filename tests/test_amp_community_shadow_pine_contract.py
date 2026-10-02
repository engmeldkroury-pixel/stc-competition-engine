from pathlib import Path


SOURCE = Path("tradingview/STC_AMP_COMMUNITY_SHADOW_PARITY_CANDIDATE.pine")


def test_amp_community_shadow_pine_is_research_only_and_has_no_execution_path():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'indicator("STC AMP Community Shadow Parity Candidate v0.1"' in source
    assert "RESEARCH / PARITY ONLY" in source
    assert "NO webhook" in source
    assert "NO order" in source
    assert "alert(" not in source
    assert "strategy.entry" not in source
    assert "strategy.order" not in source


def test_amp_shadow_pine_uses_registered_frozen_parameters():
    source = SOURCE.read_text(encoding="utf-8")

    # ZB final frozen Range Filter survivor.
    assert "samplingPeriod = 100" in source
    assert "rangeMultiplier = 3.0" in source

    # MCL final frozen SSL Hybrid survivor.
    assert "baselineLength = 100" in source
    assert "sslLength = 20" in source

    # MJY registered candidates; no combined weight is defined here.
    assert "lookback = 50" in source
    assert "almaOffset = 0.85" in source
    assert "almaSigma = 6.0" in source
    assert "bandMultiplier = 1.25" in source
    assert "period = 20" in source
    assert "coefficient = 1.0" in source
    assert "fastLength = 12" in source
    assert "slowLength = 26" in source
    assert "sensitivity = 100.0" in source
    assert "deadZoneAtrPeriod = 100" in source
    assert "deadZoneMult = 3.0" in source


def test_amp_shadow_pine_exposes_component_events_individually():
    source = SOURCE.read_text(encoding="utf-8")
    for label in (
        "ZB Range Filter",
        "MCL SSL Hybrid",
        "MJY Trendilo",
        "MJY AlphaTrend",
        "MJY WAE",
    ):
        assert label in source


def test_amp_shadow_pine_is_confirmed_bar_nonlookahead_candidate():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'request.security("CBOT:ZB1!", "15", rangeFilterEvent()' in source
    assert 'request.security("NYMEX:MCL1!", "15", sslHybridEvent()' in source
    assert 'request.security("CME_MINI:MJY1!", "15", trendiloEvent()' in source
    assert "lookahead=barmerge.lookahead_off" in source
