from __future__ import annotations

import hashlib

from pydantic import ValidationError

from .approval import build_approval_envelope
from .competition_profiles import get_profile
from .models import FactorScores, SignalEvaluationRequest, TradingViewWebhook
from .pipeline_receipt import build_pipeline_receipt
from .signals import (
    evaluate,
    factors_from_tradingview,
    confirmation_score_from_tradingview,
    historical_regime_from_tradingview,
    high_conviction_assessment,
    liquidity_quality_from_tradingview,
    setup_quality_score,
    short_term_score_from_tradingview,
    volatility_quality_from_tradingview,
)
from .trade_plan import build_locked_trade_plan


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
        status = "ingested_context"
        action = "archive_test_event"
        return {
            "event_id": event_id,
            "status": status,
            "decision": {
                "action": action,
                "execution": "none",
            },
            "receipt": build_pipeline_receipt(event_id, payload, status=status, action=action),
            "note": "Transport test event; no trading analysis.",
        }

    try:
        profile = get_profile(str(competition_id))
    except KeyError:
        status = "rejected"
        action = "reject"
        return {
            "event_id": event_id,
            "status": status,
            "decision": {"action": action, "reason": "unknown_competition"},
            "receipt": build_pipeline_receipt(event_id, payload, status=status, action=action),
            "note": "Unknown competition id.",
        }

    if symbol not in profile.max_open_position:
        status = "rejected"
        action = "reject"
        return {
            "event_id": event_id,
            "status": status,
            "decision": {"action": action, "reason": "symbol_not_allowed"},
            "receipt": build_pipeline_receipt(event_id, payload, status=status, action=action),
            "note": "Symbol is not allowed in competition profile.",
        }

    try:
        tv = TradingViewWebhook.model_validate(payload)
    except ValidationError as exc:
        status = "ingested_context"
        action = "store_context_only"
        return {
            "event_id": event_id,
            "status": status,
            "decision": {
                "action": action,
                "reason": "insufficient_signal_payload",
                "missing_or_invalid_fields": [
                    ".".join(str(x) for x in err["loc"]) for err in exc.errors()
                ],
                "execution": "none",
            },
            "receipt": build_pipeline_receipt(event_id, payload, status=status, action=action),
            "note": "Valid competition event stored, but payload is insufficient for signal evaluation.",
        }

    short_term_technical = short_term_score_from_tradingview(tv)
    confirmation_score = confirmation_score_from_tradingview(tv)
    historical_regime = historical_regime_from_tradingview(tv)
    technical = factors_from_tradingview(tv)
    volatility_quality = volatility_quality_from_tradingview(tv, technical)
    liquidity_quality = liquidity_quality_from_tradingview(tv, technical)
    req = SignalEvaluationRequest(
        competition_id=tv.competition_id,
        symbol=tv.symbol,
        factors=FactorScores(
            technical=technical,
            volatility_quality=volatility_quality,
            liquidity_quality=liquidity_quality,
        ),
    )
    base_result = evaluate(req).model_copy(update={"signal_id": deterministic_signal_id(event_id)})
    gate_passed, gate_failures = high_conviction_assessment(
        recommendation=base_result.recommendation,
        composite_score=base_result.composite_score,
        short_term_technical=short_term_technical,
        historical_regime=historical_regime,
        blended_technical=technical,
        volatility_quality=volatility_quality,
        liquidity_quality=liquidity_quality,
        confirmation_score=confirmation_score,
        trend_2h_score=tv.trend_2h_score,
        trend_4h_score=tv.trend_4h_score,
        trend_1m_score=tv.trend_1m_score,
    )

    quality_score = setup_quality_score(
        recommendation=base_result.recommendation,
        short_term_technical=short_term_technical,
        confirmation_score=confirmation_score,
        trend_2h_score=tv.trend_2h_score,
        trend_4h_score=tv.trend_4h_score,
        historical_regime=historical_regime,
        trend_1m_score=tv.trend_1m_score,
        blended_technical=technical,
        volatility_quality=volatility_quality,
        liquidity_quality=liquidity_quality,
    )

    final_gate_passed = gate_passed and quality_score >= 90
    if gate_passed and quality_score < 90:
        gate_failures = [*gate_failures, "setup_quality_below_90"]
    final_recommendation = base_result.recommendation if final_gate_passed else "WAIT"
    gate_reason = "high_conviction_gate=PASSED" if final_gate_passed else "high_conviction_gate=BLOCKED"
    gate_details = (
        ["setup_grade=A_PLUS", f"setup_quality={quality_score}/100"]
        if final_gate_passed
        else [f"gate_block={reason}" for reason in gate_failures] + [f"setup_quality={quality_score}/100"]
    )
    extra_reasons = [
        f"short_term_technical={short_term_technical:+.2f}",
        "confirmation_1h=unavailable" if confirmation_score is None else f"confirmation_1h={confirmation_score:+.2f}",
        "trend_2h=unavailable" if tv.trend_2h_score is None else f"trend_2h={tv.trend_2h_score:+.2f}",
        "trend_4h=unavailable" if tv.trend_4h_score is None else f"trend_4h={tv.trend_4h_score:+.2f}",
        "historical_regime=unavailable" if historical_regime is None else f"historical_regime={historical_regime:+.2f}",
        "trend_1m=unavailable" if tv.trend_1m_score is None else f"trend_1m={tv.trend_1m_score:+.2f}",
        f"blended_technical={technical:+.2f}",
        f"volatility_quality_live={volatility_quality:+.2f}",
        f"liquidity_quality_live={liquidity_quality:+.2f}",
        "news_factor=unavailable_live_source",
        "macro_factor=unavailable_live_source",
        gate_reason,
        *gate_details,
    ]
    result = base_result.model_copy(update={
        "recommendation": final_recommendation,
        "reasons": extra_reasons + base_result.reasons,
    })
    result_dict = result.model_dump()
    result_dict["quality_gate_passed"] = final_gate_passed
    result_dict["setup_quality_score"] = quality_score
    result_dict["setup_quality_label"] = f"{quality_score}/100 setup quality; not a win probability"
    result_dict["setup_grade"] = "A_PLUS" if final_gate_passed else "MONITOR_ONLY"
    result_dict["pre_gate_recommendation"] = base_result.recommendation
    result_dict["quality_gate_failures"] = gate_failures
    envelope = build_approval_envelope(payload, result.composite_score)
    locked_plan = build_locked_trade_plan(event_id, payload, result_dict, envelope)
    status = "analyzed"
    action = "signal_created"
    return {
        "event_id": event_id,
        "status": status,
        "decision": {
            "action": action,
            "signal": result_dict,
            "approval_envelope": envelope,
            "locked_trade_plan": locked_plan,
            "execution": "manual_approval_required",
        },
        "receipt": build_pipeline_receipt(
            event_id,
            payload,
            status=status,
            action=action,
            signal_id=result.signal_id,
        ),
        "note": "Signal created; no automatic order execution.",
    }
