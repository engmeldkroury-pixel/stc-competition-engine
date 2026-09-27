"""Paired single-TP exit research on an outcome-independent fixed-horizon cohort.

No best policy, probability, account write or live promotion is returned.
Complete paths permit terminal mark-to-market, not a fictitious broker fill.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .outcome_attribution import THRESHOLDS, evaluate_outcome, iso, number, utc
from .outcome_dataset import clean_bar, series_key, validate_dataset


def evaluate_exit_experiment(seed: dict, bars: list[dict], *, as_of: datetime,
                             horizon_bars: int = 32, cost_r: float = .02) -> dict:
    r = evaluate_outcome(seed, bars, as_of=as_of, horizon_bars=horizon_bars, cost_r=cost_r)
    r['paired_valuations'] = {}
    if r['entry'] is None:
        return r
    sign = 1 if seed['side'] == 'LONG' else -1
    entry, risk = r['entry']['price'], seed['plan_risk']
    terminal = utc(r['entry']['time']) + timedelta(minutes=(horizon_bars-1)*seed['timeframe_minutes'])
    terminal_close = None
    if r['status'] == 'COMPLETE':
        for raw in bars:
            b = clean_bar(raw)
            if series_key(b) == series_key(seed) and utc(b['time']) == terminal:
                terminal_close = b['close']
        if terminal_close is None:
            raise ValueError('terminal_bar_missing')
    for target_r in THRESHOLDS:
        key = str(target_r)
        t = r['thresholds'][key]
        val = {'kind': 'UNKNOWN_PATH', 'lower_net_plan_r': None, 'upper_net_plan_r': None}
        if t['state'] == 'AMBIGUOUS_STOP_FIRST':
            upper = sign*(t['target_price']-entry)/risk - cost_r
            val.update(kind='AMBIGUOUS_EXIT_BOUNDS', lower_net_plan_r=t['net_plan_r'], upper_net_plan_r=upper)
        elif t['net_plan_r'] is not None:
            val.update(kind='OBSERVED_OHLC_EXIT_MODEL', lower_net_plan_r=t['net_plan_r'], upper_net_plan_r=t['net_plan_r'])
        elif terminal_close is not None:
            mark = sign*(terminal_close-entry)/risk - cost_r
            val.update(kind='FIXED_HORIZON_CLOSE_MARK_NOT_EXECUTION', lower_net_plan_r=mark, upper_net_plan_r=mark,
                       mark_price=terminal_close, mark_at=iso(terminal+timedelta(minutes=seed['timeframe_minutes'])))
        r['paired_valuations'][key] = val
    r['all_policies_valued'] = all(v['lower_net_plan_r'] is not None for v in r['paired_valuations'].values())
    return r


def nonoverlapping_cohort(rows: list[dict]) -> list[dict]:
    """Selection ignores exit, profitability, ambiguity and path completeness."""
    chosen, busy, ids = [], {}, set()
    for row in rows:
        if row['event_id'] in ids:
            raise ValueError('duplicate_observations')
        ids.add(row['event_id'])
    for row in sorted((r for r in rows if r['entry'] is not None), key=lambda r: (utc(r['entry']['time']), r['event_id'])):
        key, opened = (row['competition_id'], row['symbol']), utc(row['entry']['time'])
        if opened < busy.get(key, opened):
            continue
        minutes, horizon = row['timeframe_minutes'], row['horizon_bars']
        if type(minutes) is not int or type(horizon) is not int or min(minutes,horizon) < 1:
            raise ValueError('invalid_horizon')
        busy[key] = opened + timedelta(minutes=minutes*horizon)
        chosen.append(row)
    return chosen


def _paired_summary(rows: list[dict]) -> dict:
    eligible = [r for r in rows if r.get('all_policies_valued') is True]
    policies = {}
    for k in map(str, THRESHOLDS):
        lower = [r['paired_valuations'][k]['lower_net_plan_r'] for r in eligible]
        upper = [r['paired_valuations'][k]['upper_net_plan_r'] for r in eligible]
        policies[k] = dict(common_n=len(eligible),
                           mean_lower_net_plan_r=sum(lower)/len(lower) if lower else None,
                           mean_upper_net_plan_r=sum(upper)/len(upper) if upper else None,
                           valuation_kinds=dict(Counter(r['paired_valuations'][k]['kind'] for r in eligible)))
    # Cost sensitivity always uses the exact same eligible IDs across policies.
    costs = {}
    for c in (.0, .02, .05, .10):
        costs[str(c)] = {k: {
            'common_n': len(eligible),
            'mean_lower_net_plan_r': sum(r['paired_valuations'][k]['lower_net_plan_r']+r['cost_r_proxy']-c for r in eligible)/len(eligible) if eligible else None,
            'mean_upper_net_plan_r': sum(r['paired_valuations'][k]['upper_net_plan_r']+r['cost_r_proxy']-c for r in eligible)/len(eligible) if eligible else None,
        } for k in map(str, THRESHOLDS)}
    return dict(selected_n=len(rows), common_valued_n=len(eligible), unknown_path_n=len(rows)-len(eligible),
                policies=policies, common_event_ids=[r['event_id'] for r in eligible],
                proxy_cost_sensitivity=costs, unaffected_by_settlement_denominator=True,
                unbiased_population_expectancy=False)


def audit_exit_policies(dataset: dict, *, horizon_bars: int = 32, cost_r: float = .02) -> dict:
    validate_dataset(dataset)
    cost_r = number(cost_r)
    if type(horizon_bars) is not int or not 0 < horizon_bars <= 10000 or cost_r < 0:
        raise ValueError('invalid_experiment_configuration')
    groups = defaultdict(list)
    for b in dataset['bars']:
        groups[series_key(b)].append(b)
    results = [evaluate_exit_experiment(s, groups[series_key(s)], as_of=utc(dataset['as_of']),
                                      horizon_bars=horizon_bars,cost_r=cost_r) for s in dataset['seeds']]
    cohort = nonoverlapping_cohort(results)
    breakdown = defaultdict(list)
    for r in cohort:
        key = '|'.join(map(str, (r['competition_id'],r['symbol'],r['timeframe_minutes'],r['provenance'],r['quadrant'])))
        breakdown[key].append(r)
    return dict(schema='stc-paired-exit-audit-v1', dataset_sha256=dataset['dataset_sha256'],
                research_only=True, execution='none', live_promotion_allowed=False,
                calibrated_win_probability=None, preferred_policy=None,
                as_of=dataset['as_of'], horizon_bars=horizon_bars, cost_r_proxy=cost_r,
                hypotheses=len(results), entered=sum(r['entry'] is not None for r in results),
                status_counts=dict(Counter(r['status'] for r in results)),
                provenance_counts=dict(Counter(r['provenance'] for r in results)),
                nonoverlapping_cohort=_paired_summary(cohort),
                by_competition_symbol_timeframe_provenance_quadrant={k:_paired_summary(v) for k,v in sorted(breakdown.items())},
                selected_event_ids=[r['event_id'] for r in cohort], outcomes=results,
                limitations=['Historical exploratory data, not an untouched out-of-sample test.',
                             'OHLC-based gap/trigger model is not actual broker execution.',
                             'Cost sensitivity is a fee proxy; bid/ask triggering and slippage still need evidence.',
                             'No interpolation or assumed market-closure gap filling.',
                             'Common-cohort comparison removes differing policy denominators, not missingness bias or cross-asset dependence.',
                             'Original R8 seed geometry is unchanged; adaptive stops require a separately frozen experiment.'])
