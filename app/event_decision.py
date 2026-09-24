from __future__ import annotations

import hashlib

from pydantic import ValidationError

from .approval import build_approval_envelope
from .calibration_registry import calibration_to_public_dict, lookup_runtime_calibration
from .competition_profiles import get_profile
from .evidence_engine import aggregate_live_family_scores
from .models import FactorScores, SignalEvaluationRequest, TradingViewWebhook
from .pipeline_receipt import build_pipeline_receipt
from .signals import (
    evaluate,
    factors_from_tradingview,
    confirmation_score_from_tradingview,
    historical_regime_from_tradingview,
    high_conviction_assessment,
    competition_opportunity_assessment,
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
    calibration, calibration_reasons = lookup_runtime_calibration(
        tv.symbol,
        as_of=tv.time,
        timeframe=str(tv.timeframe),
    )
    calibration_matches_entry_timeframe = (
        calibration is not None and str(calibration.timeframe) == str(tv.timeframe)
    )
    family_evidence = aggregate_live_family_scores(
        {
            "trend": tv.family_trend,
            "momentum": tv.family_momentum,
            "volatility": tv.family_volatility,
            "volume": tv.family_volume,
            "vwap": tv.family_vwap,
            "market_structure": tv.family_market_structure,
            "smc_liquidity": tv.family_smc_liquidity,
            "price_action": tv.family_price_action,
            "microstructure": tv.family_microstructure,
        },
        strategy_id=(
            calibration.strategy_id
            if calibration_matches_entry_timeframe and calibration is not None
            else None
        ),
        family_weight_override=(
            calibration.family_weights
            if calibration_matches_entry_timeframe and calibration is not None
            else None
        ),
    )
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
    competition_mode = tv.competition_id == "capital-africa-sep-2026"
    if competition_mode:
        gate_passed, gate_failures = competition_opportunity_assessment(
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
            family_evidence_score=None if family_evidence is None else family_evidence.score,
            family_agreement_ratio=None if family_evidence is None else family_evidence.agreement_ratio,
            family_aligned_count=None if family_evidence is None else family_evidence.aligned_families,
            family_conflict_count=None if family_evidence is None else family_evidence.conflicting_families,
        )
    else:
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
            family_evidence_score=None if family_evidence is None else family_evidence.score,
            family_agreement_ratio=None if family_evidence is None else family_evidence.agreement_ratio,
            family_aligned_count=None if family_evidence is None else family_evidence.aligned_families,
            family_conflict_count=None if family_evidence is None else family_evidence.conflicting_families,
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
        family_evidence_score=None if family_evidence is None else family_evidence.score,
    )

    quality_floor = 78 if competition_mode else 90
    final_gate_passed = gate_passed and quality_score >= quality_floor
    if gate_passed and quality_score < quality_floor:
        gate_failures = [*gate_failures, f"setup_quality_below_{quality_floor}"]
    final_recommendation = base_result.recommendation if final_gate_passed else "WAIT"
    gate_name = "competition_opportunity_gate" if competition_mode else "high_conviction_gate"
    gate_reason = f"{gate_name}=PASSED" if final_gate_passed else f"{gate_name}=BLOCKED"
    gate_details = (
        [
            "setup_grade=COMPETITION_OPPORTUNITY" if competition_mode else "setup_grade=A_PLUS",
            f"setup_quality={quality_score}/100",
            f"quality_floor={quality_floor}/100",
        ]
        if final_gate_passed
        else [f"gate_block={reason}" for reason in gate_failures]
        + [f"setup_quality={quality_score}/100", f"quality_floor={quality_floor}/100"]
    )
    extra_reasons = [
        f"short_term_technical={short_term_technical:+.2f}",
        "confirmation_1h=unavailable" if confirmation_score is None else f"confirmation_1h={confirmation_score:+.2f}",
        "trend_2h=unavailable" if tv.trend_2h_score is None else f"trend_2h={tv.trend_2h_score:+.2f}",
        "trend_4h=unavailable" if tv.trend_4h_score is None else f"trend_4h={tv.trend_4h_score:+.2f}",
        "historical_regime=unavailable" if historical_regime is None else f"historical_regime={historical_regime:+.2f}",
        "trend_1m=unavailable" if tv.trend_1m_score is None else f"trend_1m={tv.trend_1m_score:+.2f}",
        "family_evidence=unavailable" if family_evidence is None else f"family_evidence={family_evidence.score:+.2f}",
        "family_agreement=unavailable" if family_evidence is None else f"family_agreement={family_evidence.agreement_ratio:.2f}",
        "family_breadth=unavailable" if family_evidence is None else f"family_breadth={family_evidence.aligned_families}/9",
        "family_conflicts=unavailable" if family_evidence is None else f"family_conflicts={family_evidence.conflicting_families}",
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
    result_dict["setup_grade"] = (
        "COMPETITION_OPPORTUNITY"
        if final_gate_passed and competition_mode
        else "A_PLUS"
        if final_gate_passed
        else "MONITOR_ONLY"
    )
    result_dict["competition_mode"] = competition_mode
    result_dict["quality_floor"] = quality_floor
    result_dict["pre_gate_recommendation"] = base_result.recommendation
    result_dict["quality_gate_failures"] = gate_failures
    result_dict["live_family_evidence"] = None if family_evidence is None else {
        "score": family_evidence.score,
        "agreement_ratio": family_evidence.agreement_ratio,
        "aligned_families": family_evidence.aligned_families,
        "conflicting_families": family_evidence.conflicting_families,
        "family_scores": dict(family_evidence.family_scores),
        "family_weights_used": dict(family_evidence.family_weights_used),
        "strategy_id": family_evidence.strategy_id,
        "calibration_applied": calibration_matches_entry_timeframe,
        "calibration_timeframe": None if calibration is None else calibration.timeframe,
        "entry_timeframe": str(tv.timeframe),
    }
    result_dict["timeframe_confirmation"] = {
        "entry_timeframe": str(tv.timeframe),
        "entry_score": short_term_technical,
        "1h_score": confirmation_score,
        "2h_score": tv.trend_2h_score,
        "4h_score": tv.trend_4h_score,
        "1d_score": historical_regime,
        "1m_score": tv.trend_1m_score,
    }
    if calibration is None:
        result_dict["empirical_win_probability"] = {
            "status": "NOT_CALIBRATED",
            "estimated_probability": None,
            "sample_size": 0,
            "reasons": list(calibration_reasons),
            "note": (
                "Setup quality is not win probability. A probability is displayed only "
                "after the selected strategy/timeframe has a current calibrated out-of-sample/forward record."
            ),
        }
        result_dict["research_calibration"] = {
            "status": "UNAVAILABLE",
            "reasons": list(calibration_reasons),
        }
    else:
        result_dict["empirical_win_probability"] = {
            "status": "CALIBRATED_INFORMATIONAL",
            "estimated_probability": calibration.estimated_probability,
            "sample_size": calibration.sample_size,
            "confidence_low": calibration.confidence_low,
            "confidence_high": calibration.confidence_high,
            "strategy_id": calibration.strategy_id,
            "timeframe": calibration.timeframe,
            "data_end_utc": calibration.data_end_utc.isoformat().replace("+00:00", "Z"),
            "note": (
                "Empirical out-of-sample/forward estimate for the calibrated research strategy/timeframe; "
                "informational only and never a guarantee of this trade."
            ),
        }
        result_dict["research_calibration"] = {
            "status": "AVAILABLE_INFORMATIONAL",
            **calibration_to_public_dict(calibration),
        }
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
