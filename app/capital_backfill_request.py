from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .capital_history import CapitalHistoryClient, capital_prices_to_stc_ohlcv
from .feed_reconciliation import reconciliation_dict, reconcile_ohlcv_feeds


def parse_utc(value: Any) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("UTC timestamp is required")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def request_environment(request: dict[str, Any]) -> str:
    environment = str(request.get("environment") or "demo").strip().lower()
    if environment not in {"demo", "live"}:
        raise ValueError("Capital.com request environment must be demo or live")
    return environment


def _compact_market(row: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "epic",
        "instrumentName",
        "instrumentType",
        "marketStatus",
        "currency",
        "delayTime",
    )
    return {key: row.get(key) for key in allowed if key in row}


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def run_capital_backfill_request(
    request: dict[str, Any],
    *,
    client: CapitalHistoryClient,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Execute one bounded read-only Capital.com research request.

    The function never places trades and never merges alternate-provider data
    into the exact-provider archive. Backfill output remains quarantined.
    """
    if not isinstance(request, dict):
        raise ValueError("Capital.com request must be an object")
    mode = str(request.get("mode") or "").strip().lower()

    if mode == "discover":
        search_term = str(request.get("search_term") or "").strip()
        if not search_term:
            raise ValueError("discover mode requires search_term")
        markets = client.search_markets(search_term)
        return {
            "schema_version": "stc-capital-backfill-output-v1",
            "mode": "discover",
            "environment": request_environment(request),
            "search_term": search_term,
            "markets": [_compact_market(row) for row in markets],
            "live_calibration_authority": False,
        }

    if mode != "backfill":
        raise ValueError("Capital.com request mode must be discover or backfill")

    symbol = str(request.get("symbol") or "").strip()
    epic = str(request.get("epic") or "").strip()
    resolution = str(request.get("resolution") or "").strip().upper()
    price_basis = str(request.get("price_basis") or "mid").strip().lower()
    if not symbol or not epic or not resolution:
        raise ValueError("backfill mode requires symbol, epic and resolution")

    start = parse_utc(request.get("from"))
    end = parse_utc(request.get("to"))
    prices = client.historical_prices(
        epic=epic,
        resolution=resolution,
        start=start,
        end=end,
    )
    history = capital_prices_to_stc_ohlcv(
        symbol=symbol,
        epic=epic,
        resolution=resolution,
        prices=prices,
        price_basis=price_basis,
    )

    reconciliation = None
    reference_path = str(request.get("reference_archive") or "").strip()
    if reference_path:
        reference = _read_json(root / reference_path)
        reconciliation = reconciliation_dict(
            reconcile_ohlcv_feeds(reference, history)
        )

    return {
        "schema_version": "stc-capital-backfill-output-v1",
        "mode": "backfill",
        "environment": request_environment(request),
        "symbol": symbol,
        "epic": epic,
        "resolution": resolution,
        "price_basis": price_basis,
        "from": start.isoformat().replace("+00:00", "Z"),
        "to": end.isoformat().replace("+00:00", "Z"),
        "history": history,
        "reconciliation": reconciliation,
        "quarantine_status": "ALTERNATE_PROVIDER_RESEARCH_ONLY",
        "exact_provider_archive_merge_authority": False,
        "live_calibration_authority": False,
    }
