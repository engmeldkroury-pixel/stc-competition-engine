from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Sequence

Direction = Literal["LONG", "SHORT"]


@dataclass(frozen=True)
class Bar:
    ts: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class ShadowCandidate:
    symbol: str
    mtf_mode: Literal["1h", "vote"]
    session_start_utc: int | None
    session_end_utc: int | None
    stop_atr: float
    target_r: float
    max_entry_gap_atr: float
    authority: Literal["SHADOW_ONLY"] = "SHADOW_ONLY"


@dataclass(frozen=True)
class ShadowSignal:
    symbol: str
    direction: Direction
    signal_bar_ts: int
    entry_bar_ts: int
    entry: float
    stop: float
    target: float
    atr14: float
    higher_timeframe_1h_bar_ts: int
    higher_timeframe_4h_bar_ts: int
    authority: Literal["SHADOW_ONLY"] = "SHADOW_ONLY"


FROZEN_R10_CANDIDATES: dict[str, ShadowCandidate] = {
    "CAPITALCOM:ETHUSD": ShadowCandidate(
        symbol="CAPITALCOM:ETHUSD",
        mtf_mode="vote",
        session_start_utc=None,
        session_end_utc=None,
        stop_atr=1.5,
        target_r=1.5,
        max_entry_gap_atr=0.25,
    ),
    "CAPITALCOM:DOGEUSD": ShadowCandidate(
        symbol="CAPITALCOM:DOGEUSD",
        mtf_mode="1h",
        session_start_utc=7,
        session_end_utc=20,
        stop_atr=1.2,
        target_r=2.5,
        max_entry_gap_atr=0.25,
    ),
}


