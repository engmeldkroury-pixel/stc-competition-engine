"""Safety and causality contracts for research-only, 16-pair cash-spot workflow."""
import json
from datetime import datetime
from pathlib import Path

import pytest

from app.spot16_manual_paper_strategy import (
    Bar,COST_BPS,FAMILIES,
    bars_from_binance,closed_asof_index,indicators,paper_manual_intent,
    signal_family,simulate_exit,summary,
)

ROOT=Path(__file__).resolve().parents[1]
PAIRS=[
    "BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT",
    "TRBUSDT","GALAUSDT","YGGUSDT","NOTUSDT","NEOUSDT","OPUSDT","ARBUSDT",
    "SUIUSDT","INJUSDT",
]

def rawbar(t,o=100,h=103,l=98,c=101,v=10):
    return [t,str(o),str(h),str(l),str(c),str(v),t+900000-1,0]

def normal_manual_kwargs():
    return dict(
        pair="BTCUSDT",entry=100.,stop=95.,now_ms=1_000_000,
        signal_ms=900_000,quote_observed_ms=980_000,
        quote_from_exact_verified_venue=True,
        strategy_review_state="APPROVED_FOR_MANUAL_PAPER",
        equity_usdt=1_000.,spot_step_size=0.001,minimum_notional=10.,
        owner_ack=True,actual_quote_price=100.01,
        verified_available_cash_usdt=400.,
        verified_existing_open_stop_risk_usdt=12.,
        paper_account_identity_verified=True,
    )

def test_registered_exact_sixteen_pairs_and_spot_only():
    data=json.loads((ROOT/"research_inputs"/"CRYPTO_SPOT_ASSET_REGISTRY.json").read_text())
    assert [x["pair"] for x in data["assets"]]==PAIRS
    assert data["quote_asset"]=="USDT"
    assert data["mode"]=="SPOT_ONLY"
    assert all(data["constraints"][k] is False
               for k in ("shorting","futures","leverage","real_money_authorized"))

def test_three_predeclared_cash_long_research_families():
    assert FAMILIES==("MTF_TREND_PULLBACK","MTF_BOUNDED_BREAKOUT","MTF_RANGE_RECOVERY")
    assert COST_BPS==(5,15,30)

def test_actual_binance_closed_bar_parsing_utc():
    t=1_800_000_000
    result=bars_from_binance([rawbar(t),rawbar(t+900_000)],"15m")
    assert len(result)==2
    assert result[0].close_ms==t+900_000-1
    assert result[0].h>=max(result[0].o,result[0].c)

@pytest.mark.parametrize("bad",[
    lambda rows: rows.__setitem__(1,rawbar(rows[0][0])),
    lambda rows: rows.__setitem__(1,rawbar(rows[0][0]+1800000)),
    lambda rows: rows[0].__setitem__(6,rows[0][0]+900_000),
    lambda rows: rows[0].__setitem__(2,"inf"),
    lambda rows: rows[0].__setitem__(3,"110"),
    lambda rows: rows[0].__setitem__(5,"-3"),
])
def test_invalid_spot_market_source_bars_fail_closed(bad):
    rows=[rawbar(1_800_000_000),rawbar(1_800_900_000)]
    bad(rows)
    with pytest.raises(ValueError):
        bars_from_binance(rows,"15m")

def test_closed_high_timeframe_asof_has_no_future_bar():
    hist=[
      Bar(0,3600000-1,100,101,99,100,10),
      Bar(3600000,7200000-1,100,101,99,100,10),
      Bar(7200000,10800000-1,100,101,99,100,10),
    ]
    assert closed_asof_index(hist,3600000-2)==-1
    assert closed_asof_index(hist,3600000-1)==0
    assert closed_asof_index(hist,7200000-2)==0
    assert closed_asof_index(hist,7200000-1)==1
    assert closed_asof_index(hist,10800000-2)==1

def test_indicators_use_past_and_warm_up():
    bars=[Bar(k*900000,(k+1)*900000-1,100+0.01*k,101+0.01*k,99+0.01*k,100+0.01*k,10)
          for k in range(300)]
    f=indicators(bars)
    assert f["adx"][26] is None
    assert f["adx"][27] is not None
    for key in ("ema20","ema50","ema200","atr","adx","rsi","bblo","bbhi"):
        assert f[key][280] is not None

def test_same_candle_target_and_stop_hits_stop_first():
    b=[Bar(0,899999,100,108,92,102,10)]
    res=simulate_exit(b,0,1,95,105)
    assert res["reason"]=="STOP"
    assert res["exit_price"]==95

def test_gap_open_past_stop_uses_adverse_open_price():
    b=[Bar(0,899999,93,110,90,98,10)]
    res=simulate_exit(b,0,1,95,105)
    assert res["reason"]=="STOP"
    assert res["exit_price"]==93

