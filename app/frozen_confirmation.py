from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .historical_features import extract_feature_snapshot
from .regime_research import make_regime_signal_gate
from .research_dataset import bars_from_tradingview_ohlcv
from .walkforward import (
    BacktestParams,
    BacktestStats,
    TradeOutcome,
    backtest_strategy,
    summarize_trades,
)


_TIMEFRAME_TO_INTERVAL = {
    "1": "1m",
    "3": "3m",
    "5": "5m",
    "15": "15m",
    "30": "30m",
    "60": "1h",
    "120": "2h",
    "240": "4h",
    "1D": "1D",
}


@dataclass(frozen=True)
class FrozenHypothesis:
    hypothesis_id: str
    symbol: str
    timeframe: str
    strategy_id: str
    archive_path: str
    freeze_t: int
    params: BacktestParams
    allowed_regimes: tuple[str, ...]
    role: str
    development_status: str
    source_run_id: int | None = None


@dataclass(frozen=True)
class FrozenConfirmationResult:
    hypothesis_id: str
    symbol: str
    timeframe: str
    strategy_id: str
    role: str
    development_status: str
    freeze_t: int
    archive_last_t: int | None
    unseen_bars: int
    completed_trades: int
    incomplete_open_trades: int
    segment_stability: float
    segments_evaluated: int
    stats: BacktestStats
    status: str
    rejection_reasons: tuple[str, ...]
    optimization_locked: bool
    second_confirmation_required: bool
    live_calibration_authority: bool


def hypothesis_from_dict(raw: dict[str, Any]) -> FrozenHypothesis:
    if not isinstance(raw, dict):
        raise ValueError("Frozen hypothesis must be an object")
    required = (
        "hypothesis_id",
        "symbol",
        "timeframe",
        "strategy_id",
        "archive_path",
        "freeze_t",
        "params",
        "role",
        "development_status",
    )
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Frozen hypothesis missing fields: {missing}")

    if raw.get("live_calibration_authority") not in (None, False):
        raise ValueError("Frozen hypotheses cannot grant live calibration authority")

    params_raw = raw.get("params")
    if not isinstance(params_raw, dict):
        raise ValueError("Frozen hypothesis params must be an object")

    params = BacktestParams(
        threshold=float(params_raw["threshold"]),
        stop_atr=float(params_raw["stop_atr"]),
        target_r=float(params_raw["target_r"]),
        max_hold_bars=int(params_raw["max_hold_bars"]),
        min_agreement=float(params_raw.get("min_agreement", 0.62)),
        min_independent_confirmations=int(
            params_raw.get("min_independent_confirmations", 4)
        ),
        min_hard_confirmations=int(params_raw.get("min_hard_confirmations", 1)),
        round_turn_cost_r=float(params_raw.get("round_turn_cost_r", 0.02)),
    )
    allowed = tuple(str(value) for value in (raw.get("allowed_regimes") or ()))
    source_run_id = raw.get("source_run_id")
    return FrozenHypothesis(
        hypothesis_id=str(raw["hypothesis_id"]),
        symbol=str(raw["symbol"]),
        timeframe=str(raw["timeframe"]),
        strategy_id=str(raw["strategy_id"]),
        archive_path=str(raw["archive_path"]),
        freeze_t=int(raw["freeze_t"]),
        params=params,
        allowed_regimes=allowed,
        role=str(raw["role"]),
        development_status=str(raw["development_status"]),
        source_run_id=int(source_run_id) if source_run_id is not None else None,
    )


def load_frozen_hypotheses(manifest: dict[str, Any]) -> tuple[FrozenHypothesis, ...]:
    if not isinstance(manifest, dict):
        raise ValueError("Frozen hypothesis manifest must be an object")
    if manifest.get("schema_version") != "stc-frozen-confirmation-v1":
        raise ValueError("Unsupported frozen hypothesis manifest schema")
    if manifest.get("optimization_locked") is not True:
        raise ValueError("Frozen hypothesis manifest must set optimization_locked=true")
    rows = manifest.get("hypotheses")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Frozen hypothesis manifest requires hypotheses list")
    hypotheses = tuple(hypothesis_from_dict(row) for row in rows)
    ids = [item.hypothesis_id for item in hypotheses]
    if len(ids) != len(set(ids)):
        raise ValueError("Frozen hypothesis IDs must be unique")
    return hypotheses



