from __future__ import annotations

import hashlib
import math
from typing import Any


LIVE_PLAN_STOP_ATR_MULTIPLE = 1.20
LIVE_PLAN_TARGET1_RR = 1.50
LIVE_PLAN_FINAL_TARGET_RR = 2.50


def _finite_number(value: Any, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid_numeric_trade_plan_input")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite_trade_plan_input")
    if minimum is not None and number < minimum:
        raise ValueError("trade_plan_input_below_minimum")
    return number


def deterministic_plan_id(event_id: str, signal_id: str, rule_version: str = "stc-plan-v1") -> str:
    raw = f"{event_id}|{signal_id}|{rule_version}".encode("utf-8")
    return "plan-" + hashlib.sha256(raw).hexdigest()[:32]


def build_locked_trade_plan(
    event_id: str,
    payload: dict[str, Any],
    signal: dict[str, Any],
    envelope: dict[str, Any],
    *,
    rule_version: str = "stc-plan-v1",
    stop_atr_multiple: float = LIVE_PLAN_STOP_ATR_MULTIPLE,
    target1_rr: float = LIVE_PLAN_TARGET1_RR,
    target2_rr: float = LIVE_PLAN_FINAL_TARGET_RR,
) -> dict[str, Any] | None:
    """Build a frozen candidate plan from one analyzed signal.

    The plan is audit data only. It does not approve or execute anything.
    Levels are derived once from the persisted signal/envelope and must not be
    silently repriced by later bars. A later market state produces a new plan id.
    """
    recommendation = signal.get("recommendation")
    if recommendation == "WAIT":
        return None
    if recommendation not in {"LONG", "SHORT"}:
        raise ValueError("invalid_trade_plan_direction")

    competition_id = str(signal.get("competition_id") or "")
    symbol = str(signal.get("symbol") or "")
    signal_id = str(signal.get("signal_id") or "")
    if not competition_id or not symbol or not signal_id:
        raise ValueError("missing_trade_plan_identity")

    if payload.get("competition_id") != competition_id or payload.get("symbol") != symbol:
        raise ValueError("trade_plan_target_mismatch")
    if envelope.get("competition_id") != competition_id or envelope.get("symbol") != symbol:
        raise ValueError("trade_plan_envelope_target_mismatch")

    entry_min = _finite_number(envelope.get("entry_min"), minimum=0.0)
    entry_max = _finite_number(envelope.get("entry_max"), minimum=0.0)
    reference_price = _finite_number(envelope.get("reference_price"), minimum=0.0)
    atr = abs(_finite_number(payload.get("atr14"), minimum=0.0))
    score = _finite_number(signal.get("composite_score"))

    if not 0 < entry_min <= reference_price <= entry_max:
        raise ValueError("invalid_trade_plan_entry_envelope")
    if not -1.0 <= score <= 1.0:
        raise ValueError("invalid_trade_plan_score")

    entry_mid = (entry_min + entry_max) / 2.0
    fallback_distance = reference_price * 0.002
    stop_distance = max(atr * stop_atr_multiple, fallback_distance)

    if recommendation == "LONG":
        stop = max(1e-12, entry_min - stop_distance)
        risk_per_unit = entry_mid - stop
        target1 = entry_mid + risk_per_unit * target1_rr
        target2 = entry_mid + risk_per_unit * target2_rr
    else:
        stop = entry_max + stop_distance
        risk_per_unit = stop - entry_mid
        target1 = max(1e-12, entry_mid - risk_per_unit * target1_rr)
        target2 = max(1e-12, entry_mid - risk_per_unit * target2_rr)

    return {
        "plan_id": deterministic_plan_id(event_id, signal_id, rule_version),
        "state": "CANDIDATE_LOCKED",
        "direction": recommendation,
        "competition_id": competition_id,
        "symbol": symbol,
        "decision_timeframe": str(payload.get("timeframe") or ""),
        "source_event_id": event_id,
        "source_signal_id": signal_id,
        "source_event_time": str(payload.get("time") or ""),
        "valid_until": envelope.get("valid_until"),
        "entry_min": entry_min,
        "entry_max": entry_max,
        "entry_mid": entry_mid,
        "initial_stop": stop,
        "target1": target1,
        "target2": target2,
        "risk_per_unit": risk_per_unit,
        "target1_rr": float(target1_rr),
        "target2_rr": float(target2_rr),
        "source_composite_score": score,
        "levels_locked": True,
        "management_policy": "fixed_initial_plan_no_silent_repricing",
        "requires_human_approval": True,
        "execution": "manual_only",
        "rule_version": rule_version,
    }
