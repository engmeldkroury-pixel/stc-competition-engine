from app.event_decision import decide_bridge_event, deterministic_signal_id


def test_pure_test_event_archives_without_side_effects():
    result = decide_bridge_event(
        "evt-test-pure",
        {"competition_id": "STC-TEST", "symbol": "BITSTAMP:BTCUSD", "time": "2026-09-20T07:00:00Z"},
    )
    assert result["status"] == "ingested_context"
    assert result["decision"]["execution"] == "none"
    assert result["receipt"]["event_id"] == "evt-test-pure"
    assert result["receipt"]["status"] == "ingested_context"


def test_pure_full_event_builds_deterministic_signal_and_envelope():
    payload = {
        "event_id": "evt-full-pure",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-20T07:00:00Z",
        "open": 3600,
        "high": 3615,
        "low": 3595,
        "close": 3610,
        "volume": 1000,
        "ema20": 3605,
        "ema50": 3590,
        "rsi14": 62,
        "atr14": 10,
        "macd": 5,
        "macd_signal": 2,
        "volume_ratio": 1.7,
    }
    result = decide_bridge_event("evt-full-pure", payload)
    assert result["status"] == "analyzed"
    decision = result["decision"]
    assert decision["action"] == "signal_created"
    assert decision["signal"]["signal_id"] == deterministic_signal_id("evt-full-pure")
    assert decision["approval_envelope"]["validity_minutes"] == 30
    assert decision["execution"] == "manual_approval_required"
    receipt = result["receipt"]
    assert receipt["event_id"] == "evt-full-pure"
    assert receipt["signal_id"] == deterministic_signal_id("evt-full-pure")
    assert receipt["action"] == "signal_created"
    assert receipt["status"] == "analyzed"


def test_pipeline_receipt_is_deterministic_for_same_event_and_payload():
    payload = {
        "competition_id": "STC-TEST",
        "symbol": "BITSTAMP:BTCUSD",
        "time": "2026-09-20T07:00:00Z",
        "source": "TradingView-Manual-Test",
    }
    a = decide_bridge_event("evt-receipt-deterministic", payload)
    b = decide_bridge_event("evt-receipt-deterministic", payload)
    assert a["receipt"] == b["receipt"]
    assert a["receipt"]["receipt_id"].startswith("stc-receipt-")
    assert len(a["receipt"]["payload_sha256"]) == 64



def test_event_decision_marks_live_quality_and_unavailable_news_macro_honestly():
    payload = {
        "event_id": "evt-quality-reasons",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 4300,
        "high": 4310,
        "low": 4300,
        "close": 4308,
        "volume": 1800,
        "ema20": 4305,
        "ema50": 4290,
        "rsi14": 60,
        "atr14": 10,
        "macd": 4,
        "macd_signal": 2,
        "volume_ratio": 1.8,
    }
    result = decide_bridge_event("evt-quality-reasons", payload)
    reasons = result["decision"]["signal"]["reasons"]
    assert any(x.startswith("volatility_quality_live=") for x in reasons)
    assert any(x.startswith("liquidity_quality_live=") for x in reasons)
    assert "news_factor=unavailable_live_source" in reasons
    assert "macro_factor=unavailable_live_source" in reasons

def _strong_confirmation():
    return {
        "confirm_timeframe": "60",
        "confirm_time": "2026-09-21T17:00:00Z",
        "confirm_close": 3608,
        "confirm_ema20": 3600,
        "confirm_ema50": 3580,
        "confirm_ema200": 3400,
        "confirm_rsi14": 60,
        "confirm_atr14": 20,
        "confirm_macd": 8,
        "confirm_macd_signal": 4,
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
    }


def _strong_history():
    return {
        "history_timeframe": "1D",
        "history_time": "2026-09-20T00:00:00Z",
        "history_close": 3610,
        "history_ema50": 3500,
        "history_ema200": 3300,
        "history_rsi14": 62,
        "history_atr14": 80,
        "history_high_252": 3650,
        "history_low_252": 2500,
        "history_momentum_20": 0.08,
        "history_momentum_63": 0.15,
        "history_momentum_126": 0.20,
        "history_momentum_252": 0.35,
        "history_volatility_20": 0.02,
    }


def test_high_conviction_gate_allows_only_a_plus_directional_plan():
    payload = {
        "event_id": "evt-a-plus",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 3600,
        "high": 3615,
        "low": 3605,
        "close": 3610,
        "volume": 1800,
        "ema20": 3605,
        "ema50": 3590,
        "rsi14": 60,
        "atr14": 10,
        "macd": 5,
        "macd_signal": 2,
        "volume_ratio": 1.8,
        **_strong_confirmation(),
        **_strong_history(),
    }
    result = decide_bridge_event("evt-a-plus", payload)
    signal = result["decision"]["signal"]
    assert signal["recommendation"] == "LONG"
    assert signal["quality_gate_passed"] is True
    assert signal["setup_grade"] == "A_PLUS"
    assert result["decision"]["locked_trade_plan"] is not None
    assert "high_conviction_gate=PASSED" in signal["reasons"]


