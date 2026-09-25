from datetime import datetime, timezone

import pytest

from app.portfolio import (
    AMP_PRICE_VALUE_USD_PER_PRICE_UNIT,
    MarketState,
    PositionState,
    aggregate_open_risk,
    choose_rotation_candidate,
    price_value_usd_per_price_unit,
    propose_position_size,
    risk_cluster,
    supervise_position,
)

UTC = timezone.utc


def pos(**overrides):
    data = dict(
        position_id="p-1",
        competition_id="amp-futures-sep-2026",
        symbol="CME_MINI:MES1!",
        side="LONG",
        quantity=2,
        entry_price=7800.0,
        initial_stop=7780.0,
        current_stop=7780.0,
        target1=7830.0,
        target2=7850.0,
        opened_at_utc=datetime(2026, 9, 21, 18, 0, tzinfo=UTC),
        source_plan_id="plan-1",
    )
    data.update(overrides)
    return PositionState(**data)


def market(**overrides):
    data = dict(
        current_price=7810.0,
        recommendation="LONG",
        composite_score=0.50,
        recent_recommendations=("LONG", "LONG"),
        recent_scores=(0.45, 0.50),
    )
    data.update(overrides)
    return MarketState(**data)


def test_verified_amp_core_contract_values():
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:MES1!"] == 5
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:MNQ1!"] == 2
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CBOT_MINI:MYM1!"] == 0.5
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:M2K1!"] == 5
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["NYMEX:MCL1!"] == 100
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["NYMEX:MNG1!"] == 1000
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["COMEX_MINI:MGC1!"] == 10
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["COMEX_MINI:SIL1!"] == 1000
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:M6E1!"] == 12500
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:M6B1!"] == 6250
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:MJY1!"] == 1_250_000
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME_MINI:M6A1!"] == 10000
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME:MBT1!"] == 0.1
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CME:MET1!"] == 0.1
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CBOT:ZN1!"] == 1000
    assert AMP_PRICE_VALUE_USD_PER_PRICE_UNIT["CBOT:ZB1!"] == 1000


def test_usdzar_converts_quote_currency_risk_back_to_usd():
    value = price_value_usd_per_price_unit(
        "capital-africa-sep-2026",
        "CAPITALCOM:USDZAR",
        reference_price=18.0,
    )
    assert value == pytest.approx(1 / 18.0)


def test_amp_sizing_is_integer_and_respects_risk_budget():
    result = propose_position_size(
        competition_id="amp-futures-sep-2026",
        symbol="CME_MINI:MES1!",
        equity=250_000,
        risk_fraction=0.005,
        entry_price=7800,
        stop_price=7780,
    )
    # $100 stop risk / MES contract, $1,250 risk budget => 12 contracts.
    assert result.stop_risk_usd_per_unit == 100
    assert result.proposed_quantity == 12
    assert result.risk_amount_usd == 1200
    assert result.quantity_is_integer_contracts is True
    assert result.allowed_by_position_limit is True


def test_position_size_never_exceeds_competition_maximum():
    result = propose_position_size(
        competition_id="amp-futures-sep-2026",
        symbol="CME_MINI:MES1!",
        equity=250_000,
        risk_fraction=0.02,
        entry_price=7800,
        stop_price=7799.5,
        current_open_quantity=499,
    )
    assert result.proposed_quantity == 1
    assert result.projected_open_quantity == 500


def test_risk_fraction_above_two_percent_is_rejected():
    with pytest.raises(ValueError, match="risk_fraction"):
        propose_position_size(
            competition_id="amp-futures-sep-2026",
            symbol="CME_MINI:MES1!",
            equity=250_000,
            risk_fraction=0.021,
            entry_price=7800,
            stop_price=7780,
        )


def test_hold_when_thesis_is_not_invalidated():
    advice = supervise_position(pos(), market())
    assert advice.action == "HOLD"
    assert advice.thesis_degraded is False


