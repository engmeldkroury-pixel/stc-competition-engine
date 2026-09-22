from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class EvidenceObservation:
    feature: str
    family: str
    direction: float
    reliability: float
    freshness: float = 1.0
    independence_group: str | None = None
    hard_confirmation: bool = False


@dataclass(frozen=True)
class EvidenceSummary:
    score: float
    agreement_ratio: float
    independent_confirmations: int
    hard_confirmations: int
    family_scores: Mapping[str, float]
    family_weights_used: Mapping[str, float]
    conflicts: tuple[str, ...]
    strongest_features: tuple[str, ...]


@dataclass(frozen=True)
class NewsMacroContext:
    scheduled_high_impact: bool = False
    minutes_to_event: float | None = None
    minutes_since_event: float | None = None
    unscheduled_shock: bool = False
    news_direction: float = 0.0
    news_relevance: float = 0.0
    news_freshness: float = 0.0
    macro_direction: float = 0.0
    macro_relevance: float = 0.0


@dataclass(frozen=True)
class OverlayResult:
    technical_score: float
    adjusted_score: float
    entry_blocked: bool
    size_multiplier: float
    directional_overlay: float
    reasons: tuple[str, ...]


FAMILY_PRIOR_WEIGHT = {
    "trend": 0.15,
    "market_structure": 0.16,
    "smc_liquidity": 0.15,
    "momentum": 0.11,
    "volume": 0.10,
    "volatility": 0.10,
    "vwap": 0.08,
    "price_action": 0.08,
    "microstructure": 0.07,
}

# Reliability priors are starting points. Backtest/walk-forward calibration can
# later override them per symbol/strategy/timeframe.
FEATURE_RELIABILITY = {
    # Structural confirmations receive more weight than oscillator thresholds.
    "bos": 0.92,
    "choch": 0.90,
    "break_retest": 0.90,
    "liquidity_sweep": 0.91,
    "displacement_candle": 0.86,
    "fair_value_gap": 0.76,
    "order_block": 0.78,
    "breaker_block": 0.82,
    "mitigation_block": 0.76,
    "market_structure_trend": 0.90,
    "higher_high_lower_low_sequence": 0.88,
    "trend_efficiency_ratio": 0.78,
    "adx": 0.77,
    "dmi_plus_minus": 0.76,
    "ichimoku_cloud": 0.74,
    "supertrend": 0.70,
    "ema_9_20_50_100_200_alignment": 0.82,
    "sma_20_50_100_200_alignment": 0.76,
    "anchored_vwap_distance": 0.82,
    "vwap_reclaim_reject": 0.86,
    "volume_profile_poc_distance": 0.80,
    "relative_volume": 0.80,
    "obv": 0.67,
    "cmf": 0.69,
    "mfi": 0.64,
    "atr": 0.58,
    "squeeze_state": 0.79,
    "volatility_regime": 0.82,
    "rsi_14": 0.58,
    "stochastic": 0.52,
    "stoch_rsi": 0.50,
    "macd_histogram": 0.67,
    "cci": 0.54,
    "roc": 0.58,
    "engulfing": 0.64,
    "pin_bar": 0.58,
    "three_bar_reversal": 0.70,
    "failed_breakout": 0.84,
}

FEATURE_INDEPENDENCE_GROUP = {
    "rsi_14": "oscillator_momentum",
    "stochastic": "oscillator_momentum",
    "stoch_rsi": "oscillator_momentum",
    "cci": "oscillator_momentum",
    "williams_r": "oscillator_momentum",
    "macd_histogram": "macd_momentum",
    "ppo": "macd_momentum",
    "ema_9_20_50_100_200_alignment": "moving_average_trend",
    "sma_20_50_100_200_alignment": "moving_average_trend",
    "supertrend": "atr_trend",
    "parabolic_sar": "atr_trend",
    "bollinger_width": "volatility_band",
    "keltner_width": "volatility_band",
    "squeeze_state": "volatility_band",
    "obv": "volume_flow",
    "cmf": "volume_flow",
    "mfi": "volume_flow",
    "accumulation_distribution": "volume_flow",
    "bos": "structure_break",
    "choch": "structure_break",
    "break_retest": "structure_retest",
    "liquidity_sweep": "liquidity_event",
    "equal_highs_lows": "liquidity_pool",
    "fair_value_gap": "imbalance",
    "liquidity_void": "imbalance",
    "order_block": "institutional_zone",
    "breaker_block": "institutional_zone",
    "mitigation_block": "institutional_zone",
}

