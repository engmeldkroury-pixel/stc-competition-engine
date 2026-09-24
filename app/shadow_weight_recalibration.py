from __future__ import annotations

from dataclasses import dataclass
from math import exp
from statistics import fmean
from typing import Iterable


@dataclass(frozen=True)
class ShadowOutcome:
    observation_id: str
    symbol: str
    timeframe: str
    component_id: str
    result_r: float
    directional_hit: bool


@dataclass(frozen=True)
class FrozenOutcomeBatch:
    batch_id: str
    sealed: bool
    observations: tuple[ShadowOutcome, ...]


@dataclass(frozen=True)
class ComponentRecalibration:
    symbol: str
    timeframe: str
    component_id: str
    status: str
    observations: int
    wins: int
    hit_rate: float
    expectancy_r: float
    profit_factor: float
    max_drawdown_r: float
    prior_weight: float
    candidate_weight: float
    relative_change: float
    sample_confidence: float
    live_authority: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class RecalibratedProfile:
    symbol: str
    timeframe: str
    batch_id: str
    status: str
    components: tuple[ComponentRecalibration, ...]
    normalized_candidate_weights: dict[str, float]
    live_authority: bool
    notes: tuple[str, ...]


def _stats(rows: list[ShadowOutcome]) -> tuple[int, int, float, float, float, float]:
    if not rows:
        return 0, 0, 0.0, 0.0, 0.0, 0.0
    values=[float(x.result_r) for x in rows]
    wins=sum(value > 0 for value in values)
    hits=sum(bool(x.directional_hit) for x in rows)
    gains=sum(value for value in values if value > 0)
    losses=-sum(value for value in values if value < 0)
    pf=(gains / losses) if losses > 1e-12 else (99.0 if gains > 0 else 0.0)
    equity=0.0
    peak=0.0
    max_dd=0.0
    for value in values:
        equity += value
        peak=max(peak,equity)
        max_dd=max(max_dd,peak-equity)
    return len(rows), wins, hits/len(rows), fmean(values), pf, max_dd


def _deduplicate(rows: Iterable[ShadowOutcome]) -> tuple[ShadowOutcome, ...]:
    seen: set[str] = set()
    out: list[ShadowOutcome] = []
    for row in rows:
        key=str(row.observation_id)
        if not key:
            raise ValueError("shadow outcome requires observation_id")
        if key in seen:
            raise ValueError(f"duplicate shadow observation_id: {key}")
        seen.add(key)
        out.append(row)
    return tuple(out)


