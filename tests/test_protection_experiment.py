"""Synthetic causal protection tests, never empirical profitability evidence."""
import pytest
from datetime import timedelta
from tests.test_outcome_attribution import BASE,seed,bar
from app.protection_experiment import evaluate_protection,compare_protection
from tests.test_r9_data_exit_audit import dataset


def run(bars,policy='closed_1r_fee_proxy_breakeven',side='LONG',horizon=None):
    return evaluate_protection(seed(side),bars,as_of=BASE+timedelta(hours=10),policy=policy,horizon_bars=horizon or len(bars))


def test_same_bar_low_cannot_hit_stop_raised_only_after_close():
    r=run([bar(h=112,l=95,c=111),bar(30,o=111,h=112,l=101,c=105)])
    assert r['state']=='FIXED_HORIZON_CLOSE_MARK_NOT_EXECUTION'
    assert r['lower_net_plan_r']==pytest.approx(.48)
    assert r['stop_updates'][0]['new_stop']==pytest.approx(100.2)


def test_intrabar_high_cannot_activate_closed_price_protection():
    r=run([bar(h=112,l=95,c=100),bar(30,o=100,h=101,l=89,c=90)])
    assert r['state']=='STOP' and r['lower_net_plan_r']==pytest.approx(-1.02)
    assert r['stop_updates']==[]


def test_next_bar_protected_stop_and_gap_at_worse_open():
    r=run([bar(h=112,l=95,c=111),bar(30,o=99,h=105,l=98,c=104)])
    assert r['state']=='GAP_STOP_OPEN' and r['lower_net_plan_r']==pytest.approx(-.12)


def test_original_stop_precedes_future_close_activation():
    r=run([bar(h=112,l=89,c=111),bar(30,o=111,h=112,l=101,c=105)])
    assert r['state']=='STOP' and not r['stop_updates']


def test_stop_target_double_touch_keeps_bounds():
    r=run([bar(h=130,l=89,c=111)])
    assert r['state']=='AMBIGUOUS_STOP_TARGET'
    assert r['lower_net_plan_r']==pytest.approx(-1.02) and r['upper_net_plan_r']==pytest.approx(2.48)


def test_missing_path_never_receives_terminal_mark():
    assert run([bar(h=112,l=95,c=111),bar(45)],horizon=3)['state']=='UNKNOWN_PATH'


def test_ratchet_cannot_widen_stop_and_uses_close_not_high():
    r=run([bar(h=124,l=95,c=118),bar(30,o=118,h=123,l=116,c=117),bar(45,o=117,h=123,l=115,c=120)],'closed_1_5r_trail_0_75r')
    updates=r['stop_updates'];assert len(updates)==1
    assert updates[0]['new_stop']==pytest.approx(110.5)


@pytest.mark.parametrize('policy',['fixed_single_tp_2_5r','closed_1r_fee_proxy_breakeven','closed_1_5r_lock_0_5r','closed_1_5r_trail_0_75r'])
def test_long_short_mirror(policy):
    a=[bar(h=119,l=95,c=118),bar(30,o=118,h=119,l=104,c=105)]
    b=[bar(t=15+i*15,o=200-x['open'],h=200-x['low'],l=200-x['high'],c=200-x['close']) for i,x in enumerate(a)]
    x,y=run(a,policy),run(b,policy,'SHORT')
    assert x['state']==y['state'];assert x['lower_net_plan_r']==pytest.approx(y['lower_net_plan_r'])


def test_unregistered_policy_fails_closed_and_empty_audit_has_no_winner():
    with pytest.raises(ValueError):run([bar()],policy='best_live')
    r=compare_protection(dataset([]));assert r['preferred_policy'] is None and r['live_authorized'] is False


def test_fee_proxy_cannot_raise_stop_above_activation_close():
    with pytest.raises(ValueError,match='activation'):
        evaluate_protection(seed(),[bar()],as_of=BASE+timedelta(hours=10),
                            policy='closed_1r_fee_proxy_breakeven',cost_r=1)


def test_baseline_matches_existing_r9_evaluator_on_synthetic_paths():
    from app.exit_policy_audit import evaluate_exit_experiment
    paths=[[bar()], [bar(h=130,l=89,c=111)], [bar(),bar(30,o=85,h=86,l=84,c=85)], [bar(),bar(45)]]
    for bars in paths:
        x=run(bars,'fixed_single_tp_2_5r',horizon=2)
        y=evaluate_exit_experiment(seed(),bars,as_of=BASE+timedelta(hours=10),horizon_bars=2)['paired_valuations']['2.5']
        assert x['lower_net_plan_r']==y['lower_net_plan_r']
        assert x['upper_net_plan_r']==y['upper_net_plan_r']