HARD_CONFIRMATION_FEATURES = {
    "bos",
    "choch",
    "break_retest",
    "liquidity_sweep",
    "failed_breakout",
    "vwap_reclaim_reject",
    "market_structure_trend",
}


STRATEGY_FAMILY_MULTIPLIER = {
    "smc_structure_liquidity": {
        "market_structure": 1.35,
        "smc_liquidity": 1.40,
        "price_action": 1.10,
        "volume": 1.05,
        "trend": 0.85,
        "momentum": 0.75,
    },
    "trend_pullback": {
        "trend": 1.40,
        "market_structure": 1.25,
        "momentum": 1.10,
        "volatility": 1.05,
        "smc_liquidity": 0.90,
    },
    "breakout_expansion": {
        "volatility": 1.30,
        "volume": 1.30,
        "market_structure": 1.20,
        "trend": 1.10,
        "momentum": 1.05,
    },
    "mean_reversion": {
        "volatility": 1.25,
        "momentum": 1.20,
        "market_structure": 1.15,
        "vwap": 1.15,
        "trend": 0.65,
    },
    "vwap_intraday": {
        "vwap": 1.45,
        "volume": 1.20,
        "market_structure": 1.20,
        "microstructure": 1.10,
    },
    "microtrend_scalp": {
        "microstructure": 1.45,
        "liquidity": 1.30,
        "momentum": 1.15,
        "volatility": 1.15,
        "trend": 0.85,
    },
}


def reliability_for_feature(feature: str, fallback: float = 0.60) -> float:
    return FEATURE_RELIABILITY.get(feature, fallback)


def make_observation(
    feature: str,
    family: str,
    direction: float,
    *,
    freshness: float = 1.0,
    reliability: float | None = None,
    hard_confirmation: bool | None = None,
) -> EvidenceObservation:
    return EvidenceObservation(
        feature=feature,
        family=family,
        direction=max(-1.0, min(1.0, float(direction))),
        reliability=max(0.0, min(1.0, reliability_for_feature(feature) if reliability is None else reliability)),
        freshness=max(0.0, min(1.0, float(freshness))),
        independence_group=FEATURE_INDEPENDENCE_GROUP.get(feature, feature),
        hard_confirmation=(feature in HARD_CONFIRMATION_FEATURES) if hard_confirmation is None else hard_confirmation,
    )


