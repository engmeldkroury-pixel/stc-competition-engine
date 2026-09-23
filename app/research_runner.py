from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .asset_classification import strategy_asset_class
from .community_indicator_benchmark import benchmark_symbol_indicators, build_symbol_ensemble_profile
from .feature_validation import FeatureValidation, atr_series_by_index, validate_feature_weight
from .indicator_catalog import FEATURE_FAMILIES
from .research_dataset import (
    bars_from_tradingview_ohlcv,
    data_quality_report,
    research_timeframe_bundle,
)
from .research_report import build_strategy_research_report, report_to_dict
from .mtf_research import validate_mtf_policies
from .regime_research import validate_strategy_by_regime, validate_strategy_by_regime_pools
from .strategy_lab import STRATEGIES, classify_trial_status, robust_trial_score, trial_rejection_reasons
from .walkforward import MatrixSelection, materialize_feature_series, matrix_selections_by_timeframe, strategy_matrix


RAW_SERIES_KEYS = {
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1D": "1D",
}

OPTIONAL_RAW_SERIES_KEYS = {
    "5m": "5",
    "30m": "30",
}


def _strategy_feature_names(strategy_id: str) -> tuple[str, ...]:
    spec = next((s for s in STRATEGIES if s.strategy_id == strategy_id), None)
    if spec is None:
        raise KeyError(f"Unknown strategy: {strategy_id}")
    family_names = set(spec.feature_families)
    return tuple(
        feature
        for family in FEATURE_FAMILIES
        if family.name in family_names
        for feature in family.features
    )


def _feature_horizon(timeframe: str) -> int:
    return {
        "5": 12,
        "15": 8,
        "30": 7,
        "60": 6,
        "120": 4,
        "240": 3,
        "1D": 5,
    }.get(timeframe, 4)


def _calibrate_selection_features(
    *,
    symbol: str,
    selection: MatrixSelection,
    bundle: dict[str, list],
    snapshot_cache: dict[str, dict] | None = None,
) -> list[FeatureValidation]:
    if (
        selection.status != "VALIDATED"
        or selection.strategy_id is None
        or selection.timeframe is None
    ):
        return []
    bars = bundle.get(selection.timeframe) or []
    if len(bars) < 900:
        return []
    cache = snapshot_cache if snapshot_cache is not None else {}
    snapshots = cache.get(selection.timeframe)
    if snapshots is None:
        snapshots = materialize_feature_series(symbol, selection.timeframe, bars)
        cache[selection.timeframe] = snapshots
    atr_values = atr_series_by_index(bars, 14)
    n = len(bars)
    train_end = max(520, int(n * 0.58))
    test_end = max(train_end + 120, int(n * 0.82))
    test_end = min(test_end, n - 80)
    horizon = _feature_horizon(selection.timeframe)
    return [
        validate_feature_weight(
            feature=feature,
            symbol=symbol,
            strategy_id=selection.strategy_id,
            timeframe=selection.timeframe,
            bars=bars,
            snapshots=snapshots,
            test_start=train_end,
            test_end=test_end,
            forward_end=n - 1,
            horizon_bars=horizon,
            atr_values=atr_values,
        )
        for feature in _strategy_feature_names(selection.strategy_id)
    ]


def _select_mtf_candidate_ids(validations, *, limit: int = 3) -> tuple[str, ...]:
    candidates = []
    for row in validations:
        trial = row.trial
        if trial.timeframe != "15":
            continue
        if trial.test_trades < 8 or trial.forward_trades < 5:
            continue
        if trial.max_drawdown_r > 12.0:
            continue
        forward_expectancy = (
            float(trial.forward_expectancy_r)
            if trial.forward_expectancy_r is not None
            else -999.0
        )
        if trial.test_expectancy_r <= 0 and forward_expectancy <= 0:
            continue
        heuristic = (
            max(0.0, float(trial.test_expectancy_r)) * 10.0
            + max(0.0, forward_expectancy) * 12.0
            + min(float(trial.test_profit_factor), 3.0)
            + min(float(trial.forward_profit_factor or 0.0), 3.0)
            + min(trial.test_trades + trial.forward_trades, 80) / 80.0
        )
        candidates.append((heuristic, trial.strategy_id))
    candidates.sort(reverse=True)
    seen = set()
    selected = []
    for _, strategy_id in candidates:
        if strategy_id in seen:
            continue
        seen.add(strategy_id)
        selected.append(strategy_id)
        if len(selected) >= limit:
            break
    return tuple(selected)


