from app.asset_classification import STRATEGY_ASSET_CLASS, strategy_asset_class
from app.competition_profiles import AMP_CORE_FEED_SYMBOLS, CAPITAL_AFRICA_LIMITS
from app.research_plan import (
    RESEARCH_TIMEFRAMES,
    experiments_for_symbol,
    research_experiments,
    research_plan_summary,
)


def test_all_26_feed_symbols_have_strategy_asset_classification():
    expected = set(CAPITAL_AFRICA_LIMITS) | set(AMP_CORE_FEED_SYMBOLS)
    assert set(STRATEGY_ASSET_CLASS) == expected
    assert len(expected) == 26
    assert strategy_asset_class("CAPITALCOM:XAUUSD") == "metals"
    assert strategy_asset_class("CME_MINI:MES1!") == "indices"
    assert strategy_asset_class("NYMEX:MCL1!") == "energy"
    assert strategy_asset_class("CBOT:ZN1!") == "rates"


def test_every_symbol_has_nonempty_strategy_timeframe_research_plan():
    for symbol in STRATEGY_ASSET_CLASS:
        experiments = experiments_for_symbol(symbol)
        assert experiments, symbol
        assert all(x.symbol == symbol for x in experiments)
        assert all(x.timeframe in RESEARCH_TIMEFRAMES for x in experiments)
        assert all(x.min_bars >= 900 for x in experiments)


def test_research_plan_is_exhaustive_not_one_strategy_for_every_market():
    xau = experiments_for_symbol("CAPITALCOM:XAUUSD")
    mes = experiments_for_symbol("CME_MINI:MES1!")
    zn = experiments_for_symbol("CBOT:ZN1!")
    assert any(x.strategy_id == "smc_structure_liquidity" for x in xau)
    assert any(x.strategy_id == "vwap_intraday" for x in mes)
    assert any(x.strategy_id == "mean_reversion" for x in zn)
    assert not any(x.strategy_id == "microtrend_scalp" for x in zn)
    assert any(x.timeframe == "5" and x.strategy_id == "microtrend_scalp" for x in xau)
    assert any(x.timeframe == "30" and x.strategy_id == "smc_structure_liquidity" for x in xau)


def test_research_matrix_has_no_duplicate_experiments():
    experiments = research_experiments()
    keys = {
        (x.competition_id, x.symbol, x.timeframe, x.strategy_id)
        for x in experiments
    }
    assert len(keys) == len(experiments)


def test_research_plan_summary_counts_all_symbols_and_experiments():
    summary = research_plan_summary()
    assert summary["symbols"] == 26
    assert summary["experiments"] == len(research_experiments())
    assert summary["experiments"] > 100
    assert set(summary["timeframes"]) == {"5", "15", "30", "60", "120", "240", "1D"}
    assert sum(summary["by_competition"].values()) == summary["experiments"]
