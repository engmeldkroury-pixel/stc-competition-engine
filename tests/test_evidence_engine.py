from app.evidence_engine import (
    NewsMacroContext,
    aggregate_evidence,
    aggregate_live_family_scores,
    apply_news_macro_overlay,
    make_observation,
)


def test_correlated_momentum_indicators_do_not_get_full_independent_votes():
    one = aggregate_evidence([
        make_observation("rsi_14", "momentum", 0.9),
    ])
    many_correlated = aggregate_evidence([
        make_observation("rsi_14", "momentum", 0.9),
        make_observation("stochastic", "momentum", 0.9),
        make_observation("stoch_rsi", "momentum", 0.9),
        make_observation("cci", "momentum", 0.9),
    ])
    assert many_correlated.score <= one.score + 0.05
    assert many_correlated.independent_confirmations == 1


def test_structural_confirmations_carry_more_reliability_than_oscillator_only_setup():
    structural = aggregate_evidence([
        make_observation("liquidity_sweep", "smc_liquidity", 0.9),
        make_observation("choch", "market_structure", 0.9),
        make_observation("break_retest", "market_structure", 0.85),
        make_observation("relative_volume", "volume", 0.7),
    ], strategy_id="smc_structure_liquidity")
    oscillator = aggregate_evidence([
        make_observation("rsi_14", "momentum", 0.9),
        make_observation("stochastic", "momentum", 0.9),
        make_observation("cci", "momentum", 0.9),
    ], strategy_id="smc_structure_liquidity")
    assert structural.score > oscillator.score
    assert structural.hard_confirmations >= 2
    assert structural.independent_confirmations >= 3


def test_conflicting_family_is_reported_instead_of_hidden():
    summary = aggregate_evidence([
        make_observation("bos", "market_structure", 0.9),
        make_observation("liquidity_sweep", "smc_liquidity", 0.8),
        make_observation("rsi_14", "momentum", -0.9),
    ])
    assert summary.score > 0
    assert "momentum_conflicts_with_dominant_direction" in summary.conflicts


def test_news_and_macro_cannot_create_large_directional_signal():
    overlay = apply_news_macro_overlay(
        0.0,
        NewsMacroContext(
            news_direction=1.0,
            news_relevance=1.0,
            news_freshness=1.0,
            macro_direction=1.0,
            macro_relevance=1.0,
        ),
    )
    assert overlay.adjusted_score <= 0.10
    assert overlay.directional_overlay <= 0.10


def test_imminent_high_impact_event_blocks_entry_without_reversing_technical_thesis():
    overlay = apply_news_macro_overlay(
        0.82,
        NewsMacroContext(
            scheduled_high_impact=True,
            minutes_to_event=8,
            macro_direction=-1.0,
            macro_relevance=1.0,
        ),
    )
    assert overlay.entry_blocked is True
    assert overlay.technical_score == 0.82
    assert overlay.adjusted_score > 0
    assert "scheduled_high_impact_event_imminent" in overlay.reasons


def test_conflicting_news_reduces_size_but_does_not_flip_strong_technical_direction():
    overlay = apply_news_macro_overlay(
        0.78,
        NewsMacroContext(
            news_direction=-1.0,
            news_relevance=1.0,
            news_freshness=1.0,
            macro_direction=-1.0,
            macro_relevance=1.0,
        ),
    )
    assert overlay.adjusted_score > 0
    assert overlay.size_multiplier == 0.75
    assert "news_macro_context_conflicts_with_technical" in overlay.reasons


def test_unscheduled_shock_fails_closed():
    overlay = apply_news_macro_overlay(
        -0.8,
        NewsMacroContext(unscheduled_shock=True),
    )
    assert overlay.entry_blocked is True
    assert overlay.size_multiplier == 0.0
    assert "unscheduled_market_shock" in overlay.reasons


from app.weight_calibration import (
    FeaturePerformance,
    calibrate_feature_reliability,
    participation_percent,
)


def test_small_sample_cannot_turn_feature_into_near_certain_signal():
    perf = FeaturePerformance(
        feature="liquidity_sweep",
        symbol="CAPITALCOM:XAUUSD",
        strategy_id="smc_structure_liquidity",
        timeframe="60",
        sample_size=8,
        directional_hits=8,
        average_forward_r=0.8,
        profit_factor_when_present=3.0,
        regime_stability=1.0,
    )
    r = calibrate_feature_reliability(perf, prior_reliability=0.91)
    assert r.calibrated_reliability < 0.95
    assert r.sample_confidence < 0.25


def test_negative_forward_expectancy_penalizes_indicator_weight():
    good = FeaturePerformance(
        feature="bos",
        symbol="CME_MINI:MES1!",
        strategy_id="trend_pullback",
        timeframe="60",
        sample_size=100,
        directional_hits=65,
        average_forward_r=0.25,
        profit_factor_when_present=1.5,
        regime_stability=0.8,
    )
    bad = FeaturePerformance(
        feature="bos",
        symbol="CME_MINI:MES1!",
        strategy_id="trend_pullback",
        timeframe="60",
        sample_size=100,
        directional_hits=65,
        average_forward_r=-0.3,
        profit_factor_when_present=0.8,
        regime_stability=0.8,
    )
    rg = calibrate_feature_reliability(good, prior_reliability=0.92)
    rb = calibrate_feature_reliability(bad, prior_reliability=0.92)
    assert rg.calibrated_reliability > rb.calibrated_reliability


def test_participation_percent_is_transparent_and_normalized():
    p = participation_percent({"structure": 0.4, "trend": 0.3, "volume": 0.2, "news": 0.1})
    assert round(sum(p.values()), 10) == 100.0
    assert p["structure"] == 40.0
    assert p["news"] == 10.0



def _family_bundle(value=0.8):
    return {
        "trend": value,
        "momentum": value,
        "volatility": value,
        "volume": value,
        "vwap": value,
        "market_structure": value,
        "smc_liquidity": value,
        "price_action": value,
        "microstructure": value,
    }


def test_live_family_evidence_requires_complete_bundle_and_broad_agreement():
    assert aggregate_live_family_scores({"trend": 0.9}) is None
    result = aggregate_live_family_scores(_family_bundle(0.8))
    assert result is not None
    assert result.score > 0.70
    assert result.agreement_ratio == 1.0
    assert result.aligned_families == 9
    assert result.conflicting_families == 0


def test_live_family_conflicts_are_counted_and_reduce_agreement():
    scores = _family_bundle(0.8)
    scores["momentum"] = -0.9
    scores["price_action"] = -0.8
    result = aggregate_live_family_scores(scores)
    assert result is not None
    assert result.conflicting_families == 2
    assert result.agreement_ratio < 1.0
    assert result.aligned_families >= 5



def test_live_family_calibration_softly_reweights_without_erasing_priors():
    scores = _family_bundle(0.20)
    scores["market_structure"] = 0.95
    scores["smc_liquidity"] = 0.90
    scores["momentum"] = -0.60

    baseline = aggregate_live_family_scores(scores, strategy_id="smc_structure_liquidity")
    calibrated = aggregate_live_family_scores(
        scores,
        strategy_id="smc_structure_liquidity",
        family_weight_override={
            "market_structure": 0.55,
            "smc_liquidity": 0.35,
            "volume": 0.10,
        },
    )
    assert baseline is not None and calibrated is not None
    assert calibrated.score > baseline.score
    assert calibrated.family_weights_used["market_structure"] > baseline.family_weights_used["market_structure"]
    assert calibrated.family_weights_used["momentum"] > 0
    assert calibrated.strategy_id == "smc_structure_liquidity"
