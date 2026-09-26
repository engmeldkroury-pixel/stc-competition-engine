from app.community_shadow import build_community_component_shadow
from app.event_decision import decide_bridge_event


def test_eurusd_shadow_uses_symbol_specific_trendilo_weight_only():
    shadow = build_community_component_shadow(
        "CAPITALCOM:EURUSD",
        "15",
        {"trendilo": -0.75},
    )
    assert shadow["status"] == "COMPLETE_SHADOW_EVIDENCE"
    assert shadow["complete"] is True
    assert shadow["weighted_score"] == -0.75
    assert shadow["normalized_weights"] == {"trendilo": 1.0}
    assert shadow["selected_parameters"]["trendilo"]["lookback"] == 50
    assert shadow["selected_parameters"]["trendilo"]["alma_offset"] == 0.85
    assert shadow["live_authority"] is False
    assert shadow["used_in_quality_gate"] is False
    assert shadow["used_in_risk"] is False
    assert shadow["used_in_approval"] is False


def test_usdzar_shadow_requires_every_validated_component_before_scoring():
    shadow = build_community_component_shadow(
        "CAPITALCOM:USDZAR",
        "15",
        {"lorentzian_classification": 1.0},
    )
    assert shadow["status"] == "INCOMPLETE_SHADOW_EVIDENCE"
    assert shadow["complete"] is False
    assert shadow["weighted_score"] is None
    assert "nadaraya_watson_endpoint_nonrepaint" in shadow["missing_components"]
    assert "alphatrend" in shadow["missing_components"]
    assert "supertrend_kivanc" in shadow["missing_components"]
    assert "ut_bot_alerts" in shadow["missing_components"]


def test_xauusd_shadow_does_not_invent_a_profile_when_research_found_none():
    shadow = build_community_component_shadow(
        "CAPITALCOM:XAUUSD",
        "15",
        {"trendilo": 1.0},
    )
    assert shadow["status"] == "NO_VALIDATED_COMMUNITY_PROFILE"
    assert shadow["normalized_weights"] == {}
    assert shadow["weighted_score"] is None
    assert shadow["unexpected_components_ignored"] == ["trendilo"]


def _strong_eurusd_payload(event_id: str) -> dict:
    return {
        "event_id": event_id,
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:EURUSD",
        "timeframe": "15",
        "time": "2026-09-24T10:15:00Z",
        "open": 1.13698,
        "high": 1.13700,
        "low": 1.13613,
        "close": 1.13627,
        "volume": 1931,
        "ema20": 1.137887834,
        "ema50": 1.1382486144,
        "rsi14": 27.9164797027,
        "atr14": 0.0006102924,
        "macd": -0.0003517138,
        "macd_signal": -0.0000964527,
        "volume_ratio": 1.054903032,
        "family_trend": -1.0,
        "family_momentum": -0.9533363248,
        "family_volatility": -0.6,
        "family_volume": -0.354903032,
        "family_vwap": -1.0,
        "family_market_structure": -1.0,
        "family_smc_liquidity": -0.2,
        "family_price_action": -0.3051724138,
        "family_microstructure": -0.6316163852,
        "confirm_timeframe": "60",
        "confirm_time": "2026-09-24T09:00:00Z",
        "confirm_close": 1.13739,
        "confirm_ema20": 1.1387753142,
        "confirm_ema50": 1.1410026747,
        "confirm_ema200": 1.1476547948,
        "confirm_rsi14": 38.5035622665,
        "confirm_atr14": 0.0012161357,
        "confirm_macd": -0.0009750028,
        "confirm_macd_signal": -0.0011766183,
        "confirm_volume_ratio": 1.4395393474,
        "trend_2h_time": "2026-09-24T07:00:00Z",
        "trend_2h_score": -1.0,
        "trend_4h_time": "2026-09-24T05:00:00Z",
        "trend_4h_score": -0.85,
        "trend_1m_time": "2026-08-02T21:00:00Z",
        "trend_1m_score": 0.6,
        "history_timeframe": "1D",
        "history_time": "2026-09-22T21:00:00Z",
        "history_close": 1.13833,
        "history_ema50": 1.1541556489,
        "history_ema200": 1.1561883539,
        "history_rsi14": 26.802294643,
        "history_atr14": 0.0050095026,
        "history_high_252": 1.20824,
        "history_low_252": 1.13242,
        "history_momentum_20": -0.0230436499,
        "history_momentum_63": -0.0000175693,
        "history_momentum_126": -0.0146205917,
        "history_momentum_252": -0.0283804776,
        "history_volatility_20": 0.0044062627,
    }


