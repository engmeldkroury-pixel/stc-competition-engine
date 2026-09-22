from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureFamily:
    name: str
    features: tuple[str, ...]
    max_family_weight: float


FEATURE_FAMILIES: tuple[FeatureFamily, ...] = (
    FeatureFamily("trend", (
        "ema_9_20_50_100_200_alignment", "sma_20_50_100_200_alignment", "adx", "dmi_plus_minus",
        "supertrend", "aroon", "ichimoku_cloud", "parabolic_sar", "linear_regression_slope",
        "higher_high_lower_low_sequence", "trend_efficiency_ratio",
    ), 0.16),
    FeatureFamily("momentum", (
        "rsi_14", "stochastic", "stoch_rsi", "macd_histogram", "roc", "momentum_10",
        "cci", "williams_r", "tsi", "ultimate_oscillator", "ppo", "relative_strength_rank",
    ), 0.14),
    FeatureFamily("volatility", (
        "atr", "normalized_atr", "bollinger_width", "bollinger_percent_b", "keltner_width",
        "squeeze_state", "historical_volatility", "realized_volatility", "true_range_percentile",
        "volatility_regime", "donchian_width",
    ), 0.12),
    FeatureFamily("volume", (
        "volume_ratio", "obv", "mfi", "cmf", "accumulation_distribution", "volume_roc",
        "volume_profile_poc_distance", "relative_volume", "up_down_volume_ratio",
    ), 0.10),
    FeatureFamily("vwap", (
        "session_vwap_distance", "anchored_vwap_distance", "vwap_slope",
        "vwap_band_location", "vwap_reclaim_reject",
    ), 0.08),
    FeatureFamily("market_structure", (
        "bos", "choch", "swing_high_low", "break_retest", "range_location",
        "support_resistance_distance", "pivot_structure", "market_structure_trend",
        "failed_breakout", "inside_outside_structure",
    ), 0.14),
    FeatureFamily("smc_liquidity", (
        "liquidity_sweep", "equal_highs_lows", "fair_value_gap", "order_block",
        "breaker_block", "mitigation_block", "premium_discount_zone",
        "displacement_candle", "imbalance_fill_ratio", "liquidity_void",
    ), 0.12),
    FeatureFamily("price_action", (
        "engulfing", "pin_bar", "inside_bar", "outside_bar", "doji_context",
        "marubozu", "three_bar_reversal", "gap_behavior", "body_wick_ratio",
        "close_location_value",
    ), 0.08),
    FeatureFamily("microstructure", (
        "spread_proxy", "bar_speed", "tick_activity_proxy", "short_term_range_efficiency",
        "micro_pullback_depth", "micro_breakout_persistence",
    ), 0.06),
)


def feature_count() -> int:
    return sum(len(f.features) for f in FEATURE_FAMILIES)


def family_weight_total() -> float:
    return sum(f.max_family_weight for f in FEATURE_FAMILIES)


def feature_family(name: str) -> FeatureFamily:
    for family in FEATURE_FAMILIES:
        if family.name == name:
            return family
    raise KeyError(name)
