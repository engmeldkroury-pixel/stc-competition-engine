from __future__ import annotations

import pytest

from app.shadow_weight_recalibration import (
    FrozenOutcomeBatch,
    ShadowOutcome,
    recalibrate_component,
    recalibrate_profile,
)


def _batch(*, result_r: float, hit: bool, count: int = 40, sealed: bool = True):
    return FrozenOutcomeBatch(
        batch_id="batch-1",
        sealed=sealed,
        observations=tuple(
            ShadowOutcome(
                observation_id=f"obs-{i}",
                symbol="CBOT:ZN1!",
                timeframe="15",
                component_id="schaff_trend_cycle",
                result_r=result_r,
                directional_hit=hit,
            )
            for i in range(count)
        ),
    )


def test_unsealed_batch_cannot_recalibrate():
    with pytest.raises(ValueError, match="sealed"):
        recalibrate_component(
            symbol="CBOT:ZN1!",
            timeframe="15",
            component_id="schaff_trend_cycle",
            prior_weight=0.25,
            batch=_batch(result_r=0.2, hit=True, sealed=False),
        )


def test_small_batch_retains_prior_weight():
    row=recalibrate_component(
        symbol="CBOT:ZN1!",
        timeframe="15",
        component_id="schaff_trend_cycle",
        prior_weight=0.25,
        batch=_batch(result_r=0.2, hit=True, count=12),
    )
    assert row.status == "WAIT_FOR_FROZEN_SAMPLE"
    assert row.candidate_weight == row.prior_weight
    assert row.live_authority is False


def test_positive_sealed_batch_can_raise_weight_but_step_is_capped():
    row=recalibrate_component(
        symbol="CBOT:ZN1!",
        timeframe="15",
        component_id="schaff_trend_cycle",
        prior_weight=0.20,
        batch=_batch(result_r=0.35, hit=True, count=60),
        max_relative_step=0.20,
    )
    assert row.candidate_weight > 0.20
    assert row.candidate_weight <= 0.24 + 1e-12
    assert row.live_authority is False


def test_negative_sealed_batch_cannot_raise_weight():
    row=recalibrate_component(
        symbol="CBOT:ZN1!",
        timeframe="15",
        component_id="schaff_trend_cycle",
        prior_weight=0.20,
        batch=_batch(result_r=-0.20, hit=False, count=60),
    )
    assert row.candidate_weight < 0.20
    assert row.relative_change >= -0.25
    assert row.live_authority is False


def test_profile_normalizes_candidate_weights_and_never_grants_live_authority():
    obs=[]
    for i in range(40):
        obs.append(ShadowOutcome(
            observation_id=f"a-{i}",
            symbol="CBOT:ZN1!",
            timeframe="15",
            component_id="schaff_trend_cycle",
            result_r=0.25,
            directional_hit=True,
        ))
        obs.append(ShadowOutcome(
            observation_id=f"b-{i}",
            symbol="CBOT:ZN1!",
            timeframe="15",
            component_id="range_filter_guikroth",
            result_r=-0.10,
            directional_hit=False,
        ))
    profile=recalibrate_profile(
        symbol="CBOT:ZN1!",
        timeframe="15",
        prior_weights={"schaff_trend_cycle":0.5,"range_filter_guikroth":0.5},
        batch=FrozenOutcomeBatch(batch_id="sealed-40",sealed=True,observations=tuple(obs)),
    )
    assert abs(sum(profile.normalized_candidate_weights.values())-1.0) < 1e-12
    assert profile.normalized_candidate_weights["schaff_trend_cycle"] > profile.normalized_candidate_weights["range_filter_guikroth"]
    assert profile.live_authority is False


def test_duplicate_observation_ids_fail_closed():
    row=ShadowOutcome(
        observation_id="dup",
        symbol="CBOT:ZN1!",
        timeframe="15",
        component_id="schaff_trend_cycle",
        result_r=0.2,
        directional_hit=True,
    )
    batch=FrozenOutcomeBatch(batch_id="bad",sealed=True,observations=(row,row))
    with pytest.raises(ValueError,match="duplicate"):
        recalibrate_component(
            symbol="CBOT:ZN1!",
            timeframe="15",
            component_id="schaff_trend_cycle",
            prior_weight=0.20,
            batch=batch,
        )