def _materialize_confirmation_snapshots(
    symbol: str,
    timeframe: str,
    bars,
    *,
    start_index: int,
):
    """Materialize only snapshots that can generate unseen signals.

    Semantics match walkforward.materialize_feature_series: every snapshot uses
    the same latest-1000-bar window ending at its own index. Development-history
    bars are still available as warm-up context; snapshots before the unseen
    start are simply not recomputed.
    """
    if len(bars) <= 260:
        raise ValueError("Not enough bars after feature warmup")
    begin = max(259, int(start_index))
    return {
        i: extract_feature_snapshot(
            symbol,
            timeframe,
            bars[max(0, i - 999) : i + 1],
        )
        for i in range(begin, len(bars))
    }

def _completed_trades(
    trades: list[TradeOutcome],
    params: BacktestParams,
) -> tuple[list[TradeOutcome], int]:
    completed: list[TradeOutcome] = []
    incomplete = 0
    for trade in trades:
        truncated_time_exit = (
            trade.exit_reason == "TIME"
            and (trade.exit_index - trade.entry_index) < params.max_hold_bars
        )
        if truncated_time_exit:
            incomplete += 1
            continue
        completed.append(trade)
    return completed, incomplete


def _segment_stability(
    trades: list[TradeOutcome],
    *,
    start_index: int,
    end_index: int,
) -> tuple[float, int]:
    if end_index <= start_index:
        return 0.0, 0
    width = max(1, (end_index - start_index + 1) // 3)
    positive = 0
    used = 0
    for n in range(3):
        a = start_index + n * width
        b = end_index + 1 if n == 2 else min(end_index + 1, a + width)
        segment = [trade for trade in trades if a <= trade.signal_index < b]
        if len(segment) < 3:
            continue
        used += 1
        stats = summarize_trades(segment)
        if stats.expectancy_r >= 0 and stats.profit_factor >= 1.0:
            positive += 1
    return (0.0 if used == 0 else positive / used), used


def _confirmation_reasons(
    stats: BacktestStats,
    *,
    segment_stability: float,
    segments_evaluated: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if stats.trades < 30:
        reasons.append("insufficient_unseen_trades")
    if stats.expectancy_r <= 0.08:
        reasons.append("weak_unseen_expectancy")
    if stats.profit_factor < 1.15:
        reasons.append("weak_unseen_profit_factor")
    if stats.max_drawdown_r > 10.0:
        reasons.append("unseen_drawdown_too_large")
    if segments_evaluated < 2:
        reasons.append("insufficient_unseen_segment_coverage")
    if segment_stability < 0.60:
        reasons.append("unseen_segment_instability")
    return tuple(reasons)


def evaluate_frozen_hypothesis(
    archive_payload: dict[str, Any],
    hypothesis: FrozenHypothesis,
) -> FrozenConfirmationResult:
    symbol = str(archive_payload.get("symbol") or "").strip()
    interval = str(archive_payload.get("interval") or "").strip()
    expected_interval = _TIMEFRAME_TO_INTERVAL.get(hypothesis.timeframe)
    if expected_interval is None:
        raise ValueError(f"Unsupported frozen timeframe: {hypothesis.timeframe}")
    if symbol != hypothesis.symbol or interval != expected_interval:
        raise ValueError(
            "Frozen confirmation archive identity mismatch: "
            f"expected {hypothesis.symbol} {expected_interval}, got {symbol} {interval}"
        )

    archive_meta = archive_payload.get("archive")
    if not isinstance(archive_meta, dict):
        raise ValueError("Frozen confirmation requires a confirmed exact-provider archive")
    if archive_meta.get("provider") != "TradingView Official MCP":
        raise ValueError("Frozen confirmation requires TradingView Official MCP archive provenance")

    bars = bars_from_tradingview_ohlcv(archive_payload)
    timestamps = [int(bar.timestamp.timestamp()) for bar in bars]
    archive_last_t = timestamps[-1] if timestamps else None
    metadata_last_t = archive_meta.get("coverage_last_t")
    if archive_last_t is not None and int(metadata_last_t or 0) != archive_last_t:
        raise ValueError("Frozen confirmation archive coverage metadata does not match bars")
    withheld_t = archive_meta.get("withheld_unconfirmed_t")
    if (
        archive_last_t is not None
        and withheld_t is not None
        and archive_last_t >= int(withheld_t)
    ):
        raise ValueError("Frozen confirmation archive still contains an unconfirmed tail bar")
    start_index = next(
        (index for index, timestamp in enumerate(timestamps) if timestamp > hypothesis.freeze_t),
        len(bars),
    )
    unseen_bars = max(0, len(bars) - start_index)

    empty = BacktestStats(
        trades=0,
        wins=0,
        losses=0,
        win_rate=0.0,
        total_r=0.0,
        expectancy_r=0.0,
        profit_factor=0.0,
        max_drawdown_r=0.0,
    )
    if unseen_bars <= 0:
        return FrozenConfirmationResult(
            hypothesis_id=hypothesis.hypothesis_id,
            symbol=hypothesis.symbol,
            timeframe=hypothesis.timeframe,
            strategy_id=hypothesis.strategy_id,
            role=hypothesis.role,
            development_status=hypothesis.development_status,
            freeze_t=hypothesis.freeze_t,
            archive_last_t=archive_last_t,
            unseen_bars=0,
            completed_trades=0,
            incomplete_open_trades=0,
            segment_stability=0.0,
            segments_evaluated=0,
            stats=empty,
            status="NO_UNSEEN_DATA",
            rejection_reasons=("no_unseen_data",),
            optimization_locked=True,
            second_confirmation_required=False,
            live_calibration_authority=False,
        )

    snapshots = _materialize_confirmation_snapshots(
        hypothesis.symbol,
        hypothesis.timeframe,
        bars,
        start_index=start_index,
    )
    signal_gate = None
    if hypothesis.allowed_regimes:
        signal_gate = make_regime_signal_gate(
            snapshots=snapshots,
            allowed_regimes=hypothesis.allowed_regimes,
        )

    trades, _ = backtest_strategy(
        hypothesis.symbol,
        hypothesis.timeframe,
        bars,
        snapshots,
        hypothesis.strategy_id,
        hypothesis.params,
        start_index=start_index,
        end_index=len(bars) - 1,
        signal_gate=signal_gate,
    )
    completed, incomplete = _completed_trades(trades, hypothesis.params)
    stats = summarize_trades(completed)
    stability, segments_evaluated = _segment_stability(
        completed,
        start_index=start_index,
        end_index=len(bars) - 1,
    )
    reasons = _confirmation_reasons(
        stats,
        segment_stability=stability,
        segments_evaluated=segments_evaluated,
    )

    if stats.trades < 30:
        status = "ACCUMULATING"
    elif reasons:
        status = "UNSEEN_FAILED"
    else:
        status = "UNSEEN_SUPPORT"

    return FrozenConfirmationResult(
        hypothesis_id=hypothesis.hypothesis_id,
        symbol=hypothesis.symbol,
        timeframe=hypothesis.timeframe,
        strategy_id=hypothesis.strategy_id,
        role=hypothesis.role,
        development_status=hypothesis.development_status,
        freeze_t=hypothesis.freeze_t,
        archive_last_t=archive_last_t,
        unseen_bars=unseen_bars,
        completed_trades=stats.trades,
        incomplete_open_trades=incomplete,
        segment_stability=stability,
        segments_evaluated=segments_evaluated,
        stats=stats,
        status=status,
        rejection_reasons=reasons,
        optimization_locked=True,
        second_confirmation_required=(status == "UNSEEN_SUPPORT"),
        live_calibration_authority=False,
    )


def confirmation_result_dict(result: FrozenConfirmationResult) -> dict[str, Any]:
    return asdict(result)
