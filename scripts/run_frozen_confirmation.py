#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.frozen_confirmation import (
    confirmation_result_dict,
    evaluate_frozen_hypothesis,
    load_frozen_hypotheses,
)


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate frozen STC hypotheses only on genuinely unseen archived bars."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("research_hypotheses/frozen_15m_v2.json"),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--hypothesis", action="append", default=[])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("confirmation_outputs/frozen_15m_v2.json"),
    )
    args = parser.parse_args()

    manifest = _read_json(args.root / args.manifest)
    hypotheses = load_frozen_hypotheses(manifest)
    requested = set(args.hypothesis)
    if requested:
        available = {item.hypothesis_id for item in hypotheses}
        unknown = requested - available
        if unknown:
            raise ValueError("Unknown frozen hypothesis IDs: " + ",".join(sorted(unknown)))
        hypotheses = tuple(item for item in hypotheses if item.hypothesis_id in requested)

    results = []
    for hypothesis in hypotheses:
        archive = _read_json(args.root / hypothesis.archive_path)
        context = (
            _read_json(args.root / hypothesis.context_path)
            if hypothesis.context_path
            else None
        )
        result = evaluate_frozen_hypothesis(
            archive,
            hypothesis,
            frozen_context_payload=context,
        )
        row = confirmation_result_dict(result)
        results.append(row)
        print("STC_FROZEN_CONFIRMATION=" + json.dumps(row, sort_keys=True))

    output = {
        "schema_version": "stc-frozen-confirmation-output-v1",
        "manifest_schema_version": manifest["schema_version"],
        "optimization_locked": True,
        "live_calibration_authority": False,
        "results": results,
    }
    output_path = args.root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
