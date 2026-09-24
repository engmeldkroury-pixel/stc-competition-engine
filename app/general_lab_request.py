from __future__ import annotations

from typing import Any

from .research_runner import run_symbol_research
from .shadow_promotion_registry import public_shadow_record, shadow_candidates


def _provider_qualified(symbol: str) -> str:
    value = str(symbol or "").strip().upper()
    if not value or ":" not in value:
        raise ValueError("General Lab evaluation requires a provider-qualified exact symbol")
    return value


def build_general_lab_completion(payload: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one durable General Lab request from exact-provider series.

    This function intentionally performs no data download. An authorized data
    worker must supply exact-provider OHLCV series, keeping provider access
    separate from the hosted STC application.
    """
    request_id = str(payload.get("request_id") or "").strip()
    if not request_id:
        raise ValueError("General Lab evaluation requires request_id")

    resolved_symbol = _provider_qualified(
        str(payload.get("resolved_symbol") or payload.get("symbol") or "")
    )
    series = payload.get("series")
    if not isinstance(series, dict) or not series:
        raise ValueError("General Lab evaluation requires exact-provider series")

    research_payload: dict[str, Any] = {
        "symbol": resolved_symbol,
        "series": series,
        "research_mode": str(payload.get("research_mode") or "full"),
    }
    result = run_symbol_research(research_payload)
    result["general_lab"] = True
    result["execution"] = "research_only"
    result["live_authority"] = False
    result["promotion_required"] = True
    result["data_source_policy"] = "exact_provider_history_required_no_silent_substitution"
    result["existing_shadow_records"] = [
        public_shadow_record(row) for row in shadow_candidates(symbol=resolved_symbol)
    ]

    return {
        "action": "COMPLETE",
        "request_id": request_id,
        "resolved_symbol": resolved_symbol,
        "result": result,
    }
