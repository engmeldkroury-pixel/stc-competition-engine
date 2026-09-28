"""Prospective R10 shadow ledger and causal outcome evaluation.

Research-only. This module intentionally has no broker, account, quantity,
approval, notification, position-management or live-strategy authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from typing import Any, Literal, Sequence

from app.mtf_shadow import FROZEN_R10_CANDIDATES, ShadowSignal
from app.r10_regime_session_shadow import (
    FROZEN_PROTOCOL as REGIME_PROTOCOL,
    protocol_sha256 as regime_protocol_sha256,
)

Direction = Literal["LONG", "SHORT"]
Status = Literal[
    "OPEN", "TARGET", "STOP", "STOP_GAP", "AMBIGUOUS_STOP_FIRST",
    "HORIZON_MARK", "CENSORED_MISSING_BAR", "WAIT",
]

REGISTRY_ID = "R10-FORWARD-SHADOW-REGISTRY-V1"
MTF_FORWARD_NOT_BEFORE_UTC = "2026-09-28T07:00:00Z"
REGIME_FORWARD_NOT_BEFORE_UTC = "2026-09-28T12:00:00Z"
BASE_INTERVAL_SECONDS = 15 * 60
DEFAULT_HORIZON_BARS = 32


@dataclass(frozen=True)
class PriceBar:
    ts: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class ForwardShadowRecord:
    registry_id: str
    protocol_id: str
    protocol_sha256: str
    candidate_sha256: str | None
    evidence_sha256: str
    symbol: str
    source_open_utc: str
    decision: Literal["LONG", "SHORT", "WAIT"]
    reason: str
    entry_bar_ts: int | None
    entry: float | None
    stop: float | None
    target: float | None
    planned_risk: float | None
    evaluation_horizon_bars: int
    research_only: Literal[True] = True
    live_authorized: Literal[False] = False
    execution: Literal["none"] = "none"


@dataclass(frozen=True)
class ForwardOutcome:
    record_sha256: str
    status: Status
    exit_bar_ts: int | None
    exit_price: float | None
    net_planned_r: float | None
    cost_r: float
    bars_observed: int
    mfe_r: float | None
    mae_r: float | None
    post_stop_target_touched: bool = False


def _finite(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite_number_required")
    out = float(value)
    if not math.isfinite(out):
        raise ValueError("finite_number_required")
    return out


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("utc_timestamp_required")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("utc_timestamp_required")
    return dt.astimezone(timezone.utc)


def _canonical_sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def mtf_candidate_payload(symbol: str) -> dict[str, Any]:
    candidate = FROZEN_R10_CANDIDATES.get(symbol)
    if candidate is None:
        raise ValueError("unknown_mtf_candidate")
    body = asdict(candidate)
    if body.get("authority") != "SHADOW_ONLY":
        raise ValueError("research_boundary_violation")
    return body


def mtf_candidate_sha256(symbol: str) -> str:
    return _canonical_sha(mtf_candidate_payload(symbol))


def mtf_protocol_sha256() -> str:
    return _canonical_sha({
        "registry_id": REGISTRY_ID,
        "forward_not_before_utc": MTF_FORWARD_NOT_BEFORE_UTC,
        "horizon_bars": DEFAULT_HORIZON_BARS,
        "candidates": {
            symbol: mtf_candidate_payload(symbol)
            for symbol in sorted(FROZEN_R10_CANDIDATES)
        },
        "causal_htf_closed_only": True,
        "base_timeframe_minutes": 15,
    })


def evidence_sha256(payload: dict[str, Any]) -> str:
    """Digest the exact as-observed evidence envelope frozen at decision time."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("nonempty_evidence_payload_required")
    return _canonical_sha(payload)


def record_sha256(record: ForwardShadowRecord) -> str:
    return _canonical_sha(asdict(record))


