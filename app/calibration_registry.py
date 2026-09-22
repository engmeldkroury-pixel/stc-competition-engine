from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Mapping


UTC = timezone.utc
DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "research" / "calibration_registry.json"


@dataclass(frozen=True)
class RuntimeCalibration:
    symbol: str
    strategy_id: str
    timeframe: str
    generated_at_utc: datetime
    data_end_utc: datetime
    robust_score: float
    sample_size: int
    estimated_probability: float
    confidence_low: float
    confidence_high: float
    test_expectancy_r: float
    forward_expectancy_r: float
    test_profit_factor: float
    forward_profit_factor: float
    feature_weights: Mapping[str, float]
    informational_only: bool = True


def _parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _record_from_dict(row: Mapping[str, Any]) -> RuntimeCalibration:
    return RuntimeCalibration(
        symbol=str(row["symbol"]),
        strategy_id=str(row["strategy_id"]),
        timeframe=str(row["timeframe"]),
        generated_at_utc=_parse_utc(str(row["generated_at_utc"])),
        data_end_utc=_parse_utc(str(row["data_end_utc"])),
        robust_score=float(row["robust_score"]),
        sample_size=int(row["sample_size"]),
        estimated_probability=float(row["estimated_probability"]),
        confidence_low=float(row["confidence_low"]),
        confidence_high=float(row["confidence_high"]),
        test_expectancy_r=float(row["test_expectancy_r"]),
        forward_expectancy_r=float(row["forward_expectancy_r"]),
        test_profit_factor=float(row["test_profit_factor"]),
        forward_profit_factor=float(row["forward_profit_factor"]),
        feature_weights={
            str(k): float(v)
            for k, v in dict(row.get("feature_weights") or {}).items()
        },
        informational_only=bool(row.get("informational_only", True)),
    )


@lru_cache(maxsize=8)
def load_registry(path: str | None = None) -> tuple[RuntimeCalibration, ...]:
    target = Path(path) if path else DEFAULT_REGISTRY_PATH
    if not target.exists():
        return ()
    payload = json.loads(target.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "stc-calibration-registry-v1":
        raise ValueError("Unsupported calibration registry schema")
    rows = payload.get("records")
    if not isinstance(rows, list):
        raise ValueError("Calibration registry records must be a list")
    return tuple(_record_from_dict(row) for row in rows)


def runtime_calibration_usable(
    record: RuntimeCalibration,
    *,
    as_of: datetime,
    max_age_days: int = 14,
    min_samples: int = 50,
    min_forward_expectancy_r: float = 0.0,
    min_forward_profit_factor: float = 1.05,
) -> tuple[bool, tuple[str, ...]]:
    now = as_of.astimezone(UTC)
    reasons: list[str] = []
    age_days = (now - record.data_end_utc).total_seconds() / 86400.0
    if age_days < -0.01:
        reasons.append("research_data_end_is_in_future")
    if age_days > max_age_days:
        reasons.append("research_calibration_stale")
    if record.sample_size < min_samples:
        reasons.append("probability_sample_too_small")
    if not 0.0 < record.estimated_probability < 1.0:
        reasons.append("invalid_probability")
    if not 0.0 <= record.confidence_low <= record.estimated_probability:
        reasons.append("invalid_confidence_low")
    if not record.estimated_probability <= record.confidence_high <= 1.0:
        reasons.append("invalid_confidence_high")
    if record.robust_score <= 0:
        reasons.append("strategy_not_robust")
    if record.test_expectancy_r <= 0 or record.test_profit_factor < 1.10:
        reasons.append("out_of_sample_not_positive")
    if record.forward_expectancy_r <= min_forward_expectancy_r:
        reasons.append("forward_expectancy_not_positive")
    if record.forward_profit_factor < min_forward_profit_factor:
        reasons.append("forward_profit_factor_too_low")
    return reasons == [], tuple(reasons)


def lookup_runtime_calibration(
    symbol: str,
    *,
    as_of: datetime,
    path: str | None = None,
) -> tuple[RuntimeCalibration | None, tuple[str, ...]]:
    matches = [row for row in load_registry(path) if row.symbol == symbol]
    if not matches:
        return None, ("no_calibrated_research_record",)
    matches.sort(key=lambda row: row.data_end_utc, reverse=True)
    for row in matches:
        ok, reasons = runtime_calibration_usable(row, as_of=as_of)
        if ok:
            return row, ()
    _, reasons = runtime_calibration_usable(matches[0], as_of=as_of)
    return None, reasons


def candidate_record_from_research_result(
    result: Mapping[str, Any],
    *,
    data_end_utc: datetime,
    generated_at_utc: datetime,
) -> dict[str, Any]:
    report = dict(result.get("research_report") or {})
    probability = dict(report.get("setup_probability") or {})
    if report.get("status") != "VALIDATED":
        raise ValueError("Research result has no validated strategy")
    if probability.get("status") != "CALIBRATED":
        raise ValueError("Research probability is not calibrated")
    if probability.get("estimated_win_probability") is None:
        raise ValueError("Research probability estimate is missing")
    if int(probability.get("sample_size") or 0) < 50:
        raise ValueError("Research probability sample is below 50")

    feature_weights = {
        str(k): float(v) / 100.0
        for k, v in dict(report.get("feature_participation_pct") or {}).items()
        if float(v) > 0
    }
    forward_expectancy = report.get("forward_expectancy_r")
    forward_pf = report.get("forward_profit_factor")
    if forward_expectancy is None or float(forward_expectancy) <= 0:
        raise ValueError("Forward expectancy must be positive")
    if forward_pf is None or float(forward_pf) < 1.05:
        raise ValueError("Forward profit factor must be >= 1.05")

    return {
        "symbol": str(result["symbol"]),
        "strategy_id": str(report["selected_strategy"]),
        "timeframe": str(report["selected_timeframe"]),
        "generated_at_utc": generated_at_utc.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "data_end_utc": data_end_utc.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "robust_score": float(report["robust_score"]),
        "sample_size": int(probability["sample_size"]),
        "estimated_probability": float(probability["estimated_win_probability"]),
        "confidence_low": float(probability["confidence_low"]),
        "confidence_high": float(probability["confidence_high"]),
        "test_expectancy_r": float(report["test_expectancy_r"]),
        "forward_expectancy_r": float(forward_expectancy),
        "test_profit_factor": float(report["test_profit_factor"]),
        "forward_profit_factor": float(forward_pf),
        "feature_weights": feature_weights,
        "informational_only": True,
    }


def calibration_to_public_dict(record: RuntimeCalibration) -> dict[str, Any]:
    data = asdict(record)
    data["generated_at_utc"] = record.generated_at_utc.isoformat().replace("+00:00", "Z")
    data["data_end_utc"] = record.data_end_utc.isoformat().replace("+00:00", "Z")
    return data
