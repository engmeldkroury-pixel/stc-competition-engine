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

from app.capital_backfill_request import (
    request_environment,
    run_capital_backfill_request,
)
from app.capital_history import CapitalHistoryClient


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute one read-only Capital.com STC discovery/backfill request."
    )
    parser.add_argument(
        "--request",
        type=Path,
        default=Path("capital_backfill_inputs/request.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("capital_backfill_outputs"),
    )
    args = parser.parse_args()

    request = _read_json(args.request)
    environment = request_environment(request)
    client = CapitalHistoryClient(
        api_key=_required_env("CAPITAL_API_KEY"),
        identifier=_required_env("CAPITAL_IDENTIFIER"),
        password=_required_env("CAPITAL_PASSWORD"),
        demo=(environment == "demo"),
    )
    result = run_capital_backfill_request(
        request,
        client=client,
        root=ROOT,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if result.get("mode") == "backfill":
        history_path = args.output_dir / "history.json"
        history_path.write_text(
            json.dumps(result["history"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if result.get("reconciliation") is not None:
            reconciliation_path = args.output_dir / "reconciliation.json"
            reconciliation_path.write_text(
                json.dumps(result["reconciliation"], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

    summary = {
        "mode": result["mode"],
        "environment": result["environment"],
        "symbol": result.get("symbol"),
        "epic": result.get("epic"),
        "history_count": (result.get("history") or {}).get("count"),
        "reconciliation_status": (result.get("reconciliation") or {}).get("status"),
        "quarantine_status": result.get("quarantine_status"),
        "live_calibration_authority": False,
        "output_dir": str(args.output_dir),
    }
    print("STC_CAPITAL_BACKFILL=" + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
