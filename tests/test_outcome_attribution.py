"""Synthetic regression fixtures only; none of these are trading results."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from app.outcome_attribution import (build_outcome_seed, canonical, evaluate_outcome,
                                    summarize_outcomes, validate_seed)
from app.outcome_report import report_from_inbox
from app.pipeline_receipt import build_pipeline_receipt

BASE = datetime(2026, 9, 27, tzinfo=timezone.utc)
COMP = "capital-africa-sep-2026"
SYMBOL = "CAPITALCOM:BTCUSD"


def stamp(minutes):
    return (BASE + timedelta(minutes=minutes)).isoformat()


def fixture(side="LONG", *, issued=15, expiry=60, event_id="r8-test-1"):
    payload = {"event_id": event_id, "competition_id": COMP, "symbol": SYMBOL,
               "timeframe": "15", "time": stamp(0), "open": 100, "high": 101,
               "low": 99, "close": 100, "atr14": 7.5}
    signal = {"competition_id": COMP, "symbol": SYMBOL, "recommendation": "WAIT",
              "signal_id": "bridge-" + hashlib.sha256(event_id.encode()).hexdigest()[:32],
              "pre_gate_recommendation": side, "quality_gate_failures": ["family", "quality"],
              "gate_diagnostics": {"boolean_gate_passed": False, "setup_quality_passed": False}}
    envelope = {"competition_id": COMP, "symbol": SYMBOL, "issued_at": stamp(issued),
                "valid_until": stamp(expiry), "entry_min": 99, "entry_max": 101,
                "reference_price": 100}
    return payload, signal, envelope


def seed(side="LONG", **kwargs):
    payload, signal, envelope = fixture(side, **kwargs)
    return build_outcome_seed(payload["event_id"], payload, signal, envelope)


def bar(t=15, o=100, h=105, l=95, c=100, **kwargs):
    return {"competition_id": COMP, "symbol": SYMBOL, "timeframe_minutes": 15,
            "time": stamp(t), "open": o, "high": h, "low": l, "close": c, **kwargs}


def run(bars, *, candidate=None, as_of=600, horizon=1, cost=0.02):
    return evaluate_outcome(candidate or seed(), bars, as_of=BASE + timedelta(minutes=as_of),
                            horizon_bars=horizon, cost_r=cost)


def state(result, threshold=1.0):
    return result["thresholds"][str(threshold)]


def reseal(s):
    s = deepcopy(s)
    s["seed_sha256"] = hashlib.sha256(canonical({k: v for k, v in s.items() if k != "seed_sha256"}).encode()).hexdigest()
    return s


def test_seed_is_frozen_inert_and_includes_exact_failed_clauses():
    s = seed()
    validate_seed(s)
    assert s["execution"] == "none" and s["live_authorized"] is False
    assert s["stop"] == 90 and s["plan_risk"] == 10
    assert s["quadrant"] == "B0_Q0"
    assert s["failed_gates"] == ["family", "quality"]
    assert "quantity" not in s and "approval" not in s
    assert seed() == seed()


@pytest.mark.parametrize("b,q,label", [(False,False,"B0_Q0"), (False,True,"B0_Q1"),
                                      (True,False,"B1_Q0"), (True,True,"B1_Q1"), (1,True,"UNKNOWN")])
def test_quadrants_are_exact_booleans(b,q,label):
    p,s,e = fixture()
    s["gate_diagnostics"] = {"boolean_gate_passed": b, "setup_quality_passed": q}
    assert build_outcome_seed(p["event_id"],p,s,e)["quadrant"] == label


def test_legacy_unknown_gates_not_inferred_from_quality():
    p,s,e = fixture()
    s.pop("gate_diagnostics"); s.pop("quality_gate_failures")
    s["setup_quality_score"] = 99
    x = build_outcome_seed(p["event_id"],p,s,e)
    assert x["quadrant"] == "UNKNOWN" and x["failed_gates_known"] is False


def test_nondirectional_wait_has_no_counterfactual():
    p,s,e = fixture("WAIT")
    assert build_outcome_seed(p["event_id"],p,s,e) is None


@pytest.mark.parametrize("field,value", [("symbol","BITSTAMP:BTCUSD"), ("competition_id","other")])
def test_source_identity_mismatch_rejected(field,value):
    p,s,e = fixture(); e[field]=value
    with pytest.raises(ValueError, match="identity"):
        build_outcome_seed(p["event_id"],p,s,e)


@pytest.mark.parametrize("field,value", [("plan_risk", float("nan")), ("live_authorized",True), ("execution","trade")])
def test_tampered_seed_rejected(field,value):
    s=seed();s[field]=value
    with pytest.raises(ValueError):
        run([bar()],candidate=s)


def test_invalid_geometry_even_with_recomputed_digest_rejected():
    s=seed();s["stop"]=105;s=reseal(s)
    with pytest.raises(ValueError,match="geometry"):
        run([bar()],candidate=s)


def test_timezones_required():
    p,s,e=fixture();e["issued_at"]="2026-09-27T00:15:00"
    with pytest.raises(ValueError,match="timezone"):
        build_outcome_seed(p["event_id"],p,s,e)
    with pytest.raises(ValueError,match="timezone"):
        evaluate_outcome(seed(),[bar()],as_of=BASE.replace(tzinfo=None))


def test_entry_must_be_next_full_open_after_actual_decision():
    r=run([bar(15,h=140,l=80),bar(30)],candidate=seed(issued=15.01))
    assert r["entry"]["time"] == stamp(30).replace("+00:00","Z")
    assert state(r)["state"] == "CENSORED"


def test_source_bar_extremes_cannot_be_outcomes():
    r=run([bar(0,h=160,l=50),bar(15)])
    assert r["full_horizon_mfe_r"] == 0.5 and state(r)["state"] == "CENSORED"


def test_unclosed_and_future_bars_are_not_evidence():
    r=run([bar(15,h=130),bar(30,h=150)],as_of=29)
    assert r["entry"] is None and r["status"] == "CENSORED"


def test_missing_first_bar_does_not_fill_at_a_later_open():
    r=run([bar(30,h=130)])
    assert r["entry"] is None and r["reason"] == "missing_entry_bar"


def test_missing_path_censors_unresolved_but_retains_settled():
    r=run([bar(15,h=111),bar(45,h=130)],horizon=3)
    assert r["reason"] == "missing_path_bar" and r["bars_observed_after_entry"] == 1
    assert state(r)["state"] == "TARGET_FIRST" and state(r,1.5)["state"] == "CENSORED"


def test_exact_duplicates_idempotent_and_order_independent():
    bars=[bar(15),bar(30,h=125)]
    assert run(bars,horizon=2) == run([bars[1],bars[0],bars[0]],horizon=2)


def test_conflicting_duplicates_fail_closed():
    with pytest.raises(ValueError,match="conflicting"):
        run([bar(),bar(h=130)])


@pytest.mark.parametrize("field,value", [("symbol","BITSTAMP:BTCUSD"),("competition_id","AMP"),("timeframe_minutes",60)])
def test_no_cross_provider_competition_or_timeframe_substitution(field,value):
    r=run([bar(**{field:value})])
    assert r["entry"] is None


@pytest.mark.parametrize("kwargs", [{"h":float("inf")},{"l":float("nan")},{"h":98},{"o":True}])
def test_bad_ohlc_rejected(kwargs):
    with pytest.raises(ValueError):
        run([bar(**kwargs)])


def test_expired_delayed_signal_is_not_retimed():
    r=run([bar(60)],candidate=seed(issued=60,expiry=60))
    assert r["status"] == "NO_ENTRY" and r["reason"] == "expired_before_eligible_open"


def test_entry_does_not_assume_intrabar_limit_fill():
    r=run([bar(15,o=103,h=105,l=99,c=104)],candidate=seed(expiry=30))
    assert r["status"] == "NO_ENTRY" and r["entry"] is None


def test_later_open_inside_envelope_is_valid_before_expiry():
    r=run([bar(15,o=103,h=105,l=99,c=104),bar(30,h=111)],candidate=seed(expiry=45))
    assert r["entry"]["time"] == stamp(30).replace("+00:00","Z")
    assert state(r)["state"] == "TARGET_FIRST"


@pytest.mark.parametrize("threshold,high", [(1.0,110),(1.5,115),(2.0,120),(2.5,125)])
def test_each_target_has_independent_single_tp_result(threshold,high):
    r=run([bar(h=high)])
    o=state(r,threshold)
    assert o["state"] == "TARGET_FIRST"
    assert o["net_plan_r"] == pytest.approx(threshold-0.02)


def test_same_bar_both_touch_is_flagged_and_scored_stop_first():
    r=run([bar(h=126,l=89)])
    assert all(o["state"] == "AMBIGUOUS_STOP_FIRST" for o in r["thresholds"].values())
    assert state(r)["net_plan_r"] == pytest.approx(-1.02)
    assert r["pre_stop_mfe_lower_r"] == 0 and r["pre_stop_mfe_upper_r"] == 2.6


def test_gap_stop_executes_at_open_and_costs_can_exceed_one_r():
    r=run([bar(),bar(30,o=85,h=115,l=84,c=90)],horizon=2)
    assert state(r)["state"] == "STOP_FIRST"
    assert state(r)["exit_price"] == 85 and state(r)["net_plan_r"] == pytest.approx(-1.52)
    assert r["pre_stop_mfe_upper_r"] == 0.5  # Not the post-open rebound to 115.


def test_known_open_target_precedes_later_intrabar_stop():
    r=run([bar(),bar(30,o=115,h=126,l=89,c=100)],horizon=2)
    assert state(r)["state"] == "TARGET_FIRST"
    assert state(r,1.5)["state"] == "TARGET_FIRST"
    assert state(r,2.0)["state"] == "AMBIGUOUS_STOP_FIRST"
    assert state(r)["exit_price"] == 110  # no invented positive limit slippage


def test_post_stop_rebound_is_not_a_winning_trade():
    r=run([bar(l=89),bar(30,h=130)],horizon=2)
    assert state(r)["state"] == "STOP_FIRST" and state(r)["post_stop_target_touched"] is True
    assert r["full_horizon_mfe_r"] == 3 and r["pre_stop_mfe_upper_r"] == 0.5


def test_fill_and_plan_r_are_separate_and_targets_do_not_move():
    r=run([bar(o=101,h=110,l=100,c=108)])
    assert r["entry"]["fill_risk_per_unit"] == 11 and r["entry"]["plan_risk_per_unit"] == 10
    assert state(r)["target_price"] == 110
    assert state(r)["net_plan_r"] == pytest.approx(0.88)
    assert state(r)["net_fill_r"] == pytest.approx(8.8/11)


@pytest.mark.parametrize("bars", [[bar(h=125)],[bar(h=126,l=89)],
                                 [bar(),bar(30,o=85,h=115,l=84,c=90)]])
def test_long_short_mirror_symmetry(bars):
    mirrored=[]
    for b in bars:
        d=deepcopy(b);d.update(open=200-b["open"],close=200-b["close"],high=200-b["low"],low=200-b["high"])
        mirrored.append(d)
    a=run(bars,horizon=len(bars));b=run(mirrored,candidate=seed("SHORT"),horizon=len(bars))
    for r in (1.0,1.5,2.0,2.5):
        assert state(a,r)["state"] == state(b,r)["state"]
        assert state(a,r)["net_plan_r"] == state(b,r)["net_plan_r"]
    assert a["full_horizon_mfe_r"] == b["full_horizon_mfe_r"]


@pytest.mark.parametrize("horizon,cost", [(0,.02),(True,.02),(1,-.1),(1,float("nan")),(1,True)])
def test_bad_analysis_configuration_rejected(horizon,cost):
    with pytest.raises(ValueError):
        run([bar()],horizon=horizon,cost=cost)


def test_group_denominators_include_censoring_and_overlap_warning():
    a=run([bar(h=125)]); b=run([])
    report=summarize_outcomes([a,b])
    total=report["overall"]["thresholds"]["1.0"]
    assert report["overall"]["observations"] == 2
    assert sum(total["states"].values()) == 2 and total["settled_count"] == 1
    assert report["groups"]["failed_clause"]["family"]["observations"] == 2
    assert report["groups"]["failed_clause"]["quality"]["observations"] == 2
    assert any("not independent" in s for s in report["limitations"])


def stored_row(*, event_id="r8-test-1", frozen=True, minute=0, **ohlc):
    p,s,e=fixture(event_id=event_id,issued=minute+15,expiry=minute+60)
    p.update(time=stamp(minute),**ohlc)
    decision={"action":"signal_created","signal":s,"approval_envelope":e,"execution":"manual_approval_required"}
    if frozen:
        decision["research_outcome_seed"]=build_outcome_seed(event_id,p,s,e)
    receipt=build_pipeline_receipt(event_id,p,status="analyzed",action="signal_created",signal_id=s["signal_id"])
    return {"event_id":event_id,"status":"ingested","payload":p,
            "result":{"event_id":event_id,"status":"analyzed","receipt":receipt,"decision":decision}}


def test_report_preserves_legacy_provenance_and_never_reexecutes_strategy():
    report=report_from_inbox({"ok":True,"events":[stored_row(frozen=False)]},as_of=BASE+timedelta(hours=1))
    assert report["outcomes"][0]["provenance"] == "LEGACY_RECONSTRUCTED_GEOMETRY"
    assert report["outcomes"][0]["entry"] is None
    assert report["source_scope"] == "BOUNDED_INBOX_NOT_COMPLETE_HISTORY"


def test_report_settles_only_from_validated_future_source_bars():
    rows=[stored_row(),stored_row(event_id="r8-test-2",minute=15,high=125)]
    report=report_from_inbox({"ok":True,"events":rows},as_of=BASE+timedelta(minutes=30),horizon_bars=1)
    assert state(report["outcomes"][0],2.5)["state"] == "TARGET_FIRST"
    assert report["outcomes"][1]["status"] == "CENSORED"


def test_corrupt_receipt_and_conflicting_event_ids_quarantined():
    a=stored_row();b=deepcopy(a);b["payload"]["close"]=111
    report=report_from_inbox({"ok":True,"events":[a,b]},as_of=BASE+timedelta(hours=1))
    assert report["outcomes"] == [] and report["quarantine_counts"]["conflicting_event_duplicates"] == 2
    report=report_from_inbox({"ok":True,"events":[b]},as_of=BASE+timedelta(hours=1))
    assert report["quarantine_counts"]["receipt_mismatch"] == 1


def test_report_rejects_seed_of_other_event():
    row=stored_row();row["result"]["decision"]["research_outcome_seed"]=seed(event_id="another")
    report=report_from_inbox({"ok":True,"events":[row]},as_of=BASE+timedelta(hours=1))
    assert report["outcomes"] == [] and report["quarantine_counts"]["seed_source_identity_mismatch"] == 1


def test_report_duplicate_replay_does_not_inflate_sample():
    row=stored_row()
    a=report_from_inbox({"ok":True,"events":[row,row]},as_of=BASE+timedelta(hours=1))
    assert a["summary"]["overall"]["observations"] == 1 and a["exact_duplicate_rows_ignored"] == 1


def test_report_with_no_data_does_not_invent_performance():
    a=report_from_inbox({"ok":True,"events":[]},as_of=BASE)
    assert a["summary"]["overall"]["observations"] == 0
    assert a["summary"]["overall"]["thresholds"]["1.0"]["settled_mean_net_plan_r"] is None


def test_cli_fixture_round_trip_and_no_write_endpoint(tmp_path):
    source=tmp_path/"inbox.json";target=tmp_path/"report.json"
    source.write_text(json.dumps({"ok":True,"events":[stored_row()]}))
    result=subprocess.run([sys.executable,"scripts/run_outcome_attribution.py","--input",str(source),"--output",str(target),"--as-of",stamp(120)],capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(target.read_text())["live_authorized"] is False
    cli=Path("scripts/run_outcome_attribution.py").read_text()
    assert ".inbox(" in cli and ".claim(" not in cli and ".ack(" not in cli


def test_live_event_rejected_signal_gets_no_locked_plan_or_authority():
    from app.event_decision import decide_bridge_event
    p,_,_=fixture()
    p.update(event="bar_close",volume=1000,ema20=99,ema50=95,rsi14=62,macd=5,macd_signal=2,volume_ratio=1.7)
    result=decide_bridge_event(p["event_id"],p)
    assert result["status"] == "analyzed"
    decision=result["decision"]
    assert decision["signal"]["pre_gate_recommendation"] == "LONG"
    assert decision["signal"]["recommendation"] == "WAIT"
    assert decision["locked_trade_plan"] is None
    assert decision["research_outcome_seed"]["live_authorized"] is False
    assert decision["research_outcome_seed"]["provenance"] == "FROZEN_AT_DECISION"
    assert decision["execution"] == "manual_approval_required"


def test_research_seed_failure_does_not_change_live_signal(monkeypatch):
    import app.event_decision as event
    p,_,_=fixture();p.update(event="bar_close",volume=1000,ema20=99,ema50=95,rsi14=62,macd=5,macd_signal=2,volume_ratio=1.7)
    baseline=event.decide_bridge_event(p["event_id"],p)
    def broken(*args,**kwargs):
        raise ValueError("synthetic_failure")
    monkeypatch.setattr(event,"build_outcome_seed",broken)
    actual=event.decide_bridge_event(p["event_id"],p)
    assert actual["decision"]["signal"] == baseline["decision"]["signal"]
    assert actual["decision"]["research_outcome_seed"] is None
    assert actual["decision"]["research_outcome_seed_error"] == "ValueError"
    assert actual["decision"]["locked_trade_plan"] == baseline["decision"]["locked_trade_plan"]
