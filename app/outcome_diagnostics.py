"""Research readiness and outcome-independent cohort diagnostics, never promotion."""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import timedelta
from .outcome_attribution import THRESHOLDS, VERSION, utc


def nonoverlapping_entries(outcomes: list[dict]) -> list[dict]:
    """Earliest entry per instrument wins; block the full declared horizon.

    Do not use the winning/losing result, actual exit, or completeness to select.
    Different timeframes on the same instrument share an occupancy window.
    Cross-instrument correlation and entry-availability selection remain.
    """
    selected, free = [], {}
    entered = [row for row in outcomes if row.get('entry') is not None]
    for row in sorted(entered, key=lambda r: (utc(r['entry']['time']), r['event_id'])):
        key = (row['competition_id'], row['symbol'])
        now = utc(row['entry']['time'])
        bars, minutes = row['horizon_bars'], row['timeframe_minutes']
        if type(bars) is not int or type(minutes) is not int or min(bars, minutes) < 1:
            raise ValueError('invalid_horizon')
        if key in free and now < free[key]:
            continue
        selected.append(row)
        free[key] = now + timedelta(minutes=bars * minutes)
    return selected


def _summary(rows: list[dict]) -> dict:
    paired, rebounds, entries = 0, 0, 0
    for row in rows:
        t = row.get('thresholds', {})
        first, final = t.get('1.0', {}), t.get('2.5', {})
        stopped = final.get('state') in {'STOP_FIRST', 'AMBIGUOUS_STOP_FIRST'}
        paired += int(first.get('state') == 'TARGET_FIRST' and stopped)
        rebounds += int(stopped and final.get('post_stop_target_touched') is True)
        entries += int(row.get('entry') is not None)
    return {'observations': len(rows), 'entered_observations': entries,
            'status_counts': dict(sorted(Counter(r['status'] for r in rows).items())),
            'quadrant_counts': dict(sorted(Counter(r['quadrant'] for r in rows).items())),
            'provenance_counts': dict(sorted(Counter(r['provenance'] for r in rows).items())),
            'same_path_1r_target_then_stop_before_2p5r': paired,
            'same_path_stop_then_later_2p5r_touch': rebounds}


def diagnostic_report(report: dict) -> dict:
    if report.get('version') != VERSION or report.get('research_only') is not True or report.get('live_authorized') is not False or report.get('execution') != 'none':
        raise ValueError('invalid_research_boundary')
    rows = report['outcomes']
    ids = [row['event_id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate_observations')
    selected = nonoverlapping_entries(rows)
    groups = defaultdict(list)
    for row in rows:
        groups[row['symbol']].append(row)
    cost_sensitivity = {}
    # Explicitly conditional on settlement, never an unbiased expectancy ranking.
    for r in THRESHOLDS:
        settled = [(row['thresholds'][str(r)]['net_plan_r'], row['cost_r_proxy'])
                   for row in rows if row.get('thresholds', {}).get(str(r), {}).get('net_plan_r') is not None]
        cost_sensitivity[str(r)] = {
            'settled_count': len(settled),
            'settled_only_mean_by_round_trip_cost_r': {
                str(c): sum(net + old - c for net, old in settled) / len(settled) if settled else None
                for c in (0.0, 0.02, 0.05, 0.1)},
            'unbiased_expectancy': False,
        }
    return {'schema': 'stc-outcome-diagnostics-v1', 'as_of': report['as_of'],
            'research_only': True, 'execution': 'none', 'live_promotion_allowed': False,
            'calibrated_win_probability': None, 'preferred_exit_policy': None,
            'source_rows': report['source_rows'], 'source_scope': report['source_scope'],
            'overall': _summary(rows), 'per_symbol': {s: _summary(g) for s,g in sorted(groups.items())},
            'nonoverlapping_entered_cohort': _summary(selected),
            'cohort_method': 'earliest entry per competition/instrument, full-horizon blocking across timeframes, no outcome-dependent selection',
            'settled_cost_sensitivity': cost_sensitivity,
            'blockers': ['missing contiguous price paths', 'legacy geometry is not an original frozen plan',
                         'unknown historical gate quadrants', 'no untouched out-of-sample exit comparison',
                         'no fixed-horizon mark for unresolved exits', 'proxy costs are not observed spread/fees'],
            'limitations': ['Non-overlap does not remove cross-asset correlation or entry-selection effects.',
                            'Same-path paired counts are descriptive historical hypotheses, not independent executed trades.',
                            'Cost sensitivity changes the fee proxy only; it does not simulate spread-dependent trigger prices.']}
