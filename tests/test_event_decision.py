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