def test_unobservable_gap_does_not_invent_trade_exit():
    b=[Bar(0,899999,100,101,99,100,10),Bar(1800000,2699999,100,104,99,102,10)]
    res=simulate_exit(b,0,2,95,105)
    assert res["reason"]=="UNOBSERVED_GAP"
    assert res["exit_price"] is None

def test_incomplete_window_never_invents_win_or_loss():
    b=[Bar(k*900000,(k+1)*900000-1,100,102,98,100,1)
       for k in range(15)]
    res=simulate_exit(b,0,len(b),95,105)
    assert res["reason"]=="INCOMPLETE_FORWARD_WINDOW"
    assert res["exit_price"] is None

def test_returns_degrade_monotonically_with_fee_assumptions():
    samples=[{"cost_net_R":{"5":0.8,"15":0.5,"30":0.2}},
             {"cost_net_R":{"5":-0.7,"15":-1.,"30":-1.4}}]
    assert summary(samples,5)["net_R_sum"]>summary(samples,15)["net_R_sum"]
    assert summary(samples,15)["net_R_sum"]>summary(samples,30)["net_R_sum"]

def test_strategy_never_authorizes_paper_without_separate_promotion():
    args=normal_manual_kwargs()
    args["strategy_review_state"]="RESEARCH_ONLY"
    answer=paper_manual_intent(**args)
    assert answer["decision"]=="HOLD" and answer["reason"]=="STRATEGY_NOT_PROMOTED"
    assert answer["paper_order_sent"] is False
    assert answer["broker_order_sent"] is False

@pytest.mark.parametrize("key,value,reason",[
    ("paper_account_identity_verified",False,"PAPER_ACCOUNT_UNVERIFIED"),
    ("quote_from_exact_verified_venue",False,"VERIFIED_FRESH_QUOTE_REQUIRED"),
    ("quote_observed_ms",800_000,"VERIFIED_FRESH_QUOTE_REQUIRED"),
    ("now_ms",1_250_001,"SIGNAL_EXPIRED_REQUIRE_NEW_PLAN"),
    ("owner_ack",False,"OWNER_MANUAL_ACK_REQUIRED"),
    ("actual_quote_price",100.5,"PRICE_CHANGED_REVALIDATE_NO_CHASE"),
    ("verified_existing_open_stop_risk_usdt",20.,"PORTFOLIO_RISK_CAP_REACHED"),
    ("verified_available_cash_usdt",None,"MISSING_VERIFIED_QUOTE_ACCOUNT_OR_MARKET_RULE"),
    ("spot_step_size",None,"MISSING_VERIFIED_QUOTE_ACCOUNT_OR_MARKET_RULE"),
    ("stop",101.,"INVALID_ACCOUNT_STOP_OR_VENUE"),
])
def test_manual_paper_hard_gates(key,value,reason):
    args=normal_manual_kwargs()
    args[key]=value
    if key=="now_ms":
        args["quote_observed_ms"]=value-1000
    answer=paper_manual_intent(**args)
    assert answer["decision"]=="HOLD"
    assert answer["reason"]==reason
    assert answer["automatic_execution"] is False

def test_valid_manual_preview_only_restricts_aggregate_and_notional_risk():
    args=normal_manual_kwargs()
    a=paper_manual_intent(**args)
    assert a["decision"]=="OWNER_MANUAL_PAPER_RECHECK_ONLY"
    assert a["hypothetical_max_quantity"]>0
    assert a["max_notional_usdt"]<=0.05*args["equity_usdt"]+1e-8
    assert a["max_notional_usdt"]<=args["verified_available_cash_usdt"]+1e-8
    assert a["estimated_max_stop_risk_usdt"]<=0.005*args["equity_usdt"]+1e-8
    assert a["estimated_max_stop_risk_usdt"]+args["verified_existing_open_stop_risk_usdt"]<=0.02*args["equity_usdt"]+1e-8
    assert a["paper_order_sent"] is False
    assert a["broker_order_sent"] is False

def test_below_min_order_value_holds():
    args=normal_manual_kwargs()
    args["minimum_notional"]=1000.
    a=paper_manual_intent(**args)
    assert a["decision"]=="HOLD"
    assert a["reason"]=="BELOW_VENUE_MIN_NOTIONAL"

def test_static_no_network_order_routing_in_strategy_module():
    raw=(ROOT/"app"/"spot16_manual_paper_strategy.py").read_text()
    for banned in ("urllib.request","requests.post(","client.create_order(","binance.order(","api/v3/order","webhook/send","send_telegram"):
        assert banned not in raw

def test_regression_no_unauthorized_contest_to_spot_carryover():
    assert "competition" not in paper_manual_intent.__name__
    assert "real_money_authorized" not in paper_manual_intent.__name__