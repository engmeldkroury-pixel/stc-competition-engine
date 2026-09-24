#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.general_lab_request import build_general_lab_completion


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate an STC General Lab request from exact-provider OHLCV series."
    )
    parser.add_argument("input", type=Path, help="JSON containing request_id, resolved_symbol and exact-provider series")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    completion = build_general_lab_completion(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(completion, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "request_id": completion["request_id"],
        "resolved_symbol": completion["resolved_symbol"],
        "status": "EVALUATED_PAYLOAD_READY",
        "execution": "research_only",
        "live_authority": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
