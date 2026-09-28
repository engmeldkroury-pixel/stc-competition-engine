"""Causal evaluator for the frozen R10 shadow protocol; research only."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
from typing import Any, Iterable

from .r10_regime_session_shadow import FROZEN_PROTOCOL, protocol_sha256, shadow_decision


def _num(value: Any, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("numeric_value_required")
    value = float(value)
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError("invalid_numeric_value")
    return value


def _utc(value: Any) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone_required")
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _utc(value).isoformat().replace("+00:00", "Z")


def normalize_bars(rows: Iterable[dict], *, symbol: str, timeframe_minutes: int = 15) -> list[dict]:
    """Exact-symbol 15m closed-bar series. Conflicts/gaps are never hidden."""
    if timeframe_minutes != FROZEN_PROTOCOL.timeframe_minutes:
        raise ValueError("protocol_timeframe_mismatch")
    found: dict[datetime, dict] = {}
    for row in rows:
        if row.get("symbol") != symbol:
            continue
        if int(row.get("timeframe_minutes", timeframe_minutes)) != timeframe_minutes:
            continue
        t = _utc(row["time"])
        bar = {"time": t, **{k: _num(row[k], positive=True) for k in ("open", "high", "low", "close")}}
        if bar["high"] < max(bar["open"], bar["low"], bar["close"]) or bar["low"] > min(bar["open"], bar["high"], bar["close"]):
            raise ValueError("invalid_ohlc")
        if t in found and found[t] != bar:
            raise ValueError("conflicting_duplicate")
        found[t] = bar
    bars = [found[t] for t in sorted(found)]
    step = timedelta(minutes=timeframe_minutes)
    for prev, cur in zip(bars, bars[1:]):
        if cur["time"] - prev["time"] != step:
            raise ValueError("noncontiguous_bar_series")
    return bars


def _ema(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    alpha = 2.0 / (period + 1.0)
    out[period - 1] = sum(values[:period]) / period
    for i in range(period, len(values)):
        out[i] = values[i] * alpha + float(out[i - 1]) * (1.0 - alpha)
    return out


def _sma(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    total = 0.0
    for i, value in enumerate(values):
        total += value
        if i >= period:
            total -= values[i - period]
        if i >= period - 1:
            out[i] = total / period
    return out


def _std(values: list[float], period: int) -> list[float | None]:
    means = _sma(values, period)
    out: list[float | None] = [None] * len(values)
    for i in range(period - 1, len(values)):
        mean = float(means[i])
        out[i] = math.sqrt(sum((values[j] - mean) ** 2 for j in range(i - period + 1, i + 1)) / period)
    return out


def _atr(bars: list[dict], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(bars)
    tr: list[float] = []
    for i, bar in enumerate(bars):
        if i == 0:
            tr.append(bar["high"] - bar["low"])
        else:
            tr.append(max(bar["high"] - bar["low"], abs(bar["high"] - bars[i - 1]["close"]), abs(bar["low"] - bars[i - 1]["close"])))
    if len(bars) < period:
        return out
    out[period - 1] = sum(tr[:period]) / period
    for i in range(period, len(bars)):
        out[i] = (float(out[i - 1]) * (period - 1) + tr[i]) / period
    return out


def _rsi(closes: list[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(closes)
    if len(closes) <= period:
        return out
    gain = loss = 0.0
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gain += max(d, 0.0)
        loss += max(-d, 0.0)
    gain /= period
    loss /= period
    out[period] = 100.0 if loss == 0 else 100.0 - 100.0 / (1.0 + gain / loss)
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        gain = (gain * (period - 1) + max(d, 0.0)) / period
        loss = (loss * (period - 1) + max(-d, 0.0)) / period
        out[i] = 100.0 if loss == 0 else 100.0 - 100.0 / (1.0 + gain / loss)
    return out


def _adx(bars: list[dict], period: int = 14) -> list[float | None]:
    n = len(bars)
    out: list[float | None] = [None] * n
    if n < period * 2:
        return out
    tr = [0.0] * n
    plus = [0.0] * n
    minus = [0.0] * n
    for i in range(1, n):
        tr[i] = max(bars[i]["high"] - bars[i]["low"], abs(bars[i]["high"] - bars[i - 1]["close"]), abs(bars[i]["low"] - bars[i - 1]["close"]))
        up = bars[i]["high"] - bars[i - 1]["high"]
        down = bars[i - 1]["low"] - bars[i]["low"]
        plus[i] = up if up > down and up > 0 else 0.0
        minus[i] = down if down > up and down > 0 else 0.0
    trn = sum(tr[1:period + 1])
    pn = sum(plus[1:period + 1])
    mn = sum(minus[1:period + 1])
    dx: list[float | None] = [None] * n
    for i in range(period, n):
        if i > period:
            trn = trn - trn / period + tr[i]
            pn = pn - pn / period + plus[i]
            mn = mn - mn / period + minus[i]
        pdi = 100.0 * pn / trn if trn else 0.0
        mdi = 100.0 * mn / trn if trn else 0.0
        dx[i] = 100.0 * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi else 0.0
        if i == period * 2 - 1:
            out[i] = sum(float(dx[j]) for j in range(period, i + 1)) / period
        elif i >= period * 2 and out[i - 1] is not None:
            out[i] = (float(out[i - 1]) * (period - 1) + float(dx[i])) / period
    return out


def feature_snapshots(rows: Iterable[dict], *, symbol: str) -> list[dict]:
    """Causal indicator snapshots shared by frozen R10 research protocols."""
    bars = normalize_bars(rows, symbol=symbol)
    closes = [b["close"] for b in bars]
    e20, e50, e200 = _ema(closes, 20), _ema(closes, 50), _ema(closes, 200)
    atr, rsi, adx = _atr(bars), _rsi(closes), _adx(bars)
    mean, std = _sma(closes, 20), _std(closes, 20)
    out = []
    for i, bar in enumerate(bars):
        vals = (e20[i], e50[i], e200[i], atr[i], rsi[i], adx[i], mean[i], std[i])
        if any(v is None for v in vals) or float(std[i]) <= 0:
            continue
        snap = {
            "source_open_utc": _iso(bar["time"]),
            "open": bar["open"],
            "close": bar["close"],
            "ema20": e20[i],
            "ema50": e50[i],
            "ema200": e200[i],
            "atr14": atr[i],
            "rsi14": rsi[i],
            "adx14": adx[i],
            "zscore20": (bar["close"] - float(mean[i])) / float(std[i]),
            "range_atr": (bar["high"] - bar["low"]) / float(atr[i]),
        }
        out.append({"bar_index": i, "snapshot": snap})
    return out


def snapshots(rows: Iterable[dict], *, symbol: str) -> list[dict]:
    return [
        {**item, "decision": shadow_decision(item["snapshot"])}
        for item in feature_snapshots(rows, symbol=symbol)
    ]


def forward_signals(rows: Iterable[dict], *, symbol: str) -> list[dict]:
    return [
        item for item in snapshots(rows, symbol=symbol)
        if item["decision"]["forward_eligible"]
        and item["decision"]["decision"] in {"LONG", "SHORT"}
    ]


def evaluate_signal(rows: Iterable[dict], *, symbol: str, bar_index: int, cost_bps: float = 2.0) -> dict:
    bars = normalize_bars(rows, symbol=symbol)
    by_index = {x["bar_index"]: x for x in snapshots(bars, symbol=symbol)}
    if bar_index not in by_index:
        raise ValueError("source_features_unavailable")
    decision = by_index[bar_index]["decision"]
    if decision["decision"] not in {"LONG", "SHORT"} or not decision["forward_eligible"]:
        raise ValueError("not_forward_signal")
    if bar_index + 1 >= len(bars):
        return {"status": "CENSORED", "reason": "missing_entry_bar", "protocol_sha256": protocol_sha256()}
    side = 1 if decision["decision"] == "LONG" else -1
    entry = bars[bar_index + 1]["open"]
    atr = by_index[bar_index]["snapshot"]["atr14"]
    stop = entry - side * FROZEN_PROTOCOL.atr_stop_multiple * atr
    risk = side * (entry - stop)
    target = entry + side * FROZEN_PROTOCOL.target_r * risk
    cost_r = _num(cost_bps) / 10000.0 * entry / risk
    end = bar_index + FROZEN_PROTOCOL.horizon_bars
    if end >= len(bars):
        return {"status": "CENSORED", "reason": "insufficient_horizon", "protocol_sha256": protocol_sha256()}
    for i in range(bar_index + 1, end + 1):
        bar = bars[i]
        adverse = bar["low"] if side == 1 else bar["high"]
        favorable = bar["high"] if side == 1 else bar["low"]
        if side * (bar["open"] - stop) <= 0:
            return {"status": "SETTLED", "reason": "STOP_GAP", "net_r": side * (bar["open"] - entry) / risk - cost_r, "exit_time": _iso(bar["time"])}
        if side * (bar["open"] - target) >= 0:
            return {"status": "SETTLED", "reason": "TARGET_GAP", "net_r": FROZEN_PROTOCOL.target_r - cost_r, "exit_time": _iso(bar["time"])}
        stop_hit = side * (adverse - stop) <= 0
        target_hit = side * (favorable - target) >= 0
        if stop_hit:
            return {"status": "SETTLED", "reason": "AMBIGUOUS_STOP_FIRST" if target_hit else "STOP", "net_r": -1.0 - cost_r, "exit_time": _iso(bar["time"])}
        if target_hit:
            return {"status": "SETTLED", "reason": "TARGET", "net_r": FROZEN_PROTOCOL.target_r - cost_r, "exit_time": _iso(bar["time"])}
    last = bars[end]
    return {"status": "MARK", "reason": "HORIZON_MARK", "net_r": side * (last["close"] - entry) / risk - cost_r, "exit_time": _iso(last["time"])}
