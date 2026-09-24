from app.community_live_shadow import build_component_shadow_snapshot
from app.event_decision import decide_bridge_event


def _strong_eur_payload():
    return {
        "event_id": "evt-shadow-eur",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:EURUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 1.1000,
        "high": 1.1020,
        "low": 1.0995,
        "close": 1.1015,
        "volume": 1800,
        "ema20": 1.1010,
        "ema50": 1.0980,
        "rsi14": 60,
        "atr14": 0.0010,
        "macd": 0.0020,
        "macd_signal": 0.0010,
        "volume_ratio": 1.8,
        "confirm_timeframe": "60",
        "confirm_time": "2026-09-21T17:00:00Z",
        "confirm_close": 1.1010,
        "confirm_ema20": 1.1000,
        "confirm_ema50": 1.0950,
        "confirm_ema200": 1.0800,
        "confirm_rsi14": 60,
        "confirm_atr14": 0.0020,
        "confirm_macd": 0.0030,
        "confirm_macd_signal": 0.0010,
        "confirm_volume_ratio": 1.4,
        "trend_2h_time": "2026-09-21T16:00:00Z",
        "trend_2h_score": 0.85,
        "trend_4h_time": "2026-09-21T16:00:00Z",
        "trend_4h_score": 0.82,
        "trend_1m_time": "2026-09-01T00:00:00Z",
        "trend_1m_score": 0.72,
        "family_trend": 0.85,
        "family_momentum": 0.78,
        "family_volatility": 0.65,
        "family_volume": 0.72,
        "family_vwap": 0.70,
        "family_market_structure": 0.88,
        "family_smc_liquidity": 0.86,
        "family_price_action": 0.75,
        "family_microstructure": 0.68,
        "history_timeframe": "1D",
        "history_time": "2026-09-20T00:00:00Z",
        "history_close": 1.1015,
        "history_ema50": 1.0800,
        "history_ema200": 1.0500,
        "history_rsi14": 62,
        "history_atr14": 0.0080,
        "history_high_252": 1.1200,
        "history_low_252": 0.9500,
        "history_momentum_20": 0.08,
        "history_momentum_63": 0.15,
        "history_momentum_126": 0.20,
        "history_momentum_252": 0.35,
        "history_volatility_20": 0.02,
    }


def test_capital_profiles_are_symbol_specific_and_shadow_only():
    eur = build_component_shadow_snapshot(
        "CAPITALCOM:EURUSD",
        "15",
        {"trendilo": -1.0},
    )
    assert eur["status"] == "COMPLETE_SHADOW"
    assert eur["weighted_score"] == -1.0
    assert eur["weights_used"] == {"trendilo": 1.0}
    assert eur["live_authority"] is False
    assert eur["affects_live_gate"] is False

    xau = build_component_shadow_snapshot(
        "CAPITALCOM:XAUUSD",
        "15",
        {"trendilo": 1.0},
    )
    assert xau["status"] == "NO_VALIDATED_PROFILE"
    assert xau["weighted_score"] is None
    assert xau["live_authority"] is False


def test_multicomponent_profile_requires_complete_exact_component_set():
    snapshot = build_component_shadow_snapshot(
        "CAPITALCOM:USDZAR",
        "15",
        {"lorentzian_classification": 1.0},
    )
    assert snapshot["status"] == "AWAITING_EXACT_COMPONENTS"
    assert snapshot["complete"] is False
    assert snapshot["weighted_score"] is None
    assert "nadaraya_watson_endpoint_nonrepaint" in snapshot["missing_components"]
    assert "alphatrend" in snapshot["missing_components"]
    assert snapshot["signals_used"] == {"lorentzian_classification": 1.0}


def test_shadow_component_score_does_not_change_competition_gate():
    baseline = _strong_eur_payload()
    shadowed = dict(baseline)
    shadowed["community_component_signals"] = {"trendilo": -1.0}

    without_shadow = decide_bridge_event("evt-shadow-baseline", baseline)
    with_shadow = decide_bridge_event("evt-shadow-present", shadowed)

    a = without_shadow["decision"]["signal"]
    b = with_shadow["decision"]["signal"]
    assert a["recommendation"] == b["recommendation"] == "LONG"
    assert a["quality_gate_passed"] == b["quality_gate_passed"] is True
    assert a["setup_quality_score"] == b["setup_quality_score"]
    assert b["community_component_shadow"]["weighted_score"] == -1.0
    assert b["community_component_shadow"]["live_authority"] is False
    assert b["community_component_shadow"]["affects_live_gate"] is False


def test_invalid_component_signal_fails_payload_validation_closed():
    payload = _strong_eur_payload()
    payload["community_component_signals"] = {"trendilo": 1.5}
    result = decide_bridge_event("evt-shadow-invalid", payload)
    assert result["status"] == "ingested_context"
    assert result["decision"]["action"] == "store_context_only"
    assert any(
        "community_component_signals" in field
        for field in result["decision"]["missing_or_invalid_fields"]
    )
