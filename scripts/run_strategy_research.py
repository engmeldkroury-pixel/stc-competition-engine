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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run STC no-lookahead strategy research from exact-provider OHLCV JSON."
    )
    parser.add_argument("input", type=Path, help="Input JSON containing symbol + 15m/1h/4h/1D series")
    parser.add_argument("--output", type=Path, required=True, help="Output research JSON")
    parser.add_argument(
        "--skip-feature-calibration",
        action="store_true",
        help="Run strategy matrix only; skip per-feature OOS/forward calibration",
    )
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_symbol_research(
        payload,
        calibrate_features=not args.skip_feature_calibration,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, default=str, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
