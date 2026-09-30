from datetime import datetime, timezone

from app.crypto_data_connector import parse_closed_spot_bars, validate_spot_series


def test_parse_closed_spot_bars():
    bars = parse_closed_spot_bars(
        [[1700000000000, "100", "110", "90", "105", "500"]]
    )
    assert bars[0].timestamp == datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
    assert bars[0].close == 105.0


def test_validate_spot_series_rejects_short_history():
    result = validate_spot_series([], minimum_bars=900)
    assert result["valid"] is False
    assert result["reason"] == "insufficient_history"
