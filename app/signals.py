from __future__ import annotations

import uuid

from .competition_profiles import get_profile
from .models import SignalEvaluationRequest, SignalEvaluationResult, TradingViewWebhook


def evaluate(req: SignalEvaluationRequest) -> SignalEvaluationResult:
    profile = get_profile(req.competition_id)
    if req.symbol not in profile.max_open_position:
        raise ValueError("Symbol is not allowed in this competition")

    f = req.factors
    weights = {
        "technical": 0.45,
        "news": 0.20,
        "macro": 0.15,
        "volatility_quality": 0.10,
        "liquidity_quality": 0.10,
    }
    composite = (
        f.technical * weights["technical"]
        + f.news * weights["news"]
        + f.macro * weights["macro"]
        + f.volatility_quality * weights["volatility_quality"]
        + f.liquidity_quality * weights["liquidity_quality"]
    )
    composite = max(-1.0, min(1.0, composite))

    if composite >= 0.35:
        recommendation = "LONG"
    elif composite <= -0.35:
        recommendation = "SHORT"
    else:
        recommendation = "WAIT"

    reasons = [
        f"technical={f.technical:+.2f}",
        f"news={f.news:+.2f}",
        f"macro={f.macro:+.2f}",
        f"volatility_quality={f.volatility_quality:+.2f}",
        f"liquidity_quality={f.liquidity_quality:+.2f}",
        "Human approval remains mandatory before competition order entry.",
    ]

    return SignalEvaluationResult(
        signal_id=str(uuid.uuid4()),
        competition_id=req.competition_id,
        symbol=req.symbol,
        composite_score=composite,
        recommendation=recommendation,
        confidence=min(1.0, abs(composite)),
        requires_human_approval=True,
        reasons=reasons,
    )


def short_term_score_from_tradingview(payload: TradingViewWebhook) -> float:
    score = 0.0
    score += 0.35 if payload.close > payload.ema20 > payload.ema50 else -0.35 if payload.close < payload.ema20 < payload.ema50 else 0.0
    score += 0.30 if payload.macd > payload.macd_signal else -0.30
    if 50 <= payload.rsi14 <= 70:
        score += 0.20
    elif 30 <= payload.rsi14 < 50:
        score -= 0.10
    if payload.volume_ratio >= 1.5:
        score += 0.15 if score >= 0 else -0.15
    return max(-1.0, min(1.0, score))


def historical_regime_from_tradingview(payload: TradingViewWebhook) -> float | None:
    fields = (
        payload.history_close,
        payload.history_ema50,
        payload.history_ema200,
        payload.history_high_252,
        payload.history_low_252,
        payload.history_momentum_20,
        payload.history_momentum_63,
        payload.history_momentum_126,
        payload.history_momentum_252,
    )
    if any(value is None for value in fields):
        return None

    close = float(payload.history_close)
    ema50 = float(payload.history_ema50)
    ema200 = float(payload.history_ema200)
    high = float(payload.history_high_252)
    low = float(payload.history_low_252)
    m20 = float(payload.history_momentum_20)
    m63 = float(payload.history_momentum_63)
    m126 = float(payload.history_momentum_126)
    m252 = float(payload.history_momentum_252)

    score = 0.0
    score += 0.15 if close >= ema50 else -0.15
    score += 0.20 if ema50 >= ema200 else -0.20
    score += 0.15 if close >= ema200 else -0.15
    score += 0.10 if m20 >= 0 else -0.10
    score += 0.10 if m63 >= 0 else -0.10
    score += 0.10 if m126 >= 0 else -0.10
    score += 0.10 if m252 >= 0 else -0.10

    if high > low:
        range_position = (close - low) / (high - low)
        score += 0.10 if range_position >= 0.65 else -0.10 if range_position <= 0.35 else 0.0

    return max(-1.0, min(1.0, score))


def factors_from_tradingview(payload: TradingViewWebhook) -> float:
    short_term = short_term_score_from_tradingview(payload)
    historical = historical_regime_from_tradingview(payload)
    if historical is None:
        return short_term
    return max(-1.0, min(1.0, short_term * 0.65 + historical * 0.35))
