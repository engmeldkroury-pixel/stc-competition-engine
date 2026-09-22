from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .asset_classification import strategy_asset_class
from .feature_validation import FeatureValidation, validate_feature_weight
from .indicator_catalog import FEATURE_FAMILIES
from .research_costs import research_cost_policy
from .research_dataset import (
    bars_from_tradingview_ohlcv,
    data_quality_report,
    research_timeframe_bundle,
)
from .research_report import build_strategy_research_report, report_to_dict
from .strategy_lab import STRATEGIES, robust_trial_score, trial_rejection_reasons
from .walkforward import materialize_feature_series, strategy_matrix


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


def run_symbol_research(
    payload: dict[str, Any],
    *,
    calibrate_features: bool = True,
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
        if not quality[source_key].quality_ok:
            raise ValueError(
                f"Research data quality failed for {symbol} {source_key}: "
                + ",".join(quality[source_key].notes)
            )

    bundle = research_timeframe_bundle(
        bars_15m=raw_bars["15"],
        bars_1h=raw_bars["60"],
        bars_4h=raw_bars["240"],
        bars_1d=raw_bars["1D"],
        bars_5m=raw_bars.get("5"),
        bars_30m=raw_bars.get("30"),
    )
    asset_class = strategy_asset_class(symbol)
    validations, selection = strategy_matrix(symbol, asset_class, bundle)

    feature_validations: list[FeatureValidation] = []
    if (
        calibrate_features
        and selection.status == "VALIDATED"
        and selection.strategy_id is not None
        and selection.timeframe is not None
    ):
        bars = bundle[selection.timeframe]
        snapshots = materialize_feature_series(symbol, selection.timeframe, bars)
        n = len(bars)
        train_end = max(520, int(n * 0.58))
        test_end = max(train_end + 120, int(n * 0.82))
        test_end = min(test_end, n - 80)
        horizon = _feature_horizon(selection.timeframe)
        for feature in _strategy_feature_names(selection.strategy_id):
            feature_validations.append(
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
                )
            )

    report = build_strategy_research_report(
        selection=selection,
        validations=validations,
        feature_validations=feature_validations,
    )

    return {
        "schema_version": "stc-research-v1",
        "symbol": symbol,
        "asset_class": asset_class,
        "research_cost_model": research_cost_policy(symbol),
        "data_quality": {
            key: asdict(value) for key, value in quality.items()
        },
        "derived_timeframes": {
            key: len(value) for key, value in bundle.items()
        },
        "derived_timeframe_end_utc": {
            key: (value[-1].timestamp.isoformat().replace("+00:00", "Z") if value else None)
            for key, value in bundle.items()
        },
        "matrix_selection": asdict(selection),
        "strategy_trials": [
            {
                "trial": asdict(row.trial),
                "robust_score": robust_trial_score(row.trial),
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
        "research_report": report_to_dict(report),
        "live_trading_authority": False,
        "note": (
            "Research output only. A strategy/feature is not live-authorized merely because "
            "it passed historical validation; runtime A+ gates and manual approval remain mandatory."
        ),
    }
