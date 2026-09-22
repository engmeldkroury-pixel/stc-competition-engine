#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
        default=None,
        help="Optional latest confirmed OHLCV timestamp. Defaults to the selected report timeframe end in the research result.",
    )
    parser.add_argument(
        "--overall",
        action="store_true",
        help="Promote the overall best research report instead of the live-entry 15m report. Informational use only.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Optional ISO UTC. Defaults to current UTC time.",
    )
    args = parser.parse_args()

    result = json.loads(args.research_result.read_text(encoding="utf-8"))
    report_key = "research_report" if args.overall else "live_entry_research_report"
    report = dict(result.get(report_key) or {})
    selected_timeframe = str(report.get("selected_timeframe") or "")
    if not selected_timeframe:
        raise ValueError(f"{report_key} has no selected timeframe")
    end_raw = args.data_end_utc or dict(result.get("derived_timeframe_end_utc") or {}).get(selected_timeframe)
    if not end_raw:
        raise ValueError("Selected timeframe data end is unavailable")
    data_end = _parse_utc(str(end_raw))
    generated = _parse_utc(args.generated_at_utc) if args.generated_at_utc else datetime.now(UTC)
    record = candidate_record_from_research_result(
        result,
        data_end_utc=data_end,
        generated_at_utc=generated,
        report_key=report_key,
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
