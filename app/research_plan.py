from __future__ import annotations

from dataclasses import dataclass

from .asset_classification import strategy_asset_class
from .competition_profiles import AMP_CORE_FEED_SYMBOLS, CAPITAL_AFRICA_LIMITS
from .strategy_lab import candidate_strategies


RESEARCH_TIMEFRAMES = ("5", "15", "30", "60", "120", "240", "1D")


@dataclass(frozen=True)
class ResearchExperiment:
    competition_id: str
    symbol: str
    asset_class: str
    timeframe: str
    strategy_id: str
    min_bars: int = 900
    feature_warmup_bars: int = 260
    validation: str = "train_test_forward_walkforward"


def competition_research_symbols() -> dict[str, tuple[str, ...]]:
    return {
        "capital-africa-sep-2026": tuple(CAPITAL_AFRICA_LIMITS),
        "amp-futures-sep-2026": tuple(AMP_CORE_FEED_SYMBOLS),
    }


def research_experiments() -> tuple[ResearchExperiment, ...]:
    out: list[ResearchExperiment] = []
    for competition_id, symbols in competition_research_symbols().items():
        for symbol in symbols:
            asset_class = strategy_asset_class(symbol)
            for timeframe in RESEARCH_TIMEFRAMES:
                for strategy in candidate_strategies(asset_class, timeframe):
                    out.append(
                        ResearchExperiment(
                            competition_id=competition_id,
                            symbol=symbol,
                            asset_class=asset_class,
                            timeframe=timeframe,
                            strategy_id=strategy.strategy_id,
                        )
                    )
    return tuple(out)


def experiments_for_symbol(symbol: str) -> tuple[ResearchExperiment, ...]:
    return tuple(x for x in research_experiments() if x.symbol == symbol)


def research_plan_summary() -> dict:
    experiments = research_experiments()
    by_competition: dict[str, int] = {}
    by_asset: dict[str, int] = {}
    by_timeframe: dict[str, int] = {}
    by_strategy: dict[str, int] = {}
    for item in experiments:
        by_competition[item.competition_id] = by_competition.get(item.competition_id, 0) + 1
        by_asset[item.asset_class] = by_asset.get(item.asset_class, 0) + 1
        by_timeframe[item.timeframe] = by_timeframe.get(item.timeframe, 0) + 1
        by_strategy[item.strategy_id] = by_strategy.get(item.strategy_id, 0) + 1
    return {
        "symbols": sum(len(x) for x in competition_research_symbols().values()),
        "experiments": len(experiments),
        "timeframes": list(RESEARCH_TIMEFRAMES),
        "by_competition": by_competition,
        "by_asset_class": by_asset,
        "by_timeframe": by_timeframe,
        "by_strategy": by_strategy,
        "validation": "train/test/forward with no-lookahead strategy selection",
    }
