from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1] / "research" / "community_shadow_registry.json"
)

ALLOWED_STATES = (
    "FROZEN_PASS",
    "SHADOW",
    "MULTITF_CONFIRMED",
    "ELIGIBLE_FOR_OWNER_PROMOTION",
)

LIVE_AUTHORITY_STATES: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShadowPromotionRecord:
    symbol: str
    timeframe: str
    component_id: str
    family: str
    state: str
    selected_parameters: dict[str, Any]
    development_test_trades: int
    development_test_expectancy_r: float
    development_test_profit_factor: float
    development_forward_trades: int
    development_forward_expectancy_r: float
    development_forward_profit_factor: float
    frozen_trades: int
    frozen_expectancy_r: float
    frozen_profit_factor: float
    frozen_max_drawdown_r: float
    source_run_id: int
    source_date: str
    live_authority: bool = False
    shadow_observations: int = 0
    shadow_expectancy_r: float | None = None
    supporting_timeframes: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


def _record_from_dict(row: dict[str, Any]) -> ShadowPromotionRecord:
    state = str(row["state"])
    if state not in ALLOWED_STATES:
        raise ValueError(f"Unsupported shadow promotion state: {state}")
    if bool(row.get("live_authority", False)):
        raise ValueError("Shadow promotion registry cannot grant live authority")
    return ShadowPromotionRecord(
        symbol=str(row["symbol"]),
        timeframe=str(row["timeframe"]),
        component_id=str(row["component_id"]),
        family=str(row["family"]),
        state=state,
        selected_parameters=dict(row.get("selected_parameters") or {}),
        development_test_trades=int(row["development_test_trades"]),
        development_test_expectancy_r=float(row["development_test_expectancy_r"]),
        development_test_profit_factor=float(row["development_test_profit_factor"]),
        development_forward_trades=int(row["development_forward_trades"]),
        development_forward_expectancy_r=float(row["development_forward_expectancy_r"]),
        development_forward_profit_factor=float(row["development_forward_profit_factor"]),
        frozen_trades=int(row["frozen_trades"]),
        frozen_expectancy_r=float(row["frozen_expectancy_r"]),
        frozen_profit_factor=float(row["frozen_profit_factor"]),
        frozen_max_drawdown_r=float(row["frozen_max_drawdown_r"]),
        source_run_id=int(row["source_run_id"]),
        source_date=str(row["source_date"]),
        live_authority=False,
        shadow_observations=int(row.get("shadow_observations") or 0),
        shadow_expectancy_r=(
            None
            if row.get("shadow_expectancy_r") is None
            else float(row["shadow_expectancy_r"])
        ),
        supporting_timeframes=tuple(str(x) for x in row.get("supporting_timeframes") or ()),
        notes=tuple(str(x) for x in row.get("notes") or ()),
    )


@lru_cache(maxsize=8)
def load_shadow_registry(path: str | None = None) -> tuple[ShadowPromotionRecord, ...]:
    target = Path(path) if path else DEFAULT_REGISTRY_PATH
    if not target.exists():
        return ()
    payload = json.loads(target.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "stc-community-shadow-registry-v1":
        raise ValueError("Unsupported community shadow registry schema")
    rows = payload.get("records")
    if not isinstance(rows, list):
        raise ValueError("Community shadow registry records must be a list")
    records = tuple(_record_from_dict(dict(row)) for row in rows)
    keys = [(x.symbol, x.timeframe, x.component_id) for x in records]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate symbol/timeframe/component in shadow registry")
    return records


def shadow_candidates(
    *,
    symbol: str | None = None,
    state: str | None = None,
    path: str | None = None,
) -> tuple[ShadowPromotionRecord, ...]:
    records = load_shadow_registry(path)
    if symbol is not None:
        records = tuple(x for x in records if x.symbol == symbol)
    if state is not None:
        if state not in ALLOWED_STATES:
            raise ValueError(f"Unsupported shadow promotion state: {state}")
        records = tuple(x for x in records if x.state == state)
    return records


def next_research_state(record: ShadowPromotionRecord) -> str:
    if record.state == "FROZEN_PASS":
        return "SHADOW"
    if record.state == "SHADOW" and record.supporting_timeframes:
        return "MULTITF_CONFIRMED"
    if (
        record.state == "MULTITF_CONFIRMED"
        and record.shadow_observations >= 30
        and record.shadow_expectancy_r is not None
        and record.shadow_expectancy_r > 0
    ):
        return "ELIGIBLE_FOR_OWNER_PROMOTION"
    return record.state


def public_shadow_record(record: ShadowPromotionRecord) -> dict[str, Any]:
    return {
        **record.__dict__,
        "supporting_timeframes": list(record.supporting_timeframes),
        "notes": list(record.notes),
        "next_research_state": next_research_state(record),
        "live_authority": False,
        "execution": "research_only",
    }
