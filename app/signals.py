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


def factors_from_tradingview(payload: TradingViewWebhook):
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
