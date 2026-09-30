from app.crypto_research_pipeline import build_crypto_research_job


def test_crypto_research_job_uses_registry_policy():
    job = build_crypto_research_job("BTC")

    assert job.asset == "BTC"
    assert job.pair == "BTCUSDT"
    assert job.provider == "BINANCE_SPOT_PUBLIC"
    assert job.closed_bars_only is True
    assert job.intervals == ("15m", "1h", "4h", "1d")


def test_crypto_research_job_rejects_unknown_asset():
    try:
        build_crypto_research_job("UNKNOWN")
    except KeyError:
        return
    raise AssertionError("Unknown asset must be rejected")
