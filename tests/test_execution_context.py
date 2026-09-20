from datetime import datetime, timedelta, timezone

from app.approval import build_approval_envelope
from app.execution_context import derive_execution_context


def _envelope():
    payload = {
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "timeframe":"15m",
        "close":1.15,
        "atr14":0.002,
        "ema20":1.149,
        "ema50":1.148,
        "rsi14":60,
        "macd":0.001,
        "macd_signal":0.0005,
    }
    return build_approval_envelope(payload, 0.5)


def test_trusted_fresh_evidence_derives_verified_context():
    now = datetime.now(timezone.utc)
    q = {
        "evidence_id":"quote-evidence-001",
        "source":"tradingview_mcp_direct_quote",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "provider":"CAPITALCOM",
        "observed_at_utc":now,
        "quote_price":1.1502,
        "update_mode":"streaming",
        "market_status":"unknown",
    }
    m = {
        "evidence_id":"market-evidence-001",
        "source":"broker_session_status",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "provider":"CAPITALCOM",
        "observed_at_utc":now,
        "quote_price":None,
        "update_mode":None,
        "market_status":"open",
    }
    result = derive_execution_context(_envelope(), q, m, now=now)
    assert result["quote_freshness_verified"] is True
    assert result["market_open_verified"] is True
    assert result["current_price"] == 1.1502
    assert result["evidence_reasons"] == []


def test_stale_quote_fails_closed():
    now = datetime.now(timezone.utc)
    q = {
        "evidence_id":"quote-evidence-002",
        "source":"tradingview_mcp_direct_quote",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "provider":"CAPITALCOM",
        "observed_at_utc":now - timedelta(minutes=5),
        "quote_price":1.1502,
        "update_mode":"streaming",
        "market_status":"unknown",
    }
    result = derive_execution_context(_envelope(), q, None, now=now)
    assert result["quote_freshness_verified"] is False
    assert "quote_evidence_stale" in result["evidence_reasons"]
    assert result["market_open_verified"] is False


def test_wrong_provider_or_symbol_fails_closed():
    now = datetime.now(timezone.utc)
    q = {
        "evidence_id":"quote-evidence-003",
        "source":"owner_platform_confirmation",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"OANDA:EURUSD",
        "provider":"OANDA",
        "observed_at_utc":now,
        "quote_price":1.1502,
        "update_mode":None,
        "market_status":"open",
    }
    result = derive_execution_context(_envelope(), q, q, now=now)
    assert result["quote_freshness_verified"] is False
    assert result["market_open_verified"] is False
    assert "quote_evidence_target_mismatch" in result["evidence_reasons"]
    assert "market_evidence_target_mismatch" in result["evidence_reasons"]


def test_future_dated_evidence_fails_closed():
    now = datetime.now(timezone.utc)
    future = now + timedelta(minutes=5)
    q = {
        "evidence_id":"quote-evidence-future",
        "source":"tradingview_mcp_direct_quote",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "provider":"CAPITALCOM",
        "observed_at_utc":future,
        "quote_price":1.1502,
        "update_mode":"streaming",
        "market_status":"unknown",
    }
    m = {
        "evidence_id":"market-evidence-future",
        "source":"broker_session_status",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "provider":"CAPITALCOM",
        "observed_at_utc":future,
        "quote_price":None,
        "update_mode":None,
        "market_status":"open",
    }
    result = derive_execution_context(_envelope(), q, m, now=now)
    assert result["quote_freshness_verified"] is False
    assert result["market_open_verified"] is False
    assert "quote_evidence_from_future" in result["evidence_reasons"]
    assert "market_evidence_from_future" in result["evidence_reasons"]


def test_malformed_evidence_timestamp_fails_closed_without_exception():
    q = {
        "evidence_id":"quote-evidence-badtime",
        "source":"tradingview_mcp_direct_quote",
        "competition_id":"capital-africa-sep-2026",
        "symbol":"CAPITALCOM:EURUSD",
        "provider":"CAPITALCOM",
        "observed_at_utc":"not-a-time",
        "quote_price":1.1502,
        "update_mode":"streaming",
        "market_status":"unknown",
    }
    result = derive_execution_context(_envelope(), q, None)
    assert result["quote_freshness_verified"] is False
    assert "quote_evidence_stale" in result["evidence_reasons"]
