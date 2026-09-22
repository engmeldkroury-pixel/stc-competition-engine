#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.research_runner import run_symbol_research


SERIES_FILES = {
    "15m": "15m.json",
    "1h": "1h.json",
    "4h": "4h.json",
    "1D": "1D.json",
}

OPTIONAL_SERIES_FILES = {
    "5m": "5m.json",
    "30m": "30m.json",
}


def load_series_dir(path: Path) -> dict:
    meta_path = path / "meta.json"
    if not meta_path.exists():
        raise ValueError(f"Missing {meta_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    symbol = str(meta.get("symbol") or "").strip()
    if not symbol:
        raise ValueError("meta.json requires symbol")

    series = {}
    for key, filename in SERIES_FILES.items():
        source = path / filename
        if not source.exists():
            raise ValueError(f"Missing required series file: {source}")
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("bars"), list):
            raise ValueError(f"{source} must contain TradingView OHLCV bars")
        series[key] = payload

    for key, filename in OPTIONAL_SERIES_FILES.items():
        source = path / filename
        if not source.exists():
            continue
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("bars"), list):
            raise ValueError(f"{source} must contain TradingView OHLCV bars")
        series[key] = payload

    research_mode = str(meta.get("research_mode") or "full").strip().lower()
    if research_mode not in {"full", "matrix_only", "mtf_compare"}:
        raise ValueError("meta.json research_mode must be full, matrix_only, or mtf_compare")
    return {"symbol": symbol, "series": series, "research_mode": research_mode}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run STC exact-provider research from a split OHLCV directory."
    )
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--skip-feature-calibration",
        action="store_true",
        help="Run strategy matrix only; skip selected-strategy feature calibration.",
    )
    args = parser.parse_args()

    payload = load_series_dir(args.input_dir)
    research_mode = payload.get("research_mode", "full")
    calibrate_features = (
        not args.skip_feature_calibration
        and research_mode == "full"
    )
    result = run_symbol_research(
        payload,
        calibrate_features=calibrate_features,
        compare_mtf=(research_mode == "mtf_compare"),
    )
    result["research_mode"] = payload.get("research_mode", "full")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, default=str, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report = result["research_report"]
    probability = report.get("setup_probability") or {}
    summary = {
        "symbol": result["symbol"],
        "asset_class": result["asset_class"],
        "status": report["status"],
        "selected_strategy": report.get("selected_strategy"),
        "selected_timeframe": report.get("selected_timeframe"),
        "robust_score": report.get("robust_score"),
        "test_trades": report.get("test_trades"),
        "forward_trades": report.get("forward_trades"),
        "test_expectancy_r": report.get("test_expectancy_r"),
        "forward_expectancy_r": report.get("forward_expectancy_r"),
        "test_profit_factor": report.get("test_profit_factor"),
        "forward_profit_factor": report.get("forward_profit_factor"),
        "probability_status": probability.get("status"),
        "estimated_win_probability": probability.get("estimated_win_probability"),
        "probability_sample_size": probability.get("sample_size"),
        "deployable_feature_count": report.get("deployable_feature_count"),
        "blocked_feature_count": report.get("blocked_feature_count"),
        "research_mode": result.get("research_mode", "full"),
    }
    print("STC_RESEARCH_SUMMARY=" + json.dumps(summary, sort_keys=True))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
