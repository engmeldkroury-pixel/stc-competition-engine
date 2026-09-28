"""Frozen AMP crypto futures shadow hypothesis; no live authority."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json, math
from typing import Any

VERSION = "stc-r10-amp-crypto-shadow-v1"
ALLOWED_SYMBOLS = ("CME:MBT1!", "CME:MET1!")


@dataclass(frozen=True)
class AMPCryptoProtocol:
    timeframe_minutes: int = 15
    adx_min: float = 30.0
    atr_stop_multiple: float = 2.0
    target_r: float = 2.0
    horizon_bars: int = 32
    not_before_utc: str = "2026-09-28T04:15:00Z"
    research_only: bool = True
    live_authorized: bool = False


FROZEN_AMP_CRYPTO = AMPCryptoProtocol()


def _num(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite_number_required")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("finite_number_required")
    return value


def _utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("utc_timestamp_required")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("utc_timestamp_required")
    return dt.astimezone(timezone.utc)


def protocol_sha256(protocol: AMPCryptoProtocol = FROZEN_AMP_CRYPTO) -> str:
    body = {"version": VERSION, "symbols": ALLOWED_SYMBOLS, **asdict(protocol)}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def shadow_decision(symbol: str, snapshot: dict[str, Any], protocol: AMPCryptoProtocol = FROZEN_AMP_CRYPTO) -> dict[str, Any]:
    if symbol not in ALLOWED_SYMBOLS:
        raise ValueError("symbol_not_in_frozen_universe")
    required = ("source_open_utc", "open", "close", "ema20", "ema50", "ema200", "atr14", "adx14", "rsi14", "range_atr")
    missing = [k for k in required if k not in snapshot]
    if missing:
        raise ValueError("missing_features:" + ",".join(missing))
    ts = snapshot["source_open_utc"]
    values = {k: _num(snapshot[k]) for k in required if k != "source_open_utc"}
    atr = values["atr14"]
    if atr <= 0:
        raise ValueError("positive_atr_required")
    eligible = _utc(ts) >= _utc(protocol.not_before_utc)
    ext = (values["close"] - values["ema20"]) / atr
    long_trend = values["ema20"] > values["ema50"] > values["ema200"]
    short_trend = values["ema20"] < values["ema50"] < values["ema200"]
    decision, reason = "WAIT", "no_frozen_setup"
    if values["adx14"] >= protocol.adx_min:
        if long_trend and -0.30 <= ext <= 0.60 and 48 <= values["rsi14"] <= 64 and values["close"] > values["open"] and values["range_atr"] <= 2.0:
            decision, reason = "LONG", "amp_crypto_trend_pullback"
        elif short_trend and -0.60 <= ext <= 0.30 and 36 <= values["rsi14"] <= 52 and values["close"] < values["open"] and values["range_atr"] <= 2.0:
            decision, reason = "SHORT", "amp_crypto_trend_pullback"
    return {
        "version": VERSION,
        "protocol_sha256": protocol_sha256(protocol),
        "symbol": symbol,
        "decision": decision,
        "reason": reason,
        "extension_atr": ext,
        "source_open_utc": ts,
        "forward_eligible": eligible,
        "initial_stop_atr_multiple": protocol.atr_stop_multiple,
        "single_target_r": protocol.target_r,
        "horizon_bars": protocol.horizon_bars,
        "research_only": True,
        "live_authorized": False,
        "execution": "none",
    }
