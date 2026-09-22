#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.feed_reconciliation import reconcile_ohlcv_feeds, reconciliation_dict


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare overlapping TradingView/alternate OHLCV feeds for research compatibility."
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--min-overlap", type=int, default=200)
    parser.add_argument("--max-median-close-bps", type=float)
    parser.add_argument("--max-p95-close-bps", type=float)
    parser.add_argument("--min-return-correlation", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = reconcile_ohlcv_feeds(
        _read(args.reference),
        _read(args.candidate),
        min_overlap_bars=args.min_overlap,
        max_median_close_bps=args.max_median_close_bps,
        max_p95_close_bps=args.max_p95_close_bps,
        min_return_correlation=args.min_return_correlation,
    )
    payload = reconciliation_dict(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("STC_FEED_RECONCILIATION=" + json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