def _ema(values: Sequence[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    alpha = 2.0 / (period + 1.0)
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * alpha + prev * (1.0 - alpha)
        out[i] = prev
    return out


def _rsi(values: Sequence[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return out
    gain = loss = 0.0
    for i in range(1, period + 1):
        delta = values[i] - values[i - 1]
        gain += max(delta, 0.0)
        loss += max(-delta, 0.0)
    gain /= period
    loss /= period
    out[period] = 100.0 if loss == 0 else 100.0 - 100.0 / (1.0 + gain / loss)
    for i in range(period + 1, len(values)):
        delta = values[i] - values[i - 1]
        gain = (gain * (period - 1) + max(delta, 0.0)) / period
        loss = (loss * (period - 1) + max(-delta, 0.0)) / period
        out[i] = 100.0 if loss == 0 else 100.0 - 100.0 / (1.0 + gain / loss)
    return out


def _atr(bars: Sequence[Bar], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(bars)
    if len(bars) < period:
        return out
    tr: list[float] = []
    for i, bar in enumerate(bars):
        if i == 0:
            tr.append(bar.high - bar.low)
        else:
            prev = bars[i - 1].close
            tr.append(max(bar.high - bar.low, abs(bar.high - prev), abs(bar.low - prev)))
    seed = sum(tr[:period]) / period
    out[period - 1] = seed
    prev_atr = seed
    for i in range(period, len(bars)):
        prev_atr = (prev_atr * (period - 1) + tr[i]) / period
        out[i] = prev_atr
    return out


def _last_fully_closed_index(bars: Sequence[Bar], decision_close_ts: int, interval_seconds: int) -> int:
    lo, hi, ans = 0, len(bars) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if bars[mid].ts + interval_seconds <= decision_close_ts:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def _trend_sign(ema20: float, ema50: float) -> int:
    if ema20 > ema50:
        return 1
    if ema20 < ema50:
        return -1
    return 0


def _session_ok(candidate: ShadowCandidate, ts: int) -> bool:
    if candidate.session_start_utc is None or candidate.session_end_utc is None:
        return True
    hour = datetime.fromtimestamp(ts, tz=timezone.utc).hour
    return candidate.session_start_utc <= hour < candidate.session_end_utc


def evaluate_shadow_signal(
    *,
    candidate: ShadowCandidate,
    bars_15m: Sequence[Bar],
    bars_1h: Sequence[Bar],
    bars_4h: Sequence[Bar],
    signal_index: int,
) -> ShadowSignal | None:
    """Evaluate one frozen R10 shadow candidate causally.

    The 15m signal bar is assumed closed. Only 1h/4h bars whose full interval
    ended by the 15m decision close are eligible. The next 15m open is the
    modeled entry. This function has no execution or live-strategy authority.
    """
    if candidate.authority != "SHADOW_ONLY":
        raise ValueError("R10 evaluator is research-only")
    if signal_index < 50 or signal_index + 1 >= len(bars_15m):
        return None
    signal_bar = bars_15m[signal_index]
    if not _session_ok(candidate, signal_bar.ts):
        return None

    close15 = [b.close for b in bars_15m]
    close1 = [b.close for b in bars_1h]
    close4 = [b.close for b in bars_4h]
    e20_15, e50_15 = _ema(close15, 20), _ema(close15, 50)
    e20_1, e50_1 = _ema(close1, 20), _ema(close1, 50)
    e20_4, e50_4 = _ema(close4, 20), _ema(close4, 50)
    rsi15, atr15 = _rsi(close15), _atr(bars_15m)

    a = atr15[signal_index]
    e20 = e20_15[signal_index]
    e50 = e50_15[signal_index]
    rsi = rsi15[signal_index]
    if a is None or a <= 0 or e20 is None or e50 is None or rsi is None:
        return None

    decision_close_ts = signal_bar.ts + 15 * 60
    j1 = _last_fully_closed_index(bars_1h, decision_close_ts, 60 * 60)
    j4 = _last_fully_closed_index(bars_4h, decision_close_ts, 4 * 60 * 60)
    if j1 < 49 or j4 < 49:
        return None
    if any(x is None for x in (e20_1[j1], e50_1[j1], e20_4[j4], e50_4[j4])):
        return None

    local = _trend_sign(float(e20), float(e50))
    trend1 = _trend_sign(float(e20_1[j1]), float(e50_1[j1]))
    trend4 = _trend_sign(float(e20_4[j4]), float(e50_4[j4]))
    if candidate.mtf_mode == "1h":
        direction = trend1
    else:
        vote = local + trend1 + trend4
        direction = 1 if vote >= 2 else -1 if vote <= -2 else 0
    if direction == 0:
        return None

    distance = (signal_bar.close - float(e20)) / a
    slope = (float(e20) - float(e20_15[signal_index - 4])) / a if e20_15[signal_index - 4] is not None else 0.0
    if direction == 1:
        pullback_ok = (
            -0.40 <= distance <= 0.35
            and signal_bar.close > float(e20)
            and signal_bar.close > signal_bar.open
            and slope > -0.15
            and 44.0 <= rsi <= 63.0
        )
    else:
        pullback_ok = (
            -0.35 <= distance <= 0.40
            and signal_bar.close < float(e20)
            and signal_bar.close < signal_bar.open
            and slope < 0.15
            and 37.0 <= rsi <= 56.0
        )
    if not pullback_ok:
        return None

    entry_bar = bars_15m[signal_index + 1]
    if abs(entry_bar.open - signal_bar.close) / a > candidate.max_entry_gap_atr:
        return None

    stop = entry_bar.open - direction * candidate.stop_atr * a
    risk = direction * (entry_bar.open - stop)
    if risk <= 0:
        return None
    target = entry_bar.open + direction * candidate.target_r * risk
    return ShadowSignal(
        symbol=candidate.symbol,
        direction="LONG" if direction > 0 else "SHORT",
        signal_bar_ts=signal_bar.ts,
        entry_bar_ts=entry_bar.ts,
        entry=entry_bar.open,
        stop=stop,
        target=target,
        atr14=a,
        higher_timeframe_1h_bar_ts=bars_1h[j1].ts,
        higher_timeframe_4h_bar_ts=bars_4h[j4].ts,
    )
