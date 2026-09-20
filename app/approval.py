from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone


def timeframe_validity_minutes(timeframe: str) -> int:
    tf = str(timeframe).strip().lower()
    table = {"1": 5, "1m": 5, "5": 15, "5m": 15, "15": 30, "15m": 30,
             "30": 45, "30m": 45, "60": 90, "1h": 90, "240": 360, "4h": 360,
             "1d": 720}
    return table.get(tf, 15)


def market_state_hash(payload: dict) -> str:
    keys = ["competition_id", "symbol", "timeframe", "close", "ema20", "ema50", "rsi14", "atr14", "macd", "macd_signal"]
    state = {k: payload.get(k) for k in keys}
    raw = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_approval_envelope(payload: dict, composite_score: float, rule_version: str = "stc-rule-v1") -> dict:
    now = datetime.now(timezone.utc)
    minutes = timeframe_validity_minutes(str(payload.get("timeframe", "5")))
    ref = float(payload.get("close") or 0.0)
    atr = abs(float(payload.get("atr14") or 0.0))
    # Dynamic price tolerance: half ATR, bounded to 0.10%..1.00% of reference price.
    pct = 0.002
    if ref > 0 and atr > 0:
        pct = min(0.01, max(0.001, (0.5 * atr) / ref))
    return {
        "issued_at": now.isoformat(),
        "valid_until": (now + timedelta(minutes=minutes)).isoformat(),
        "validity_minutes": minutes,
        "competition_id": payload.get("competition_id"),
        "symbol": payload.get("symbol"),
        "reference_price": ref,
        "entry_min": ref * (1 - pct) if ref else 0.0,
        "entry_max": ref * (1 + pct) if ref else 0.0,
        "price_tolerance_fraction": pct,
        "reference_signal_score": float(composite_score),
        "max_signal_score_drop": 0.15,
        "market_state_hash": market_state_hash(payload),
        "rule_version": rule_version,
        "max_volatility_ratio": 1.5,
        "requires_quote_freshness_verified": True,
        "requires_market_open_verified": True,
    }


def revalidate_envelope(envelope: dict, current: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    try:
        valid_until = datetime.fromisoformat(str(envelope["valid_until"]).replace("Z", "+00:00"))
    except Exception:
        valid_until = now - timedelta(seconds=1)
        reasons.append("invalid_valid_until")
    if now > valid_until:
        reasons.append("expired")

    price = float(current.get("current_price", 0.0))
    if price < float(envelope.get("entry_min", 0.0)) or price > float(envelope.get("entry_max", 0.0)):
        reasons.append("price_outside_envelope")

    score = float(current.get("current_signal_score", 0.0))
    floor = float(envelope.get("reference_signal_score", 0.0)) - float(envelope.get("max_signal_score_drop", 0.15))
    if score < floor:
        reasons.append("signal_degraded")

    if current.get("current_market_state_hash") != envelope.get("market_state_hash"):
        reasons.append("market_state_changed")
    if current.get("current_rule_version") != envelope.get("rule_version"):
        reasons.append("rule_version_changed")
    if bool(current.get("news_block", False)):
        reasons.append("news_block")
    if float(current.get("volatility_ratio", 1.0)) > float(envelope.get("max_volatility_ratio", 1.5)):
        reasons.append("volatility_spike")
    if bool(envelope.get("requires_quote_freshness_verified", True)) and not bool(current.get("quote_freshness_verified", False)):
        reasons.append("quote_freshness_unverified")
    if bool(envelope.get("requires_market_open_verified", True)) and not bool(current.get("market_open_verified", False)):
        reasons.append("market_closed_or_unverified")
    if bool(current.get("kill_switch", False)):
        reasons.append("kill_switch_active")
    if bool(current.get("safe_mode", False)):
        reasons.append("safe_mode_active")

    return {"valid": not reasons, "reasons": reasons, "status": "approved_fresh" if not reasons else "stale_or_blocked"}
