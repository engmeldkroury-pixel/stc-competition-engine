from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommunityIndicatorSpec:
    indicator_id: str
    display_name: str
    author: str
    source_url: str
    signal_family: str
    suitable_asset_classes: tuple[str, ...]
    preferred_timeframes: tuple[str, ...]
    open_source: bool
    editor_pick: bool = False
    popularity_uses: int | None = None
    implementation_status: str = "pending"
    notes: tuple[str, ...] = ()
    review_urls: tuple[str, ...] = ()


INDICATORS: tuple[CommunityIndicatorSpec, ...] = (
    CommunityIndicatorSpec(
        indicator_id="lorentzian_classification",
        display_name="Machine Learning: Lorentzian Classification",
        author="jdehorty",
        source_url="https://www.tradingview.com/script/WhBzgfDu-Machine-Learning-Lorentzian-Classification/",
        signal_family="machine_learning",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240", "1D"),
        open_source=True,
        editor_pick=True,
        popularity_uses=1_229_919,
        implementation_status="pending_exact_port",
        notes=(
            "Candidate is high priority because it publishes a backtest stream and explicit ANN/Lorentzian logic.",
            "Do not approximate the classifier in production; exact causal semantics must be verified first.",
        ),
        review_urls=(
            "https://www.tradingview.com/script/Pu38F2pB-Backtest-Adapter/",
            "https://www.reddit.com/r/TradingView/comments/15qr7mr",
        ),
    ),
    CommunityIndicatorSpec(
        indicator_id="ut_bot_alerts",
        display_name="UT Bot Alerts",
        author="QuantNomad",
        source_url="https://www.tradingview.com/script/n8ss8BID-UT-Bot-Alerts/",
        signal_family="atr_trend",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240"),
        open_source=True,
        popularity_uses=1_605_966,
        implementation_status="implemented_conceptual",
        notes=(
            "ATR trailing-stop crossover family. Benchmark only on confirmed bars.",
            "Community feedback is mixed and therefore cannot be used as a performance weight.",
        ),
        review_urls=(
            "https://www.reddit.com/r/algotrading/comments/zxh9vb/is_the_ut_bot_alerts_indicator_legit_or_does_it/",
            "https://www.reddit.com/r/TradingView/comments/12gsrc9/ut_bot_alerts_linreg_candles_heikin_ashi/",
        ),
    ),
    CommunityIndicatorSpec(
        indicator_id="squeeze_momentum_lazybear",
        display_name="Squeeze Momentum Indicator [LazyBear]",
        author="LazyBear",
        source_url="https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/",
        signal_family="volatility_momentum",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240", "1D"),
        open_source=True,
        popularity_uses=3_083_229,
        implementation_status="implemented_conceptual",
        notes=(
            "Compression/expansion detector using Bollinger/Keltner state plus linear-regression momentum.",
            "Original TradingView page documents a historical multiplier typo; STC uses the corrected published intent.",
        ),
        review_urls=(
            "https://www.reddit.com/r/TradingView/comments/1ccl46q",
            "https://www.reddit.com/r/TradingView/comments/1lqg6ra/best_tradingview_indicators_3_years_experience/",
        ),
    ),
    CommunityIndicatorSpec(
        indicator_id="wavetrend_crosses",
        display_name="WaveTrend with Crosses [LazyBear]",
        author="lonestar108 / LazyBear",
        source_url="https://www.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/",
        signal_family="momentum",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240"),
        open_source=True,
        popularity_uses=540_320,
        implementation_status="implemented_conceptual",
        notes=("Benchmark as a momentum timing component, not as a standalone probability model.",),
    ),
    CommunityIndicatorSpec(
        indicator_id="hull_suite",
        display_name="Hull Suite",
        author="InSilico",
        source_url="https://www.tradingview.com/script/hg92pFwS-Hull-Suite/",
        signal_family="trend",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240", "1D"),
        open_source=True,
        popularity_uses=635_066,
        implementation_status="implemented_conceptual",
        notes=("Benchmark HMA slope/trend state with confirmed-bar semantics.",),
        review_urls=("https://www.reddit.com/r/TradingView/comments/1jbq7f2/top_3_community_indicators_on_tradingview/",),
    ),
    CommunityIndicatorSpec(
        indicator_id="qqe_mod",
        display_name="QQE MOD",
        author="Mihkel00",
        source_url="https://www.tradingview.com/script/TpUW4muw-QQE-MOD/",
        signal_family="momentum",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240"),
        open_source=True,
        popularity_uses=406_909,
        implementation_status="pending_exact_port",
        notes=("Dual QQE agreement plus Bollinger-style zero-line confirmation.",),
    ),
    CommunityIndicatorSpec(
        indicator_id="optimized_trend_tracker",
        display_name="Optimized Trend Tracker",
        author="KivancOzbilgic",
        source_url="https://www.tradingview.com/script/zVhoDQME/",
        signal_family="trend",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240", "1D"),
        open_source=True,
        editor_pick=True,
        popularity_uses=575_019,
        implementation_status="pending_exact_port",
        notes=("Confirmed reversals are suitable for causal benchmarking; potential reversals must not be used.",),
        review_urls=("https://www.reddit.com/r/TradingView/comments/1lqg6ra/best_tradingview_indicators_3_years_experience/",),
    ),
    CommunityIndicatorSpec(
        indicator_id="smart_money_concepts_luxalgo",
        display_name="Smart Money Concepts [LuxAlgo]",
        author="LuxAlgo",
        source_url="https://www.tradingview.com/script/CnB3fSph-Smart-Money-Concepts-SMC-LuxAlgo/",
        signal_family="structure_liquidity",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("5", "15", "30", "60", "120", "240", "1D"),
        open_source=True,
        popularity_uses=4_903_394,
        implementation_status="native_proxy_only",
        notes=(
            "STC already contains BOS/CHoCH/order-block/FVG/liquidity families.",
            "Use as a cross-check benchmark before adding any extra weight to avoid double-counting the same evidence.",
        ),
    ),
    CommunityIndicatorSpec(
        indicator_id="williams_r_trend_exhaustion",
        display_name="%R Trend Exhaustion family",
        author="community",
        source_url="https://www.tradingview.com/scripts/search/%25R%20Trend%20Exhaustion/",
        signal_family="reversal",
        suitable_asset_classes=("forex", "crypto", "indices", "metals", "energy", "rates"),
        preferred_timeframes=("15", "30", "60", "120", "240", "1D"),
        open_source=False,
        implementation_status="discovery_only",
        notes=("Discovery candidate from community review; exact source/version must be verified before any benchmark.",),
        review_urls=("https://www.reddit.com/r/TradingView/comments/1jbq7f2/top_3_community_indicators_on_tradingview/",),
    ),
    CommunityIndicatorSpec(
        indicator_id="cm_williams_vix_fix",
        display_name="CM Williams Vix Fix family",
        author="ChrisMoody / community",
        source_url="https://www.tradingview.com/scripts/search/CM_Williams_Vix_Fix/",
        signal_family="volatility_reversal",
        suitable_asset_classes=("indices", "crypto", "metals"),
        preferred_timeframes=("15", "30", "60", "120", "240", "1D"),
        open_source=False,
        implementation_status="discovery_only",
        notes=("Potentially asset-specific; require symbol-level evidence before participation.",),
    ),
)


def indicator_by_id(indicator_id: str) -> CommunityIndicatorSpec:
    for spec in INDICATORS:
        if spec.indicator_id == indicator_id:
            return spec
    raise KeyError(indicator_id)


def eligible_indicators(
    asset_class: str,
    timeframe: str,
    *,
    implemented_only: bool = True,
) -> tuple[CommunityIndicatorSpec, ...]:
    allowed = {"implemented_conceptual", "native_proxy_only"}
    return tuple(
        spec
        for spec in INDICATORS
        if asset_class in spec.suitable_asset_classes
        and timeframe in spec.preferred_timeframes
        and (not implemented_only or spec.implementation_status in allowed)
    )


def catalog_summary() -> dict:
    return {
        "total": len(INDICATORS),
        "implemented_or_proxy": sum(
            1 for spec in INDICATORS
            if spec.implementation_status in {"implemented_conceptual", "native_proxy_only"}
        ),
        "pending_exact_port": sum(1 for spec in INDICATORS if spec.implementation_status == "pending_exact_port"),
        "discovery_only": sum(1 for spec in INDICATORS if spec.implementation_status == "discovery_only"),
        "rule": "Popularity/reviews prioritize research discovery only; they never become trading weights.",
    }