def test_borderline_direction_is_downgraded_to_wait_and_has_no_plan():
    payload = {
        "event_id": "evt-borderline",
        "event": "bar_close",
        "competition_id": "amp-futures-sep-2026",
        "symbol": "CBOT:ZN1!",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 105.0,
        "high": 105.2,
        "low": 104.9,
        "close": 105.0,
        "volume": 1000,
        "ema20": 105.05,
        "ema50": 105.10,
        "rsi14": 49,
        "atr14": 0.25,
        "macd": -0.01,
        "macd_signal": 0.0,
        "volume_ratio": 0.7,
    }
    result = decide_bridge_event("evt-borderline", payload)
    signal = result["decision"]["signal"]
    assert signal["recommendation"] == "WAIT"
    assert signal["quality_gate_passed"] is False
    assert signal["setup_grade"] == "MONITOR_ONLY"
    assert result["decision"]["locked_trade_plan"] is None
    assert "high_conviction_gate=BLOCKED" in signal["reasons"]

def test_directional_candidate_without_1h_confirmation_fails_closed_to_wait():
    payload = {
        "event_id": "evt-missing-confirm",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 3600,
        "high": 3615,
        "low": 3605,
        "close": 3610,
        "volume": 1800,
        "ema20": 3605,
        "ema50": 3590,
        "rsi14": 60,
        "atr14": 10,
        "macd": 5,
        "macd_signal": 2,
        "volume_ratio": 1.8,
        **_strong_history(),
    }
    result = decide_bridge_event("evt-missing-confirm", payload)
    signal = result["decision"]["signal"]
    assert signal["recommendation"] == "WAIT"
    assert signal["quality_gate_passed"] is False
    assert "gate_block=confirmation_context_present" in signal["reasons"]
    assert result["decision"]["locked_trade_plan"] is None




def test_live_signal_exposes_mtf_confirmation_and_separates_quality_from_probability():
    payload = {
        "event_id": "evt-owner-visibility",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 3600,
        "high": 3614,
        "low": 3598,
        "close": 3610,
        "volume": 1800,
        "ema20": 3605,
        "ema50": 3590,
        "rsi14": 60,
        "atr14": 10,
        "macd": 5,
        "macd_signal": 2,
        "volume_ratio": 1.8,
        **_strong_confirmation(),
        **_strong_history(),
    }
    result = decide_bridge_event("evt-owner-visibility", payload)
    signal = result["decision"]["signal"]
    assert signal["setup_quality_score"] >= 90
    assert signal["timeframe_confirmation"]["entry_timeframe"] == "15"
    assert signal["timeframe_confirmation"]["1h_score"] is not None
    assert signal["timeframe_confirmation"]["2h_score"] == 0.85
    assert signal["timeframe_confirmation"]["4h_score"] == 0.82
    assert signal["timeframe_confirmation"]["1m_score"] == 0.72
    probability = signal["empirical_win_probability"]
    assert probability["status"] == "NOT_CALIBRATED"
    assert probability["estimated_probability"] is None
    assert "not win probability" in probability["note"].lower()



def _strong_directional_payload(event_id: str):
    return {
        "event_id": event_id,
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "15",
        "time": "2026-09-21T18:00:00Z",
        "open": 3600,
        "high": 3614,
        "low": 3598,
        "close": 3610,
        "volume": 1800,
        "ema20": 3605,
        "ema50": 3590,
        "rsi14": 60,
        "atr14": 10,
        "macd": 5,
        "macd_signal": 2,
        "volume_ratio": 1.8,
        **_strong_confirmation(),
        **_strong_history(),
    }


def test_strong_mtf_candidate_without_family_breadth_fails_closed():
    payload = _strong_directional_payload("evt-no-families")
    for key in list(payload):
        if key.startswith("family_"):
            del payload[key]
    result = decide_bridge_event("evt-no-families", payload)
    signal = result["decision"]["signal"]
    assert signal["recommendation"] == "WAIT"
    assert signal["live_family_evidence"] is None
    assert "gate_block=family_evidence_present" in signal["reasons"]
    assert result["decision"]["locked_trade_plan"] is None


def test_three_strongly_conflicting_evidence_families_block_a_plus_plan():
    payload = _strong_directional_payload("evt-family-conflict")
    payload["family_momentum"] = -0.90
    payload["family_price_action"] = -0.85
    payload["family_microstructure"] = -0.80
    result = decide_bridge_event("evt-family-conflict", payload)
    signal = result["decision"]["signal"]
    assert signal["recommendation"] == "WAIT"
    assert signal["live_family_evidence"]["conflicting_families"] >= 3
    assert "gate_block=family_conflicts" in signal["reasons"]
    assert result["decision"]["locked_trade_plan"] is None
