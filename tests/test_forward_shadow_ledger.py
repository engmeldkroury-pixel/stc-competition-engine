from dataclasses import replace

import pytest

from app.forward_shadow_ledger import (
    MTF_FORWARD_NOT_BEFORE_UTC,
    ForwardShadowRecord,
    PriceBar,
    evaluate_outcome,
    mtf_candidate_sha256,
    mtf_protocol_sha256,
    record_sha256,
    regime_record,
)
from app.mtf_shadow import ShadowSignal
from app.r10_regime_session_shadow import shadow_decision


def directional_record(direction="LONG"):
    if direction == "LONG":
        entry, stop, target = 100.0, 99.0, 102.0
    else:
        entry, stop, target = 100.0, 101.0, 98.0
    return ForwardShadowRecord(
        registry_id="R10-FORWARD-SHADOW-REGISTRY-V1",
        protocol_id="test",
        protocol_sha256="p",
        candidate_sha256="c",
        symbol="CAPITALCOM:TEST",
        source_open_utc="2026-09-28T12:00:00Z",
        decision=direction,
        reason="test",
        entry_bar_ts=1_000_000_000,
        entry=entry,
        stop=stop,
        target=target,
        planned_risk=1.0,
        evaluation_horizon_bars=32,
    )


def test_candidate_and_protocol_digests_are_stable_and_symbol_specific():
    assert MTF_FORWARD_NOT_BEFORE_UTC == "2026-09-28T07:00:00Z"
    assert mtf_candidate_sha256("CAPITALCOM:ETHUSD") == mtf_candidate_sha256("CAPITALCOM:ETHUSD")
    assert mtf_candidate_sha256("CAPITALCOM:ETHUSD") != mtf_candidate_sha256("CAPITALCOM:DOGEUSD")
    assert len(mtf_protocol_sha256()) == 64


def test_record_hash_changes_when_geometry_changes():
    r = directional_record()
    assert record_sha256(r) != record_sha256(replace(r, target=103.0))


def test_regime_wait_has_no_trade_geometry():
    snapshot = {
        "source_open_utc": "2026-09-28T12:00:00Z",
        "open": 100.0, "close": 100.0,
        "ema20": 100.0, "ema50": 100.0, "ema200": 100.0,
        "atr14": 1.0, "adx14": 25.0, "rsi14": 50.0,
        "zscore20": 0.0, "range_atr": 1.0,
    }
    result = shadow_decision(snapshot)
    rec = regime_record(symbol="CAPITALCOM:TEST", snapshot=snapshot, decision_result=result, next_bar=None)
    assert rec.decision == "WAIT"
    assert rec.entry is rec.stop is rec.target is None
    assert rec.research_only is True and rec.live_authorized is False


def test_regime_directional_geometry_is_next_bar_open_and_research_only():
    snapshot = {
        "source_open_utc": "2026-09-28T13:00:00Z",
        "open": 100.0, "close": 100.2,
        "ema20": 100.0, "ema50": 99.0, "ema200": 98.0,
        "atr14": 1.0, "adx14": 31.0, "rsi14": 55.0,
        "zscore20": 0.4, "range_atr": 1.0,
    }
    result = shadow_decision(snapshot)
    next_bar = PriceBar(1790601300, 100.1, 100.5, 99.8, 100.3)
    rec = regime_record(symbol="CAPITALCOM:TEST", snapshot=snapshot, decision_result=result, next_bar=next_bar)
    assert rec.decision == "LONG"
    assert rec.entry == pytest.approx(100.1)
    assert rec.stop == pytest.approx(98.6)
    assert rec.target == pytest.approx(103.1)
    assert rec.planned_risk == pytest.approx(1.5)
    assert rec.execution == "none"


def test_regime_pre_forward_observation_is_rejected():
    snapshot = {
        "source_open_utc": "2026-09-28T11:45:00Z",
        "open": 100.0, "close": 100.2,
        "ema20": 100.0, "ema50": 99.0, "ema200": 98.0,
        "atr14": 1.0, "adx14": 31.0, "rsi14": 55.0,
        "zscore20": 0.4, "range_atr": 1.0,
    }
    result = shadow_decision(snapshot)
    with pytest.raises(ValueError, match="pre_forward_boundary"):
        regime_record(
            symbol="CAPITALCOM:TEST",
            snapshot=snapshot,
            decision_result=result,
            next_bar=PriceBar(1790596800, 100.1, 100.2, 99.9, 100.0),
        )


def test_outcome_target_and_cost_in_planned_r():
    r = directional_record()
    bars = [PriceBar(r.entry_bar_ts + i * 900, 100.0, 102.1 if i == 0 else 100.2, 99.5, 100.1) for i in range(32)]
    out = evaluate_outcome(r, bars, cost_bps=2)
    assert out.status == "TARGET"
    assert out.net_planned_r == pytest.approx(2.0 - 0.02)
    assert out.mfe_r >= 2.0


def test_same_bar_stop_and_target_is_conservative_stop_first():
    r = directional_record()
    bars = [PriceBar(r.entry_bar_ts, 100.0, 102.2, 98.8, 100.0)]
    out = evaluate_outcome(r, bars)
    assert out.status == "AMBIGUOUS_STOP_FIRST"
    assert out.net_planned_r < -1.0
    assert out.post_stop_target_touched is True


def test_stop_gap_uses_open_not_stop_price():
    r = directional_record()
    bars = [PriceBar(r.entry_bar_ts, 98.5, 99.0, 98.0, 98.8)]
    out = evaluate_outcome(r, bars, cost_bps=0)
    assert out.status == "STOP_GAP"
    assert out.exit_price == pytest.approx(98.5)
    assert out.net_planned_r == pytest.approx(-1.5)


def test_missing_bar_interval_censors_instead_of_interpolating():
    r = directional_record()
    bars = [
        PriceBar(r.entry_bar_ts, 100.0, 100.4, 99.6, 100.1),
        PriceBar(r.entry_bar_ts + 1800, 100.1, 100.4, 99.8, 100.0),
    ]
    out = evaluate_outcome(r, bars)
    assert out.status == "CENSORED_MISSING_BAR"
    assert out.bars_observed == 1


def test_wait_outcome_has_no_profit_claim():
    r = replace(
        directional_record(),
        decision="WAIT",
        entry_bar_ts=None,
        entry=None,
        stop=None,
        target=None,
        planned_risk=None,
    )
    out = evaluate_outcome(r, [])
    assert out.status == "WAIT"
    assert out.net_planned_r is None
