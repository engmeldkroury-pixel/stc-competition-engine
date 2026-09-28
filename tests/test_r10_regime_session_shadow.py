from copy import deepcopy

import pytest

from app.r10_regime_session_shadow import (
    FROZEN_PROTOCOL, classify_regime, forward_eligible, in_session,
    protocol_sha256, shadow_decision,
)


def snap(**updates):
    base = {
        "source_open_utc": "2026-09-28T13:00:00Z",
        "open": 100.0, "close": 100.2,
        "ema20": 100.0, "ema50": 99.0, "ema200": 98.0,
        "atr14": 1.0, "adx14": 31.0, "rsi14": 55.0,
        "zscore20": 0.4, "range_atr": 1.0,
    }
    base.update(updates)
    return base


def test_protocol_is_frozen_research_only_and_has_stable_digest():
    assert FROZEN_PROTOCOL.research_only is True
    assert FROZEN_PROTOCOL.live_authorized is False
    assert FROZEN_PROTOCOL.not_before_utc == "2026-09-28T12:00:00Z"
    assert protocol_sha256() == protocol_sha256()


def test_session_is_half_open_and_utc_explicit():
    assert in_session("2026-09-28T12:00:00Z")
    assert in_session("2026-09-28T16:59:59Z")
    assert not in_session("2026-09-28T11:59:59Z")
    assert not in_session("2026-09-28T17:00:00Z")
    with pytest.raises(ValueError):
        in_session("2026-09-28T13:00:00")


def test_forward_boundary_is_not_backdated():
    assert not forward_eligible("2026-09-28T11:59:59Z")
    assert forward_eligible("2026-09-28T12:00:00Z")


def test_regime_thresholds_are_frozen():
    assert classify_regime(30.0) == "TREND"
    assert classify_regime(20.0) == "RANGE"
    assert classify_regime(25.0) == "NEUTRAL"


def test_trend_long_and_short_are_directionally_symmetric():
    long = shadow_decision(snap())
    short = shadow_decision(snap(open=100.0, close=99.8, ema20=100.0, ema50=101.0,
                                 ema200=102.0, rsi14=45.0))
    assert long["decision"] == "LONG" and long["reason"] == "trend_pullback"
    assert short["decision"] == "SHORT" and short["reason"] == "trend_pullback"
    for result in (long, short):
        assert result["research_only"] is True and result["live_authorized"] is False
        assert result["execution"] == "none"
        assert "quantity" not in result and "approval" not in result


def test_anti_chase_extension_rejects_overextended_trend_bar():
    result = shadow_decision(snap(close=101.0))
    assert result["decision"] == "WAIT"
    assert result["extension_atr"] == pytest.approx(1.0)


def test_range_extreme_fades_both_directions():
    short = shadow_decision(snap(adx14=18.0, zscore20=2.2, rsi14=72.0))
    long = shadow_decision(snap(adx14=18.0, zscore20=-2.2, rsi14=28.0))
    assert short["decision"] == "SHORT" and short["regime"] == "RANGE"
    assert long["decision"] == "LONG" and long["regime"] == "RANGE"


def test_outside_session_is_wait_even_if_features_match():
    result = shadow_decision(snap(source_open_utc="2026-09-28T18:00:00Z"))
    assert result["decision"] == "WAIT"
    assert result["reason"] == "outside_session"


def test_neutral_regime_is_wait():
    result = shadow_decision(snap(adx14=25.0))
    assert result["decision"] == "WAIT" and result["regime"] == "NEUTRAL"


def test_input_is_not_mutated_and_missing_or_nonfinite_features_fail_closed():
    source = snap(); before = deepcopy(source)
    shadow_decision(source)
    assert source == before
    bad = snap(); bad.pop("rsi14")
    with pytest.raises(ValueError, match="missing_features"):
        shadow_decision(bad)
    with pytest.raises(ValueError, match="finite_number"):
        shadow_decision(snap(adx14=float("nan")))