def recalibrate_component(
    *,
    symbol: str,
    timeframe: str,
    component_id: str,
    prior_weight: float,
    batch: FrozenOutcomeBatch,
    min_observations: int = 30,
    max_relative_step: float = 0.25,
) -> ComponentRecalibration:
    """Create a research-only candidate weight from a sealed shadow batch.

    The function deliberately refuses to learn from a still-growing window.
    It also caps each recalibration step so one unusually strong/weak batch
    cannot dominate the historical OOS/forward/frozen evidence.
    """
    if not batch.sealed:
        raise ValueError("recalibration requires a sealed frozen outcome batch")
    if min_observations < 10:
        raise ValueError("min_observations must be at least 10")
    if not 0.0 < max_relative_step <= 0.50:
        raise ValueError("max_relative_step must be in (0, 0.50]")
    prior=max(0.0,float(prior_weight))

    all_rows=_deduplicate(batch.observations)
    rows=[
        row for row in all_rows
        if row.symbol == symbol
        and row.timeframe == timeframe
        and row.component_id == component_id
    ]
    n,wins,hit_rate,expectancy,pf,max_dd=_stats(rows)
    if n < min_observations:
        return ComponentRecalibration(
            symbol=symbol,
            timeframe=timeframe,
            component_id=component_id,
            status="WAIT_FOR_FROZEN_SAMPLE",
            observations=n,
            wins=wins,
            hit_rate=hit_rate,
            expectancy_r=expectancy,
            profit_factor=pf,
            max_drawdown_r=max_dd,
            prior_weight=prior,
            candidate_weight=prior,
            relative_change=0.0,
            sample_confidence=1.0-exp(-n/max(float(min_observations),1.0)),
            live_authority=False,
            notes=(
                "No weight change before the minimum sealed shadow sample.",
                "Candidate weights are research-only and require a later validation/promotion step.",
            ),
        )

    confidence=1.0-exp(-n/40.0)
    # Directional hit rate is deliberately shrunk toward 50%.
    shrunk_hit=(hit_rate*n + 0.50*40.0)/(n+40.0)
    hit_factor=max(0.70,min(1.20,0.70+shrunk_hit))
    expectancy_factor=max(0.55,min(1.25,1.0+expectancy*0.35))
    pf_factor=max(0.60,min(1.20,0.85+min(max(pf,0.0),2.5)*0.14))
    drawdown_factor=max(0.60,1.0-min(max_dd,12.0)*0.025)

    empirical_factor=hit_factor*expectancy_factor*pf_factor*drawdown_factor
    # Negative expectancy or sub-1 PF cannot increase participation.
    if expectancy <= 0.0 or pf < 1.0:
        empirical_factor=min(empirical_factor,0.85)
    target=prior*empirical_factor
    blended=prior*(1.0-confidence)+target*confidence

    low=prior*(1.0-max_relative_step)
    high=prior*(1.0+max_relative_step)
    candidate=max(0.0,min(high,max(low,blended)))
    relative=0.0 if prior <= 1e-12 else (candidate-prior)/prior
    status="RESEARCH_WEIGHT_UP" if candidate > prior+1e-12 else "RESEARCH_WEIGHT_DOWN" if candidate < prior-1e-12 else "RESEARCH_WEIGHT_UNCHANGED"
    return ComponentRecalibration(
        symbol=symbol,
        timeframe=timeframe,
        component_id=component_id,
        status=status,
        observations=n,
        wins=wins,
        hit_rate=hit_rate,
        expectancy_r=expectancy,
        profit_factor=pf,
        max_drawdown_r=max_dd,
        prior_weight=prior,
        candidate_weight=candidate,
        relative_change=relative,
        sample_confidence=confidence,
        live_authority=False,
        notes=(
            "Weight update uses one sealed shadow batch and is capped per recalibration step.",
            "This is a research candidate weight, not live authority or a win probability.",
        ),
    )


def recalibrate_profile(
    *,
    symbol: str,
    timeframe: str,
    prior_weights: dict[str, float],
    batch: FrozenOutcomeBatch,
    min_observations: int = 30,
    max_relative_step: float = 0.25,
) -> RecalibratedProfile:
    """Recalibrate and normalize a symbol/timeframe research profile.

    Only exact matching component observations participate. Components without
    enough new sealed evidence retain their prior weight.
    """
    if not prior_weights:
        return RecalibratedProfile(
            symbol=symbol,
            timeframe=timeframe,
            batch_id=batch.batch_id,
            status="NO_PRIOR_COMPONENTS",
            components=(),
            normalized_candidate_weights={},
            live_authority=False,
            notes=("No research weights exist for this symbol/timeframe.",),
        )

    rows=tuple(
        recalibrate_component(
            symbol=symbol,
            timeframe=timeframe,
            component_id=component_id,
            prior_weight=weight,
            batch=batch,
            min_observations=min_observations,
            max_relative_step=max_relative_step,
        )
        for component_id,weight in sorted(prior_weights.items())
    )
    raw={row.component_id:max(0.0,row.candidate_weight) for row in rows}
    total=sum(raw.values())
    normalized=(
        {key:value/total for key,value in raw.items()}
        if total > 1e-12
        else {key:0.0 for key in raw}
    )
    changed=any(abs(row.candidate_weight-row.prior_weight)>1e-12 for row in rows)
    return RecalibratedProfile(
        symbol=symbol,
        timeframe=timeframe,
        batch_id=batch.batch_id,
        status="RESEARCH_PROFILE_RECALIBRATED" if changed else "RESEARCH_PROFILE_UNCHANGED",
        components=rows,
        normalized_candidate_weights=normalized,
        live_authority=False,
        notes=(
            "Weights are symbol/timeframe specific and use only sealed shadow evidence.",
            "Recalibration does not write live weights; explicit validation and owner promotion remain separate.",
        ),
    )