def _utc_from_epoch(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_record(record: ForwardShadowRecord) -> None:
    if record.registry_id != REGISTRY_ID:
        raise ValueError("registry_id_mismatch")
    if record.research_only is not True or record.live_authorized is not False:
        raise ValueError("research_boundary_violation")
    if record.execution != "none":
        raise ValueError("execution_boundary_violation")
    if not isinstance(record.evidence_sha256, str) or len(record.evidence_sha256) != 64:
        raise ValueError("evidence_sha256_required")
    try:
        int(record.evidence_sha256, 16)
    except ValueError as exc:
        raise ValueError("evidence_sha256_required") from exc
    if record.decision == "WAIT":
        if any(x is not None for x in (record.entry, record.stop, record.target, record.planned_risk)):
            raise ValueError("wait_must_not_have_trade_geometry")
        return
    if record.decision not in ("LONG", "SHORT"):
        raise ValueError("invalid_decision")
    if record.entry_bar_ts is None:
        raise ValueError("entry_bar_required")
    entry, stop, target, risk = map(
        _finite, (record.entry, record.stop, record.target, record.planned_risk)
    )
    if risk <= 0:
        raise ValueError("positive_risk_required")
    if record.decision == "LONG" and not (stop < entry < target):
        raise ValueError("invalid_long_geometry")
    if record.decision == "SHORT" and not (target < entry < stop):
        raise ValueError("invalid_short_geometry")


def mtf_record(signal: ShadowSignal, *, evidence_payload: dict[str, Any]) -> ForwardShadowRecord:
    if signal.symbol not in FROZEN_R10_CANDIDATES:
        raise ValueError("unknown_mtf_candidate")
    source_utc = _utc_from_epoch(signal.signal_bar_ts)
    if _parse_utc(source_utc) < _parse_utc(MTF_FORWARD_NOT_BEFORE_UTC):
        raise ValueError("pre_forward_boundary")
    direction = signal.direction
    risk = (signal.entry - signal.stop) if direction == "LONG" else (signal.stop - signal.entry)
    record = ForwardShadowRecord(
        registry_id=REGISTRY_ID,
        protocol_id="mtf_eth_doge_v1",
        protocol_sha256=mtf_protocol_sha256(),
        candidate_sha256=mtf_candidate_sha256(signal.symbol),
        evidence_sha256=evidence_sha256(evidence_payload),
        symbol=signal.symbol,
        source_open_utc=source_utc,
        decision=direction,
        reason="causal_mtf_pullback",
        entry_bar_ts=signal.entry_bar_ts,
        entry=signal.entry,
        stop=signal.stop,
        target=signal.target,
        planned_risk=risk,
        evaluation_horizon_bars=DEFAULT_HORIZON_BARS,
    )
    _validate_record(record)
    return record


def regime_record(
    *,
    symbol: str,
    snapshot: dict[str, Any],
    decision_result: dict[str, Any],
    next_bar: PriceBar | None,
) -> ForwardShadowRecord:
    source_utc = decision_result.get("source_open_utc")
    if not isinstance(source_utc, str):
        raise ValueError("source_open_utc_required")
    if _parse_utc(source_utc) < _parse_utc(REGIME_FORWARD_NOT_BEFORE_UTC):
        raise ValueError("pre_forward_boundary")
    if decision_result.get("protocol_sha256") != regime_protocol_sha256(REGIME_PROTOCOL):
        raise ValueError("regime_protocol_digest_mismatch")
    if decision_result.get("research_only") is not True or decision_result.get("live_authorized") is not False:
        raise ValueError("research_boundary_violation")
    decision = decision_result.get("decision")
    if decision == "WAIT":
        record = ForwardShadowRecord(
            registry_id=REGISTRY_ID,
            protocol_id="regime_session_v1",
            protocol_sha256=regime_protocol_sha256(REGIME_PROTOCOL),
            candidate_sha256=None,
            evidence_sha256=evidence_sha256({
                "snapshot": snapshot,
                "decision_result": decision_result,
                "next_bar": None,
            }),
            symbol=symbol,
            source_open_utc=source_utc,
            decision="WAIT",
            reason=str(decision_result.get("reason") or "wait"),
            entry_bar_ts=None,
            entry=None,
            stop=None,
            target=None,
            planned_risk=None,
            evaluation_horizon_bars=REGIME_PROTOCOL.horizon_bars,
        )
        _validate_record(record)
        return record
    if decision not in ("LONG", "SHORT"):
        raise ValueError("invalid_decision")
    if next_bar is None:
        raise ValueError("next_bar_required_for_directional_decision")
    atr = _finite(snapshot.get("atr14"))
    if atr <= 0:
        raise ValueError("positive_atr_required")
    source_dt = _parse_utc(source_utc)
    expected_entry_ts = int(source_dt.timestamp()) + BASE_INTERVAL_SECONDS
    if next_bar.ts != expected_entry_ts:
        raise ValueError("next_bar_time_mismatch")
    direction = 1 if decision == "LONG" else -1
    entry = _finite(next_bar.open)
    stop = entry - direction * REGIME_PROTOCOL.atr_stop_multiple * atr
    risk = abs(entry - stop)
    target = entry + direction * REGIME_PROTOCOL.target_r * risk
    record = ForwardShadowRecord(
        registry_id=REGISTRY_ID,
        protocol_id="regime_session_v1",
        protocol_sha256=regime_protocol_sha256(REGIME_PROTOCOL),
        candidate_sha256=None,
        evidence_sha256=evidence_sha256({
            "snapshot": snapshot,
            "decision_result": decision_result,
            "next_bar": asdict(next_bar),
        }),
        symbol=symbol,
        source_open_utc=source_utc,
        decision=decision,
        reason=str(decision_result.get("reason") or "frozen_regime_setup"),
        entry_bar_ts=next_bar.ts,
        entry=entry,
        stop=stop,
        target=target,
        planned_risk=risk,
        evaluation_horizon_bars=REGIME_PROTOCOL.horizon_bars,
    )
    _validate_record(record)
    return record


def evaluate_outcome(
    record: ForwardShadowRecord,
    bars: Sequence[PriceBar],
    *,
    cost_bps: float = 2.0,
) -> ForwardOutcome:
    _validate_record(record)
    if record.decision == "WAIT":
        return ForwardOutcome(
            record_sha256=record_sha256(record),
            status="WAIT",
            exit_bar_ts=None,
            exit_price=None,
            net_planned_r=None,
            cost_r=0.0,
            bars_observed=0,
            mfe_r=None,
            mae_r=None,
        )
    cost_bps = _finite(cost_bps)
    if cost_bps < 0:
        raise ValueError("nonnegative_cost_required")
    entry = float(record.entry)
    stop = float(record.stop)
    target = float(record.target)
    risk = float(record.planned_risk)
    direction = 1 if record.decision == "LONG" else -1
    cost_r = (cost_bps / 10_000.0) * entry / risk

    if not bars:
        return ForwardOutcome(
            record_sha256=record_sha256(record),
            status="CENSORED_MISSING_BAR",
            exit_bar_ts=None,
            exit_price=None,
            net_planned_r=None,
            cost_r=cost_r,
            bars_observed=0,
            mfe_r=None,
            mae_r=None,
        )

    expected_ts = int(record.entry_bar_ts)
    mfe = 0.0
    mae = 0.0
    observed = 0
    stopped_at: int | None = None
    post_stop_target = False

    for bar in bars[: record.evaluation_horizon_bars]:
        if bar.ts != expected_ts:
            return ForwardOutcome(
                record_sha256=record_sha256(record),
                status="CENSORED_MISSING_BAR",
                exit_bar_ts=None,
                exit_price=None,
                net_planned_r=None,
                cost_r=cost_r,
                bars_observed=observed,
                mfe_r=mfe,
                mae_r=mae,
                post_stop_target_touched=post_stop_target,
            )
        expected_ts += BASE_INTERVAL_SECONDS
        observed += 1
        fav = bar.high if direction > 0 else bar.low
        adv = bar.low if direction > 0 else bar.high
        mfe = max(mfe, direction * (fav - entry) / risk)
        mae = max(mae, -direction * (adv - entry) / risk)

        if direction * (bar.open - stop) <= 0:
            value = direction * (bar.open - entry) / risk - cost_r
            return ForwardOutcome(
                record_sha256=record_sha256(record),
                status="STOP_GAP",
                exit_bar_ts=bar.ts,
                exit_price=bar.open,
                net_planned_r=value,
                cost_r=cost_r,
                bars_observed=observed,
                mfe_r=mfe,
                mae_r=mae,
            )
        if direction * (bar.open - target) >= 0:
            rr = direction * (target - entry) / risk
            return ForwardOutcome(
                record_sha256=record_sha256(record),
                status="TARGET",
                exit_bar_ts=bar.ts,
                exit_price=target,
                net_planned_r=rr - cost_r,
                cost_r=cost_r,
                bars_observed=observed,
                mfe_r=mfe,
                mae_r=mae,
            )

        stop_hit = direction * (adv - stop) <= 0
        target_hit = direction * (fav - target) >= 0
        if stop_hit:
            stopped_at = bar.ts
            post_stop_target = bool(target_hit)
            return ForwardOutcome(
                record_sha256=record_sha256(record),
                status="AMBIGUOUS_STOP_FIRST" if target_hit else "STOP",
                exit_bar_ts=bar.ts,
                exit_price=stop,
                net_planned_r=-1.0 - cost_r,
                cost_r=cost_r,
                bars_observed=observed,
                mfe_r=mfe,
                mae_r=mae,
                post_stop_target_touched=post_stop_target,
            )
        if target_hit:
            rr = direction * (target - entry) / risk
            return ForwardOutcome(
                record_sha256=record_sha256(record),
                status="TARGET",
                exit_bar_ts=bar.ts,
                exit_price=target,
                net_planned_r=rr - cost_r,
                cost_r=cost_r,
                bars_observed=observed,
                mfe_r=mfe,
                mae_r=mae,
            )

    if observed < record.evaluation_horizon_bars:
        return ForwardOutcome(
            record_sha256=record_sha256(record),
            status="CENSORED_MISSING_BAR",
            exit_bar_ts=None,
            exit_price=None,
            net_planned_r=None,
            cost_r=cost_r,
            bars_observed=observed,
            mfe_r=mfe,
            mae_r=mae,
            post_stop_target_touched=bool(stopped_at and post_stop_target),
        )

    last = bars[record.evaluation_horizon_bars - 1]
    mark_r = direction * (last.close - entry) / risk - cost_r
    return ForwardOutcome(
        record_sha256=record_sha256(record),
        status="HORIZON_MARK",
        exit_bar_ts=last.ts,
        exit_price=last.close,
        net_planned_r=mark_r,
        cost_r=cost_r,
        bars_observed=observed,
        mfe_r=mfe,
        mae_r=mae,
    )
