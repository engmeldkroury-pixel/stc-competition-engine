#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from app.calibration_registry import candidate_record_from_research_result


UTC = timezone.utc


def _parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a validated STC research output into the versioned informational calibration registry."
    )
    parser.add_argument("research_result", type=Path)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("research/calibration_registry.json"),
    )
    parser.add_argument(
        "--data-end-utc",
        required=True,
        help="Latest confirmed OHLCV timestamp used in research, ISO UTC.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Optional ISO UTC. Defaults to current UTC time.",
    )
    args = parser.parse_args()

    result = json.loads(args.research_result.read_text(encoding="utf-8"))
    data_end = _parse_utc(args.data_end_utc)
    generated = _parse_utc(args.generated_at_utc) if args.generated_at_utc else datetime.now(UTC)
    record = candidate_record_from_research_result(
        result,
        data_end_utc=data_end,
        generated_at_utc=generated,
    )

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    if registry.get("schema_version") != "stc-calibration-registry-v1":
        raise ValueError("Unsupported registry schema")
    rows = registry.get("records")
    if not isinstance(rows, list):
        raise ValueError("Registry records must be a list")

    key = (record["symbol"], record["strategy_id"], record["timeframe"])
    kept = [
        row
        for row in rows
        if (row.get("symbol"), row.get("strategy_id"), row.get("timeframe")) != key
    ]
    kept.append(record)
    kept.sort(key=lambda row: (row["symbol"], row["strategy_id"], row["timeframe"]))
    registry["records"] = kept
    args.registry.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Promoted informational calibration for {record['symbol']} "
        f"{record['strategy_id']} {record['timeframe']} "
        f"n={record['sample_size']} p={record['estimated_probability']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
