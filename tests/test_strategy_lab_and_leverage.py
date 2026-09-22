from app.indicator_catalog import family_weight_total, feature_count, feature_family
from app.leverage import leverage_capacity
from app.strategy_lab import (
    StrategyTrial,
    candidate_strategies,
    select_strategy,
    trial_rejection_reasons,
)


def _trial(strategy_id: str, *, test_expectancy: float, forward_expectancy: float) -> StrategyTrial:
    return StrategyTrial(
        strategy_id=strategy_id,
        symbol="CAPITALCOM:XAUUSD",
        timeframe="60",
        train_trades=180,
        test_trades=80,
        forward_trades=30,
        train_expectancy_r=0.35,
        test_expectancy_r=test_expectancy,
        forward_expectancy_r=forward_expectancy,
        test_profit_factor=1.42,
        forward_profit_factor=1.28,
        test_win_rate=0.56,
        max_drawdown_r=5.5,
        parameter_stability=0.82,
        regime_stability=0.78,
    )


def test_indicator_catalog_is_broad_but_family_weighted_not_vote_counted():
    assert feature_count() >= 80
    assert abs(family_weight_total() - 1.0) < 1e-12
    assert "rsi_14" in feature_family("momentum").features
    assert "order_block" in feature_family("smc_liquidity").features
    assert feature_family("momentum").max_family_weight < 0.20


def test_strategy_candidates_are_symbol_class_and_timeframe_specific():
    ids = {s.strategy_id for s in candidate_strategies("metals", "60")}
    assert "smc_structure_liquidity" in ids
    assert "trend_pullback" in ids
    assert "mean_reversion" in ids
    assert "microtrend_scalp" not in ids


def test_selector_prefers_out_of_sample_and_forward_robustness():
    weak = _trial("trend_pullback", test_expectancy=0.09, forward_expectancy=0.01)
    strong = _trial("smc_structure_liquidity", test_expectancy=0.28, forward_expectancy=0.22)
    selected = select_strategy([weak, strong])
    assert selected.status == "VALIDATED"
    assert selected.strategy_id == "smc_structure_liquidity"


def test_selector_rejects_pretty_backtest_with_bad_forward():
    overfit = StrategyTrial(
        strategy_id="breakout_expansion",
        symbol="CME_MINI:MNQ1!",
        timeframe="15",
        train_trades=250,
        test_trades=70,
        forward_trades=20,
        train_expectancy_r=0.8,
        test_expectancy_r=0.2,
        forward_expectancy_r=-0.05,
        test_profit_factor=1.35,
        forward_profit_factor=0.92,
        test_win_rate=0.58,
        max_drawdown_r=6.0,
        parameter_stability=0.75,
        regime_stability=0.70,
    )
    selected = select_strategy([overfit])
    assert selected.status == "NO_VALIDATED_STRATEGY"
    assert selected.strategy_id is None
    assert any("negative_forward_expectancy" in r for r in selected.reasons)


def test_amp_leverage_is_fixed_20_to_1_and_quantity_controls_exposure():
    cap = leverage_capacity(
        "amp-futures-sep-2026",
        "CME_MINI:MES1!",
        price=7000,
        quantity=2,
        equity_usd=250000,
    )
    assert cap.official_leverage == 20.0
    assert cap.notional_usd == 70000.0
    assert cap.margin_required_usd == 3500.0
    assert cap.within_margin_budget is True


def test_capital_crypto_has_no_leverage_but_forex_has_25_to_1():
    btc = leverage_capacity(
        "capital-africa-sep-2026",
        "CAPITALCOM:BTCUSD",
        price=85000,
        quantity=0.2,
        equity_usd=100000,
    )
    eur = leverage_capacity(
        "capital-africa-sep-2026",
        "CAPITALCOM:EURUSD",
        price=1.18,
        quantity=100000,
        equity_usd=100000,
    )
    assert btc.official_leverage == 1.0
    assert eur.official_leverage == 25.0



def test_trial_diagnostics_expose_rejection_reasons():
    overfit = StrategyTrial(
        strategy_id="breakout_expansion",
        symbol="CME_MINI:MNQ1!",
        timeframe="15",
        train_trades=250,
        test_trades=20,
        forward_trades=20,
        train_expectancy_r=0.8,
        test_expectancy_r=0.01,
        forward_expectancy_r=-0.05,
        test_profit_factor=0.95,
        forward_profit_factor=0.92,
        test_win_rate=0.48,
        max_drawdown_r=6.0,
        parameter_stability=0.50,
        regime_stability=0.40,
    )
    reasons = trial_rejection_reasons(overfit)
    assert "insufficient_out_of_sample_trades" in reasons
    assert "weak_out_of_sample_expectancy" in reasons
    assert "negative_forward_expectancy" in reasons
