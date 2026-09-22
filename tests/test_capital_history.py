from datetime import datetime, timezone

import httpx
import pytest

from app.capital_history import CapitalHistoryClient, capital_prices_to_stc_ohlcv


UTC = timezone.utc


def _price(ts, o=(100, 102), h=(104, 106), l=(98, 100), c=(101, 103), v=10):
    def p(pair):
        return {"bid": pair[0], "ask": pair[1]}
    return {
        "snapshotTimeUTC": ts,
        "openPrice": p(o),
        "highPrice": p(h),
        "lowPrice": p(l),
        "closePrice": p(c),
        "lastTradedVolume": v,
    }


def test_capital_prices_convert_midpoint_and_preserve_research_quarantine():
    payload = capital_prices_to_stc_ohlcv(
        symbol="CAPITALCOM:XAUUSD",
        epic="GOLD",
        resolution="MINUTE_15",
        prices=[
            _price("2026-01-01T00:15:00", c=(103, 105)),
            _price("2026-01-01T00:00:00"),
        ],
        price_basis="mid",
    )
    assert [bar["t"] for bar in payload["bars"]] == sorted(bar["t"] for bar in payload["bars"])
    assert payload["bars"][0]["o"] == 101
    assert payload["bars"][0]["c"] == 102
    assert payload["source"]["provider_epic"] == "GOLD"
    assert payload["source"]["live_calibration_authority"] is False
    assert payload["source"]["fresh_cross_feed_reconciliation_required"] is True


@pytest.mark.parametrize(("basis", "expected"), [("bid", 100), ("ask", 102), ("mid", 101)])
def test_capital_price_basis_is_explicit(basis, expected):
    payload = capital_prices_to_stc_ohlcv(
        symbol="CAPITALCOM:XAUUSD",
        epic="GOLD",
        resolution="MINUTE_15",
        prices=[_price("2026-01-01T00:00:00")],
        price_basis=basis,
    )
    assert payload["bars"][0]["o"] == expected


def test_capital_history_client_authenticates_and_chunks_requests():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.path == "/api/v1/session":
            return httpx.Response(
                200,
                headers={"CST": "cst-token", "X-SECURITY-TOKEN": "security-token"},
                json={"accountInfo": {}},
            )
        if request.url.path == "/api/v1/prices/GOLD":
            params = dict(request.url.params)
            assert params["resolution"] == "MINUTE_15"
            assert params["max"] == "1000"
            assert request.headers["CST"] == "cst-token"
            assert request.headers["X-SECURITY-TOKEN"] == "security-token"
            return httpx.Response(
                200,
                json={"prices": [_price(params["from"])]},
            )
        return httpx.Response(404)

    client = httpx.Client(
        base_url="https://demo-api-capital.backend-capital.com",
        transport=httpx.MockTransport(handler),
    )
    api = CapitalHistoryClient(
        api_key="test-key",
        identifier="user",
        password="pass",
        client=client,
        min_request_interval_s=0,
        sleeper=lambda _: None,
    )
    rows = api.historical_prices(
        epic="GOLD",
        resolution="MINUTE_15",
        start=datetime(2026, 1, 1, tzinfo=UTC),
        end=datetime(2026, 1, 20, tzinfo=UTC),
        target_bars_per_window=900,
    )
    price_calls = [call for call in calls if call.url.path == "/api/v1/prices/GOLD"]
    assert len(price_calls) >= 2
    assert len(rows) == len(price_calls)


def test_capital_history_rejects_unaware_dates_and_invalid_max():
    api = CapitalHistoryClient(
        api_key="a",
        identifier="b",
        password="c",
        client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(500))),
        min_request_interval_s=0,
    )
    with pytest.raises(ValueError, match="timezone-aware"):
        api.historical_prices(
            epic="GOLD",
            resolution="MINUTE_15",
            start=datetime(2026, 1, 1),
            end=datetime(2026, 1, 2),
        )
    with pytest.raises(ValueError, match="max_per_request"):
        api.historical_prices(
            epic="GOLD",
            resolution="MINUTE_15",
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 1, 2, tzinfo=UTC),
            max_per_request=1001,
        )


def test_capital_conversion_rejects_invalid_basis_and_ohlc():
    with pytest.raises(ValueError, match="price_basis"):
        capital_prices_to_stc_ohlcv(
            symbol="CAPITALCOM:XAUUSD",
            epic="GOLD",
            resolution="MINUTE_15",
            prices=[],
            price_basis="last",
        )
    with pytest.raises(ValueError, match="Invalid Capital.com OHLC"):
        capital_prices_to_stc_ohlcv(
            symbol="CAPITALCOM:XAUUSD",
            epic="GOLD",
            resolution="MINUTE_15",
            prices=[_price("2026-01-01T00:00:00", h=(99, 99))],
            price_basis="mid",
        )


def test_capital_market_discovery_is_read_only_and_authenticated():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/session":
            return httpx.Response(
                200,
                headers={"CST": "cst-token", "X-SECURITY-TOKEN": "security-token"},
                json={},
            )
        if request.url.path == "/api/v1/markets":
            assert request.url.params["searchTerm"] == "gold"
            assert request.headers["CST"] == "cst-token"
            return httpx.Response(
                200,
                json={"markets": [{"epic": "GOLD", "instrumentName": "Gold"}]},
            )
        return httpx.Response(404)

    api = CapitalHistoryClient(
        api_key="test-key",
        identifier="user",
        password="pass",
        client=httpx.Client(
            base_url="https://demo-api-capital.backend-capital.com",
            transport=httpx.MockTransport(handler),
        ),
        min_request_interval_s=0,
    )
    rows = api.search_markets("gold")
    assert rows == [{"epic": "GOLD", "instrumentName": "Gold"}]
