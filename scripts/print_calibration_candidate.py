#!/usr/bin/env python3
from __future__ import annotations

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


def build_candidate(
    result: dict,
    *,
    report_key: str = "live_entry_research_report",
) -> dict:
    report = dict(result.get(report_key) or {})
    timeframe = str(report.get("selected_timeframe") or "")
    if report.get("status") != "VALIDATED" or not timeframe:
        raise ValueError("research_result_not_validated")
    end_map = dict(result.get("derived_timeframe_end_utc") or {})
    end_raw = end_map.get(timeframe)
    if not end_raw:
        raise ValueError("selected_timeframe_data_end_missing")
    return candidate_record_from_research_result(
        result,
        data_end_utc=_parse_utc(str(end_raw)),
        generated_at_utc=datetime.now(UTC),
        report_key=report_key,
    )


def main() -> int:
    args = list(sys.argv[1:])
    overall = False
    if "--overall" in args:
        args.remove("--overall")
        overall = True
    if len(args) != 1:
        print(
            "Usage: print_calibration_candidate.py RESEARCH_RESULT.json [--overall]",
            file=sys.stderr,
        )
        return 2
    path = Path(args[0])
    result = json.loads(path.read_text(encoding="utf-8"))
    report_key = "research_report" if overall else "live_entry_research_report"
    prefix = "STC_OVERALL_RESEARCH_CANDIDATE" if overall else "STC_CALIBRATION_CANDIDATE"
    try:
        candidate = build_candidate(result, report_key=report_key)
    except ValueError as exc:
        print(prefix + "=NONE reason=" + str(exc))
        return 0
    print(prefix + "=" + json.dumps(candidate, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
