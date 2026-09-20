from __future__ import annotations

import math
from statistics import fmean

from .models import Bar, TechnicalAnalysisResult


def ema(values: list[float], period: int) -> float:
    if len(values) < period:
        raise ValueError(f"Need at least {period} values")
    alpha = 2.0 / (period + 1.0)
    value = fmean(values[:period])
    for x in values[period:]:
        value = alpha * x + (1.0 - alpha) * value
    return value


def ema_series(values: list[float], period: int) -> list[float]:
    if len(values) < period:
        raise ValueError(f"Need at least {period} values")
    alpha = 2.0 / (period + 1.0)
    seed = fmean(values[:period])
    out = [seed]
    value = seed
    for x in values[period:]:
        value = alpha * x + (1.0 - alpha) * value
        out.append(value)
    return out


def rsi(values: list[float], period: int = 14) -> float:
    if len(values) < period + 1:
        raise ValueError(f"Need at least {period + 1} values")
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]
    avg_gain = fmean(gains[:period])
    avg_loss = fmean(losses[:period])
    for i in range(period, len(gains)):
        avg_gain = ((period - 1) * avg_gain + gains[i]) / period
        avg_loss = ((period - 1) * avg_loss + losses[i]) / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def atr(bars: list[Bar], period: int = 14) -> float:
    if len(bars) < period + 1:
        raise ValueError(f"Need at least {period + 1} bars")
    trs: list[float] = []
    for i in range(1, len(bars)):
        prev_close = bars[i - 1].close
        b = bars[i]
        trs.append(max(b.high - b.low, abs(b.high - prev_close), abs(b.low - prev_close)))
    value = fmean(trs[:period])
    for tr in trs[period:]:
        value = ((period - 1) * value + tr) / period
    return value


def macd(values: list[float]) -> tuple[float, float]:
    if len(values) < 35:
        raise ValueError("Need at least 35 values")
    fast = ema_series(values, 12)
    slow = ema_series(values, 26)
    offset = len(fast) - len(slow)
    macd_series = [fast[i + offset] - slow[i] for i in range(len(slow))]
    signal = ema(macd_series, 9)
    return macd_series[-1], signal


def analyze(symbol: str, bars: list[Bar]) -> TechnicalAnalysisResult:
    closes = [b.close for b in bars]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    r = rsi(closes, 14)
    a = atr(bars, 14)
    m, ms = macd(closes)
    mom10 = closes[-1] / closes[-11] - 1.0

    score = 0.0
    score += 0.40 if closes[-1] > e20 > e50 else -0.40 if closes[-1] < e20 < e50 else 0.0
    score += 0.20 if m > ms else -0.20
    score += 0.25 if mom10 > 0 else -0.25
    if 50 <= r <= 70:
        score += 0.15
    elif 30 <= r < 50:
        score -= 0.10
    elif r > 80:
        score -= 0.05
    elif r < 20:
        score += 0.05

    score = max(-1.0, min(1.0, score))
    if score >= 0.35:
        regime = "bullish"
    elif score <= -0.35:
        regime = "bearish"
    else:
        regime = "mixed"

    return TechnicalAnalysisResult(
        symbol=symbol,
        latest_close=closes[-1],
        ema20=e20,
        ema50=e50,
        rsi14=r,
        atr14=a,
        macd=m,
        macd_signal=ms,
        momentum_10=mom10,
        technical_score=score,
        regime=regime,
    )


def finite(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("non-finite analysis value")
    return value
