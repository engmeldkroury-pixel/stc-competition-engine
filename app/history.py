from __future__ import annotations

from statistics import fmean, pstdev

from .analysis import atr, ema, rsi
from .models import Bar, HistoricalRegimeResult


def build_historical_regime(symbol: str, daily_bars: list[Bar]) -> HistoricalRegimeResult:
    """Build a one-year daily regime snapshot from raw OHLCV.

    Requires at least 254 daily bars so 252-day momentum can be measured using
    confirmed historical closes. This function is deterministic and is intended
    for historical bootstrap, validation and backtest research.
    """
    if len(daily_bars) < 254:
        raise ValueError("Need at least 254 daily bars for one-year historical regime")

    bars = daily_bars[-4000:]
    closes = [b.close for b in bars]
    latest = closes[-1]
    e50 = ema(closes, 50)
    e200 = ema(closes, 200)
    r14 = rsi(closes, 14)
    a14 = atr(bars, 14)

    window252 = bars[-252:]
    high252 = max(b.high for b in window252)
    low252 = min(b.low for b in window252)

    m20 = latest / closes[-21] - 1.0
    m63 = latest / closes[-64] - 1.0
    m126 = latest / closes[-127] - 1.0
    m252 = latest / closes[-253] - 1.0

    returns20 = [closes[i] / closes[i - 1] - 1.0 for i in range(len(closes) - 19, len(closes))]
    volatility20 = pstdev(returns20) if len(returns20) >= 2 else 0.0

    score = 0.0
    score += 0.15 if latest >= e50 else -0.15
    score += 0.20 if e50 >= e200 else -0.20
    score += 0.15 if latest >= e200 else -0.15
    score += 0.10 if m20 >= 0 else -0.10
    score += 0.10 if m63 >= 0 else -0.10
    score += 0.10 if m126 >= 0 else -0.10
    score += 0.10 if m252 >= 0 else -0.10

    if high252 > low252:
        position = (latest - low252) / (high252 - low252)
        score += 0.10 if position >= 0.65 else -0.10 if position <= 0.35 else 0.0

    score = max(-1.0, min(1.0, score))
    regime = "bullish" if score >= 0.35 else "bearish" if score <= -0.35 else "mixed"

    return HistoricalRegimeResult(
        symbol=symbol,
        bars_used=len(bars),
        latest_close=latest,
        ema50=e50,
        ema200=e200,
        rsi14=r14,
        atr14=a14,
        high_252=high252,
        low_252=low252,
        momentum_20=m20,
        momentum_63=m63,
        momentum_126=m126,
        momentum_252=m252,
        volatility_20=volatility20,
        regime_score=score,
        regime=regime,
    )
