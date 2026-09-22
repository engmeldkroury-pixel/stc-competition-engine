import json
from datetime import datetime, timezone

import pytest

from app.capital_backfill_request import (
    request_environment,
    run_capital_backfill_request,
)


def _capital_price(ts, base=100.0):
    def node(value):
        return {"bid": value - 0.1, "ask": value + 0.1}
    return {
        "snapshotTimeUTC": ts,
        "openPrice": node(base),
        "highPrice": node(base + 1.0),
        "lowPrice": node(base - 1.0),
        "closePrice": node(base + 0.5),
        "lastTradedVolume": 10,
    }


class FakeCapitalClient:
    def __init__(self):
        self.search_terms = []
        self.history_calls = []

    def search_markets(self, term):
        self.search_terms.append(term)
        return [
            {
                "epic": "GOLD",
                "instrumentName": "Gold",
                "instrumentType": "COMMODITIES",
                "marketStatus": "TRADEABLE",
                "currency": "USD",
                "delayTime": 0,
                "ignored": "not exported",
            }
        ]

    def historical_prices(self, *, epic, resolution, start, end):
        self.history_calls.append((epic, resolution, start, end))
        return [
            _capital_price("2026-01-01T00:00:00Z", 100.0),
            _capital_price("2026-01-01T00:15:00Z", 101.0),
        ]


def test_capital_backfill_discovery_is_bounded_and_read_only():
    client = FakeCapitalClient()
    result = run_capital_backfill_request(
        {
            "mode": "discover",
            "environment": "demo",
            "search_term": "gold",
        },
        client=client,
    )

    assert client.search_terms == ["gold"]
    assert result["mode"] == "discover"
    assert result["markets"] == [{
        "epic": "GOLD",
        "instrumentName": "Gold",
        "instrumentType": "COMMODITIES",
        "marketStatus": "TRADEABLE",
        "currency": "USD",
        "delayTime": 0,
    }]
    assert result["live_calibration_authority"] is False


def test_capital_backfill_request_produces_quarantined_history():
    client = FakeCapitalClient()
    result = run_capital_backfill_request(
        {
            "mode": "backfill",
            "environment": "live",
            "symbol": "CAPITALCOM:XAUUSD",
            "epic": "GOLD",
            "resolution": "MINUTE_15",
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-01-02T00:00:00Z",
            "price_basis": "mid",
        },
        client=client,
    )

    assert len(client.history_calls) == 1
    epic, resolution, start, end = client.history_calls[0]
    assert epic == "GOLD"
    assert resolution == "MINUTE_15"
    assert start == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert end == datetime(2026, 1, 2, tzinfo=timezone.utc)
    assert result["history"]["count"] == 2
    assert result["history"]["source"]["live_calibration_authority"] is False
    assert result["quarantine_status"] == "ALTERNATE_PROVIDER_RESEARCH_ONLY"
    assert result["exact_provider_archive_merge_authority"] is False
    assert result["live_calibration_authority"] is False


def test_capital_backfill_can_reconcile_without_granting_authority(tmp_path):
    reference = {
        "symbol": "CAPITALCOM:XAUUSD",
        "interval": "15m",
        "bars": [
            {"t": 1767225600, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 10},
            {"t": 1767226500, "o": 101.0, "h": 102.0, "l": 100.0, "c": 101.5, "v": 10},
        ],
    }
    path = tmp_path / "reference.json"
    path.write_text(json.dumps(reference), encoding="utf-8")

    result = run_capital_backfill_request(
        {
            "mode": "backfill",
            "symbol": "CAPITALCOM:XAUUSD",
            "epic": "GOLD",
            "resolution": "MINUTE_15",
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-01-02T00:00:00Z",
            "price_basis": "mid",
            "reference_archive": "reference.json",
        },
        client=FakeCapitalClient(),
        root=tmp_path,
    )

    assert result["reconciliation"]["status"] == "INSUFFICIENT_OVERLAP"
    assert result["reconciliation"]["live_calibration_authority"] is False
    assert result["live_calibration_authority"] is False


@pytest.mark.parametrize("environment", ["prod", "paper", ""])
def test_capital_environment_rejects_unknown_values(environment):
    request = {"environment": environment}
    if environment == "":
        assert request_environment(request) == "demo"
    else:
        with pytest.raises(ValueError, match="demo or live"):
            request_environment(request)


def test_capital_backfill_rejects_unknown_mode():
    with pytest.raises(ValueError, match="discover or backfill"):
        run_capital_backfill_request(
            {"mode": "trade"},
            client=FakeCapitalClient(),
        )
