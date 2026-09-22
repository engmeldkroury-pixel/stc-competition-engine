import pytest

from app.ohlcv_archive import merge_ohlcv_payloads


def _payload(symbol="TEST:X", interval="15m", bars=None):
    return {
        "success": True,
        "symbol": symbol,
        "interval": interval,
        "bars": bars or [],
    }


def _bar(t, o=100, h=102, l=99, c=101, v=10):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v}


def test_archive_merge_deduplicates_orders_and_replaces_revised_overlap():
    existing = _payload(bars=[
        _bar(200),
        _bar(100),
    ])
    incoming = _payload(bars=[
        _bar(200, c=101.5),
        _bar(300),
    ])
    merged, report = merge_ohlcv_payloads(existing, incoming)

    assert [row["t"] for row in merged["bars"]] == [100, 200, 300]
    assert merged["bars"][1]["c"] == 101.5
    assert report.added_bars == 1
    assert report.replaced_bars == 1
    assert report.total_bars == 3
    assert merged["archive"]["coverage_first_t"] == 100
    assert merged["archive"]["coverage_last_t"] == 300


def test_archive_merge_counts_unchanged_overlap():
    existing = _payload(bars=[_bar(100)])
    incoming = _payload(bars=[_bar(100), _bar(200)])
    merged, report = merge_ohlcv_payloads(existing, incoming)

    assert report.unchanged_overlap_bars == 1
    assert report.added_bars == 1
    assert merged["archive"]["snapshots_merged"] == 2


def test_archive_merge_can_initialize_from_first_snapshot():
    incoming = _payload(symbol="CAPITALCOM:XAUUSD", bars=[_bar(100), _bar(200)])
    merged, report = merge_ohlcv_payloads(None, incoming)

    assert report.existing_bars == 0
    assert report.total_bars == 2
    assert merged["archive"]["snapshots_merged"] == 1
    assert merged["symbol"] == "CAPITALCOM:XAUUSD"


@pytest.mark.parametrize(
    ("existing", "incoming"),
    [
        (_payload(symbol="TEST:A"), _payload(symbol="TEST:B")),
        (_payload(interval="15m"), _payload(interval="1h")),
    ],
)
def test_archive_merge_rejects_symbol_or_interval_mismatch(existing, incoming):
    with pytest.raises(ValueError, match="Cannot merge different OHLCV identities"):
        merge_ohlcv_payloads(existing, incoming)


def test_archive_merge_rejects_duplicate_timestamps_within_snapshot():
    incoming = _payload(bars=[_bar(100), _bar(100)])
    with pytest.raises(ValueError, match="duplicate timestamps"):
        merge_ohlcv_payloads(None, incoming)


def test_archive_merge_rejects_invalid_ohlc_envelope():
    incoming = _payload(bars=[_bar(100, o=100, h=99, l=98, c=101)])
    with pytest.raises(ValueError, match="Invalid OHLC envelope"):
        merge_ohlcv_payloads(None, incoming)
