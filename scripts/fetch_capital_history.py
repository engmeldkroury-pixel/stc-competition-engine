#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.capital_history import CapitalHistoryClient, capital_prices_to_stc_ohlcv


def _dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Capital.com historical backfill for STC research."
    )
    parser.add_argument("--symbol", required=True, help="STC/TradingView symbol label, e.g. CAPITALCOM:XAUUSD")
    parser.add_argument("--epic", required=True, help="Capital.com provider epic; must be verified before use")
    parser.add_argument("--resolution", required=True, choices=["MINUTE","MINUTE_5","MINUTE_15","MINUTE_30","HOUR","HOUR_4","DAY","WEEK"])
    parser.add_argument("--from", dest="start", required=True, help="UTC ISO timestamp")
    parser.add_argument("--to", dest="end", required=True, help="UTC ISO timestamp")
    parser.add_argument("--price-basis", default="mid", choices=["bid","ask","mid"])
    parser.add_argument("--live", action="store_true", help="Use live Capital.com base URL. Default is demo.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    client = CapitalHistoryClient(
        api_key=_required_env("CAPITAL_API_KEY"),
        identifier=_required_env("CAPITAL_IDENTIFIER"),
        password=_required_env("CAPITAL_PASSWORD"),
        demo=not args.live,
    )
    prices = client.historical_prices(
        epic=args.epic,
        resolution=args.resolution,
        start=_dt(args.start),
        end=_dt(args.end),
    )
    payload = capital_prices_to_stc_ohlcv(
        symbol=args.symbol,
        epic=args.epic,
        resolution=args.resolution,
        prices=prices,
        price_basis=args.price_basis,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "symbol": payload["symbol"],
        "provider_epic": args.epic,
        "interval": payload["interval"],
        "count": payload["count"],
        "price_basis": args.price_basis,
        "live_calibration_authority": False,
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
