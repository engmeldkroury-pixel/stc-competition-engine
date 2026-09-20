from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["human_approval_required"] is True


def test_competitions():
    r = client.get("/competitions")
    assert r.status_code == 200
    data = r.json()
    assert data["amp-futures-sep-2026"]["allowed_symbols_count"] > 80
    assert data["capital-africa-sep-2026"]["allowed_symbols_count"] == 10


def test_order_validation_endpoint():
    r = client.post(
        "/rules/validate-order",
        json={
            "competition_id": "capital-africa-sep-2026",
            "symbol": "CAPITALCOM:NAS100",
            "side": "BUY",
            "requested_quantity": 11,
            "current_open_quantity": 0,
            "transactions_last_60s": 0,
            "account_equity": 100000,
            "risk_amount": 500,
            "max_risk_fraction": 0.02,
        },
    )
    assert r.status_code == 200
    assert r.json()["allowed"] is False


def test_webhook_creates_manual_signal():
    r = client.post(
        "/webhooks/tradingview",
        json={
            "event": "bar_close",
            "competition_id": "capital-africa-sep-2026",
            "symbol": "CAPITALCOM:XAUUSD",
            "timeframe": "5",
            "time": "2026-09-19T12:00:00Z",
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
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["received"] is True
    assert body["execution"] == "manual_approval_required"
    assert body["signal"]["requires_human_approval"] is True


def test_trade_event_summary_tracks_realized_pnl_and_days():
    open_event = {
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "event": "OPEN",
        "side": "LONG",
        "quantity": 1,
        "price": 3600,
        "event_time": "2026-09-19T10:00:00Z",
        "realized_pnl_delta": 0,
    }
    r = client.post("/trade-events", json=open_event)
    assert r.status_code == 200
    trade_id = r.json()["trade_id"]

    close_event = dict(open_event)
    close_event.update({
        "event": "CLOSE",
        "price": 3620,
        "event_time": "2026-09-20T10:00:00Z",
        "trade_id": trade_id,
        "realized_pnl_delta": 500,
    })
    r = client.post("/trade-events", json=close_event)
    assert r.status_code == 200
    assert r.json()["realized_pnl_total"] >= 500
    assert r.json()["qualifying_trading_days"] >= 2


def test_dashboard_renders():
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "STC Competition Dashboard" in r.text


def test_capability_endpoint_reports_verified_capital_xau_limitations():
    r = client.get("/data/capabilities/CAPITALCOM:XAUUSD")
    assert r.status_code == 200
    body = r.json()
    assert body["verified"] is True
    assert body["native_technicals"] is False
    assert body["technical_path"] == "local_from_ohlcv"


def test_provider_check_blocks_silent_oanda_substitution():
    r = client.post(
        "/data/provider-check",
        json={
            "requested_symbol": "CAPITALCOM:XAUUSD",
            "candidate_symbol": "OANDA:XAUUSD",
            "allow_cross_provider": False,
        },
    )
    assert r.status_code == 200
    assert r.json()["allowed"] is False


def test_webhook_duplicate_is_idempotent():
    payload = {
        "event_id": "evt-test-idempotency-1",
        "event": "bar_close",
        "competition_id": "capital-africa-sep-2026",
        "symbol": "CAPITALCOM:XAUUSD",
        "timeframe": "5",
        "time": "2026-09-19T12:05:00Z",
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
    first = client.post("/webhooks/tradingview", json=payload)
    second = client.post("/webhooks/tradingview", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is True
    assert second.json()["execution"] == "no_duplicate_processing"


def test_approval_request_rejects_caller_verification_booleans():
    r = client.post(
        "/signals/missing-signal/approve",
        json={
            "current_signal_score": 0.5,
            "current_market_state_hash": "hash",
            "quote_evidence_id": "quote-evidence-123",
            "market_evidence_id": "market-evidence-123",
            "quote_freshness_verified": True,
            "market_open_verified": True,
        },
    )
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert any(x["type"] == "extra_forbidden" for x in detail)
