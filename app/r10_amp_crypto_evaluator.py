"""Causal forward evaluator for the frozen AMP crypto shadow; research only."""
from __future__ import annotations

from typing import Any, Iterable

from .r10_amp_crypto_shadow import (
    ALLOWED_SYMBOLS,
    FROZEN_AMP_CRYPTO,
    protocol_sha256,
    shadow_decision,
)
from .r10_forward_evaluator import _iso, _num, feature_snapshots, normalize_bars


def snapshots(rows: Iterable[dict], *, symbol: str) -> list[dict]:
    if symbol not in ALLOWED_SYMBOLS:
        raise ValueError("symbol_not_in_frozen_universe")
    return [
        {**item, "decision": shadow_decision(symbol, item["snapshot"])}
        for item in feature_snapshots(rows, symbol=symbol)
    ]


def forward_signals(rows: Iterable[dict], *, symbol: str) -> list[dict]:
    return [
        item for item in snapshots(rows, symbol=symbol)
        if item["decision"]["forward_eligible"]
        and item["decision"]["decision"] in {"LONG", "SHORT"}
    ]


def _evidence_meta(*, symbol: str, decision: dict, cost_bps: float) -> dict[str, Any]:
    cost = _num(cost_bps)
    source = decision["source_open_utc"]
    return {
        "protocol_sha256": protocol_sha256(),
        "symbol": symbol,
        "source_open_utc": source,
        "day": source[:10],
        "cost_bps": cost,
        "decision": decision["decision"],
        "research_only": True,
        "live_authorized": False,
    }


def evaluate_signal(
    rows: Iterable[dict], *, symbol: str, bar_index: int, cost_bps: float = 1.0
) -> dict[str, Any]:
    bars = normalize_bars(rows, symbol=symbol)
    by_index = {item["bar_index"]: item for item in snapshots(bars, symbol=symbol)}
    if bar_index not in by_index:
        raise ValueError("source_features_unavailable")
    item = by_index[bar_index]
    decision = item["decision"]
    if decision["decision"] not in {"LONG", "SHORT"} or not decision["forward_eligible"]:
        raise ValueError("not_forward_signal")
    meta = _evidence_meta(symbol=symbol, decision=decision, cost_bps=cost_bps)
    if bar_index + 1 >= len(bars):
        return {**meta, "status": "CENSORED", "reason": "missing_entry_bar"}

    side = 1 if decision["decision"] == "LONG" else -1
    entry = bars[bar_index + 1]["open"]
    atr = item["snapshot"]["atr14"]
    stop = entry - side * FROZEN_AMP_CRYPTO.atr_stop_multiple * atr
    risk = side * (entry - stop)
    target = entry + side * FROZEN_AMP_CRYPTO.target_r * risk
    cost_r = meta["cost_bps"] / 10000.0 * entry / risk
    end = bar_index + FROZEN_AMP_CRYPTO.horizon_bars
    if end >= len(bars):
        return {**meta, "status": "CENSORED", "reason": "insufficient_horizon"}

    for i in range(bar_index + 1, end + 1):
        bar = bars[i]
        adverse = bar["low"] if side == 1 else bar["high"]
        favorable = bar["high"] if side == 1 else bar["low"]
        if side * (bar["open"] - stop) <= 0:
            return {**meta, "status": "SETTLED", "reason": "STOP_GAP", "net_r": side * (bar["open"] - entry) / risk - cost_r, "exit_time": _iso(bar["time"])}
        if side * (bar["open"] - target) >= 0:
            return {**meta, "status": "SETTLED", "reason": "TARGET_GAP", "net_r": FROZEN_AMP_CRYPTO.target_r - cost_r, "exit_time": _iso(bar["time"])}
        stop_hit = side * (adverse - stop) <= 0
        target_hit = side * (favorable - target) >= 0
        if stop_hit:
            return {**meta, "status": "SETTLED", "reason": "AMBIGUOUS_STOP_FIRST" if target_hit else "STOP", "net_r": -1.0 - cost_r, "exit_time": _iso(bar["time"])}
        if target_hit:
            return {**meta, "status": "SETTLED", "reason": "TARGET", "net_r": FROZEN_AMP_CRYPTO.target_r - cost_r, "exit_time": _iso(bar["time"])}

    last = bars[end]
    return {**meta, "status": "MARK", "reason": "HORIZON_MARK", "net_r": side * (last["close"] - entry) / risk - cost_r, "exit_time": _iso(last["time"])}
