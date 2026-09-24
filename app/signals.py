from __future__ import annotations

import uuid

from .competition_profiles import get_profile
from .models import SignalEvaluationRequest, SignalEvaluationResult, TradingViewWebhook


def evaluate(req: SignalEvaluationRequest) -> SignalEvaluationResult:
    profile = get_profile(req.competition_id)
    if req.symbol not in profile.max_open_position:
        raise ValueError("Symbol is not allowed in this competition")

    f = req.factors
    # Direction comes primarily from price/structure evidence. News and macro
    # are deliberately low-weight directional inputs; event risk is handled
    # separately by the fail-closed news/macro overlay.
    weights = {
        "technical": 0.60,
        "news": 0.05,
        "macro": 0.05,
        "volatility_quality": 0.15,
        "liquidity_quality": 0.15,
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


def confirmation_score_from_tradingview(payload: TradingViewWebhook) -> float | None:
    fields = (
        payload.confirm_timeframe,
        payload.confirm_time,
        payload.confirm_close,
        payload.confirm_ema20,
        payload.confirm_ema50,
        payload.confirm_ema200,
        payload.confirm_rsi14,
        payload.confirm_atr14,
        payload.confirm_macd,
        payload.confirm_macd_signal,
        payload.confirm_volume_ratio,
    )
    if any(value is None for value in fields):
        return None

    close = float(payload.confirm_close)
    ema20 = float(payload.confirm_ema20)
    ema50 = float(payload.confirm_ema50)
    ema200 = float(payload.confirm_ema200)
    rsi = float(payload.confirm_rsi14)
    macd = float(payload.confirm_macd)
    macd_signal = float(payload.confirm_macd_signal)
    volume_ratio = float(payload.confirm_volume_ratio)

    score = 0.0
    score += 0.30 if close > ema20 > ema50 else -0.30 if close < ema20 < ema50 else 0.0
    score += 0.20 if ema50 >= ema200 else -0.20
    score += 0.20 if macd >= macd_signal else -0.20
    if 50 <= rsi <= 68:
        score += 0.15
    elif 32 <= rsi < 50:
        score -= 0.15
    if volume_ratio >= 1.0:
        score += 0.15 if close >= ema20 else -0.15
    return max(-1.0, min(1.0, score))


def high_conviction_assessment(
    *,
    recommendation: str,
    composite_score: float,
    short_term_technical: float,
    historical_regime: float | None,
    blended_technical: float,
    volatility_quality: float,
    liquidity_quality: float,
    confirmation_score: float | None,
    trend_2h_score: float | None,
    trend_4h_score: float | None,
    trend_1m_score: float | None,
    family_evidence_score: float | None,
    family_agreement_ratio: float | None,
    family_aligned_count: int | None,
    family_conflict_count: int | None,
) -> tuple[bool, list[str]]:
    """Fail-closed A+ entry gate for competition alerts.

    This gate deliberately prefers missed trades over low-quality entries.
    It does not claim certainty or probability of profit.
    """
    if recommendation not in {"LONG", "SHORT"}:
        return False, ["base_recommendation_not_directional"]

    sign = 1.0 if recommendation == "LONG" else -1.0
    checks: list[tuple[str, bool]] = [
        ("historical_context_present", historical_regime is not None),
        ("confirmation_context_present", confirmation_score is not None),
        ("confirmation_alignment_1h", confirmation_score is not None and sign * confirmation_score >= 0.70),
        ("trend_2h_present", trend_2h_score is not None),
        ("trend_2h_alignment", trend_2h_score is not None and sign * trend_2h_score >= 0.65),
        ("trend_4h_present", trend_4h_score is not None),
        ("trend_4h_alignment", trend_4h_score is not None and sign * trend_4h_score >= 0.65),
        ("trend_1m_present", trend_1m_score is not None),
        ("trend_1m_alignment", trend_1m_score is not None and sign * trend_1m_score >= 0.55),
        ("family_evidence_present", family_evidence_score is not None),
        ("family_direction_alignment", family_evidence_score is not None and sign * family_evidence_score >= 0.45),
        ("family_agreement", family_agreement_ratio is not None and family_agreement_ratio >= 0.65),
        ("family_breadth", family_aligned_count is not None and family_aligned_count >= 5),
        ("family_conflicts", family_conflict_count is not None and family_conflict_count <= 2),
        ("short_term_strength", sign * short_term_technical >= 0.75),
        ("historical_alignment", historical_regime is not None and sign * historical_regime >= 0.55),
        ("blended_technical_strength", sign * blended_technical >= 0.70),
        ("composite_strength", sign * composite_score >= 0.45),
        ("volatility_quality", sign * volatility_quality >= 0.20),
        ("liquidity_quality", sign * liquidity_quality >= 0.30),
    ]
    failed = [name for name, ok in checks if not ok]
    return failed == [], failed



def competition_opportunity_assessment(
    *,
    recommendation: str,
    composite_score: float,
    short_term_technical: float,
    historical_regime: float | None,
    blended_technical: float,
    volatility_quality: float,
    liquidity_quality: float,
    confirmation_score: float | None,
    trend_2h_score: float | None,
    trend_4h_score: float | None,
    family_evidence_score: float | None,
    family_agreement_ratio: float | None,
    family_aligned_count: int | None,
    family_conflict_count: int | None,
) -> tuple[bool, list[str]]:
    """Competition-only opportunity gate.

    This gate is intentionally less restrictive than the A+ gate so a short
    paper-trading competition does not require every long-horizon timeframe to
    agree. It still requires directional strength, majority intraday alignment,
    family confirmation, and non-poor execution quality. Human approval remains
    mandatory and this gate does not imply a probability of profit.
    """
    if recommendation not in {"LONG", "SHORT"}:
        return False, ["base_recommendation_not_directional"]

    sign = 1.0 if recommendation == "LONG" else -1.0
    intraday = (
        confirmation_score,
        trend_2h_score,
        trend_4h_score,
    )
    aligned_intraday = sum(
        1 for value in intraday
        if value is not None and sign * value >= 0.35
    )

    checks: list[tuple[str, bool]] = [
        ("historical_context_present", historical_regime is not None),
        ("confirmation_context_present", confirmation_score is not None),
        ("intraday_majority_alignment", aligned_intraday >= 2),
        ("short_term_strength", sign * short_term_technical >= 0.55),
        ("blended_technical_strength", sign * blended_technical >= 0.45),
        ("composite_strength", sign * composite_score >= 0.35),
        ("historical_not_strongly_opposed", historical_regime is not None and sign * historical_regime >= -0.15),
        ("family_evidence_present", family_evidence_score is not None),
        ("family_direction_alignment", family_evidence_score is not None and sign * family_evidence_score >= 0.25),
        ("family_agreement", family_agreement_ratio is not None and family_agreement_ratio >= 0.55),
        ("family_breadth", family_aligned_count is not None and family_aligned_count >= 4),
        ("family_conflicts", family_conflict_count is not None and family_conflict_count <= 3),
        ("volatility_quality", sign * volatility_quality >= 0.0),
        ("liquidity_quality", sign * liquidity_quality >= 0.0),
    ]
    failed = [name for name, ok in checks if not ok]
    return failed == [], failed


def setup_quality_score(
    *,
    recommendation: str,
    short_term_technical: float,
    confirmation_score: float | None,
    trend_2h_score: float | None,
    trend_4h_score: float | None,
    historical_regime: float | None,
    trend_1m_score: float | None,
    blended_technical: float,
    volatility_quality: float,
    liquidity_quality: float,
    family_evidence_score: float | None,
) -> int:
    """Return a transparent 0-100 setup-quality score, not win probability."""
    if recommendation not in {"LONG", "SHORT"}:
        return 0
    sign = 1.0 if recommendation == "LONG" else -1.0

    components = [
        (sign * short_term_technical, 0.14),
        (sign * (confirmation_score if confirmation_score is not None else -1.0), 0.15),
        (sign * (trend_2h_score if trend_2h_score is not None else -1.0), 0.12),
        (sign * (trend_4h_score if trend_4h_score is not None else -1.0), 0.12),
        (sign * (historical_regime if historical_regime is not None else -1.0), 0.12),
        (sign * (trend_1m_score if trend_1m_score is not None else -1.0), 0.08),
        (sign * blended_technical, 0.06),
        (sign * volatility_quality, 0.03),
        (sign * liquidity_quality, 0.03),
        (sign * (family_evidence_score if family_evidence_score is not None else -1.0), 0.15),
    ]
    raw = 0.0
    for value, weight in components:
        normalized = max(0.0, min(1.0, (float(value) + 1.0) / 2.0))
        raw += normalized * weight
    return int(round(max(0.0, min(1.0, raw)) * 100.0))


def factors_from_tradingview(payload: TradingViewWebhook) -> float:
    short_term = short_term_score_from_tradingview(payload)
    historical = historical_regime_from_tradingview(payload)
    if historical is None:
        return short_term
    return max(-1.0, min(1.0, short_term * 0.65 + historical * 0.35))



def _directional_quality(technical_direction: float, raw_quality: float) -> float:
    """Align non-directional market quality with the active technical thesis.

    Quality must never create a LONG or SHORT by itself. Good quality increases
    confidence in the technical direction; poor quality reduces it symmetrically.
    """
    if technical_direction > 0:
        sign = 1.0
    elif technical_direction < 0:
        sign = -1.0
    else:
        return 0.0
    return max(-1.0, min(1.0, sign * raw_quality))


def volatility_quality_from_tradingview(
    payload: TradingViewWebhook,
    technical_direction: float,
) -> float:
    """Directional execution-quality factor from closed-bar range vs ATR.

    This is not a volatility-direction signal. It only judges whether the latest
    confirmed bar is reasonably tradable relative to its own ATR. Extreme shock
    bars reduce confidence; ordinary movement increases confidence.
    """
    atr = float(payload.atr14)
    if atr <= 0:
        return 0.0

    bar_range = max(0.0, float(payload.high) - float(payload.low))
    ratio = bar_range / atr

    if 0.40 <= ratio <= 1.80:
        raw_quality = 0.50
    elif 0.20 <= ratio <= 2.50:
        raw_quality = 0.20
    elif ratio > 3.00:
        raw_quality = -0.80
    else:
        raw_quality = -0.20

    return _directional_quality(technical_direction, raw_quality)


def liquidity_quality_from_tradingview(
    payload: TradingViewWebhook,
    technical_direction: float,
) -> float:
    """Directional liquidity/participation quality from relative volume.

    TradingView volume can be exchange volume for futures and a provider/tick
    volume proxy for some CFDs, so this factor is deliberately modest. It never
    creates direction by itself.
    """
    volume = float(payload.volume)
    ratio = float(payload.volume_ratio)
    if volume <= 0 or ratio < 0:
        return 0.0

    if ratio >= 1.50:
        raw_quality = 0.60
    elif ratio >= 0.80:
        raw_quality = 0.30
    elif ratio >= 0.40:
        raw_quality = 0.00
    else:
        raw_quality = -0.50

    return _directional_quality(technical_direction, raw_quality)
