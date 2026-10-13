"""Paper research-only score and eligibility projections for registered contest rules.

Never routes trade orders, reads a TradingView account, or claims official
score/position measurements. Source: research_inputs/CONTEST_THE_LEAP_COMMODITIES_OCT2026.json
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INTAKE = (
    Path(__file__).resolve().parents[1]
    / "research_inputs"
    / "CONTEST_THE_LEAP_COMMODITIES_OCT2026.json"
)


def load_october_commodities_intake(path: str | Path | None = None) -> dict[str, Any]:
    doc = json.loads(Path(path or DEFAULT_INTAKE).read_text(encoding="utf-8"))
    if doc.get("competition_id") != "tradingview-commodities-oct-2026":
        raise ValueError("Competition identity not verified")
    if not (
        doc.get("status") == "DISCOVERED_RESEARCH_ONLY_NOT_REGISTERED"
        and doc.get("paper_only") is True
        and doc.get("trading_authority") == "NONE"
        and doc.get("strategy_promoted") is False
        and doc.get("owner_registration_confirmed") is False
        and doc.get("notification_route_enabled") is False
        and doc.get("no_email") is True
    ):
        raise ValueError("Research intake must remain paper-only and not activated")
    symbols = doc.get("allowed_symbols_and_max_open_position")
    if not isinstance(symbols, list) or len(symbols) != 8:
        raise ValueError("Invalid contest symbol register")
    names = [row.get("symbol") for row in symbols]
    if len(set(names)) != 8 or any(
        not isinstance(name, str) or not name.startswith("OANDA:")
        for name in names
    ):
        raise ValueError("Exact OANDA symbol registry required")
    return doc


def projected_leap_score(
    realized_pnl_usd: float,
    observed_max_drawdown_pct: float,
    *,
    initial_balance_usd: float = 100_000.0,
    drawdown_floor_pct: float = 5.0,
) -> dict[str, float | bool]:
    """Official-formula projection from caller-supplied records, NOT official account data.

    TradingView measures equity on a proprietary, variable schedule. It is
    impossible to derive authoritative MaxDD from an OHLCV backtest alone.
    """
    values = (realized_pnl_usd, observed_max_drawdown_pct, initial_balance_usd, drawdown_floor_pct)
    if not all(type(v) in (float, int) and math.isfinite(v) for v in values):
        raise ValueError("Nonfinite or nonnumeric contest input")
    if initial_balance_usd <= 0 or observed_max_drawdown_pct < 0 or drawdown_floor_pct != 5.0:
        raise ValueError("Invalid balance, drawdown or official 5% floor")
    profit_pct = realized_pnl_usd / initial_balance_usd * 100.0
    divisor = 5.0 if profit_pct <= 0 else max(observed_max_drawdown_pct, 5.0)
    return {
        "projected_score": round(profit_pct / divisor, 8),
        "profit_pct": round(profit_pct, 8),
        "max_drawdown_pct_assumed": observed_max_drawdown_pct,
        "effective_denominator_pct": divisor,
        "official_score_verified": False,
        "paper_execution_authorized": False,
    }


def distinct_qualifying_activity_dates(events: list[dict[str, str]]) -> tuple[str, ...]:
    """Counts UTC dates with documented position OPEN or CLOSE actions only.

    Does NOT by itself establish full prize eligibility, nor synthesize fills
    from alerts or recommendations.
    """
    valid_dates = set()
    for event in events:
        action = event.get("action")
        if action not in ("OPEN", "CLOSE"):
            continue
        raw = event.get("executed_at_utc")
        if not isinstance(raw, str):
            raise ValueError("Missing dated external paper position action")
        moment = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("Timezone-aware trade activity required")
        valid_dates.add(moment.astimezone(timezone.utc).date().isoformat())
    return tuple(sorted(valid_dates))


def within_official_position_cap(symbol: str, quantity: float) -> bool:
    """Simple rule boundary, not a position-sizing instruction."""
    rules = load_october_commodities_intake()
    if not isinstance(symbol, str) or type(quantity) not in (float, int):
        return False
    if not math.isfinite(quantity) or quantity <= 0:
        return False
    limits = {row["symbol"]: float(row["maximum_quantity"])
              for row in rules["allowed_symbols_and_max_open_position"]}
    return symbol in limits and quantity <= limits[symbol]
