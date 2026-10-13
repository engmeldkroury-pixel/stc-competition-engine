"""Negative fixtures for Spot market-data proof and registry fail-closed rules."""

import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from math import inf, nan
from pathlib import Path

import pytest

from app.crypto_data_connector import SpotBar, parse_closed_spot_bars, validate_spot_series
from app.crypto_spot_registry import load_crypto_spot_registry


UTC = timezone.utc
START = datetime(2026, 10, 1, tzinfo=UTC)
AS_OF = datetime(2026, 10, 11, tzinfo=UTC)


def valid_bars():
    start_ms = int(START.timestamp() * 1000)
    return parse_closed_spot_bars(
        [
            [
                start_ms + index * 900_000,
                "100", "110", "90", "105", "500",
                start_ms + (index + 1) * 900_000 - 1,
            ]
            for index in range(900)
        ]
    )


def test_900_realistic_closed_candles_pass_quality():
    bars = valid_bars()
    assert len(bars) == 900
    report = validate_spot_series(bars, as_of_utc=AS_OF)
    assert report["valid"] is True
    assert report["closed_bars_only"] is True
    assert report["ohlc_consistent"] is True


@pytest.mark.parametrize(
    ("edit", "reason"),
    [
        ({"high": 99}, "ohlc_consistent"),
        ({"low": 106}, "ohlc_consistent"),
        ({"volume": -1}, "nonnegative_volume"),
        ({"volume": nan}, "finite_numbers"),
        ({"close": inf}, "finite_numbers"),
        ({"open": 0}, "positive_prices"),
        ({"close_time": None}, "closed_bars_only"),
        ({"close_time": START}, "closed_bars_only"),
        ({"timestamp": START + timedelta(days=90)}, "chronological"),
    ],
)
def test_invalid_exchange_candles_fail_closed(edit, reason):
    bars = valid_bars()
    bars[0] = replace(bars[0], **edit)
    report = validate_spot_series(bars, as_of_utc=AS_OF)
    assert report["valid"] is False
    assert report["reason"] == reason


def test_duplicate_time_and_out_of_order_candles_rejected():
    bars = valid_bars()
    bars[1] = replace(bars[1], timestamp=bars[0].timestamp)
    assert validate_spot_series(bars, as_of_utc=AS_OF)["chronological"] is False


def test_6_column_row_parses_but_cannot_claim_finalization():
    synthetic = [
        SpotBar(
            timestamp=START + timedelta(minutes=15 * i),
            open=100, high=110, low=90, close=105, volume=1,
        )
        for i in range(900)
    ]
    result = validate_spot_series(synthetic, as_of_utc=AS_OF)
    assert result["valid"] is False
    assert result["reason"] == "closed_bars_only"


def test_current_partial_exchange_candle_cannot_be_backtested():
    bars = valid_bars()
    bar = bars[-1]
    result = validate_spot_series(
        bars,
        as_of_utc=bar.timestamp + timedelta(minutes=7),
    )
    assert result["valid"] is False
    assert result["reason"] == "closed_bars_only"


def test_bad_timestamps_and_truncated_rows_rejected():
    with pytest.raises(ValueError):
        parse_closed_spot_bars([[0, "100", "110", "90", "105"]])
    with pytest.raises(ValueError):
        parse_closed_spot_bars([["not-int", "100", "110", "90", "105", "0"]])
    with pytest.raises(ValueError):
        validate_spot_series(valid_bars(), as_of_utc=datetime(2026, 10, 11))


def test_registered_spot_research_assets_remain_separate_from_queued():
    registry = load_crypto_spot_registry()
    assert [asset.asset for asset in registry.research_assets] == [
        "BTC", "ETH", "SOL", "TRB", "GALA", "YGG", "NOT",
    ]
    assert registry.by_pair("BTCUSDT").asset == "BTC"
    assert registry.by_asset("BNB").status == "QUEUED"
    with pytest.raises(KeyError):
        registry.by_asset("DOGE")
    with pytest.raises(KeyError):
        registry.by_pair("BTCUSD")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["constraints"].update(futures=True),
        lambda d: d["constraints"].update(leverage=True),
        lambda d: d["constraints"].update(shorting=True),
        lambda d: d["constraints"].update(real_money_authorized=True),
        lambda d: d.update(mode="FUTURES"),
        lambda d: d.update(research_order=["BTC", "ETH"]),
        lambda d: d["assets"].append(dict(d["assets"][0])),
        lambda d: d["data_policy"].update(closed_bars_only=False),
    ],
)
def test_unapproved_registry_must_fail_closed(tmp_path, mutate):
    data = json.loads(
        (Path(__file__).resolve().parents[1] / "research_inputs" / "CRYPTO_SPOT_ASSET_REGISTRY.json")
        .read_text(encoding="utf-8")
    )
    mutate(data)
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_crypto_spot_registry(path)