def test_stop_breach_is_critical_exit():
    advice = supervise_position(pos(), market(current_price=7779))
    assert advice.action == "EXIT_NOW"
    assert advice.urgency == "critical"
    assert advice.thesis_degraded is True


def test_single_opposite_bar_does_not_force_exit():
    advice = supervise_position(
        pos(),
        market(
            current_price=7790,
            recommendation="SHORT",
            composite_score=-0.70,
            recent_recommendations=("LONG", "SHORT"),
            recent_scores=(0.40, -0.70),
        ),
    )
    assert advice.action == "HOLD"


def test_two_strong_opposite_closed_bars_exit_to_prevent_thesis_drift():
    advice = supervise_position(
        pos(),
        market(
            current_price=7790,
            recommendation="SHORT",
            composite_score=-0.70,
            recent_recommendations=("SHORT", "SHORT"),
            recent_scores=(-0.60, -0.70),
        ),
    )
    assert advice.action == "EXIT_NOW"
    assert advice.thesis_degraded is True


def test_target1_recommends_partial_profit_and_breakeven_protection():
    advice = supervise_position(pos(), market(current_price=7831))
    assert advice.action == "PARTIAL_TAKE_PROFIT"
    assert advice.suggested_partial_fraction == 0.50
    assert advice.suggested_stop == 7800


def test_one_r_profit_recommends_protection_not_rotation():
    advice = supervise_position(
        pos(target1=7860, target2=7900),
        market(current_price=7821),
    )
    assert advice.action == "PROTECT"
    assert advice.suggested_stop > 7800


def test_peak_r_retrace_exits_to_protect_competition_score():
    advice = supervise_position(
        pos(target1=7890, target2=7920),
        market(
            current_price=7831,
            peak_r_multiple=2.90,
        ),
    )
    assert advice.action == "EXIT_NOW"
    assert advice.urgency == "high"
    assert "profit_retrace_breached_dynamic_floor" in advice.reasons


def test_peak_r_progressive_lock_raises_stop_without_forcing_exit():
    advice = supervise_position(
        pos(target1=7890, target2=7920),
        market(
            current_price=7850,
            peak_r_multiple=2.80,
        ),
    )
    # 2.80R peak -> dynamic floor 2.05R -> 7800 + 2.05 * 20 = 7841.
    assert advice.action == "PROTECT"
    assert advice.suggested_stop == pytest.approx(7841.0)
    assert "progressive_profit_lock_from_closed_bar_high_water" in advice.reasons


def test_rotation_requires_degraded_thesis_and_material_score_advantage():
    p = pos()
    degraded = supervise_position(
        p,
        market(
            current_price=7790,
            recommendation="SHORT",
            composite_score=-0.60,
            recent_recommendations=("SHORT", "SHORT"),
            recent_scores=(-0.60, -0.60),
        ),
    )
    opps = [
        {
            "competition_id": "amp-futures-sep-2026",
            "symbol": "CME_MINI:MNQ1!",
            "recommendation": "LONG",
            "composite_score": 0.90,
            "locked_trade_plan": {"plan_id": "plan-new"},
        },
        {
            "competition_id": "capital-africa-sep-2026",
            "symbol": "CAPITALCOM:XAUUSD",
            "recommendation": "LONG",
            "composite_score": 1.0,
            "locked_trade_plan": {"plan_id": "wrong-account"},
        },
    ]
    rotation = choose_rotation_candidate(
        position=p,
        advice=degraded,
        current_alignment_score=0.40,
        opportunities=opps,
    )
    assert rotation is not None
    assert rotation.to_symbol == "CME_MINI:MNQ1!"


