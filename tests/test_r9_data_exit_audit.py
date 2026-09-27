"""Synthetic correctness fixtures; they are never reported as market performance."""
from copy import deepcopy
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from app.outcome_dataset import (prepare_dataset,validate_dataset,coverage_audit,
                                reconcile_candidate_bars,digest)
from app.exit_policy_audit import evaluate_exit_experiment,nonoverlapping_cohort,audit_exit_policies
from app.execution_reconciliation import reconcile_visible_trade
from app.pipeline_receipt import build_pipeline_receipt
from tests.test_outcome_attribution import BASE,bar,seed,stamp,stored_row,reseal


def dataset(rows):
    return prepare_dataset({'ok':True,'events':rows},as_of=BASE+timedelta(hours=12))


def test_normalized_dataset_hash_and_secret_minimization():
    row=stored_row();row['result']['private']='PRIVATE_TEST_MARKER'
    d=dataset([row]);validate_dataset(d)
    assert 'PRIVATE_TEST_MARKER' not in json.dumps(d)
    assert d['seeds'][0]['provenance']=='FROZEN_AT_DECISION'
    assert len(d['receipt_proofs'])==1 and 'payload' not in d
    d['bars'][0]['close']=111
    with pytest.raises(ValueError,match='hash'):validate_dataset(d)


def test_identical_duplicates_idempotent_and_shuffle_stable():
    a,b=stored_row(),stored_row(event_id='b',minute=15)
    d=dataset([a,b,a]);e=dataset([b,a,a])
    assert d['bars']==e['bars'] and d['seeds']==e['seeds']
    assert d['exact_duplicate_rows_ignored']==1 and len(d['seeds'])==2


def test_conflicting_event_ids_quarantine_every_version():
    a=stored_row();b=deepcopy(a);b['payload']['close']=123
    d=dataset([a,b]);assert not d['bars'] and not d['seeds']
    assert d['quarantine_counts']['conflicting_event_duplicates']==2


def test_conflicting_ohlc_different_event_ids_cannot_make_a_clean_path():
    a=stored_row();b=stored_row(event_id='b',high=150)
    d=dataset([a,b]);assert not d['bars'] and not d['seeds']
    assert d['quarantine_counts']['conflicting_ohlc_records']==2


@pytest.mark.parametrize('field,value',[('symbol','BITSTAMP:BTCUSD'),('available_at',stamp(30)),('entry_min',98)])
def test_resealed_but_source_inconsistent_seed_is_quarantined_atomically(field,value):
    a=stored_row();s=a['result']['decision']['research_outcome_seed'];s[field]=value
    a['result']['decision']['research_outcome_seed']=reseal(s)
    d=dataset([a]);assert not d['bars'] and not d['seeds']


@pytest.mark.parametrize('field,value',[('high',1),('open',True)])
def test_invalid_bars_never_enter_coverage_or_outcomes(field,value):
    a=stored_row();a['payload'][field]=value
    d=dataset([a]);assert not d['bars']


def test_future_source_and_future_decision_do_not_enter_dataset():
    d=prepare_dataset({'ok':True,'events':[stored_row()]},as_of=BASE+timedelta(minutes=14))
    assert not d['bars']
    a=stored_row();a['result']['decision']['approval_envelope']['issued_at']=stamp(800)
    assert not dataset([a])['bars']


def test_unknown_gap_not_called_session_closure_or_filled():
    out=coverage_audit([bar(15),bar(45)])
    v=next(iter(out.values()));assert v['unique_bars']==2
    assert v['unobserved_grid_slots']==1
    assert v['gaps'][0]['classification']=='UNKNOWN_NOT_ASSUMED_MARKET_CLOSURE'


def test_external_comparison_is_per_provider_and_never_auto_merges():
    a=[bar(15),bar(30)];b=deepcopy(a)
    r=reconcile_candidate_bars(a,b,as_of=BASE+timedelta(hours=2),min_overlap=2)
    assert r['overlap']==2 and r['mismatches']==0 and not r['auto_merge_allowed']
    b[0]['symbol']='BITSTAMP:BTCUSD'
    r=reconcile_candidate_bars(a,b,as_of=BASE+timedelta(hours=2),min_overlap=2)
    assert r['overlap']==1 and not any(v['price_consistency_passed'] for v in r['by_series'].values())


