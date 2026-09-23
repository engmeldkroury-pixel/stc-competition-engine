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
from app.research_dataset import bars_from_tradingview_ohlcv


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run STC community-indicator frozen 15m holdout confirmation."
    )
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    meta = json.loads((args.input_dir / "meta.json").read_text(encoding="utf-8"))
    payload = json.loads((args.input_dir / "15m.json").read_text(encoding="utf-8"))
    symbol = str(meta["symbol"])
    bars = bars_from_tradingview_ohlcv(payload)
    asset_class = strategy_asset_class(symbol)

    report = confirm_community_symbol(
        symbol=symbol,
        asset_class=asset_class,
        timeframe="15",
        bars=bars,
    )
    result = {
        "symbol": symbol,
        "asset_class": asset_class,
        "timeframe": "15",
        "bars": len(bars),
        "report": asdict(report),
        "execution": "research_only",
        "live_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "symbol": symbol,
        "bars": len(bars),
        "development_bars": report.development_bars,
        "confirmation_bars": report.confirmation_bars,
        "status": report.status,
        "promotion_candidates": list(report.promotion_candidates),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
