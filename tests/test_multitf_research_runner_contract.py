from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.research_dataset import resample_hourly_to_two_hour
from app.models import Bar


def _hourly(count: int = 20) -> list[Bar]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        Bar(
            timestamp=start + timedelta(hours=i),
            open=100+i,
            high=101+i,
            low=99+i,
            close=100.5+i,
            volume=1000,
        )
        for i in range(count)
    ]


def test_two_hour_support_is_derived_only_from_exact_hourly_bars():
    bars = resample_hourly_to_two_hour(_hourly())
    assert len(bars) == 10
    assert all((bars[i+1].timestamp-bars[i].timestamp).total_seconds() == 7200 for i in range(len(bars)-1))
