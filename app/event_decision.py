from __future__ import annotations

import hashlib

from pydantic import ValidationError

from .approval import build_approval_envelope
from .competition_profiles import get_profile
from .models import FactorScores, SignalEvaluationRequest, TradingViewWebhook
from .signals import evaluate, factors_from_tradingview


def deterministic_signal_id(event_id: str) -> str:
    digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()[:32]
    return f"bridge-{digest}"


def decide_bridge_event(event_id: str, payload: dict) -> dict:
    """Pure event decision function.

    This function has no persistence side effects and is therefore safe for
    serverless runtimes. The caller owns persistence/acknowledgement.
    """
    competition_id = payload.get("competition_id")
    symbol = payload.get("symbol")

    if competition_id == "STC-TEST":
        return {
            "event_id": event_id,
            "status": "ingested_context",
            "decision": {
                "action": "archive_test_event",
                "execution": "none",
            },
            "note": "Transport test event; no trading analysis.",
        }

    try:
        profile = get_profile(str(competition_id))
    except KeyError:
        return {
            "event_id": event_id,
            "status": "rejected",
            "decision": {"action": "reject", "reason": "unknown_competition"},
            "note": "Unknown competition id.",
        }

    if symbol not in profile.max_open_position:
        return {
            "event_id": event_id,
            "status": "rejected",
            "decision": {"action": "reject", "reason": "symbol_not_allowed"},
            "note": "Symbol is not allowed in competition profile.",
        }

    try:
        tv = TradingViewWebhook.model_validate(payload)
    except ValidationError as exc:
        return {
            "event_id": event_id,
            "status": "ingested_context",
            "decision": {
                "action": "store_context_only",
                "reason": "insufficient_signal_payload",
                "missing_or_invalid_fields": [
                    ".".join(str(x) for x in err["loc"]) for err in exc.errors()
                ],
                "execution": "none",
            },
            "note": "Valid competition event stored, but payload is insufficient for signal evaluation.",
        }

    technical = factors_from_tradingview(tv)
    req = SignalEvaluationRequest(
        competition_id=tv.competition_id,
        symbol=tv.symbol,
        factors=FactorScores(technical=technical),
    )
    result = evaluate(req).model_copy(update={"signal_id": deterministic_signal_id(event_id)})
    result_dict = result.model_dump()
    envelope = build_approval_envelope(payload, result.composite_score)
    return {
        "event_id": event_id,
        "status": "analyzed",
        "decision": {
            "action": "signal_created",
            "signal": result_dict,
            "approval_envelope": envelope,
            "execution": "manual_approval_required",
        },
        "note": "Signal created; no automatic order execution.",
    }
