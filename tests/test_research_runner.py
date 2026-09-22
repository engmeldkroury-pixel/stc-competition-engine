from app import research_runner as rr
from app.walkforward import MatrixSelection


def _series(count: int, step_seconds: int) -> dict:
    return {
        "bars": [
            {
                "t": 1700000000 + i * step_seconds,
                "o": 100 + i * 0.01,
                "h": 101 + i * 0.01,
                "l": 99 + i * 0.01,
                "c": 100.5 + i * 0.01,
                "v": 1000 + i,
            }
            for i in range(count)
        ]
    }


def test_research_runner_builds_quality_checked_standard_bundle(monkeypatch):
    captured = {}

    def fake_matrix(symbol, asset_class, bundle, **kwargs):
        captured["symbol"] = symbol
        captured["asset_class"] = asset_class
        captured["keys"] = set(bundle)
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe=None,
            robust_score=None,
            trial_count=0,
            reason="fixture",
        )

    monkeypatch.setattr(rr, "strategy_matrix", fake_matrix)
    payload = {
        "symbol": "CAPITALCOM:XAUUSD",
        "series": {
            "15m": _series(901, 900),
            "1h": _series(901, 3600),
            "4h": _series(901, 14400),
            "1D": _series(901, 86400),
        },
    }
    result = rr.run_symbol_research(payload, calibrate_features=False)
    assert captured["symbol"] == "CAPITALCOM:XAUUSD"
    assert captured["asset_class"] == "metals"
    assert captured["keys"] == {"15", "60", "120", "240", "1D", "1M"}
    assert set(result["derived_timeframe_end_utc"]) == {"15", "60", "120", "240", "1D", "1M"}
    assert set(result["derived_timeframe_start_utc"]) == {"15", "60", "120", "240", "1D", "1M"}
    assert set(result["derived_timeframe_span_days"]) == {"15", "60", "120", "240", "1D", "1M"}
    assert result["derived_timeframe_end_utc"]["15"] is not None
    assert result["derived_timeframe_start_utc"]["15"] is not None
    assert result["derived_timeframe_span_days"]["15"] > 0
    assert result["research_report"]["status"] == "NO_VALIDATED_STRATEGY"
    assert result["live_trading_authority"] is False
    assert all(q["quality_ok"] for q in result["data_quality"].values())


def test_research_runner_rejects_missing_required_provider_series():
    payload = {
        "symbol": "CAPITALCOM:XAUUSD",
        "series": {
            "15m": _series(901, 900),
            "1h": _series(901, 3600),
        },
    }
    try:
        rr.run_symbol_research(payload, calibrate_features=False)
    except ValueError as exc:
        assert "Missing required exact-provider OHLCV series" in str(exc)
    else:
        raise AssertionError("Expected missing-series failure")


def test_strategy_feature_scope_is_family_specific():
    smc = set(rr._strategy_feature_names("smc_structure_liquidity"))
    trend = set(rr._strategy_feature_names("trend_pullback"))
    assert "liquidity_sweep" in smc
    assert "bos" in smc
    assert "rsi_14" not in smc
    assert "rsi_14" in trend
    assert "liquidity_sweep" not in trend



def test_research_runner_adds_optional_5m_and_30m_to_matrix(monkeypatch):
    captured = {}

    def fake_matrix(symbol, asset_class, bundle, **kwargs):
        captured["keys"] = set(bundle)
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe=None,
            robust_score=None,
            trial_count=0,
            reason="fixture",
        )

    monkeypatch.setattr(rr, "strategy_matrix", fake_matrix)
    payload = {
        "symbol": "CAPITALCOM:XAUUSD",
        "series": {
            "5m": _series(901, 300),
            "15m": _series(901, 900),
            "30m": _series(901, 1800),
            "1h": _series(901, 3600),
            "4h": _series(901, 14400),
            "1D": _series(901, 86400),
        },
    }
    result = rr.run_symbol_research(payload, calibrate_features=False)
    assert {"5", "30"}.issubset(captured["keys"])
    assert result["data_quality"]["5m"]["quality_ok"] is True
    assert result["data_quality"]["30m"]["quality_ok"] is True



def test_research_runner_passes_snapshot_cache_to_strategy_matrix(monkeypatch):
    captured = {}

    def fake_matrix(symbol, asset_class, bundle, **kwargs):
        captured["cache"] = kwargs.get("snapshot_cache")
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe=None,
            robust_score=None,
            trial_count=0,
            reason="fixture",
        )

    monkeypatch.setattr(rr, "strategy_matrix", fake_matrix)
    payload = {
        "symbol": "CAPITALCOM:XAUUSD",
        "series": {
            "15m": _series(901, 900),
            "1h": _series(901, 3600),
            "4h": _series(901, 14400),
            "1D": _series(901, 86400),
        },
    }
    rr.run_symbol_research(payload, calibrate_features=False)
    assert isinstance(captured["cache"], dict)



def test_research_runner_runs_mtf_only_when_explicitly_requested(monkeypatch):
    captured = {"mtf_calls": 0}

    def fake_matrix(symbol, asset_class, bundle, **kwargs):
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe=None,
            robust_score=None,
            trial_count=0,
            reason="baseline fixture",
        )

    def fake_mtf(*, symbol, asset_class, bars_by_timeframe, snapshot_cache=None):
        captured["mtf_calls"] += 1
        assert "15" in bars_by_timeframe
        return [], MatrixSelection(
            status="NO_VALIDATED_STRATEGY",
            symbol=symbol,
            strategy_id=None,
            timeframe="15",
            robust_score=None,
            trial_count=0,
            reason="mtf fixture",
        )

    monkeypatch.setattr(rr, "strategy_matrix", fake_matrix)
    monkeypatch.setattr(rr, "mtf_strategy_matrix", fake_mtf)
    payload = {
        "symbol": "CAPITALCOM:XAUUSD",
        "series": {
            "15m": _series(901, 900),
            "1h": _series(901, 3600),
            "4h": _series(901, 14400),
            "1D": _series(901, 86400),
        },
    }

    baseline = rr.run_symbol_research(
        payload,
        calibrate_features=False,
        run_mtf=False,
    )
    assert captured["mtf_calls"] == 0
    assert baseline["mtf_research_enabled"] is False
    assert baseline["mtf_strategy_trials"] == []

    mtf = rr.run_symbol_research(
        payload,
        calibrate_features=False,
        run_mtf=True,
    )
    assert captured["mtf_calls"] == 1
    assert mtf["mtf_research_enabled"] is True
    assert mtf["mtf_selection"]["timeframe"] == "15"
    assert mtf["live_trading_authority"] is False
