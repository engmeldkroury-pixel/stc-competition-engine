"""R10 frozen regime/session candidate for forward research only.

This module has no broker, approval, quantity, account, notification or live
strategy authority. It freezes the hypothesis discovered on historical data
so future observations can be scored without retuning the rules.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from typing import Any

VERSION = "stc-r10-regime-session-shadow-v1"


@dataclass(frozen=True)
class R10Protocol:
    session_start_utc: int = 12
    session_end_utc: int = 17
    adx_trend_min: float = 30.0
    adx_range_max: float = 20.0
    atr_stop_multiple: float = 1.5
    target_r: float = 2.0
    horizon_bars: int = 32
    timeframe_minutes: int = 15
    not_before_utc: str = "2026-09-28T12:00:00Z"
    research_only: bool = True
    live_authorized: bool = False


FROZEN_PROTOCOL = R10Protocol()


def _finite(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite_number_required")
    out = float(value)
    if not math.isfinite(out):
        raise ValueError("finite_number_required")
    return out


def protocol_payload(protocol: R10Protocol = FROZEN_PROTOCOL) -> dict[str, Any]:
    body = {"version": VERSION, **asdict(protocol)}
    if body["research_only"] is not True or body["live_authorized"] is not False:
        raise ValueError("research_boundary_violation")
    return body


def protocol_sha256(protocol: R10Protocol = FROZEN_PROTOCOL) -> str:
    raw = json.dumps(protocol_payload(protocol), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("utc_timestamp_required")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("utc_timestamp_required")
    return dt.astimezone(timezone.utc)


def in_session(source_open_utc: str, protocol: R10Protocol = FROZEN_PROTOCOL) -> bool:
    opened = parse_utc(source_open_utc)
    return protocol.session_start_utc <= opened.hour < protocol.session_end_utc


def forward_eligible(source_open_utc: str, protocol: R10Protocol = FROZEN_PROTOCOL) -> bool:
    return parse_utc(source_open_utc) >= parse_utc(protocol.not_before_utc)


def classify_regime(adx: float, protocol: R10Protocol = FROZEN_PROTOCOL) -> str:
    adx = _finite(adx)
    if adx >= protocol.adx_trend_min:
        return "TREND"
    if adx <= protocol.adx_range_max:
        return "RANGE"
    return "NEUTRAL"


def shadow_decision(snapshot: dict[str, Any], protocol: R10Protocol = FROZEN_PROTOCOL) -> dict[str, Any]:
    """Classify one already-closed source bar using frozen, causal features.

    The caller must compute all indicator fields using bars available no later
    than this source bar. This function deliberately has no position sizing or
    execution output.
    """
    required = (
        "source_open_utc", "open", "close", "ema20", "ema50", "ema200",
        "atr14", "adx14", "rsi14", "zscore20", "range_atr",
    )
    missing = [key for key in required if key not in snapshot]
    if missing:
        raise ValueError("missing_features:" + ",".join(missing))

    opened = snapshot["source_open_utc"]
    values = {key: _finite(snapshot[key]) for key in required if key != "source_open_utc"}
    atr = values["atr14"]
    if atr <= 0:
        raise ValueError("positive_atr_required")

    decision = "WAIT"
    reason = "outside_session"
    regime = classify_regime(values["adx14"], protocol)
    extension_atr = (values["close"] - values["ema20"]) / atr
    long_trend = values["ema20"] > values["ema50"] > values["ema200"]
    short_trend = values["ema20"] < values["ema50"] < values["ema200"]

    if in_session(opened, protocol):
        reason = "no_frozen_setup"
        if regime == "TREND":
            long_ok = (
                long_trend and -0.25 <= extension_atr <= 0.50
                and 48.0 <= values["rsi14"] <= 62.0
                and values["close"] > values["open"]
                and values["range_atr"] <= 1.80
            )
            short_ok = (
                short_trend and -0.50 <= extension_atr <= 0.25
                and 38.0 <= values["rsi14"] <= 52.0
                and values["close"] < values["open"]
                and values["range_atr"] <= 1.80
            )
            if long_ok:
                decision, reason = "LONG", "trend_pullback"
            elif short_ok:
                decision, reason = "SHORT", "trend_pullback"
        elif regime == "RANGE":
            if values["zscore20"] >= 2.0 and values["rsi14"] >= 68.0 and values["range_atr"] <= 2.20:
                decision, reason = "SHORT", "range_extreme_fade"
            elif values["zscore20"] <= -2.0 and values["rsi14"] <= 32.0 and values["range_atr"] <= 2.20:
                decision, reason = "LONG", "range_extreme_fade"

    return {
        "version": VERSION,
        "protocol_sha256": protocol_sha256(protocol),
        "decision": decision,
        "reason": reason,
        "regime": regime,
        "extension_atr": extension_atr,
        "source_open_utc": opened,
        "forward_eligible": forward_eligible(opened, protocol),
        "timeframe_minutes": protocol.timeframe_minutes,
        "initial_stop_atr_multiple": protocol.atr_stop_multiple,
        "single_target_r": protocol.target_r,
        "horizon_bars": protocol.horizon_bars,
        "research_only": True,
        "live_authorized": False,
        "execution": "none",
    }
