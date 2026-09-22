from app.research_costs import (
    ASSET_ROUND_TRIP_ATR_FRICTION,
    estimate_research_cost_r,
    research_cost_policy,
)


def test_capital_research_cost_includes_profile_commission_and_market_friction():
    estimate = estimate_research_cost_r(
        "CAPITALCOM:XAUUSD",
        reference_price=4300.0,
        atr=20.0,
        planned_risk_per_unit=34.0,
    )
    assert estimate.commission_rate == 0.0001
    assert estimate.commission_price_units == 0.86
    assert estimate.market_friction_price_units == 0.8
    assert 0.04 < estimate.total_r < 0.06
    assert "Research-only" in estimate.note


def test_amp_research_cost_keeps_nonzero_friction_even_with_zero_profile_commission():
    estimate = estimate_research_cost_r(
        "COMEX_MINI:MGC1!",
        reference_price=4300.0,
        atr=20.0,
        planned_risk_per_unit=34.0,
    )
    assert estimate.commission_rate == 0.0
    assert estimate.commission_price_units == 0.0
    assert estimate.total_r > 0


def test_crypto_friction_assumption_is_more_conservative_than_forex():
    assert ASSET_ROUND_TRIP_ATR_FRICTION["crypto"] > ASSET_ROUND_TRIP_ATR_FRICTION["forex"]
    policy = research_cost_policy("CAPITALCOM:BTCUSD")
    assert policy["authority"] == "research_only_not_live_quote"
    assert policy["commission_rate_per_side"] == 0.0001
