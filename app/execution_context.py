from __future__ import annotations

from datetime import datetime, timezone

from .data_capabilities import provider_of


QUOTE_SOURCES = {"tradingview_mcp_direct_quote", "owner_platform_confirmation"}
MARKET_STATUS_SOURCES = {"broker_session_status", "owner_platform_confirmation"}


def _age_seconds(observed_at, now: datetime) -> float:
    ts = observed_at
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        return float("inf")
    return max(0.0, (now - ts.astimezone(timezone.utc)).total_seconds())


def _matches_target(evidence: dict, envelope: dict) -> bool:
    expected_symbol = str(envelope.get("symbol") or "")
    expected_provider = provider_of(expected_symbol)
    expected_competition = str(envelope.get("competition_id") or "")
    if evidence.get("symbol") != expected_symbol:
        return False
    if str(evidence.get("provider") or "").upper() != expected_provider:
        return False
    ev_comp = evidence.get("competition_id")
    if ev_comp not in (None, "", expected_competition):
        return False
    return True


def derive_execution_context(
    envelope: dict,
    quote_evidence: dict | None,
    market_evidence: dict | None,
    *,
    now: datetime | None = None,
    direct_quote_max_age_seconds: int = 30,
    owner_quote_max_age_seconds: int = 60,
    market_status_max_age_seconds: int = 120,
) -> dict:
    """Derive approval execution context from persisted evidence.

    Caller supplied verification booleans are intentionally not accepted here.
    The function fails closed whenever evidence is missing, stale, mismatched,
    or from a source that is not trusted for the relevant assertion.
    """
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []

    price = 0.0
    quote_verified = False
    if quote_evidence is None:
        reasons.append("quote_evidence_missing")
    elif not _matches_target(quote_evidence, envelope):
        reasons.append("quote_evidence_target_mismatch")
    elif quote_evidence.get("source") not in QUOTE_SOURCES:
        reasons.append("quote_evidence_untrusted_source")
    elif not quote_evidence.get("quote_price"):
        reasons.append("quote_evidence_missing_price")
    else:
        source = quote_evidence.get("source")
        max_age = direct_quote_max_age_seconds if source == "tradingview_mcp_direct_quote" else owner_quote_max_age_seconds
        age = _age_seconds(quote_evidence.get("observed_at_utc"), now)
        if age > max_age:
            reasons.append("quote_evidence_stale")
        elif source == "tradingview_mcp_direct_quote" and str(quote_evidence.get("update_mode") or "").lower() != "streaming":
            reasons.append("quote_evidence_not_streaming")
        else:
            price = float(quote_evidence["quote_price"])
            quote_verified = True

    market_verified = False
    if market_evidence is None:
        reasons.append("market_evidence_missing")
    elif not _matches_target(market_evidence, envelope):
        reasons.append("market_evidence_target_mismatch")
    elif market_evidence.get("source") not in MARKET_STATUS_SOURCES:
        reasons.append("market_evidence_untrusted_source")
    else:
        age = _age_seconds(market_evidence.get("observed_at_utc"), now)
        if age > market_status_max_age_seconds:
            reasons.append("market_evidence_stale")
        elif market_evidence.get("market_status") != "open":
            reasons.append("market_not_open")
        else:
            market_verified = True

    return {
        "current_price": price,
        "quote_freshness_verified": quote_verified,
        "market_open_verified": market_verified,
        "evidence_reasons": reasons,
        "quote_evidence_id": quote_evidence.get("evidence_id") if quote_evidence else None,
        "market_evidence_id": market_evidence.get("evidence_id") if market_evidence else None,
    }