def test_external_disagreement_and_unclosed_bar_are_not_silently_accepted():
    a=[bar()];b=[bar(c=104),bar(45)]
    r=reconcile_candidate_bars(a,b,as_of=BASE+timedelta(minutes=50),min_overlap=1)
    assert r['mismatches']==1 and r['unclosed_excluded']==1
    with pytest.raises(ValueError,match='conflicting'):
        reconcile_candidate_bars(a,[bar(),bar(h=120)],as_of=BASE+timedelta(hours=2))


def experiment(bars,side='LONG',horizon=1):
    return evaluate_exit_experiment(seed(side),bars,as_of=BASE+timedelta(hours=10),horizon_bars=horizon)


def test_complete_untriggered_policy_gets_terminal_mark_not_broker_fill():
    r=experiment([bar(c=104)])
    val=r['paired_valuations']['2.5']
    assert r['thresholds']['2.5']['state']=='CENSORED'  # R8 contract preserved
    assert val['kind']=='FIXED_HORIZON_CLOSE_MARK_NOT_EXECUTION'
    assert val['lower_net_plan_r']==pytest.approx(.38)
    assert val['mark_at']==stamp(30).replace('+00:00','Z')
    assert r['all_policies_valued']


def test_partial_path_never_gets_terminal_mark():
    r=experiment([bar(),bar(45,c=104)],horizon=3)
    assert r['paired_valuations']['2.5']['kind']=='UNKNOWN_PATH'
    assert not r['all_policies_valued']


def test_all_policies_exited_before_gap_remain_comparable():
    r=experiment([bar(l=89)],horizon=3)
    assert r['status']=='CENSORED' and r['all_policies_valued']
    assert r['paired_valuations']['2.5']['lower_net_plan_r']==pytest.approx(-1.02)


def test_same_bar_ambiguity_preserves_bounds_not_fake_certainty():
    r=experiment([bar(h=130,l=89)])
    v=r['paired_valuations']['2.5']
    assert v['kind']=='AMBIGUOUS_EXIT_BOUNDS'
    assert v['lower_net_plan_r']==pytest.approx(-1.02)
    assert v['upper_net_plan_r']==pytest.approx(2.48)


def test_gap_stop_uses_open_and_not_stop_level():
    r=experiment([bar(),bar(30,o=85,h=86,l=84,c=85)],horizon=2)
    assert r['paired_valuations']['2.5']['lower_net_plan_r']==pytest.approx(-1.52)


@pytest.mark.parametrize('prices',[(105,95,104),(130,89,100),(125,95,125)])
def test_terminal_and_exit_bound_long_short_symmetry(prices):
    h,l,c=prices;a=bar(h=h,l=l,c=c)
    b=bar(o=200-a['open'],h=200-l,l=200-h,c=200-c)
    left,right=experiment([a]),experiment([b],side='SHORT')
    for k in left['paired_valuations']:
        assert left['paired_valuations'][k]['lower_net_plan_r']==right['paired_valuations'][k]['lower_net_plan_r']
        assert left['paired_valuations'][k]['upper_net_plan_r']==right['paired_valuations'][k]['upper_net_plan_r']


def test_nonoverlap_keeps_earliest_censored_not_later_winner():
    a=experiment([bar()],horizon=4);b=deepcopy(a)
    b['event_id']='later';b['entry']['time']=stamp(30);b['status']='COMPLETE'
    assert nonoverlapping_cohort([b,a])==[a]
    with pytest.raises(ValueError,match='duplicate'):nonoverlapping_cohort([a,a])


