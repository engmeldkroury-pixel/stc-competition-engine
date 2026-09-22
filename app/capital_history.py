from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import time
from typing import Any, Callable

import httpx


LIVE_BASE_URL = "https://api-capital.backend-capital.com"
DEMO_BASE_URL = "https://demo-api-capital.backend-capital.com"

RESOLUTION_TO_INTERVAL = {
    "MINUTE": "1m",
    "MINUTE_5": "5m",
    "MINUTE_15": "15m",
    "MINUTE_30": "30m",
    "HOUR": "1h",
    "HOUR_4": "4h",
    "DAY": "1D",
    "WEEK": "1W",
}

RESOLUTION_SECONDS = {
    "MINUTE": 60,
    "MINUTE_5": 5 * 60,
    "MINUTE_15": 15 * 60,
    "MINUTE_30": 30 * 60,
    "HOUR": 60 * 60,
    "HOUR_4": 4 * 60 * 60,
    "DAY": 24 * 60 * 60,
    "WEEK": 7 * 24 * 60 * 60,
}


@dataclass(frozen=True)
class CapitalSession:
    cst: str
    security_token: str


class CapitalHistoryClient:
    """Read-only Capital.com historical-price client.

    This client never opens or modifies trades. It authenticates a REST session,
    reads historical prices, and maps them into the STC OHLCV research shape.
    """

    def __init__(
        self,
        *,
        api_key: str,
        identifier: str,
        password: str,
        demo: bool = True,
        client: httpx.Client | None = None,
        min_request_interval_s: float = 0.12,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key or not identifier or not password:
            raise ValueError("Capital.com API key, identifier and password are required")
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.base_url = DEMO_BASE_URL if demo else LIVE_BASE_URL
        self.client = client or httpx.Client(base_url=self.base_url, timeout=30.0)
        self.min_request_interval_s = max(0.0, float(min_request_interval_s))
        self.sleeper = sleeper
        self.session: CapitalSession | None = None

    def authenticate(self) -> CapitalSession:
        response = self.client.post(
            "/api/v1/session",
            headers={"X-CAP-API-KEY": self.api_key},
            json={
                "identifier": self.identifier,
                "password": self.password,
                "encryptedPassword": False,
            },
        )
        response.raise_for_status()
        cst = str(response.headers.get("CST") or "").strip()
        security_token = str(response.headers.get("X-SECURITY-TOKEN") or "").strip()
        if not cst or not security_token:
            raise RuntimeError("Capital.com session response did not include CST/security token")
        self.session = CapitalSession(cst=cst, security_token=security_token)
        return self.session

    def _auth_headers(self) -> dict[str, str]:
        if self.session is None:
            self.authenticate()
        assert self.session is not None
        return {
            "X-CAP-API-KEY": self.api_key,
            "CST": self.session.cst,
            "X-SECURITY-TOKEN": self.session.security_token,
        }

    def historical_prices(
        self,
        *,
        epic: str,
        resolution: str,
        start: datetime,
        end: datetime,
        max_per_request: int = 1000,
        target_bars_per_window: int = 900,
    ) -> list[dict[str, Any]]:
        epic = str(epic or "").strip()
        resolution = str(resolution or "").strip().upper()
        if not epic:
            raise ValueError("Capital.com epic is required")
        if resolution not in RESOLUTION_SECONDS:
            raise ValueError(f"Unsupported Capital.com resolution: {resolution}")
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("start/end must be timezone-aware")
        start = start.astimezone(timezone.utc)
        end = end.astimezone(timezone.utc)
        if end <= start:
            raise ValueError("end must be after start")
        if not 1 <= int(max_per_request) <= 1000:
            raise ValueError("max_per_request must be between 1 and 1000")
        if not 1 <= int(target_bars_per_window) <= 950:
            raise ValueError("target_bars_per_window must be between 1 and 950")

        step = timedelta(seconds=RESOLUTION_SECONDS[resolution] * int(target_bars_per_window))
        cursor = start
        by_timestamp: dict[str, dict[str, Any]] = {}

        while cursor < end:
            chunk_end = min(cursor + step, end)
            response = self.client.get(
                f"/api/v1/prices/{epic}",
                headers=self._auth_headers(),
                params={
                    "resolution": resolution,
                    "max": int(max_per_request),
                    "from": _api_timestamp(cursor),
                    "to": _api_timestamp(chunk_end),
                },
            )
            response.raise_for_status()
            payload = response.json()
            prices = payload.get("prices") if isinstance(payload, dict) else None
            if not isinstance(prices, list):
                raise RuntimeError("Capital.com historical price response missing prices list")

            for row in prices:
                if not isinstance(row, dict):
                    continue
                key = str(row.get("snapshotTimeUTC") or "").strip()
                if not key:
                    continue
                by_timestamp[key] = row

            cursor = chunk_end
            if cursor < end and self.min_request_interval_s:
                self.sleeper(self.min_request_interval_s)

        return [by_timestamp[key] for key in sorted(by_timestamp)]


def _api_timestamp(value: datetime) -> str:
    value = value.astimezone(timezone.utc).replace(tzinfo=None, microsecond=0)
    return value.isoformat(timespec="seconds")


def _number(value: Any, *, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Capital.com price field {label} is not numeric") from exc


def _price_component(node: Any, *, basis: str, label: str) -> float:
    if not isinstance(node, dict):
        raise ValueError(f"Capital.com {label} price is missing")
    bid = _number(node.get("bid"), label=f"{label}.bid")
    ask = _number(node.get("ask"), label=f"{label}.ask")
    if basis == "bid":
        return bid
    if basis == "ask":
        return ask
    if basis == "mid":
        return (bid + ask) / 2.0
    raise ValueError("price_basis must be bid, ask, or mid")


def _parse_utc_timestamp(value: Any) -> int:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Capital.com snapshotTimeUTC is missing")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.astimezone(timezone.utc).timestamp())


def capital_prices_to_stc_ohlcv(
    *,
    symbol: str,
    epic: str,
    resolution: str,
    prices: list[dict[str, Any]],
    price_basis: str = "mid",
) -> dict[str, Any]:
    symbol = str(symbol or "").strip()
    epic = str(epic or "").strip()
    resolution = str(resolution or "").strip().upper()
    price_basis = str(price_basis or "").strip().lower()
    if not symbol or not epic:
        raise ValueError("symbol and epic are required")
    if resolution not in RESOLUTION_TO_INTERVAL:
        raise ValueError(f"Unsupported Capital.com resolution: {resolution}")
    if price_basis not in {"bid", "ask", "mid"}:
        raise ValueError("price_basis must be bid, ask, or mid")

    bars_by_t: dict[int, dict[str, int | float]] = {}
    for row in prices:
        if not isinstance(row, dict):
            raise ValueError("Capital.com price row must be an object")
        t = _parse_utc_timestamp(row.get("snapshotTimeUTC"))
        bar = {
            "t": t,
            "o": _price_component(row.get("openPrice"), basis=price_basis, label="open"),
            "h": _price_component(row.get("highPrice"), basis=price_basis, label="high"),
            "l": _price_component(row.get("lowPrice"), basis=price_basis, label="low"),
            "c": _price_component(row.get("closePrice"), basis=price_basis, label="close"),
            "v": _number(row.get("lastTradedVolume") or 0, label="lastTradedVolume"),
        }
        if bar["h"] < max(bar["o"], bar["l"], bar["c"]) or bar["l"] > min(bar["o"], bar["h"], bar["c"]):
            raise ValueError(f"Invalid Capital.com OHLC envelope at t={t}")
        bars_by_t[t] = bar

    bars = [bars_by_t[t] for t in sorted(bars_by_t)]
    return {
        "success": True,
        "symbol": symbol,
        "interval": RESOLUTION_TO_INTERVAL[resolution],
        "count": len(bars),
        "bars": bars,
        "source": {
            "provider": "Capital.com REST API",
            "provider_epic": epic,
            "resolution": resolution,
            "price_basis": price_basis,
            "feed_comparability": "PROVIDER_CONSISTENT_NOT_PROVEN_IDENTICAL_TO_TRADINGVIEW_CAPITALCOM_FEED",
            "live_calibration_authority": False,
            "fresh_cross_feed_reconciliation_required": True,
        },
    }
