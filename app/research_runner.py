from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .asset_classification import strategy_asset_class
from .feature_validation import FeatureValidation, validate_feature_weight
from .indicator_catalog import FEATURE_FAMILIES
from .mtf_research import mtf_strategy_matrix
from .research_dataset import (
    bars_from_tradingview_ohlcv,
    data_quality_report,
    research_timeframe_bundle,
)
from .research_report import build_strategy_research_report, report_to_dict
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
        )
        for feature in _strategy_feature_names(selection.strategy_id)
    ]


def run_symbol_research(
    payload: dict[str, Any],
    *,
    calibrate_features: bool = True,
    run_mtf: bool = False,
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
    snapshot_cache: dict[str, dict] = {}
    validations, selection = strategy_matrix(
        symbol,
        asset_class,
        bundle,
        snapshot_cache=snapshot_cache,
    )
    timeframe_selections = matrix_selections_by_timeframe(symbol, validations)
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

    mtf_validations = []
    mtf_selection = MatrixSelection(
        status="NOT_RUN",
        symbol=symbol,
        strategy_id=None,
        timeframe="15",
        robust_score=None,
        trial_count=0,
        reason="MTF research was not requested.",
    )
    mtf_report = None
    if run_mtf:
        mtf_validations, mtf_selection = mtf_strategy_matrix(
            symbol=symbol,
            asset_class=asset_class,
            bars_by_timeframe=bundle,
            snapshot_cache=snapshot_cache,
        )
        mtf_report = build_strategy_research_report(
            selection=mtf_selection,
            validations=mtf_validations,
            feature_validations=(),
        )

    return {
        "schema_version": "stc-research-v1",
        "symbol": symbol,
        "asset_class": asset_class,
        "data_quality": {
            key: asdict(value) for key, value in quality.items()
        },
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
        "mtf_research_enabled": bool(run_mtf),
        "mtf_selection": asdict(mtf_selection),
        "mtf_strategy_trials": [
            {
                "trial": asdict(row.trial),
                "base_strategy_id": row.base_strategy_id,
                "robust_score": robust_trial_score(row.trial),
                "research_class": classify_trial_status(row.trial),
                "rejection_reasons": list(trial_rejection_reasons(row.trial)),
                "selected_params": asdict(row.selected_params),
                "mtf_gate_params": asdict(row.gate_params),
                "train": asdict(row.train_stats),
                "test": asdict(row.test_stats),
                "forward": asdict(row.forward_stats),
            }
            for row in mtf_validations
        ],
        "mtf_research_report": (
            report_to_dict(mtf_report) if mtf_report is not None else None
        ),
        "live_trading_authority": False,
        "note": (
            "Research output only. A strategy/feature is not live-authorized merely because "
            "it passed historical validation; runtime A+ gates and manual approval remain mandatory."
        ),
    }
