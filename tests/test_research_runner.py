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



def test_select_mtf_candidates_prefers_supported_15m_edge():
    from app.research_runner import _select_mtf_candidate_ids
    from app.strategy_lab import StrategyTrial
    from app.walkforward import BacktestParams, BacktestStats, WalkForwardValidation

    def row(strategy_id, timeframe, test_trades, forward_trades, test_exp, forward_exp, dd=3.0):
        test = BacktestStats(
            test_trades,
            max(0, test_trades // 2),
            test_trades - max(0, test_trades // 2),
            0.5 if test_trades else 0.0,
            test_exp * test_trades,
            test_exp,
            1.4 if test_exp > 0 else 0.8,
            dd,
        )
        forward = BacktestStats(
            forward_trades,
            max(0, forward_trades // 2),
            forward_trades - max(0, forward_trades // 2),
            0.5 if forward_trades else 0.0,
            forward_exp * forward_trades,
            forward_exp,
            1.3 if forward_exp > 0 else 0.7,
            dd,
        )
        train = BacktestStats(50, 30, 20, 0.6, 10.0, 0.2, 1.5, dd)
        trial = StrategyTrial(
            strategy_id=strategy_id,
            symbol="TEST:X",
            timeframe=timeframe,
            train_trades=train.trades,
            test_trades=test.trades,
            forward_trades=forward.trades,
            train_expectancy_r=train.expectancy_r,
            test_expectancy_r=test.expectancy_r,
            forward_expectancy_r=forward.expectancy_r,
            test_profit_factor=test.profit_factor,
            forward_profit_factor=forward.profit_factor,
            test_win_rate=test.win_rate,
            max_drawdown_r=dd,
            parameter_stability=0.8,
            regime_stability=0.8,
        )
        return WalkForwardValidation(
            trial=trial,
            selected_params=BacktestParams(0.62, 1.2, 2.5, 16),
            train_stats=train,
            test_stats=test,
            forward_stats=forward,
        )

    rows = [
        row("supported", "15", 32, 18, 0.18, 0.12),
        row("tiny_sample", "15", 4, 3, 0.90, 0.80),
        row("other_tf", "60", 40, 20, 0.30, 0.20),
        row("hopeless", "15", 40, 20, -0.20, -0.10),
    ]
    selected = _select_mtf_candidate_ids(rows, limit=3)
    assert selected == ("supported",)



def test_research_runner_skips_short_daily_history_without_aborting_symbol(monkeypatch):
    captured = {}

    def fake_matrix(symbol, asset_class, bundle, **kwargs):
        captured["lengths"] = {key: len(value) for key, value in bundle.items()}
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
        "symbol": "NYMEX:MNG1!",
        "series": {
            "5m": _series(901, 300),
            "15m": _series(901, 900),
            "30m": _series(901, 1800),
            "1h": _series(901, 3600),
            "4h": _series(901, 14400),
            "1D": _series(722, 86400),
        },
    }
    result = rr.run_symbol_research(payload, calibrate_features=False)
    assert result["data_quality"]["1D"]["quality_ok"] is False
    assert result["insufficient_history_series"] == ["1D"]
    assert captured["lengths"]["15"] >= 900
    assert captured["lengths"]["1D"] < 900
    assert result["research_report"]["status"] == "NO_VALIDATED_STRATEGY"


def test_research_runner_still_rejects_duplicate_timestamps_even_with_enough_other_data():
    duplicate_daily = _series(901, 86400)
    duplicate_daily["bars"][1]["t"] = duplicate_daily["bars"][0]["t"]
    payload = {
        "symbol": "NYMEX:MNG1!",
        "series": {
            "15m": _series(901, 900),
            "1h": _series(901, 3600),
            "4h": _series(901, 14400),
            "1D": duplicate_daily,
        },
    }
    try:
        rr.run_symbol_research(payload, calibrate_features=False)
    except ValueError as exc:
        assert "Research data quality failed" in str(exc)
    else:
        raise AssertionError("Expected duplicate-timestamp integrity failure")


def test_shadow_batch_parser_rejects_unsealed_windows():
    payload = {
        "shadow_batch": {
            "batch_id": "open-window",
            "sealed": False,
            "observations": [],
        }
    }
    try:
        rr._shadow_batch_from_payload(payload)
    except ValueError as exc:
        assert "sealed" in str(exc)
    else:
        raise AssertionError("Expected unsealed shadow batch to fail closed")


def test_shadow_batch_parser_requires_exact_typed_observations():
    payload = {
        "shadow_batch": {
            "batch_id": "sealed-1",
            "sealed": True,
            "observations": [
                {
                    "observation_id": "obs-1",
                    "symbol": "CBOT:ZN1!",
                    "timeframe": "15",
                    "component_id": "schaff_trend_cycle",
                    "result_r": 0.25,
                    "directional_hit": "yes",
                }
            ],
        }
    }
    try:
        rr._shadow_batch_from_payload(payload)
    except ValueError as exc:
        assert "directional_hit" in str(exc)
    else:
        raise AssertionError("Expected non-boolean directional_hit to fail closed")


def test_research_runner_recalibrates_ensemble_from_sealed_batch_only():
    from app.community_indicator_benchmark import (
        EnsembleComponentWeight,
        SymbolEnsembleProfile,
    )

    profile = SymbolEnsembleProfile(
        symbol="CBOT:ZN1!",
        timeframe="15",
        components=(
            EnsembleComponentWeight(
                component_id="schaff_trend_cycle",
                source_type="community_indicator",
                family="momentum_cycle",
                symbol="CBOT:ZN1!",
                timeframe="15",
                raw_score=30.0,
                normalized_weight=0.5,
                test_trades=40,
                forward_trades=20,
                note="fixture",
            ),
            EnsembleComponentWeight(
                component_id="range_filter_guikroth",
                source_type="community_indicator",
                family="adaptive_range_trend",
                symbol="CBOT:ZN1!",
                timeframe="15",
                raw_score=30.0,
                normalized_weight=0.5,
                test_trades=40,
                forward_trades=20,
                note="fixture",
            ),
        ),
        community_weight_share=1.0,
        core_weight_share=0.0,
        status="RESEARCH_PROFILE_READY",
        notes=("fixture",),
    )
    observations = []
    for i in range(40):
        observations.append({
            "observation_id": f"good-{i}",
            "symbol": "CBOT:ZN1!",
            "timeframe": "15",
            "component_id": "schaff_trend_cycle",
            "result_r": 0.30,
            "directional_hit": True,
        })
        observations.append({
            "observation_id": f"bad-{i}",
            "symbol": "CBOT:ZN1!",
            "timeframe": "15",
            "component_id": "range_filter_guikroth",
            "result_r": -0.15,
            "directional_hit": False,
        })
    batch = rr._shadow_batch_from_payload({
        "shadow_batch": {
            "batch_id": "sealed-40",
            "sealed": True,
            "observations": observations,
        }
    })
    result = rr._recalibrate_ensemble_profiles(
        symbol="CBOT:ZN1!",
        profiles={"15": profile},
        batch=batch,
    )
    recalibrated = result["15"]
    assert recalibrated.live_authority is False
    assert recalibrated.status == "RESEARCH_PROFILE_RECALIBRATED"
    assert abs(sum(recalibrated.normalized_candidate_weights.values()) - 1.0) < 1e-12
    assert (
        recalibrated.normalized_candidate_weights["schaff_trend_cycle"]
        > recalibrated.normalized_candidate_weights["range_filter_guikroth"]
    )


def test_research_runner_small_shadow_batch_keeps_prior_profile_weights():
    from app.community_indicator_benchmark import (
        EnsembleComponentWeight,
        SymbolEnsembleProfile,
    )

    profile = SymbolEnsembleProfile(
        symbol="CBOT:ZN1!",
        timeframe="15",
        components=(
            EnsembleComponentWeight(
                component_id="schaff_trend_cycle",
                source_type="community_indicator",
                family="momentum_cycle",
                symbol="CBOT:ZN1!",
                timeframe="15",
                raw_score=30.0,
                normalized_weight=0.7,
                test_trades=40,
                forward_trades=20,
                note="fixture",
            ),
            EnsembleComponentWeight(
                component_id="range_filter_guikroth",
                source_type="community_indicator",
                family="adaptive_range_trend",
                symbol="CBOT:ZN1!",
                timeframe="15",
                raw_score=20.0,
                normalized_weight=0.3,
                test_trades=40,
                forward_trades=20,
                note="fixture",
            ),
        ),
        community_weight_share=1.0,
        core_weight_share=0.0,
        status="RESEARCH_PROFILE_READY",
        notes=("fixture",),
    )
    batch = rr._shadow_batch_from_payload({
        "shadow_batch": {
            "batch_id": "small-sealed",
            "sealed": True,
            "observations": [
                {
                    "observation_id": f"small-{i}",
                    "symbol": "CBOT:ZN1!",
                    "timeframe": "15",
                    "component_id": "schaff_trend_cycle",
                    "result_r": 1.0,
                    "directional_hit": True,
                }
                for i in range(10)
            ],
        }
    })
    result = rr._recalibrate_ensemble_profiles(
        symbol="CBOT:ZN1!",
        profiles={"15": profile},
        batch=batch,
    )["15"]
    assert result.live_authority is False
    assert result.status == "RESEARCH_PROFILE_UNCHANGED"
    assert abs(result.normalized_candidate_weights["schaff_trend_cycle"] - 0.7) < 1e-12
    assert abs(result.normalized_candidate_weights["range_filter_guikroth"] - 0.3) < 1e-12
