from datetime import datetime, timedelta, timezone

from app.feature_validation import atr_series_by_index, validate_feature_weight
from app.historical_features import HistoricalFeatureSnapshot
from app.models import Bar
from app.research_report import build_strategy_research_report, report_to_dict
from app.strategy_lab import StrategyTrial
from app.walkforward import BacktestParams, BacktestStats, MatrixSelection, WalkForwardValidation


UTC = timezone.utc


def _bars(count: int = 520) -> list[Bar]:
    t0 = datetime(2025, 1, 1, tzinfo=UTC)
    price = 100.0
    out = []
    for i in range(count):
        price += 0.12
        out.append(
            Bar(
                timestamp=t0 + timedelta(minutes=15 * i),
                open=price - 0.04,
                high=price + 0.45,
                low=price - 0.45,
                close=price,
                volume=1000 + i,
            )
        )
    return out


def test_feature_weight_requires_test_and_forward_confirmation():
    bars = _bars()
    snapshots = {
        i: HistoricalFeatureSnapshot(
            symbol="TEST:X",
            timeframe="15",
            timestamp=bars[i].timestamp,
            values={"bos": 0.9},
            observations=(),
        )
        for i in range(260, len(bars))
    }
    result = validate_feature_weight(
        feature="bos",
        symbol="TEST:X",
        strategy_id="trend_pullback",
        timeframe="15",
        bars=bars,
        snapshots=snapshots,
        test_start=260,
        test_end=420,
        forward_end=520,
        horizon_bars=4,
        min_test_samples=40,
        min_forward_samples=15,
    )
    assert result.test_performance.sample_size >= 40
    assert result.forward_performance.sample_size >= 15
    assert result.test_performance.average_forward_r > 0
    assert result.forward_performance.average_forward_r > 0
    assert result.deployable is True


def _validation() -> WalkForwardValidation:
    train = BacktestStats(120, 100, 20, 100 / 120, 80, 80 / 120, 2.2, 5.0)
    test = BacktestStats(35, 25, 10, 25 / 35, 15, 15 / 35, 1.6, 3.0)
    forward = BacktestStats(20, 12, 8, 0.6, 5, 0.25, 1.3, 2.0)
    trial = StrategyTrial(
        strategy_id="trend_pullback",
        symbol="TEST:X",
        timeframe="15",
        train_trades=train.trades,
        test_trades=test.trades,
        forward_trades=forward.trades,
        train_expectancy_r=train.expectancy_r,
        test_expectancy_r=test.expectancy_r,
        forward_expectancy_r=forward.expectancy_r,
        test_profit_factor=test.profit_factor,
        forward_profit_factor=forward.profit_factor,
        test_win_rate=test.win_rate,
        max_drawdown_r=3.0,
        parameter_stability=0.8,
        regime_stability=0.8,
    )
    return WalkForwardValidation(
        trial=trial,
        selected_params=BacktestParams(0.62, 1.5, 1.5, 16),
        train_stats=train,
        test_stats=test,
        forward_stats=forward,
    )


def test_research_probability_excludes_training_trades():
    validation = _validation()
    selection = MatrixSelection(
        status="VALIDATED",
        symbol="TEST:X",
        strategy_id="trend_pullback",
        timeframe="15",
        robust_score=55.0,
        trial_count=1,
        reason="test",
    )
    report = build_strategy_research_report(
        selection=selection,
        validations=[validation],
        min_probability_samples=50,
    )
    assert report.setup_probability is not None
    assert report.setup_probability.sample_size == 55
    assert report.setup_probability.wins == 37
    assert report.setup_probability.losses == 18
    assert report.setup_probability.status == "CALIBRATED"
    assert report.test_trades == 35
    assert report.forward_trades == 20
    assert "setup_probability" in report_to_dict(report)


def test_no_validated_strategy_never_fabricates_probability():
    selection = MatrixSelection(
        status="NO_VALIDATED_STRATEGY",
        symbol="TEST:X",
        strategy_id=None,
        timeframe=None,
        robust_score=None,
        trial_count=9,
        reason="none passed",
    )
    report = build_strategy_research_report(selection=selection, validations=[])
    assert report.status == "NO_VALIDATED_STRATEGY"
    assert report.setup_probability is None
    assert report.selected_strategy is None



def test_cached_atr_series_matches_analysis_and_validation_result():
    from app.analysis import atr

    bars = _bars(520)
    cached = atr_series_by_index(bars, 14)
    for index in (260, 333, 419, 519):
        assert cached[index] == atr(bars[: index + 1], 14)

    snapshots = {
        i: HistoricalFeatureSnapshot(
            symbol="TEST:X",
            timeframe="15",
            timestamp=bars[i].timestamp,
            values={"bos": 0.9},
            observations=(),
        )
        for i in range(260, len(bars))
    }
    uncached = validate_feature_weight(
        feature="bos",
        symbol="TEST:X",
        strategy_id="trend_pullback",
        timeframe="15",
        bars=bars,
        snapshots=snapshots,
        test_start=260,
        test_end=420,
        forward_end=520,
        horizon_bars=4,
        min_test_samples=40,
        min_forward_samples=15,
    )
    cached_result = validate_feature_weight(
        feature="bos",
        symbol="TEST:X",
        strategy_id="trend_pullback",
        timeframe="15",
        bars=bars,
        snapshots=snapshots,
        test_start=260,
        test_end=420,
        forward_end=520,
        horizon_bars=4,
        min_test_samples=40,
        min_forward_samples=15,
        atr_values=cached,
    )
    assert cached_result == uncached
