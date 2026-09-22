#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ohlcv_archive import merge_ohlcv_payloads, merge_report_dict


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge exact-provider TradingView OHLCV snapshots into a deduplicated archive."
    )
    parser.add_argument("incoming", type=Path)
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    incoming = _read(args.incoming)
    existing = _read(args.existing) if args.existing and args.existing.exists() else None
    merged, report = merge_ohlcv_payloads(existing, incoming)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(merged, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("STC_OHLCV_ARCHIVE_MERGE=" + json.dumps(merge_report_dict(report), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
