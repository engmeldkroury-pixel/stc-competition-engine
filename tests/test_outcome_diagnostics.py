from copy import deepcopy
import pytest
from app.outcome_diagnostics import nonoverlapping_entries, diagnostic_report
from app.outcome_attribution import VERSION

def row(i,t,state='CENSORED',symbol='CAPITALCOM:BTCUSD',minutes=15):
    return dict(event_id=str(i),competition_id='c',symbol=symbol,entry={'time':f'2026-09-27T{t}:00Z'},horizon_bars=4,timeframe_minutes=minutes,status=state,quadrant='UNKNOWN',provenance='LEGACY_RECONSTRUCTED_GEOMETRY',thresholds={},cost_r_proxy=0.02)

def report(rows):
    return dict(version=VERSION,research_only=True,live_authorized=False,execution='none',outcomes=rows,as_of='2026-09-27T19:00:00Z',source_rows=10,source_scope='BOUNDED_INBOX_NOT_COMPLETE_HISTORY')

def test_cohort_never_selects_later_winner_or_skips_censored_first_entry():
    a=row(1,'10:00'); b=row(2,'10:15','COMPLETE'); c=row(3,'11:00')
    assert [x['event_id'] for x in nonoverlapping_entries([b,c,a])] == ['1','3']

def test_different_timeframes_same_asset_share_block_but_other_assets_do_not():
    a=row(1,'10:00');b=row(2,'10:30',minutes=30);c=row(3,'10:30',symbol='CAPITALCOM:ETHUSD')
    assert [x['event_id'] for x in nonoverlapping_entries([a,b,c])] == ['1','3']

def test_pair_requires_same_observation_and_does_not_join_unrelated_paths():
    a=row(1,'10:00');b=row(2,'11:00')
    a['thresholds']={'1.0':{'state':'TARGET_FIRST'}}
    b['thresholds']={'2.5':{'state':'STOP_FIRST'}}
    assert diagnostic_report(report([a,b]))['overall']['same_path_1r_target_then_stop_before_2p5r']==0
    a['thresholds']['2.5']={'state':'STOP_FIRST'}
    assert diagnostic_report(report([a]))['overall']['same_path_1r_target_then_stop_before_2p5r']==1

def test_no_promotion_or_probability_even_for_all_target_wins():
    a=row(1,'10:00','COMPLETE');a['thresholds']={'1.0':{'state':'TARGET_FIRST','net_plan_r':0.98}}
    d=diagnostic_report(report([a]));assert not d['live_promotion_allowed']
    assert d['calibrated_win_probability'] is None and d['preferred_exit_policy'] is None
    s=d['settled_cost_sensitivity']['1.0'];assert s['settled_only_mean_by_round_trip_cost_r']['0.1']==pytest.approx(.9)
    assert not s['unbiased_expectancy']

def test_duplicate_observations_and_live_input_rejected():
    a=row(1,'10:00')
    with pytest.raises(ValueError,match='duplicate'):diagnostic_report(report([a,a]))
    r=report([a]);r['live_authorized']=True
    with pytest.raises(ValueError,match='boundary'):diagnostic_report(r)
