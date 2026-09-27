"""Read-only research dataset. Receipts prove consistency, not authenticity.

The caller must obtain the inbox through an authenticated, read-only channel.
Raw payloads, database credentials, account values and broker operations are not
part of the normalized export. Unknown gaps are never treated as market closure.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib
from typing import Iterable

from .approval import timeframe_duration_minutes
from .cloud_approval import _validate_record
from .trade_plan import deterministic_plan_id
from .outcome_attribution import build_outcome_seed, canonical, iso, number, utc, validate_seed

SCHEMA = 'stc-outcome-dataset-v1'
OHLC = ('open', 'high', 'low', 'close')
SEED_KEYS = ('version', 'event_id', 'competition_id', 'symbol', 'timeframe_minutes',
             'side', 'source_open', 'available_at', 'expires_at', 'entry_min', 'entry_max',
             'plan_mid', 'stop', 'plan_risk', 'quadrant', 'failed_gates',
             'failed_gates_known', 'provenance', 'research_only', 'live_authorized',
             'execution', 'seed_sha256')


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def series_key(row: dict) -> tuple[str, str, int]:
    competition, symbol, minutes = (row.get(k) for k in ('competition_id', 'symbol', 'timeframe_minutes'))
    if not isinstance(competition, str) or not competition or not isinstance(symbol, str) or ':' not in symbol:
        raise ValueError('invalid_series_identity')
    if type(minutes) is not int or not 0 < minutes <= 44640:
        raise ValueError('invalid_timeframe')
    return competition, symbol, minutes


def clean_bar(row: dict) -> dict:
    series_key(row)
    b = {k: row[k] for k in ('competition_id', 'symbol', 'timeframe_minutes')}
    b['time'] = iso(utc(row['time']))
    b.update({k: number(row[k], positive=True) for k in OHLC})
    if b['high'] < max(b['open'], b['low'], b['close']) or b['low'] > min(b['open'], b['high'], b['close']):
        raise ValueError('invalid_ohlc')
    return b


def prepare_dataset(inbox: dict, *, as_of: datetime) -> dict:
    """Freeze normalized source before computing performance, with atomic rows.

    Quarantine conflicting events AND conflicting OHLC at the same series/time.
    A corrupted seed cannot contribute an apparently clean bar to other trades.
    Source bar receipt identity, envelope prices/times, seed hash and seed/source
    semantics are checked before any component is admitted.
    """
    as_of = utc(as_of)
    if inbox.get('ok') is not True or not isinstance(inbox.get('events'), list):
        raise ValueError('invalid_inbox_contract')
    source_hash = digest(inbox)  # Reject an entire non-canonical (NaN/Inf) snapshot.
    versions, errors, entries = defaultdict(list), Counter(), []
    plans = []
    duplicates = 0
    for row in inbox['events']:
        if not isinstance(row, dict):
            errors['invalid_row'] += 1
        else:
            versions[str(row.get('event_id', ''))].append(row)
    for event_id, rows in sorted(versions.items()):
        try:
            if len({digest(row) for row in rows}) != 1:
                errors['conflicting_event_duplicates'] += len(rows)
                continue
            duplicates += len(rows) - 1
            result, receipt, payload = _validate_record(rows[0])
            d = result['decision']
            if d.get('action') != 'signal_created':
                errors['non_signal_event'] += 1
                continue
            minutes = timeframe_duration_minutes(str(payload.get('timeframe', '')))
            b = clean_bar({**payload, 'timeframe_minutes': minutes})
            if utc(b['time']) + timedelta(minutes=minutes) > as_of:
                errors['unclosed_source_bar'] += 1
                continue
            signal, envelope = d['signal'], d['approval_envelope']
            signal_id = 'bridge-' + hashlib.sha256(event_id.encode()).hexdigest()[:32]
            if signal.get('signal_id') != signal_id or receipt.get('signal_id') != signal_id:
                raise ValueError('signal_identity_mismatch')
            if any(e.get(k) != payload.get(k) for e in (signal, envelope) for k in ('competition_id', 'symbol')):
                raise ValueError('target_identity_mismatch')
            lo, ref, hi = (number(envelope[k], positive=True) for k in ('entry_min', 'reference_price', 'entry_max'))
            if not lo <= ref <= hi or ref != b['close']:
                raise ValueError('invalid_price_envelope')
            issued, expires = utc(envelope['issued_at']), utc(envelope['valid_until'])
            if expires <= issued or issued > as_of:
                raise ValueError('invalid_decision_window')
            seed = d.get('research_outcome_seed')
            if seed is not None:
                validate_seed(seed)
                if set(seed) != set(SEED_KEYS):
                    raise ValueError('unsupported_seed_schema')
                expected = build_outcome_seed(event_id, payload, signal, envelope)
                if expected is None or canonical(seed) != canonical(expected):
                    raise ValueError('frozen_seed_source_mismatch')
            else:
                seed = build_outcome_seed(event_id, payload, signal, envelope,
                                          provenance='LEGACY_RECONSTRUCTED_GEOMETRY')
            if seed is not None:
                validate_seed(seed)
            plan = d.get('locked_trade_plan')
            if plan is not None:
                if plan.get('levels_locked') is not True or plan.get('execution') != 'manual_only':
                    raise ValueError('invalid_plan_boundary')
                if plan.get('source_event_id') != event_id or plan.get('source_signal_id') != signal_id:
                    raise ValueError('invalid_plan_source')
                if any(plan.get(k) != payload[k] for k in ('competition_id','symbol')):
                    raise ValueError('invalid_plan_target')
                if plan.get('plan_id') != deterministic_plan_id(event_id,signal_id,plan.get('rule_version')):
                    raise ValueError('invalid_plan_identity')
                if plan.get('direction') != signal.get('recommendation') or plan.get('direction') not in ('LONG','SHORT'):
                    raise ValueError('invalid_plan_direction')
                pl = {k: plan[k] for k in ('plan_id','competition_id','symbol','source_event_id','source_signal_id','direction','rule_version')}
                pl.update({k: number(plan[k], positive=True) for k in ('entry_min','entry_max','entry_mid','initial_stop','target1','target2','risk_per_unit')})
                if pl['entry_min'] != lo or pl['entry_max'] != hi or not lo <= pl['entry_mid'] <= hi:
                    raise ValueError('invalid_plan_envelope')
                sign = 1 if pl['direction']=='LONG' else -1
                if sign*(pl['entry_min']-pl['initial_stop']) <= 0 or sign*(pl['entry_max']-pl['initial_stop']) <= 0 or sign*(pl['target1']-pl['entry_mid']) <= 0 or sign*(pl['target2']-pl['target1']) <= 0:
                    raise ValueError('invalid_plan_geometry')
                if utc(plan['valid_until']) != expires:
                    raise ValueError('invalid_plan_expiry')
                pl.update(issued_at=iso(issued),expires_at=iso(expires),source_open=b['time'],execution='none')
                plans.append(pl)
            entries.append((b, seed, {k: receipt[k] for k in ('event_id', 'receipt_id', 'payload_sha256')}))
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
            # Do not reflect raw source exception text into public logs/artifacts.
            errors['invalid_source_record'] += 1
    grouped = defaultdict(list)
    for b, s, receipt in entries:
        grouped[(*series_key(b), b['time'])].append((b, s, receipt))
    bars, seeds, receipts = [], [], []
    valid_event_ids = set()
    for _, group in sorted(grouped.items()):
        if len({canonical(x[0]) for x in group}) != 1:
            errors['conflicting_ohlc_records'] += len(group)
            continue
        bars.append(group[0][0])
        for _, s, r in group:
            if s is not None:
                seeds.append(s)
            receipts.append(r)
            valid_event_ids.add(r['event_id'])
    data = dict(schema=SCHEMA, as_of=iso(as_of), research_only=True,
                execution='none', live_authorized=False,
                source_scope='VALIDATED_SIGNAL_BARS_NOT_COMPLETE_MARKET_OR_BROKER_HISTORY',
                raw_inbox_sha256=source_hash, source_rows=len(inbox['events']),
                exact_duplicate_rows_ignored=duplicates, quarantine_counts=dict(sorted(errors.items())),
                bars=bars, seeds=sorted(seeds, key=lambda s: (s['available_at'], s['event_id'])),
                receipt_proofs=receipts, original_plans=[p for p in plans if p['source_event_id'] in valid_event_ids])
    data['dataset_sha256'] = digest(data)
    return data


def validate_dataset(data: dict) -> None:
    if data.get('schema') != SCHEMA or data.get('research_only') is not True or data.get('live_authorized') is not False or data.get('execution') != 'none':
        raise ValueError('invalid_research_boundary')
    if digest({k: v for k, v in data.items() if k != 'dataset_sha256'}) != data.get('dataset_sha256'):
        raise ValueError('dataset_hash_mismatch')
    utc(data['as_of'])


def coverage_audit(bars: Iterable[dict]) -> dict:
    groups = defaultdict(dict)
    for raw in bars:
        b = clean_bar(raw)
        key, t = series_key(b), utc(b['time'])
        if t in groups[key] and groups[key][t] != b:
            raise ValueError('conflicting_bar_duplicates')
        groups[key][t] = b
    result = {}
    for (competition, symbol, minutes), indexed in sorted(groups.items()):
        times = sorted(indexed)
        step = timedelta(minutes=minutes)
        gaps, irregular = [], 0
        for left, right in zip(times, times[1:]):
            delta = right - left
            if delta % step:
                irregular += 1
            if delta > step:
                gaps.append({'after_open': iso(left), 'before_open': iso(right),
                             'unobserved_grid_slots': max(0, int(delta // step) - 1),
                             'classification': 'UNKNOWN_NOT_ASSUMED_MARKET_CLOSURE'})
        result[f'{competition}|{symbol}|{minutes}m'] = {
            'unique_bars': len(times), 'first_open': iso(times[0]), 'last_open': iso(times[-1]),
            'unknown_gap_intervals': len(gaps), 'unobserved_grid_slots': sum(g['unobserved_grid_slots'] for g in gaps),
            'irregular_spacing_count': irregular, 'gaps': gaps,
        }
    return result


def reconcile_candidate_bars(base: list[dict], candidate: list[dict], *, as_of: datetime,
                             tolerance: float = 0.0, min_overlap: int = 20) -> dict:
    """Read-only comparison, never auto-merge an external feed.

    Matching prices cannot prove session/exchange identity. Require a later
    reviewed manifest before any external bars become outcome-path evidence.
    """
    as_of = utc(as_of)
    tolerance = number(tolerance)
    if tolerance < 0 or type(min_overlap) is not int or min_overlap < 1:
        raise ValueError('invalid_comparison_configuration')
    def index(rows):
        found = {}
        excluded = 0
        for raw in rows:
            b = clean_bar(raw)
            if utc(b['time']) + timedelta(minutes=b['timeframe_minutes']) > as_of:
                excluded += 1
                continue
            key = (*series_key(b), b['time'])
            if key in found and found[key] != b:
                raise ValueError('conflicting_bar_duplicates')
            found[key] = b
        return found, excluded
    a, excluded_a = index(base)
    b, excluded_b = index(candidate)
    common = sorted(a.keys() & b.keys())
    mismatches = [key for key in common if any(abs(a[key][k] - b[key][k]) > tolerance for k in OHLC)]
    by_series = {}
    for key in sorted({k[:3] for k in a} | {k[:3] for k in b}):
        overlap = [x for x in common if x[:3] == key]
        bad = [x for x in mismatches if x[:3] == key]
        by_series['|'.join(map(str, key))] = dict(overlap=len(overlap), mismatches=len(bad),
                                               price_consistency_passed=len(overlap) >= min_overlap and not bad)
    return dict(research_only=True, execution='none', live_authorized=False,
                as_of=iso(as_of), base_sha256=digest(base), candidate_sha256=digest(candidate),
                tolerance=tolerance, min_overlap=min_overlap, by_series=by_series,
                overlap=len(common), mismatches=len(mismatches),
                candidate_only_bars=len(b.keys()-a.keys()), unclosed_excluded=excluded_a+excluded_b,
                auto_merge_allowed=False, session_identity_verified=False,
                mismatch_times=[list(k) for k in mismatches])
