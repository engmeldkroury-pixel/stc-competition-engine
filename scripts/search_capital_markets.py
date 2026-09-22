#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.capital_history import CapitalHistoryClient


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Capital.com market/epic discovery for STC research."
    )
    parser.add_argument("search_term")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    client = CapitalHistoryClient(
        api_key=_required_env("CAPITAL_API_KEY"),
        identifier=_required_env("CAPITAL_IDENTIFIER"),
        password=_required_env("CAPITAL_PASSWORD"),
        demo=not args.live,
    )
    markets = client.search_markets(args.search_term)
    compact = []
    for row in markets:
        compact.append({
            key: row.get(key)
            for key in (
                "epic",
                "instrumentName",
                "instrumentType",
                "marketStatus",
                "currency",
                "delayTime",
            )
            if key in row
        })
    print(json.dumps(compact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
