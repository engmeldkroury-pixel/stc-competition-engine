import pytest

from app.feed_reconciliation import reconcile_ohlcv_feeds


def _payload(offset=0.0, count=300, symbol="CAPITALCOM:XAUUSD", interval="15m"):
    bars = []
    for i in range(count):
        base = 2000.0 + i
        bars.append({
            "t": 1700000000 + i * 900,
            "o": base + offset,
            "h": base + 2 + offset,
            "l": base - 2 + offset,
            "c": base + 1 + offset,
            "v": 100 + i,
        })
    return {"symbol": symbol, "interval": interval, "bars": bars}


def test_reconciliation_requires_review_without_explicit_thresholds():
    result = reconcile_ohlcv_feeds(_payload(), _payload(offset=0.01))
    assert result.overlap_bars == 300
    assert result.status == "REVIEW_REQUIRED"
    assert result.live_calibration_authority is False
    assert result.median_abs_close_bps is not None
    assert result.return_correlation is not None
    assert result.return_correlation > 0.999


def test_reconciliation_can_flag_candidate_match_but_never_live_authority():
    result = reconcile_ohlcv_feeds(
        _payload(),
        _payload(offset=0.01),
        max_median_close_bps=1.0,
        max_p95_close_bps=1.0,
        min_return_correlation=0.999,
    )
    assert result.status == "CANDIDATE_MATCH"
    assert result.live_calibration_authority is False


def test_reconciliation_rejects_mismatch():
    result = reconcile_ohlcv_feeds(
        _payload(),
        _payload(offset=20.0),
        max_median_close_bps=1.0,
        max_p95_close_bps=2.0,
        min_return_correlation=0.999,
    )
    assert result.status == "MISMATCH"


def test_reconciliation_marks_small_overlap_insufficient():
    result = reconcile_ohlcv_feeds(_payload(count=50), _payload(count=50), min_overlap_bars=200)
    assert result.status == "INSUFFICIENT_OVERLAP"


def test_reconciliation_fails_closed_on_identity_mismatch():
    with pytest.raises(ValueError, match="Feed identity mismatch"):
        reconcile_ohlcv_feeds(_payload(), _payload(symbol="CAPITALCOM:BTCUSD"))
