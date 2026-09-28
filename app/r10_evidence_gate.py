"""Fail-closed evidence gate for R10 frozen shadow observations.

Research governance only. A positive result means "eligible for human review", never
live promotion, broker authority or a calibrated win probability.
"""
from __future__ import annotations

from collections import defaultdict
import math
from typing import Any, Iterable


def _finite(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite_number_required")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("finite_number_required")
    return value


def _xorshift(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        yield (state & 0xFFFFFFFF) / 2**32


def _day_bootstrap_ci(day_values: dict[str, list[float]], *, samples: int = 5000, seed: int = 17092026) -> tuple[float, float, float]:
    days = sorted(day_values)
    if not days:
        raise ValueError("no_settled_days")
    rng = _xorshift(seed)
    means=[]
    for _ in range(samples):
        vals=[]
        for _ in days:
            picked=days[min(int(next(rng)*len(days)),len(days)-1)]
            vals.extend(day_values[picked])
        means.append(sum(vals)/len(vals))
    means.sort()
    lo=means[int((samples-1)*0.025)]
    hi=means[int((samples-1)*0.975)]
    p_nonpositive=sum(value <= 0 for value in means)/samples
    return lo,hi,p_nonpositive


def assess_forward_evidence(
    rows: Iterable[dict[str, Any]], *, expected_protocol_sha256: str,
    min_settled: int, min_days: int, min_symbols: int,
) -> dict[str, Any]:
    """Validate and summarize settled forward observations without auto-promotion."""
    seen=set(); settled=[]; costs=set()
    for row in rows:
        if row.get("protocol_sha256") != expected_protocol_sha256:
            raise ValueError("protocol_sha_mismatch")
        cost_bps=_finite(row.get("cost_bps"))
        costs.add(cost_bps)
        if len(costs) > 1:
            raise ValueError("mixed_cost_scenarios")
        key=(row.get("symbol"),row.get("source_open_utc"),cost_bps)
        if key in seen:
            raise ValueError("duplicate_observation")
        seen.add(key)
        if row.get("status") != "SETTLED":
            continue
        net_r=_finite(row.get("net_r"))
        symbol=row.get("symbol"); day=row.get("day"); source=row.get("source_open_utc")
        if not isinstance(symbol,str) or not symbol or not isinstance(day,str) or not day or not isinstance(source,str) or not source:
            raise ValueError("settled_identity_required")
        settled.append({"symbol":symbol,"day":day,"source_open_utc":source,"net_r":net_r})

    settled.sort(key=lambda x: (x["source_open_utc"], x["symbol"]))
    symbols=sorted({x["symbol"] for x in settled})
    days=sorted({x["day"] for x in settled})
    gross_profit=sum(max(x["net_r"],0.0) for x in settled)
    gross_loss=-sum(min(x["net_r"],0.0) for x in settled)
    total=sum(x["net_r"] for x in settled)
    mean=total/len(settled) if settled else None
    pf=(gross_profit/gross_loss) if gross_loss else (math.inf if gross_profit else None)
    equity=peak=max_drawdown=0.0
    for x in settled:
        equity += x["net_r"]
        peak=max(peak,equity)
        max_drawdown=max(max_drawdown,peak-equity)
    day_values=defaultdict(list)
    for x in settled:
        day_values[x["day"]].append(x["net_r"])
    day_totals={d:sum(v) for d,v in day_values.items()}
    largest_abs_day=max((abs(v) for v in day_totals.values()), default=0.0)
    total_abs_days=sum(abs(v) for v in day_totals.values())
    concentration=largest_abs_day/total_abs_days if total_abs_days else None

    enough=len(settled)>=min_settled and len(days)>=min_days and len(symbols)>=min_symbols
    ci_lo=ci_hi=p_nonpositive=None
    if enough:
        ci_lo,ci_hi,p_nonpositive=_day_bootstrap_ci(dict(day_values))

    reasons=[]
    if len(settled)<min_settled: reasons.append("insufficient_settled")
    if len(days)<min_days: reasons.append("insufficient_days")
    if len(symbols)<min_symbols: reasons.append("insufficient_symbols")
    if enough:
        if mean is None or mean <= 0: reasons.append("nonpositive_mean")
        if pf is None or pf <= 1: reasons.append("profit_factor_not_above_one")
        if ci_lo is None or ci_lo <= 0: reasons.append("cluster_ci_crosses_zero")
        if concentration is not None and concentration > 0.50: reasons.append("day_concentration_above_half")

    status="INSUFFICIENT_EVIDENCE" if not enough else ("CANDIDATE_FOR_HUMAN_REVIEW" if not reasons else "NOT_SUPPORTED")
    return {
        "status":status,
        "settled":len(settled),"days":len(days),"symbols":symbols,
        "cost_bps":next(iter(costs)) if costs else None,
        "mean_r":mean,"profit_factor":pf,"max_drawdown_r":max_drawdown,
        "day_concentration":concentration,"cluster_ci95":[ci_lo,ci_hi],
        "bootstrap_p_mean_le_zero":p_nonpositive,"reasons":reasons,
        "live_authorized":False,"auto_promotion":False,
    }