def test_shadow_component_score_cannot_change_live_trade_decision():
    payload = _strong_eurusd_payload("evt-shadow-boundary")
    baseline = decide_bridge_event("evt-shadow-boundary", payload)

    contradicted = {
        **payload,
        "community_component_signals": {"trendilo": 1.0},
    }
    with_shadow = decide_bridge_event("evt-shadow-boundary", contradicted)

    base_signal = baseline["decision"]["signal"]
    shadow_signal = with_shadow["decision"]["signal"]
    assert base_signal["recommendation"] == shadow_signal["recommendation"]
    assert base_signal["quality_gate_passed"] == shadow_signal["quality_gate_passed"]
    assert base_signal["setup_quality_score"] == shadow_signal["setup_quality_score"]
    assert base_signal["composite_score"] == shadow_signal["composite_score"]
    assert shadow_signal["community_component_shadow"]["weighted_score"] == 1.0
    assert shadow_signal["community_component_shadow"]["live_authority"] is False
    assert with_shadow["decision"]["locked_trade_plan"] == baseline["decision"]["locked_trade_plan"]


def test_invalid_shadow_signal_value_is_stored_as_context_only():
    payload = _strong_eurusd_payload("evt-shadow-invalid")
    payload["community_component_signals"] = {"trendilo": 1.5}
    result = decide_bridge_event("evt-shadow-invalid", payload)
    assert result["status"] == "ingested_context"
    assert result["decision"]["action"] == "store_context_only"
    assert result["decision"]["reason"] == "insufficient_signal_payload"


def test_amp_mng_shadow_uses_validated_range_filter_profile():
    shadow = build_community_component_shadow(
        "NYMEX:MNG1!",
        "15m",
        {"range_filter_guikroth": -1.0},
    )
    assert shadow["status"] == "COMPLETE_SHADOW_EVIDENCE"
    assert shadow["weighted_score"] == -1.0
    assert shadow["normalized_weights"] == {"range_filter_guikroth": 1.0}
    assert shadow["selected_parameters"]["range_filter_guikroth"] == {
        "sampling_period": 100,
        "range_multiplier": 2.0,
    }
    assert shadow["live_authority"] is False
    assert shadow["used_in_quality_gate"] is False


def test_amp_mcl_shadow_requires_full_validated_ensemble():
    shadow = build_community_component_shadow(
        "NYMEX:MCL1!",
        "15",
        {
            "ssl_hybrid": 1.0,
            "qqe_mod": 1.0,
        },
    )
    assert shadow["status"] == "INCOMPLETE_SHADOW_EVIDENCE"
    assert shadow["weighted_score"] is None
    assert "chandelier_exit_everget" in shadow["missing_components"]
    assert "range_filter_guikroth" in shadow["missing_components"]
    assert "ut_bot_alerts" in shadow["missing_components"]
    assert "schaff_trend_cycle" in shadow["missing_components"]
    assert "squeeze_momentum_lazybear" in shadow["missing_components"]


def test_amp_mgc_complete_shadow_weight_is_normalized():
    shadow = build_community_component_shadow(
        "COMEX_MINI:MGC1!",
        "15",
        {
            "qqe_mod": 1.0,
            "ssl_hybrid": 1.0,
        },
    )
    assert shadow["status"] == "COMPLETE_SHADOW_EVIDENCE"
    assert abs(shadow["weighted_score"] - 1.0) < 1e-12
    assert abs(sum(shadow["normalized_weights"].values()) - 1.0) < 1e-12
    assert shadow["selected_parameters"]["qqe_mod"]["rsi_period"] == 8
    assert shadow["selected_parameters"]["ssl_hybrid"]["baseline_length"] == 60


def test_amp_unvalidated_core_symbol_does_not_invent_shadow_profile():
    shadow = build_community_component_shadow(
        "CME_MINI:MES1!",
        "15",
        {"ssl_hybrid": 1.0},
    )
    assert shadow["status"] == "NO_VALIDATED_COMMUNITY_PROFILE"
    assert shadow["normalized_weights"] == {}
    assert shadow["weighted_score"] is None
    assert shadow["unexpected_components_ignored"] == ["ssl_hybrid"]