def run_symbol_research(
    payload: dict[str, Any],
    *,
    calibrate_features: bool = True,
    compare_mtf: bool = False,
    compare_regimes: bool = False,
    compare_regime_pools: bool = False,
) -> dict[str, Any]:
    symbol = str(payload.get("symbol") or "").strip()
    if not symbol:
        raise ValueError("Research payload requires symbol")
    series = payload.get("series")
    if not isinstance(series, dict):
        raise ValueError("Research payload requires series object")

    missing = [key for key in RAW_SERIES_KEYS if key not in series]
    if missing:
        raise ValueError(f"Missing required exact-provider OHLCV series: {missing}")

    raw_bars = {}
    quality = {}
    requested_series = {
        **RAW_SERIES_KEYS,
        **{
            source_key: normalized_key
            for source_key, normalized_key in OPTIONAL_RAW_SERIES_KEYS.items()
            if source_key in series
        },
    }
    for source_key, normalized_key in requested_series.items():
        part = series[source_key]
        if not isinstance(part, dict):
            raise ValueError(f"Series {source_key} must be an OHLCV object")
        bars = bars_from_tradingview_ohlcv(part)
        raw_bars[normalized_key] = bars
        quality[source_key] = data_quality_report(symbol, source_key, bars)
        report = quality[source_key]
        fatal_integrity_failure = (
            report.bars == 0
            or report.duplicate_timestamps > 0
            or report.non_monotonic_pairs > 0
        )
        if fatal_integrity_failure:
            raise ValueError(
                f"Research data quality failed for {symbol} {source_key}: "
                + ",".join(report.notes)
            )
        # Short provider history is not an integrity failure. Keep the exact
        # series in the bundle and let strategy_matrix skip any timeframe with
        # fewer than the 900 bars required for walk-forward validation.

    bundle = research_timeframe_bundle(
        bars_15m=raw_bars["15"],
        bars_1h=raw_bars["60"],
        bars_4h=raw_bars["240"],
        bars_1d=raw_bars["1D"],
        bars_5m=raw_bars.get("5"),
        bars_30m=raw_bars.get("30"),
    )
    asset_class = strategy_asset_class(symbol)
    snapshot_cache: dict[str, dict] = {}
    validations, selection = strategy_matrix(
        symbol,
        asset_class,
        bundle,
        snapshot_cache=snapshot_cache,
    )
    timeframe_selections = matrix_selections_by_timeframe(symbol, validations)

    community_indicator_trials = []
    community_ensemble_profiles = {}
    for timeframe, bars in bundle.items():
        if len(bars) < 300:
            continue
        trials = benchmark_symbol_indicators(
            symbol=symbol,
            asset_class=asset_class,
            timeframe=timeframe,
            bars=bars,
        )
        community_indicator_trials.extend(trials)
        profile = build_symbol_ensemble_profile(
            symbol=symbol,
            timeframe=timeframe,
            core_trials=[row.trial for row in validations if row.trial.timeframe == timeframe],
            community_trials=trials,
        )
        community_ensemble_profiles[timeframe] = profile
    live_entry_selection = timeframe_selections.get(
        "15",
        MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe="15",
            robust_score=None,
            trial_count=0,
            reason="15m research timeframe unavailable.",
        ),
    )

    feature_validations: list[FeatureValidation] = []
    live_entry_feature_validations: list[FeatureValidation] = []
    if calibrate_features:
        feature_validations = _calibrate_selection_features(
            symbol=symbol,
            selection=selection,
            bundle=bundle,
            snapshot_cache=snapshot_cache,
        )
        if (
            live_entry_selection.status == "VALIDATED"
            and (
                selection.strategy_id != live_entry_selection.strategy_id
                or selection.timeframe != live_entry_selection.timeframe
            )
        ):
            live_entry_feature_validations = _calibrate_selection_features(
                symbol=symbol,
                selection=live_entry_selection,
                bundle=bundle,
                snapshot_cache=snapshot_cache,
            )
        else:
            live_entry_feature_validations = list(feature_validations)

    report = build_strategy_research_report(
        selection=selection,
        validations=validations,
        feature_validations=feature_validations,
    )
    live_entry_report = build_strategy_research_report(
        selection=live_entry_selection,
        validations=validations,
        feature_validations=live_entry_feature_validations,
    )

    mtf_validation = []
    if compare_mtf:
        by_strategy = {
            row.trial.strategy_id: row
            for row in validations
            if row.trial.timeframe == "15"
        }
        for strategy_id in _select_mtf_candidate_ids(validations):
            baseline = by_strategy[strategy_id]
            policies = validate_mtf_policies(
                symbol=symbol,
                strategy_id=strategy_id,
                bundle=bundle,
            )
            mtf_validation.append({
                "strategy_id": strategy_id,
                "baseline": {
                    "research_class": classify_trial_status(baseline.trial),
                    "rejection_reasons": list(trial_rejection_reasons(baseline.trial)),
                    "robust_score": robust_trial_score(baseline.trial),
                    "trial": asdict(baseline.trial),
                    "test": asdict(baseline.test_stats),
                    "forward": asdict(baseline.forward_stats),
                },
                "policies": [
                    {
                        "policy": item.policy,
                        "research_class": classify_trial_status(item.validation.trial),
                        "rejection_reasons": list(trial_rejection_reasons(item.validation.trial)),
                        "robust_score": item.robust_score,
                        "test_retention": item.test_retention,
                        "forward_retention": item.forward_retention,
                        "test_trades_per_30d": item.test_trades_per_30d,
                        "forward_trades_per_30d": item.forward_trades_per_30d,
                        "trial": asdict(item.validation.trial),
                        "test": asdict(item.validation.test_stats),
                        "forward": asdict(item.validation.forward_stats),
                    }
                    for item in policies
                ],
            })

    regime_validation = []
    if compare_regimes:
        by_strategy = {
            row.trial.strategy_id: row
            for row in validations
            if row.trial.timeframe == "15"
        }
        entry_bars = bundle.get("15") or []
        snapshots = snapshot_cache.get("15")
        if snapshots is None and len(entry_bars) >= 900:
            snapshots = materialize_feature_series(symbol, "15", entry_bars)
            snapshot_cache["15"] = snapshots
        for strategy_id in _select_mtf_candidate_ids(validations):
            baseline = by_strategy[strategy_id]
            regimes = validate_strategy_by_regime(
                symbol=symbol,
                timeframe="15",
                bars=entry_bars,
                strategy_id=strategy_id,
                snapshots=snapshots,
            )
            regime_validation.append({
                "strategy_id": strategy_id,
                "baseline": {
                    "research_class": classify_trial_status(baseline.trial),
                    "rejection_reasons": list(trial_rejection_reasons(baseline.trial)),
                    "robust_score": robust_trial_score(baseline.trial),
                    "trial": asdict(baseline.trial),
                    "test": asdict(baseline.test_stats),
                    "forward": asdict(baseline.forward_stats),
                },
                "regimes": [
                    {
                        "regime": item.regime,
                        "research_class": classify_trial_status(item.validation.trial),
                        "rejection_reasons": list(trial_rejection_reasons(item.validation.trial)),
                        "robust_score": item.robust_score,
                        "test_retention": item.test_retention,
                        "forward_retention": item.forward_retention,
                        "trial": asdict(item.validation.trial),
                        "test": asdict(item.validation.test_stats),
                        "forward": asdict(item.validation.forward_stats),
                    }
                    for item in regimes
                ],
            })

    regime_pool_validation = []
    if compare_regime_pools:
        by_strategy = {
            row.trial.strategy_id: row
            for row in validations
            if row.trial.timeframe == "15"
        }
        entry_bars = bundle.get("15") or []
        snapshots = snapshot_cache.get("15")
        if snapshots is None and len(entry_bars) >= 900:
            snapshots = materialize_feature_series(symbol, "15", entry_bars)
            snapshot_cache["15"] = snapshots
        # Keep this exploratory sweep bounded: two strongest adequately sampled
        # 15m candidates, with no authority to promote on the same dataset.
        for strategy_id in _select_mtf_candidate_ids(validations, limit=2):
            baseline = by_strategy[strategy_id]
            pools = validate_strategy_by_regime_pools(
                symbol=symbol,
                timeframe="15",
                bars=entry_bars,
                strategy_id=strategy_id,
                snapshots=snapshots,
            )
            regime_pool_validation.append({
                "strategy_id": strategy_id,
                "baseline": {
                    "research_class": classify_trial_status(baseline.trial),
                    "rejection_reasons": list(trial_rejection_reasons(baseline.trial)),
                    "robust_score": robust_trial_score(baseline.trial),
                    "trial": asdict(baseline.trial),
                    "test": asdict(baseline.test_stats),
                    "forward": asdict(baseline.forward_stats),
                },
                "pools": [
                    {
                        "pool": item.pool,
                        "allowed_regimes": list(item.allowed_regimes),
                        "research_class": classify_trial_status(item.validation.trial),
                        "rejection_reasons": list(trial_rejection_reasons(item.validation.trial)),
                        "robust_score": item.robust_score,
                        "test_retention": item.test_retention,
                        "forward_retention": item.forward_retention,
                        "fresh_confirmation_required": item.fresh_confirmation_required,
                        "promotion_status": (
                            "FRESH_CONFIRMATION_REQUIRED"
                            if item.robust_score > 0
                            else "RESEARCH_ONLY_REJECTED"
                        ),
                        "trial": asdict(item.validation.trial),
                        "test": asdict(item.validation.test_stats),
                        "forward": asdict(item.validation.forward_stats),
                    }
                    for item in pools
                ],
            })

    return {
        "schema_version": "stc-research-v1",
        "symbol": symbol,
        "asset_class": asset_class,
        "data_quality": {
            key: asdict(value) for key, value in quality.items()
        },
        "insufficient_history_series": [
            key
            for key, value in quality.items()
            if "insufficient_for_walk_forward_900_bar_minimum" in value.notes
        ],
        "derived_timeframes": {
            key: len(value) for key, value in bundle.items()
        },
        "derived_timeframe_start_utc": {
            key: (value[0].timestamp.isoformat().replace("+00:00", "Z") if value else None)
            for key, value in bundle.items()
        },
        "derived_timeframe_end_utc": {
            key: (value[-1].timestamp.isoformat().replace("+00:00", "Z") if value else None)
            for key, value in bundle.items()
        },
        "derived_timeframe_span_days": {
            key: (
                round((value[-1].timestamp - value[0].timestamp).total_seconds() / 86400.0, 3)
                if len(value) >= 2
                else 0.0
            )
            for key, value in bundle.items()
        },
        "matrix_selection": asdict(selection),
        "timeframe_selections": {
            key: asdict(value) for key, value in timeframe_selections.items()
        },
        "live_entry_timeframe": "15",
        "live_entry_selection": asdict(live_entry_selection),
        "mtf_validation": mtf_validation,
        "regime_validation": regime_validation,
        "regime_pool_validation": regime_pool_validation,
        "community_indicator_trials": [
            asdict(item) for item in community_indicator_trials
        ],
        "community_ensemble_profiles": {
            key: asdict(value) for key, value in community_ensemble_profiles.items()
        },
        "community_indicator_live_authority": False,
        "community_indicator_weighting_rule": (
            "OOS/forward robustness only. Reviews/popularity prioritize research discovery and "
            "never become live trading weights. Weight changes require frozen-window recalibration."
        ),
        "strategy_trials": [
            {
                "trial": asdict(row.trial),
                "robust_score": robust_trial_score(row.trial),
                "research_class": classify_trial_status(row.trial),
                "rejection_reasons": list(trial_rejection_reasons(row.trial)),
                "selected_params": asdict(row.selected_params),
                "train": asdict(row.train_stats),
                "test": asdict(row.test_stats),
                "forward": asdict(row.forward_stats),
            }
            for row in validations
        ],
        "feature_validations": [
            {
                "feature": item.feature,
                "deployable": item.deployable,
                "reason": item.reason,
                "test": asdict(item.test_performance),
                "forward": asdict(item.forward_performance),
                "calibration": asdict(item.calibrated_weight),
            }
            for item in feature_validations
        ],
        "live_entry_feature_validations": [
            {
                "feature": item.feature,
                "deployable": item.deployable,
                "reason": item.reason,
                "test": asdict(item.test_performance),
                "forward": asdict(item.forward_performance),
                "calibration": asdict(item.calibrated_weight),
            }
            for item in live_entry_feature_validations
        ],
        "research_report": report_to_dict(report),
        "live_entry_research_report": report_to_dict(live_entry_report),
        "live_trading_authority": False,
        "note": (
            "Research output only. A strategy/feature is not live-authorized merely because "
            "it passed historical validation; runtime A+ gates and manual approval remain mandatory."
        ),
    }
