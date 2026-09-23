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
from app.community_frozen_confirmation import confirm_community_symbol
from app.research_dataset import (
    bars_from_tradingview_ohlcv,
    normalize_confirmed_bars,
    resample_hourly_to_two_hour,
)


SERIES_FILES = {
    "5": "5m.json",
    "30": "30m.json",
    "60": "1h.json",
    "240": "4h.json",
    "1D": "1D.json",
}


def _load(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return normalize_confirmed_bars(bars_from_tradingview_ohlcv(payload))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    meta = json.loads((args.input_dir / "meta.json").read_text(encoding="utf-8"))
    symbol = str(meta["symbol"])
    asset_class = strategy_asset_class(symbol)

    series = {tf: _load(args.input_dir / filename) for tf, filename in SERIES_FILES.items()}
    series["120"] = resample_hourly_to_two_hour(series["60"])

    reports = {}
    for timeframe in ("5", "30", "60", "120", "240", "1D"):
        bars = series[timeframe]
        report = confirm_community_symbol(
            symbol=symbol,
            asset_class=asset_class,
            timeframe=timeframe,
            bars=bars,
        )
        reports[timeframe] = asdict(report)

    result = {
        "symbol": symbol,
        "asset_class": asset_class,
        "source": "TradingView Official MCP exact-symbol OHLCV; 2h derived from exact 1h",
        "reports": reports,
        "live_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "symbol": symbol,
        "promotion_candidates_by_timeframe": {
            tf: report["promotion_candidates"] for tf, report in reports.items()
        },
        "bars_by_timeframe": {
            tf: report["development_bars"] + report["confirmation_bars"]
            for tf, report in reports.items()
        },
        "live_authority": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