def test_paired_audit_uses_same_ids_for_all_targets_and_costs_and_no_promotion():
    rows=[stored_row(event_id=str(t),minute=t,high=111 if t==15 else 101) for t in (0,15,30,45,60)]
    d=dataset(rows);r=audit_exit_policies(d,horizon_bars=2)
    group=r['nonoverlapping_cohort'];counts={v['common_n'] for v in group['policies'].values()}
    assert len(counts)==1 and group['common_valued_n']>0
    assert all(v['common_n']==group['common_valued_n'] for c in group['proxy_cost_sensitivity'].values() for v in c.values())
    assert r['preferred_policy'] is None and r['calibrated_win_probability'] is None
    assert not r['live_promotion_allowed'] and not group['unbiased_population_expectancy']


@pytest.mark.parametrize('horizon,cost',[(0,.02),(True,.02),(1,-1),(1,float('nan'))])
def test_invalid_audit_configuration_rejected_on_empty_dataset(horizon,cost):
    with pytest.raises(ValueError):audit_exit_policies(dataset([]),horizon_bars=horizon,cost_r=cost)


def test_arithmetic_explains_new_delta_without_inventing_old_residual_trade():
    r=reconcile_visible_trade(ledger_realized='-3370.87',platform_realized='-3566.10',
        previously_documented_residual='-54.39',side='LONG',quantity='.5',
        entry_price='84564.60',exit_price='84299.80',entry_commission='4.2282',exit_commission='4.215')
    assert r['matches_displayed_cents'] and r['visible_net_pnl']=='-140.8432'
    assert not r['ledger_write_allowed'] and r['remaining_rounding_difference']=='0.0032'


def test_cli_projection_preserves_receipt_but_removes_unneeded_fields():
    a=stored_row();a['result']['private']='PRIVATE_MARKER'
    raw=dict(event_id=a['event_id'],status=a['status'],payload_json=json.dumps(a['payload']),result_json=json.dumps(a['result']))
    out=subprocess.run(['php','scripts/export_r9_history.php'],input=json.dumps(raw),text=True,capture_output=True,
                       env={**os.environ,'STC_R9_PROJECTION_TEST':'1'})
    assert out.returncode==0,out.stderr
    assert 'PRIVATE_MARKER' not in out.stdout and len(dataset([json.loads(out.stdout)])['seeds'])==1


def test_reader_is_bounded_read_only_cli_and_never_writes_accounts():
    s=Path('scripts/export_r9_history.php').read_text()
    assert 'WITH CONSISTENT SNAPSHOT, READ ONLY' in s and 'LIMIT 12000' in s
    assert "PHP_SAPI !== 'cli'" in s
    for bad in ('INSERT INTO','DELETE FROM','UPDATE stc_','DROP TABLE','stc_positions','stc_account_state','file_put_contents'):
        assert bad not in s
    assert subprocess.run(['php','-l','scripts/export_r9_history.php'],capture_output=True).returncode==0


def test_cli_round_trip_no_secret_in_artifacts(tmp_path):
    source=tmp_path/'in.json';target=tmp_path/'out';a=stored_row();a['result']['private']='PRIVATE_MARKER'
    source.write_text(json.dumps({'ok':True,'events':[a]}))
    p=subprocess.run([sys.executable,'scripts/run_r9_audit.py','--input',str(source),'--output-dir',str(target)],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert 'PRIVATE_MARKER' not in ''.join(f.read_text() for f in target.iterdir())
    assert not json.loads((target/'manifest.json').read_text())['raw_source_exported']


def test_nonfinite_snapshot_fails_closed_before_export():
    a=stored_row();a['payload']['close']=float('nan')
    with pytest.raises(ValueError):dataset([a])


def test_original_locked_plan_preserved_as_research_not_execution():
    from app.trade_plan import build_locked_trade_plan
    a=stored_row();s=a['result']['decision']['signal'];s.update(recommendation='LONG',composite_score=.8)
    e=a['result']['decision']['approval_envelope'];a['result']['decision']['research_outcome_seed']=None
    plan=build_locked_trade_plan(a['event_id'],a['payload'],s,e)
    a['result']['decision']['locked_trade_plan']=plan
    d=dataset([a]);assert d['original_plans'][0]['plan_id']==plan['plan_id']
    assert d['original_plans'][0]['execution']=='none'
    plan['source_event_id']='wrong'
    assert not dataset([a])['original_plans'] and not dataset([a])['bars']
