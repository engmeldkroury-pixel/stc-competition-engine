#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.asset_classification import strategy_asset_class
from app.community_indicator_benchmark import benchmark_symbol_indicators, build_symbol_ensemble_profile
from app.research_dataset import bars_from_tradingview_ohlcv
from app.walkforward import strategy_matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    meta = json.loads((args.input_dir / "meta.json").read_text(encoding="utf-8"))
    payload = json.loads((args.input_dir / "15m.json").read_text(encoding="utf-8"))
    symbol = str(meta["symbol"])
    bars = bars_from_tradingview_ohlcv(payload)
    asset_class = strategy_asset_class(symbol)

    native, selection = strategy_matrix(symbol, asset_class, {"15": bars})
    community = benchmark_symbol_indicators(
        symbol=symbol,
        asset_class=asset_class,
        timeframe="15",
        bars=bars,
    )
    ensemble = build_symbol_ensemble_profile(
        symbol=symbol,
        timeframe="15",
        core_trials=[row.trial for row in native],
        community_trials=community,
    )

    result = {
        "symbol": symbol,
        "asset_class": asset_class,
        "timeframe": "15",
        "bars": len(bars),
        "native_selection": asdict(selection),
        "native_trials": [
            {
                "trial": asdict(row.trial),
                "selected_params": asdict(row.selected_params),
                "train": asdict(row.train_stats),
                "test": asdict(row.test_stats),
                "forward": asdict(row.forward_stats),
            }
            for row in native
        ],
        "community_trials": [asdict(row) for row in community],
        "ensemble_profile": asdict(ensemble),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    validated_native = sum(1 for row in native if row.trial.test_trades >= 30 and row.trial.test_expectancy_r > 0.08 and row.trial.test_profit_factor >= 1.15)
    validated_community = sum(1 for row in community if row.validated)
    top_component = ensemble.components[0].component_id if ensemble.components else None
    print(json.dumps({
        "symbol": symbol,
        "bars": len(bars),
        "native_status": selection.status,
        "native_strategy": selection.strategy_id,
        "native_score": selection.robust_score,
        "native_trials": len(native),
        "community_trials": len(community),
        "validated_native_approx": validated_native,
        "validated_community": validated_community,
        "ensemble_status": ensemble.status,
        "top_component": top_component,
        "community_weight_share": ensemble.community_weight_share,
        "core_weight_share": ensemble.core_weight_share,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
