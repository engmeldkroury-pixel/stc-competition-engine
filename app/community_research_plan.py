from __future__ import annotations

from dataclasses import dataclass

from .asset_classification import strategy_asset_class
from .community_indicator_catalog import INDICATORS, eligible_indicators
from .research_plan import RESEARCH_TIMEFRAMES, competition_research_symbols


@dataclass(frozen=True)
class CommunityResearchExperiment:
    scope: str
    symbol: str
    asset_class: str
    timeframe: str
    indicator_id: str
    implementation_status: str
    validation: str = "train_test_forward_standardized_no_lookahead"


def community_research_experiments(
    *,
    lab_symbols: tuple[str, ...] = (),
    include_pending: bool = True,
) -> tuple[CommunityResearchExperiment, ...]:
    rows: list[CommunityResearchExperiment] = []

    universes: list[tuple[str, tuple[str, ...]]] = [
        (competition_id, symbols)
        for competition_id, symbols in competition_research_symbols().items()
    ]
    if lab_symbols:
        universes.append(("general-lab", tuple(dict.fromkeys(lab_symbols))))

    for scope, symbols in universes:
        for symbol in symbols:
            asset_class = strategy_asset_class(symbol)
            for timeframe in RESEARCH_TIMEFRAMES:
                specs = (
                    tuple(
                        spec
                        for spec in INDICATORS
                        if asset_class in spec.suitable_asset_classes
                        and timeframe in spec.preferred_timeframes
                    )
                    if include_pending
                    else eligible_indicators(asset_class, timeframe, implemented_only=True)
                )
                for spec in specs:
                    rows.append(
                        CommunityResearchExperiment(
                            scope=scope,
                            symbol=symbol,
                            asset_class=asset_class,
                            timeframe=timeframe,
                            indicator_id=spec.indicator_id,
                            implementation_status=spec.implementation_status,
                        )
                    )
    return tuple(rows)


def community_research_plan_summary(*, lab_symbols: tuple[str, ...] = ()) -> dict:
    rows = community_research_experiments(lab_symbols=lab_symbols, include_pending=True)
    implemented = [
        row
        for row in rows
        if row.implementation_status in {"implemented_conceptual", "native_proxy_only"}
    ]
    by_scope: dict[str, int] = {}
    by_indicator: dict[str, int] = {}
    for row in rows:
        by_scope[row.scope] = by_scope.get(row.scope, 0) + 1
        by_indicator[row.indicator_id] = by_indicator.get(row.indicator_id, 0) + 1
    return {
        "symbols": sum(len(symbols) for symbols in competition_research_symbols().values()) + len(set(lab_symbols)),
        "timeframes": list(RESEARCH_TIMEFRAMES),
        "experiments_total": len(rows),
        "experiments_currently_implementable": len(implemented),
        "by_scope": by_scope,
        "by_indicator": by_indicator,
        "general_lab_rule": (
            "Any General Lab symbol is routed through the same per-symbol/timeframe matrix; "
            "it does not inherit weights from a different asset automatically."
        ),
    }
