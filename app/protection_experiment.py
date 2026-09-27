"""Research-only causal stop protection. No approval/order/account operations.

Trigger protection from a CLOSED bar; its stop becomes active next bar. This is
an idealized next-open activation, not evidence that a human changed an order.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from datetime import timedelta
from .outcome_attribution import _closed_bars, evaluate_outcome, iso, utc, number
from .outcome_dataset import validate_dataset, series_key, digest
from .exit_policy_audit import nonoverlapping_cohort

POLICIES = {
    'fixed_single_tp_2_5r': {'activation_r': None, 'lock_r': None, 'giveback_r': None},
    'closed_1r_fee_proxy_breakeven': {'activation_r': 1.0, 'lock_r': 'cost', 'giveback_r': None},
    'closed_1_5r_lock_0_5r': {'activation_r': 1.5, 'lock_r': .5, 'giveback_r': None},
    'closed_1_5r_trail_0_75r': {'activation_r': 1.5, 'lock_r': .5, 'giveback_r': .75},
}


def evaluate_protection(seed: dict, rows: list[dict], *, as_of, policy: str,
                        horizon_bars: int = 32, cost_r: float = .02) -> dict:
    if policy not in POLICIES:
        raise ValueError('unregistered_policy')
    if POLICIES[policy]['lock_r']=='cost' and number(cost_r)>=POLICIES[policy]['activation_r']:
        raise ValueError('cost_exceeds_protection_activation')
    baseline = evaluate_outcome(seed, rows, as_of=as_of, horizon_bars=horizon_bars, cost_r=cost_r)
    result = {'event_id': seed['event_id'], 'policy': policy, 'state': 'NO_ENTRY' if baseline['status']=='NO_ENTRY' else 'UNKNOWN_PATH',
              'lower_net_plan_r': None, 'upper_net_plan_r': None,
              'execution': 'none', 'research_only': True, 'stop_updates': []}
    if baseline['entry'] is None:
        return result
    entry = baseline['entry']['price'];risk=seed['plan_risk'];sign=1 if seed['side']=='LONG' else -1
    stop = seed['stop']; target=seed['plan_mid']+sign*2.5*risk
    start=utc(baseline['entry']['time']);step=timedelta(minutes=seed['timeframe_minutes'])
    bars=[b for b in _closed_bars(seed, rows, utc(as_of)) if b['time']>=start]
    cfg=POLICIES[policy]; high_water=0.0
    def finish(state, low_price, high_price=None, when=None):
        result.update(state=state,lower_net_plan_r=sign*(low_price-entry)/risk-cost_r,
                      upper_net_plan_r=sign*((high_price if high_price is not None else low_price)-entry)/risk-cost_r,
                      exit_or_mark_bar_open=iso(when), final_stop=stop)
        return result
    for i in range(horizon_bars):
        expected=start+i*step
        if i>=len(bars) or bars[i]['time']!=expected:
            return result
        b=bars[i];favourable=b['high'] if sign==1 else b['low'];adverse=b['low'] if sign==1 else b['high']
        if sign*(b['open']-stop)<=0:
            return finish('GAP_STOP_OPEN',b['open'],when=expected)
        if sign*(b['open']-target)>=0:
            return finish('TARGET_LIMIT',target,when=expected)
        stop_hit=sign*(adverse-stop)<=0;target_hit=sign*(favourable-target)>=0
        if stop_hit and target_hit:
            return finish('AMBIGUOUS_STOP_TARGET',stop,target,expected)
        if stop_hit:
            return finish('STOP',stop,when=expected)
        if target_hit:
            return finish('TARGET_LIMIT',target,when=expected)
        if i==horizon_bars-1:
            return finish('FIXED_HORIZON_CLOSE_MARK_NOT_EXECUTION',b['close'],when=expected)
        high_water=max(high_water,sign*(b['close']-entry)/risk)
        if cfg['activation_r'] is not None and high_water>=cfg['activation_r']:
            locked=cost_r if cfg['lock_r']=='cost' else cfg['lock_r']
            if cfg['giveback_r'] is not None:
                locked=max(locked,high_water-cfg['giveback_r'])
            new_stop=entry+sign*locked*risk
            if sign*(new_stop-stop)>0:
                result['stop_updates'].append({'based_on_closed_bar_open':iso(expected),
                  'effective_from_open':iso(expected+step),'old_stop':stop,'new_stop':new_stop,
                  'basis':'closed_price_high_water_not_intrabar_extreme'})
                stop=new_stop
    return result


def compare_protection(dataset: dict, *, horizon_bars: int=32,cost_r: float=.02) -> dict:
    validate_dataset(dataset)
    if type(horizon_bars) is not int or not 0<horizon_bars<=10000 or number(cost_r)<0:
        raise ValueError('invalid_configuration')
    groups=defaultdict(list)
    for b in dataset['bars']:groups[series_key(b)].append(b)
    seed_by_id={s['event_id']:s for s in dataset['seeds']}
    baselines=[evaluate_outcome(s,groups[series_key(s)],as_of=utc(dataset['as_of']),horizon_bars=horizon_bars,cost_r=cost_r) for s in dataset['seeds']]
    cohort=nonoverlapping_cohort(baselines)
    results=[]
    for base in cohort:
        s=seed_by_id[base['event_id']]
        results.append({'event_id':s['event_id'],'competition_id':s['competition_id'],'symbol':s['symbol'],
          'provenance':s['provenance'],'entry':base['entry'],
          'policies':{policy:evaluate_protection(s,groups[series_key(s)],as_of=utc(dataset['as_of']),policy=policy,horizon_bars=horizon_bars,cost_r=cost_r) for policy in POLICIES}})
    eligible=[r for r in results if all(p['lower_net_plan_r'] is not None for p in r['policies'].values())]
    stats={}
    for policy in POLICIES:
        values=[r['policies'][policy] for r in eligible]
        stats[policy]={'common_n':len(values),'mean_lower_net_plan_r':sum(p['lower_net_plan_r'] for p in values)/len(values) if values else None,
          'mean_upper_net_plan_r':sum(p['upper_net_plan_r'] for p in values)/len(values) if values else None,
          'states':dict(Counter(p['state'] for p in values))}
    return {'schema':'stc-protection-experiment-v1','dataset_sha256':dataset['dataset_sha256'],
      'experiment_configuration_sha256':digest({'policies':POLICIES,'horizon_bars':horizon_bars,'cost_r':cost_r}),
      'policies':POLICIES,'horizon_bars':horizon_bars,'cost_r_proxy':cost_r,'selected_n':len(results),
      'common_valued_n':len(eligible),'unknown_path_n':len(results)-len(eligible),'policy_statistics':stats,
      'outcomes':results,'common_event_ids':[r['event_id'] for r in eligible],
      'live_authorized':False,'execution':'none','preferred_policy':None,'calibrated_win_probability':None,
      'limitations':['Exploratory historical hypotheses, not executed trades or untouched out-of-sample evidence.',
        'Common cohort and all policy parameters retained; no winner promoted.',
        'Protection assumes next-bar activation and proxy costs; manual latency, bid/ask and actual fees not modeled.',
        'Missing paths remain unknown; no price interpolation or gap-as-session assumptions.',
        'Initial stop and entry geometry unchanged; volatility/structure-aware initial stops remain a separate experiment.']}
