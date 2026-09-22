from datetime import datetime, timedelta, timezone

from app.evidence_engine import EvidenceSummary
from app.models import Bar
from app.mtf_research import (
    POLICIES,
    ConfirmedTrendPoint,
    confirmed_trend_series,
    evaluate_mtf_policy,
    make_mtf_signal_gate,
)


UTC = timezone.utc


def _bars(count: int = 80, *, step_minutes: int = 60) -> list[Bar]:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    out = []
    price = 100.0
    for i in range(count):
        price += 0.20
        out.append(
            Bar(
                timestamp=t0 + timedelta(minutes=step_minutes * i),
                open=price - 0.05,
                high=price + 0.40,
                low=price - 0.40,
                close=price,
                volume=1000 + i,
            )
        )
    return out


def _policy(name: str):
    return next(item for item in POLICIES if item.name == name)


def test_confirmed_trend_series_never_uses_last_unconfirmed_source_bar():
    bars = _bars()
    baseline = confirmed_trend_series(bars)

    mutated = list(bars)
    mutated[-1] = mutated[-1].model_copy(
        update={
            "open": 1000.0,
            "high": 1100.0,
            "low": 10.0,
            "close": 20.0,
            "volume": 999999.0,
        }
    )
    after = confirmed_trend_series(mutated)

    assert baseline == after
    assert baseline[-1].confirmed_at == bars[-1].timestamp


def test_mtf_policy_fails_closed_when_any_required_timeframe_is_missing():
    decision = evaluate_mtf_policy(
        side=1,
        scores={"60": 0.8, "120": 0.7, "240": 0.6, "1D": 0.5, "1M": None},
        policy=_policy("MAJORITY"),
    )
    assert decision.passed is False
    assert decision.reason.startswith("missing_confirmed_timeframes:")


def test_majority_can_pass_when_four_of_five_align_but_strict_rejects():
    scores = {"60": 0.60, "120": 0.50, "240": 0.45, "1D": 0.35, "1M": -0.10}
    majority = evaluate_mtf_policy(side=1, scores=scores, policy=_policy("MAJORITY"))
    strict = evaluate_mtf_policy(side=1, scores=scores, policy=_policy("STRICT"))
    assert majority.passed is True
    assert majority.aligned == 4
    assert strict.passed is False


def test_trend_weighted_policy_rejects_strong_daily_or_monthly_conflict():
    scores = {"60": 0.80, "120": 0.75, "240": 0.60, "1D": -0.50, "1M": 0.55}
    decision = evaluate_mtf_policy(
        side=1,
        scores=scores,
        policy=_policy("TREND_WEIGHTED"),
    )
    assert decision.passed is False
    assert decision.reason in {"too_many_strong_conflicts", "higher_timeframe_floor_failed"}


def test_signal_gate_uses_next_entry_bar_timestamp_as_signal_close():
    entry = _bars(20, step_minutes=15)
    t0 = entry[0].timestamp
    trend_map = {
        tf: (
            ConfirmedTrendPoint(confirmed_at=t0 + timedelta(minutes=60), score=0.70),
        )
        for tf in ("60", "120", "240", "1D", "1M")
    }
    gate = make_mtf_signal_gate(
        entry_bars=entry,
        trend_map=trend_map,
        policy=_policy("STRICT"),
    )
    summary = EvidenceSummary(
        score=0.8,
        agreement_ratio=0.9,
        independent_confirmations=6,
        hard_confirmations=2,
        family_scores={},
        family_weights_used={},
        conflicts=(),
        strongest_features=(),
    )

    # Signal index 2 closes when bar 3 opens at +45m: HTF evidence not confirmed.
    assert gate(2, 1, 0.8, summary) is False
    # Signal index 3 closes when bar 4 opens at +60m: evidence is now confirmed.
    assert gate(3, 1, 0.8, summary) is True
