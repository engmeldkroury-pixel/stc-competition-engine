from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models import Bar
from app.native_frozen_confirmation import confirm_native_symbol


def _bars(count: int = 4000) -> list[Bar]:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows=[]
    price=100.0
    for i in range(count):
        drift=0.04 if (i//180)%2==0 else -0.035
        cycle=((i%23)-11)*0.004
        open_=price
        close=max(1.0,open_+drift+cycle)
        rows.append(Bar(
            timestamp=start+timedelta(minutes=15*i),
            open=open_,
            high=max(open_,close)+0.20,
            low=min(open_,close)-0.20,
            close=close,
            volume=1000+(i%40)*13,
        ))
        price=close
    return rows


def test_native_frozen_confirmation_preserves_exact_85_15_split():
    report=confirm_native_symbol(
        symbol="CAPITALCOM:EURUSD",
        asset_class="forex",
        timeframe="15",
        bars=_bars(),
    )
    assert report.development_bars == 3400
    assert report.confirmation_bars == 600
    assert report.live_authority is False
    assert len(report.components) > 0
    assert all(row.symbol == "CAPITALCOM:EURUSD" for row in report.components)
