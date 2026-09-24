from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.community_indicator_benchmark import (
    CommunityIndicatorTrial,
    IndicatorStats,
    benchmark_symbol_indicators,
    build_symbol_ensemble_profile,
)
from app.community_indicator_catalog import benchmarkable_indicators, catalog_summary, eligible_indicators
from app.community_indicator_signals import indicator_signal_series
from app.community_research_plan import community_research_plan_summary
from app.models import Bar
from app.strategy_lab import StrategyTrial


def _bars(count: int = 700) -> list[Bar]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows: list[Bar] = []
    price = 100.0
    for i in range(count):
        # Deterministic trend/cycle mix creates realistic enough variation for
        # causal adapter and benchmark contract tests.
        drift = 0.035 if (i // 90) % 2 == 0 else -0.030
        cycle = ((i % 17) - 8) * 0.006
        open_ = price
        close = max(1.0, open_ + drift + cycle)
        high = max(open_, close) + 0.18 + (i % 5) * 0.01
        low = min(open_, close) - 0.18 - (i % 3) * 0.01
        rows.append(
            Bar(
                timestamp=start + timedelta(minutes=15 * i),
                open=open_,
                high=high,
                low=low,
                close=close,
                volume=1000 + (i % 31) * 17,
            )
        )
        price = close
    return rows


def test_community_catalog_separates_research_popularity_from_live_weighting():
    summary = catalog_summary()
    assert summary["total"] >= 20
    assert summary["implemented_or_proxy"] >= 20
    assert "never become trading weights" in summary["rule"]

    ids = {x.indicator_id for x in eligible_indicators("rates", "15", implemented_only=True)}
    assert "ut_bot_alerts" in ids
    assert "squeeze_momentum_lazybear" in ids
    assert "wavetrend_crosses" in ids
    assert "hull_suite" in ids


@pytest.mark.parametrize(
    "indicator_id",
    (
        "lorentzian_classification",
        "ut_bot_alerts",
        "squeeze_momentum_lazybear",
        "wavetrend_crosses",
        "hull_suite",
        "supertrend_kivanc",
        "chandelier_exit_everget",
        "schaff_trend_cycle",
        "range_filter_guikroth",
        "alphatrend",
        "optimized_trend_tracker",
        "qqe_mod",
        "ssl_hybrid",
        "waddah_attar_explosion",
        "qqe_ssl_wae_composite",
        "halftrend_everget",
        "trendilo",
        "nadaraya_watson_endpoint_nonrepaint",
        "rsi_kernel_optimized_flux",
        "vumanchu_cipher_b",
    ),
)
def test_community_indicator_adapters_are_causal(indicator_id: str):
    bars = _bars()
    full = indicator_signal_series(indicator_id, bars)
    prefix = indicator_signal_series(indicator_id, bars[:501])
    assert {
        i: value for i, value in full.items() if i < 500
    } == {
        i: value for i, value in prefix.items() if i < 500
    }
    assert all(-1.0 <= value <= 1.0 for value in full.values())



def test_lorentzian_adapter_maps_official_port_buy_sell_stream_exactly():
    from lorentzian_classification import LorentzianClassification, Settings

    bars = _bars(900)
    records = [
        {
            "time": bar.timestamp.isoformat(),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
        }
        for bar in bars
    ]
    official = LorentzianClassification(records, settings=Settings())
    expected = {}
    for i, row in enumerate(official.results):
        if row.buy and not row.sell:
            expected[i] = 1.0
        elif row.sell and not row.buy:
            expected[i] = -1.0

    assert indicator_signal_series("lorentzian_classification", bars) == expected

def test_symbol_benchmark_runs_each_implemented_indicator_independently():
    trials = benchmark_symbol_indicators(
        symbol="CBOT:ZN1!",
        asset_class="rates",
        timeframe="15",
        bars=_bars(),
    )
    ids = {trial.indicator_id for trial in trials}
    assert {
        "lorentzian_classification",
        "ut_bot_alerts",
        "squeeze_momentum_lazybear",
        "wavetrend_crosses",
        "hull_suite",
        "supertrend_kivanc",
        "chandelier_exit_everget",
        "schaff_trend_cycle",
        "range_filter_guikroth",
        "alphatrend",
        "optimized_trend_tracker",
        "qqe_mod",
        "ssl_hybrid",
        "waddah_attar_explosion",
        "qqe_ssl_wae_composite",
        "halftrend_everget",
        "trendilo",
        "nadaraya_watson_endpoint_nonrepaint",
        "rsi_kernel_optimized_flux",
        "vumanchu_cipher_b",
    } <= ids
    assert all(trial.symbol == "CBOT:ZN1!" for trial in trials)
    assert all(trial.timeframe == "15" for trial in trials)
    assert all(trial.train.trades >= 0 and trial.test.trades >= 0 and trial.forward.trades >= 0 for trial in trials)


def test_better_validated_community_component_can_outweigh_core_for_same_symbol():
    core = StrategyTrial(
        strategy_id="trend_pullback",
        symbol="CBOT:ZN1!",
        timeframe="15",
        train_trades=90,
        test_trades=45,
        forward_trades=25,
        train_expectancy_r=0.30,
        test_expectancy_r=0.18,
        forward_expectancy_r=0.14,
        test_profit_factor=1.30,
        forward_profit_factor=1.20,
        test_win_rate=0.53,
        max_drawdown_r=4.0,
        parameter_stability=0.80,
        regime_stability=0.75,
    )
    stats = IndicatorStats(
        trades=45,
        wins=27,
        losses=18,
        win_rate=0.60,
        expectancy_r=0.28,
        profit_factor=1.55,
        max_drawdown_r=3.0,
    )
    community = CommunityIndicatorTrial(
        indicator_id="ut_bot_alerts",
        symbol="CBOT:ZN1!",
        timeframe="15",
        family="atr_trend",
        selected_parameters={"atr_period": 10, "key_value": 1.5},
        train=stats,
        test=stats,
        forward=stats,
        robust_score=120.0,
        validated=True,
        reasons=(),
    )
    profile = build_symbol_ensemble_profile(
        symbol="CBOT:ZN1!",
        timeframe="15",
        core_trials=[core],
        community_trials=[community],
    )
    weights = {item.component_id: item.normalized_weight for item in profile.components}
    assert profile.status == "RESEARCH_PROFILE_READY"
    assert weights["ut_bot_alerts"] > weights["trend_pullback"]
    assert profile.community_weight_share > profile.core_weight_share


def test_general_lab_gets_same_matrix_engine_for_arbitrary_symbols():
    summary = community_research_plan_summary(lab_symbols=("CAPITALCOM:BTCUSD", "CBOT:ZN1!"))
    assert summary["symbols"] >= 28
    assert summary["by_scope"]["general-lab"] > 0
    assert "does not inherit weights from a different asset" in summary["general_lab_rule"]


def test_historical_shadow_component_ids_remain_benchmarkable():
    ids = {x.indicator_id for x in eligible_indicators("crypto", "5", implemented_only=True)}
    assert "nadaraya_watson_endpoint_nonrepaint" in ids
    assert "halftrend_everget" in ids
    assert "nadaraya_watson_envelope_luxalgo" not in ids


def test_trendilo_parameter_contract_matches_existing_shadow_registry():
    from app.community_indicator_benchmark import indicator_parameter_grid

    grid = indicator_parameter_grid("trendilo")
    assert any(
        row.get("smoothing") == 1
        and row.get("lookback") == 50
        and row.get("band_multiplier") == 1.25
        for row in grid
    )


def test_benchmark_matrix_includes_official_ports_but_not_native_proxy_only():
    trials = benchmark_symbol_indicators(
        symbol="CBOT:ZN1!",
        asset_class="rates",
        timeframe="15",
        bars=_bars(900),
    )
    ids = {trial.indicator_id for trial in trials}
    assert "lorentzian_classification" in ids
    assert "smart_money_concepts_luxalgo" not in ids


def test_vumanchu_divergence_is_emitted_on_confirmation_bar_not_backdated():
    from app.community_indicator_signals import _vumanchu_confirmed_divergence_events

    bars = _bars(12)
    oscillator = [
        10.0, 30.0, 70.0, 40.0, 20.0,
        15.0, 35.0, 60.0, 30.0, 10.0,
        5.0, 0.0,
    ]
    bars[2] = Bar(
        timestamp=bars[2].timestamp,
        open=bars[2].open,
        high=101.0,
        low=bars[2].low,
        close=bars[2].close,
        volume=bars[2].volume,
    )
    bars[7] = Bar(
        timestamp=bars[7].timestamp,
        open=bars[7].open,
        high=103.0,
        low=bars[7].low,
        close=bars[7].close,
        volume=bars[7].volume,
    )
    events = _vumanchu_confirmed_divergence_events(
        bars,
        oscillator,
        bearish_min=45.0,
        bullish_max=-65.0,
    )
    assert 7 not in events
    assert events[9] < 0


def test_benchmarkable_selector_includes_official_ports_and_excludes_native_proxies():
    ids = {spec.indicator_id for spec in benchmarkable_indicators("rates", "15")}
    assert "lorentzian_classification" in ids
    assert "smart_money_concepts_luxalgo" not in ids
    assert "vumanchu_cipher_b" in ids
