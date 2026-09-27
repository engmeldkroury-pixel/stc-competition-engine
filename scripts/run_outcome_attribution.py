#!/usr/bin/env python3
"""Read a JSON inbox snapshot or GET the authenticated bridge; write local report."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.bridge_client import BridgeClient
from app.outcome_attribution import utc
from app.outcome_report import report_from_inbox


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--bridge-url")
    parser.add_argument("--token-env", default="STC_WORKER_TOKEN")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--as-of", help="ISO time with timezone; default current UTC")
    parser.add_argument("--horizon-bars", type=int, default=32)
    parser.add_argument("--cost-r", type=float, default=0.02, help="Round-trip COST PROXY per frozen planned R")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.limit <= 10000:
        parser.error("limit must be 1..10000; server may apply a smaller cap")
    cutoff = utc(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if args.input:
        inbox = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        if args.bridge_url.rstrip("/") != "https://stc.feama.site":
            parser.error("authenticated reader is restricted to the approved STC production host")
        token = os.environ.get(args.token_env)
        if not token:
            parser.error("configured token environment variable is missing")
        # No claim, ack, approval, position, account or notification writes.
        try:
            inbox = BridgeClient(args.bridge_url, token, timeout_seconds=30).inbox(status="ingested", limit=args.limit)
        except Exception as exc:
            print(f"Read-only inbox fetch failed ({type(exc).__name__}); response body withheld.", file=sys.stderr)
            return 2
    report = report_from_inbox(inbox, as_of=cutoff, horizon_bars=args.horizon_bars,
                              cost_r=args.cost_r, requested_limit=args.limit if args.bridge_url else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    brief = {k: report[k] for k in ("as_of", "source_scope", "source_rows", "quarantine_counts", "coverage")}
    brief["overall"] = report["summary"]["overall"]
    print("STC_OUTCOME_ATTRIBUTION=" + json.dumps(brief, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