def aggregate_evidence(
    observations: Iterable[EvidenceObservation],
    *,
    strategy_id: str | None = None,
) -> EvidenceSummary:
    obs = tuple(observations)
    if not obs:
        return EvidenceSummary(0.0, 0.0, 0, 0, {}, {}, (), ())

    strategy_mult = STRATEGY_FAMILY_MULTIPLIER.get(strategy_id or "", {})
    grouped: dict[str, list[EvidenceObservation]] = {}
    for item in obs:
        grouped.setdefault(item.family, []).append(item)

    family_scores: dict[str, float] = {}
    family_weights: dict[str, float] = {}
    weighted_total = 0.0
    weight_total = 0.0
    conflicts: list[str] = []
    strongest: list[tuple[float, str]] = []

    for family, items in grouped.items():
        by_group: dict[str, list[EvidenceObservation]] = {}
        for item in items:
            by_group.setdefault(item.independence_group or item.feature, []).append(item)

        family_num = 0.0
        family_den = 0.0
        for independent_items in by_group.values():
            ranked = sorted(
                independent_items,
                key=lambda x: x.reliability * x.freshness * abs(x.direction),
                reverse=True,
            )
            for index, item in enumerate(ranked):
                # Correlated indicators do not each receive a full vote.
                correlation_discount = 1.0 if index == 0 else 0.30 ** index
                effective = item.reliability * item.freshness * correlation_discount
                family_num += item.direction * effective
                family_den += effective
                strongest.append((abs(item.direction) * effective, item.feature))

        family_score = 0.0 if family_den == 0 else max(-1.0, min(1.0, family_num / family_den))
        family_scores[family] = family_score

        prior = FAMILY_PRIOR_WEIGHT.get(family, 0.04)
        multiplier = strategy_mult.get(family, 1.0)
        effective_family_weight = prior * multiplier
        family_weights[family] = effective_family_weight
        weighted_total += family_score * effective_family_weight
        weight_total += effective_family_weight

    direction_score = 0.0 if weight_total == 0 else max(-1.0, min(1.0, weighted_total / weight_total))
    # Breadth matters: a single correlated family cannot earn the same overall
    # evidence score as several independent families agreeing. 0.50 is the
    # approximate family-weight coverage expected before evidence is considered
    # broadly confirmed.
    breadth = min(1.0, weight_total / 0.50) if weight_total > 0 else 0.0
    breadth_multiplier = 0.45 + 0.55 * breadth
    score = max(-1.0, min(1.0, direction_score * breadth_multiplier))

    positive_strength = sum(
        max(0.0, item.direction) * item.reliability * item.freshness for item in obs
    )
    negative_strength = sum(
        max(0.0, -item.direction) * item.reliability * item.freshness for item in obs
    )
    total_directional = positive_strength + negative_strength
    dominant = max(positive_strength, negative_strength)
    agreement = 0.0 if total_directional == 0 else dominant / total_directional

    sign = 1.0 if score > 0 else -1.0 if score < 0 else 0.0
    independent_confirmations = len({
        item.independence_group
        for item in obs
        if item.independence_group
        and sign != 0
        and sign * item.direction >= 0.45
        and item.reliability >= 0.55
    })
    hard_confirmations = sum(
        1
        for item in obs
        if item.hard_confirmation
        and sign != 0
        and sign * item.direction >= 0.55
        and item.reliability >= 0.75
    )

    for family, family_score in family_scores.items():
        if sign != 0 and sign * family_score <= -0.45:
            conflicts.append(f"{family}_conflicts_with_dominant_direction")

    strongest_features = tuple(
        feature for _, feature in sorted(strongest, reverse=True)[:8]
    )

    return EvidenceSummary(
        score=score,
        agreement_ratio=agreement,
        independent_confirmations=independent_confirmations,
        hard_confirmations=hard_confirmations,
        family_scores=family_scores,
        family_weights_used=family_weights,
        conflicts=tuple(conflicts),
        strongest_features=strongest_features,
    )


def apply_news_macro_overlay(
    technical_score: float,
    context: NewsMacroContext,
    *,
    pre_event_block_minutes: float = 20.0,
    post_event_cooldown_minutes: float = 10.0,
) -> OverlayResult:
    """Treat news/macro as context and risk control, not the primary direction engine."""
    technical_score = max(-1.0, min(1.0, float(technical_score)))
    reasons: list[str] = []
    entry_blocked = False
    size_multiplier = 1.0

    if context.scheduled_high_impact and context.minutes_to_event is not None:
        if 0 <= context.minutes_to_event <= pre_event_block_minutes:
            entry_blocked = True
            reasons.append("scheduled_high_impact_event_imminent")

    if context.scheduled_high_impact and context.minutes_since_event is not None:
        if 0 <= context.minutes_since_event <= post_event_cooldown_minutes:
            entry_blocked = True
            reasons.append("post_event_price_discovery_cooldown")

    if context.unscheduled_shock:
        entry_blocked = True
        size_multiplier = 0.0
        reasons.append("unscheduled_market_shock")

    # Directional news/macro influence is deliberately capped. Price/structure
    # leads the thesis; context can support or weaken it but cannot create it.
    news_component = (
        max(-1.0, min(1.0, context.news_direction))
        * max(0.0, min(1.0, context.news_relevance))
        * max(0.0, min(1.0, context.news_freshness))
        * 0.06
    )
    macro_component = (
        max(-1.0, min(1.0, context.macro_direction))
        * max(0.0, min(1.0, context.macro_relevance))
        * 0.04
    )
    overlay = max(-0.10, min(0.10, news_component + macro_component))

    if technical_score != 0 and overlay * technical_score < 0:
        size_multiplier *= 0.75
        reasons.append("news_macro_context_conflicts_with_technical")
    elif technical_score != 0 and overlay * technical_score > 0:
        reasons.append("news_macro_context_supports_technical")

    adjusted = max(-1.0, min(1.0, technical_score + overlay))

    return OverlayResult(
        technical_score=technical_score,
        adjusted_score=adjusted,
        entry_blocked=entry_blocked,
        size_multiplier=size_multiplier,
        directional_overlay=overlay,
        reasons=tuple(reasons),
    )
