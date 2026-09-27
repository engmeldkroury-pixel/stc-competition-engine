"""Inert, causal counterfactual outcomes; never an execution/approval API.

Each threshold is an alternative single-TP experiment, not a partial exit.
Missing bar coverage is censored. Same-bar double touches are conservative
stop-first *and* explicitly ambiguous. Overlapping signals are not trades.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from typing import Any, Iterable

from .approval import timeframe_duration_minutes
from .trade_plan import calculate_plan_levels

VERSION = "stc-outcome-v1"
THRESHOLDS = (1.0, 1.5, 2.0, 2.5)


def utc(value: Any) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone_required")
    return value.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return utc(value).isoformat().replace("+00:00", "Z")


def number(value: Any, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("numeric_value_required")
    result = float(value)
    if not math.isfinite(result) or (positive and result <= 0):
        raise ValueError("invalid_finite_number")
    return result


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def build_outcome_seed(event_id: str, payload: dict, signal: dict, envelope: dict,
                       *, provenance: str = "FROZEN_AT_DECISION") -> dict | None:
    """Freeze rejected AND accepted directional setups outside live plan fields."""
    side = signal.get("pre_gate_recommendation", signal.get("recommendation"))
    if side not in {"LONG", "SHORT"}:
        return None
    competition, symbol = payload.get("competition_id"), payload.get("symbol")
    if not isinstance(event_id, str) or not event_id or not competition or not isinstance(symbol, str) or ":" not in symbol:
        raise ValueError("missing_exact_identity")
    for evidence in (signal, envelope):
        if evidence.get("competition_id") != competition or evidence.get("symbol") != symbol:
            raise ValueError("target_identity_mismatch")
    minutes = timeframe_duration_minutes(str(payload.get("timeframe", "")))
    if not minutes:
        raise ValueError("unsupported_timeframe")
    source_open = utc(payload["time"])
    source_close = source_open + timedelta(minutes=minutes)
    available = max(source_close, utc(envelope["issued_at"]))
    expires = utc(envelope["valid_until"])
    # A late decision is retained as EXPIRED, not given a fresh validity window.
    levels = calculate_plan_levels(side, entry_min=envelope["entry_min"],
                                   entry_max=envelope["entry_max"],
                                   reference_price=envelope["reference_price"],
                                   atr=payload["atr14"])
    diag = signal.get("gate_diagnostics") or {}
    boolean, quality = diag.get("boolean_gate_passed"), diag.get("setup_quality_passed")
    quadrant = (f"B{int(boolean)}_Q{int(quality)}" if type(boolean) is bool and type(quality) is bool else "UNKNOWN")
    failures = signal.get("quality_gate_failures")
    failures_known = isinstance(failures, list) and all(isinstance(x, str) for x in failures)
    seed = {
        "version": VERSION, "event_id": event_id, "competition_id": competition,
        "symbol": symbol, "timeframe_minutes": minutes, "side": side,
        "source_open": iso(source_open), "available_at": iso(available), "expires_at": iso(expires),
        "entry_min": number(envelope["entry_min"], positive=True),
        "entry_max": number(envelope["entry_max"], positive=True),
        "plan_mid": levels["entry_mid"], "stop": levels["initial_stop"],
        "plan_risk": levels["risk_per_unit"], "quadrant": quadrant,
        "failed_gates": sorted(set(failures)) if failures_known else [],
        "failed_gates_known": failures_known,
        "provenance": provenance, "research_only": True, "live_authorized": False,
        "execution": "none",
    }
    seed["seed_sha256"] = hashlib.sha256(canonical(seed).encode()).hexdigest()
    return seed


def validate_seed(seed: dict) -> None:
    body = {k: v for k, v in seed.items() if k != "seed_sha256"}
    if hashlib.sha256(canonical(body).encode()).hexdigest() != seed.get("seed_sha256"):
        raise ValueError("seed_integrity_mismatch")
    if seed.get("version") != VERSION or seed.get("research_only") is not True or seed.get("live_authorized") is not False or seed.get("execution") != "none":
        raise ValueError("research_boundary_violation")
    if seed.get("side") not in {"LONG", "SHORT"}:
        raise ValueError("invalid_side")
    minutes = seed.get("timeframe_minutes")
    if type(minutes) is not int or minutes <= 0:
        raise ValueError("invalid_timeframe")
    lo, hi = number(seed["entry_min"], positive=True), number(seed["entry_max"], positive=True)
    mid, stop, risk = (number(seed[k], positive=True) for k in ("plan_mid", "stop", "plan_risk"))
    sign = 1 if seed["side"] == "LONG" else -1
    if not lo <= mid <= hi or not math.isclose(sign * (mid - stop), risk, rel_tol=1e-10):
        raise ValueError("invalid_geometry")
    if sign * (lo - stop) <= 0 or sign * (hi - stop) <= 0:
        raise ValueError("stop_inside_entry_envelope")
    if utc(seed["available_at"]) < utc(seed["source_open"]) + timedelta(minutes=minutes):
        raise ValueError("noncausal_decision_time")
    utc(seed["expires_at"])


def _closed_bars(seed: dict, rows: Iterable[dict], as_of: datetime) -> list[dict]:
    """Do not silently replace the provider or tolerate conflicting duplicates."""
    found: dict[datetime, dict] = {}
    duration = timedelta(minutes=seed["timeframe_minutes"])
    for row in rows:
        if (row.get("competition_id"), row.get("symbol"), row.get("timeframe_minutes")) != (seed["competition_id"], seed["symbol"], seed["timeframe_minutes"]):
            continue
        opened = utc(row["time"])
        if opened + duration > as_of or opened < utc(seed["available_at"]):
            continue
        bar = {"time": opened, **{k: number(row[k], positive=True) for k in ("open", "high", "low", "close")}}
        if bar["high"] < max(bar["open"], bar["close"], bar["low"]) or bar["low"] > min(bar["open"], bar["close"], bar["high"]):
            raise ValueError("invalid_ohlc")
        if opened in found and found[opened] != bar:
            raise ValueError("conflicting_bar_duplicates")
        found[opened] = bar
    return [found[t] for t in sorted(found)]


def evaluate_outcome(seed: dict, rows: Iterable[dict], *, as_of: datetime,
                     horizon_bars: int = 32, cost_r: float = 0.02) -> dict:
    """All result R values retain the frozen plan denominator; fill R is separate.

    Entry: first fully observable scheduled bar OPEN within frozen bounds.
    Expiry: exclusive. No invented fill inside a bar or missing-data interval.
    Cost: explicit round-trip proxy in units of planned R, not measured fees.
    """
    validate_seed(seed)
    as_of = utc(as_of)
    if type(horizon_bars) is not int or horizon_bars < 1 or horizon_bars > 10000:
        raise ValueError("invalid_horizon")
    cost_r = number(cost_r)
    if cost_r < 0:
        raise ValueError("negative_cost")
    bars = _closed_bars(seed, rows, as_of)
    duration = timedelta(minutes=seed["timeframe_minutes"])
    source = utc(seed["source_open"])
    available, expires = utc(seed["available_at"]), utc(seed["expires_at"])
    # Anchor to the observed source series, not UTC midnight (session alignment).
    steps = math.ceil((available - source) / duration)
    expected = source + steps * duration
    result = {
        "version": VERSION, "event_id": seed["event_id"], "seed_sha256": seed["seed_sha256"],
        "competition_id": seed["competition_id"], "symbol": seed["symbol"],
        "side": seed["side"], "timeframe_minutes": seed["timeframe_minutes"],
        "quadrant": seed["quadrant"], "failed_gates": seed["failed_gates"],
        "failed_gates_known": seed["failed_gates_known"], "provenance": seed["provenance"],
        "as_of": iso(as_of), "horizon_bars": horizon_bars, "cost_r_proxy": cost_r,
        "research_only": True, "execution": "none", "live_authorized": False,
        "status": "CENSORED", "reason": "insufficient_closed_bars", "entry": None,
        "thresholds": {}, "bars_observed_after_entry": 0,
        "full_horizon_mfe_r": None, "full_horizon_mae_r": None,
        "pre_stop_mfe_lower_r": None, "pre_stop_mfe_upper_r": None,
    }
    if expected >= expires:
        result.update(status="NO_ENTRY", reason="expired_before_eligible_open")
        return result
    indexed = {b["time"]: b for b in bars}
    entry = None
    while expected < expires:
        if expected + duration > as_of:
            return result
        if expected not in indexed:
            result["reason"] = "missing_entry_bar"
            return result
        bar = indexed[expected]
        if seed["entry_min"] <= bar["open"] <= seed["entry_max"]:
            entry = bar["open"]
            break
        expected += duration
    if entry is None:
        result.update(status="NO_ENTRY", reason="no_open_inside_frozen_envelope")
        return result

    sign = 1 if seed["side"] == "LONG" else -1
    risk, stop = seed["plan_risk"], seed["stop"]
    fill_risk = sign * (entry - stop)
    targets = {str(r): seed["plan_mid"] + sign * risk * r for r in THRESHOLDS}
    if any(t <= 0 for t in targets.values()):
        raise ValueError("nonpositive_counterfactual_target")
    result["entry"] = {"time": iso(expected), "price": entry, "plan_risk_per_unit": risk, "fill_risk_per_unit": fill_risk}
    outcomes = {k: {"state": "CENSORED", "target_price": t, "net_plan_r": None, "net_fill_r": None,
                    "post_stop_target_touched": False} for k, t in targets.items()}
    result["thresholds"] = outcomes
    mfe = mae = pre_lower = pre_upper = 0.0
    stop_index = None
    for i in range(horizon_bars):
        if expected + duration > as_of:
            break
        if expected not in indexed:
            result["reason"] = "missing_path_bar"
            break
        bar = indexed[expected]
        favourable = bar["high"] if sign == 1 else bar["low"]
        adverse = bar["low"] if sign == 1 else bar["high"]
        mfe = max(mfe, sign * (favourable - entry) / risk)
        mae = max(mae, -sign * (adverse - entry) / risk)
        stop_gap = sign * (bar["open"] - stop) <= 0
        stop_touch = sign * (adverse - stop) <= 0
        if stop_index is None:
            # A gap stop executes at OPEN: later extremes cannot count pre-stop.
            pre_lower = max(pre_lower, sign * (bar["open"] - entry) / risk)
            pre_upper = max(pre_upper, pre_lower if stop_gap else sign * (favourable - entry) / risk)
            if not stop_touch:
                pre_lower = pre_upper
            if stop_touch:
                stop_index = i
        for k, target in targets.items():
            outcome = outcomes[k]
            target_gap = sign * (bar["open"] - target) >= 0
            target_touch = sign * (favourable - target) >= 0
            if stop_index is not None and i > stop_index and target_touch and outcome["state"] in {"STOP_FIRST", "AMBIGUOUS_STOP_FIRST"}:
                outcome["post_stop_target_touched"] = True
            if outcome["state"] != "CENSORED":
                continue
            # OPEN is ordered; intrabar high/low are not. Limit fill is conservative.
            state, price = None, None
            if stop_gap:
                state, price = "STOP_FIRST", bar["open"]
            elif target_gap:
                state, price = "TARGET_FIRST", target
            elif stop_touch:
                state, price = ("AMBIGUOUS_STOP_FIRST" if target_touch else "STOP_FIRST"), stop
            elif target_touch:
                state, price = "TARGET_FIRST", target
            if state:
                net = sign * (price - entry) - cost_r * risk
                outcome.update(state=state, exit_time=iso(expected), exit_price=price,
                               net_plan_r=net / risk, net_fill_r=net / fill_risk)
        result["bars_observed_after_entry"] += 1
        expected += duration
    if result["bars_observed_after_entry"] == horizon_bars:
        result.update(status="COMPLETE", reason="fixed_horizon_observed")
    result.update(full_horizon_mfe_r=mfe, full_horizon_mae_r=mae,
                  pre_stop_mfe_lower_r=pre_lower, pre_stop_mfe_upper_r=pre_upper,
                  full_horizon_complete=result["status"] == "COMPLETE",
                  stopped=stop_index is not None)
    return result


def summarize_outcomes(outcomes: list[dict]) -> dict:
    """Descriptive inclusive counts, NOT causal gate effects or a win probability."""
    def summarize(rows: list[dict]) -> dict:
        thresholds = {}
        for r in THRESHOLDS:
            k = str(r)
            counts = Counter(x.get("thresholds", {}).get(k, {}).get("state", "NO_ENTRY_OR_UNOBSERVED") for x in rows)
            settled = [x["thresholds"][k]["net_plan_r"] for x in rows if x.get("thresholds", {}).get(k, {}).get("net_plan_r") is not None]
            thresholds[k] = {"states": dict(sorted(counts.items())), "settled_count": len(settled),
                             "settled_mean_net_plan_r": sum(settled) / len(settled) if settled else None}
        return {"observations": len(rows), "status_counts": dict(sorted(Counter(x["status"] for x in rows).items())), "thresholds": thresholds}
    grouped: dict[str, dict[str, list]] = {key: defaultdict(list) for key in ("competition_id", "symbol", "timeframe_minutes", "quadrant", "failed_clause", "exact_failure_set", "provenance")}
    for row in outcomes:
        for key in ("competition_id", "symbol", "timeframe_minutes", "quadrant", "provenance"):
            grouped[key][str(row[key])].append(row)
        known = row["failed_gates_known"]
        grouped["exact_failure_set"][canonical(row["failed_gates"]) if known else "UNKNOWN"].append(row)
        for gate in row["failed_gates"] if known else ["UNKNOWN"]:
            grouped["failed_clause"][gate].append(row)
    return {"overall": summarize(outcomes), "groups": {key: {name: summarize(rows) for name, rows in sorted(groups.items())} for key, groups in grouped.items()},
            "limitations": ["Overlapping observations are not independent trades or a portfolio backtest.",
                            "Failed-clause groups overlap; do not sum their counts.",
                            "Settled-only means exclude censored paths and are not unbiased expectancy estimates.",
                            "Legacy reconstructed geometry is not the original frozen decision plan.",
                            "No causal ablation, calibrated win probability, or live promotion is implied."]}
