from pathlib import Path


def test_advanced_community_pine_candidate_is_shadow_only():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_ADVANCED_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
    assert 'indicator("STC Community Shadow Advanced Parity Candidate v0.1"' in source
    assert "NO webhook" in source
    assert "alert(" not in source
    assert "strategy.entry" not in source
    assert "Lorentzian is intentionally excluded" in source


def test_advanced_candidate_locks_frozen_btcusd_parameters():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_ADVANCED_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
    assert "rsiPeriod = 21" in source
    assert "pivotLength = 12" in source
    assert "bandwidth = 6.0" in source
    assert "minSamples = 12" in source
    assert "dominanceRatio = 1.35" in source


def test_advanced_candidate_locks_frozen_usdzar_parameters():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_ADVANCED_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
    assert "lookback = 500" in source
    assert "deviationLength = 499" in source
    assert "multiplier = 3.0" in source
    assert "period = 20" in source
    assert "coefficient = 1.0" in source
    assert "atrPeriod = 14" in source
    assert "keyValue = 1.5" in source
    assert "zero_volume_fraction = 0" in source


def test_advanced_candidate_exposes_component_events_separately():
    source = Path("tradingview/STC_COMMUNITY_SHADOW_ADVANCED_PARITY_CANDIDATE.pine").read_text(encoding="utf-8")
    for label in (
        "RSI Kernel event",
        "Nadaraya-Watson event",
        "AlphaTrend event",
        "Supertrend event",
        "UT Bot event",
    ):
        assert label in source
