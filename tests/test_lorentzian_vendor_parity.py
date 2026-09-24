from __future__ import annotations

from math import isclose, isnan
from pathlib import Path

from app._vendor.lorentzian_classification import Settings, calculate, read_tradingview_csv


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "lorentzian"
    / "pine_btcusd_h1_trimmed_limited_history.csv"
)


def _assert_float_parity(expected: float, actual: float, tolerance: float = 1e-6) -> None:
    if isnan(expected):
        assert isnan(actual)
        return
    assert isclose(expected, actual, abs_tol=tolerance, rel_tol=0.0)


def test_vendored_lorentzian_reference_matches_pine_fixture() -> None:
    tv_rows, price_scale = read_tradingview_csv(FIXTURE)
    results = calculate(
        tv_rows,
        settings=Settings(include_full_history=False),
        price_scale=price_scale,
    )

    assert len(results) == len(tv_rows)
    for tv, result in zip(tv_rows, results, strict=True):
        for field in ("f1", "f2", "f3", "f4", "f5", "kernel"):
            _assert_float_parity(float(getattr(tv, field)), float(getattr(result, field)))

        assert tv.prediction == result.prediction
        assert tv.direction == result.direction
        assert tv.buy is result.buy
        assert tv.sell is result.sell

        # Pine exports StopBuy/StopSell. The exact reference exposes those as
        # ResultRow.stop_buy/stop_sell while TvRow stores the same source
        # columns in exit_buy/exit_sell.
        assert tv.exit_buy is result.stop_buy
        assert tv.exit_sell is result.stop_sell

        if tv.backtest_stream is not None:
            assert tv.backtest_stream == result.backtest_stream


def test_vendored_lorentzian_provenance_is_pinned_and_licensed() -> None:
    vendor = Path(__file__).parents[1] / "app" / "_vendor" / "lorentzian_classification"
    notice = (vendor / "STC_VENDOR_NOTICE.md").read_text(encoding="utf-8")
    license_text = (vendor / "LICENSE.md").read_text(encoding="utf-8")

    assert "27776bd51cbd3e07b6383cfa468d4d33f4b50297" in notice
    assert "MIT License" in license_text
    assert "AI Edge" in license_text