def test_stronger_signal_never_rotates_healthy_position():
    p = pos()
    healthy = supervise_position(p, market())
    rotation = choose_rotation_candidate(
        position=p,
        advice=healthy,
        current_alignment_score=0.40,
        opportunities=[
            {
                "competition_id": "amp-futures-sep-2026",
                "symbol": "CME_MINI:MNQ1!",
                "recommendation": "LONG",
                "composite_score": 1.0,
                "locked_trade_plan": {"plan_id": "plan-new"},
            }
        ],
    )
    assert rotation is None


def test_aggregate_open_risk_is_separate_by_competition():
    p1 = pos(quantity=2)
    p2 = PositionState(
        position_id="p-2",
        competition_id="capital-africa-sep-2026",
        symbol="CAPITALCOM:XAUUSD",
        side="SHORT",
        quantity=5,
        entry_price=4350,
        initial_stop=4360,
        current_stop=4360,
        target1=4335,
        target2=4325,
        opened_at_utc=datetime(2026, 9, 21, 18, 0, tzinfo=UTC),
    )
    result = aggregate_open_risk([p1, p2])
    assert result["amp-futures-sep-2026"]["initial_risk_usd"] == 200
    assert result["capital-africa-sep-2026"]["initial_risk_usd"] == 50



def test_risk_cluster_groups_known_correlated_exposures():
    assert risk_cluster("CME_MINI:MES1!") == "equity_indices"
    assert risk_cluster("CAPITALCOM:NAS100") == "equity_indices"
    assert risk_cluster("CME:MBT1!") == "crypto"
    assert risk_cluster("CAPITALCOM:BTCUSD") == "crypto"
    assert risk_cluster("COMEX_MINI:MGC1!") == "metals"
    assert risk_cluster("CAPITALCOM:XAUUSD") == "metals"


def test_position_sizing_is_reduced_by_cluster_capacity_before_new_trade():
    result = propose_position_size(
        competition_id="amp-futures-sep-2026",
        symbol="CME_MINI:MES1!",
        equity=250_000,
        risk_fraction=0.005,
        entry_price=7800,
        stop_price=7780,
        portfolio_open_risk_usd=1000,
        cluster_open_risk_usd=3600,
    )
    # Base trade budget is $1,250, but cluster cap is 3 x 0.5% = $3,750.
    # Only $150 remains in the equity-index cluster, allowing one MES contract
    # at $100 stop risk.
    assert result.cluster_risk_cap_usd == 3750
    assert result.risk_budget_usd == 150
    assert result.proposed_quantity == 1
    assert result.cluster_risk_after_usd == 3700
    assert "correlation_cluster_capacity" in result.risk_budget_limited_by


def test_position_sizing_blocks_when_portfolio_risk_capacity_is_exhausted():
    result = propose_position_size(
        competition_id="amp-futures-sep-2026",
        symbol="CME_MINI:MES1!",
        equity=250_000,
        risk_fraction=0.005,
        entry_price=7800,
        stop_price=7780,
        portfolio_open_risk_usd=7500,
        cluster_open_risk_usd=0,
    )
    assert result.portfolio_risk_cap_usd == 7500
    assert result.risk_budget_usd == 0
    assert result.proposed_quantity == 0
    assert result.allowed_by_position_limit is False
    assert "portfolio_risk_capacity" in result.risk_budget_limited_by


def test_aggregate_open_risk_includes_cluster_breakdown():
    positions = [
        pos(position_id="mes", quantity=2),
        pos(
            position_id="mnq",
            symbol="CME_MINI:MNQ1!",
            quantity=1,
            entry_price=30000,
            initial_stop=29950,
            current_stop=29950,
            target1=30100,
            target2=30200,
        ),
    ]
    result = aggregate_open_risk(positions)["amp-futures-sep-2026"]
    assert result["open_positions"] == 2
    assert result["clusters"]["equity_indices"]["open_positions"] == 2
    # MES: 20 points * $5 * 2 = $200; MNQ: 50 * $2 = $100.
    assert result["clusters"]["equity_indices"]["initial_risk_usd"] == 300
