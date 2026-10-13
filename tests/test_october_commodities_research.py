"""October 2026 The Leap commodities rules, no trade/order authority tests."""
import json
from pathlib import Path

import pytest

from app.october_commodities_research import (
    distinct_qualifying_activity_dates,
    load_october_commodities_intake,
    projected_leap_score,
    within_official_position_cap,
)


def test_contest_rules_exact_market_source_and_paper_only():
    rules=load_october_commodities_intake()
    assert rules["registration_close_utc"]=="2026-10-14T08:00:00Z"
    assert rules["contest_end_utc"]=="2026-10-20T08:00:00Z"
    assert rules["min_distinct_utc_trading_days"]==3
    assert rules["owner_registration_confirmed"] is False
    assert rules["strategy_promoted"] is False
    assert rules["trading_authority"]=="NONE"
    assert rules["notification_route_enabled"] is False
    assert rules["no_email"] is True
    assert [row["symbol"] for row in rules["allowed_symbols_and_max_open_position"]]==[
        "OANDA:XAUUSD","OANDA:XAGUSD","OANDA:XCUUSD","OANDA:WTICOUSD",
        "OANDA:NATGASUSD","OANDA:CORNUSD","OANDA:WHEATUSD","OANDA:SOYBNUSD",
    ]


def test_score_floor_for_positive_profit():
    score=projected_leap_score(10_000,3)
    assert score["profit_pct"]==10
    assert score["effective_denominator_pct"]==5
    assert score["projected_score"]==2
    assert score["official_score_verified"] is False
    assert score["paper_execution_authorized"] is False


def test_high_drawdown_reduces_score_even_if_profit_equal():
    score=projected_leap_score(10_000,8)
    assert score["projected_score"]==1.25
    assert score["effective_denominator_pct"]==8


def test_negative_profit_always_uses_floor_denominator():
    score=projected_leap_score(-3_000,9)
    assert score["projected_score"]==-0.6
    assert score["effective_denominator_pct"]==5


@pytest.mark.parametrize("profit,drawdown,balance",[
    (float("nan"),4,100000),(1000,float("inf"),100000),
    (1000,-1,100000),(1000,1,0),(1000,1,-10000),
])
def test_score_rejects_invalid_source_records(profit,drawdown,balance):
    with pytest.raises(ValueError):
        projected_leap_score(profit,drawdown,initial_balance_usd=balance)


def test_utc_activity_days_ignore_signal_without_external_position():
    dates=distinct_qualifying_activity_dates([
        {"action":"OPEN","executed_at_utc":"2026-10-14T22:00:00+00:00"},
        {"action":"CLOSE","executed_at_utc":"2026-10-14T23:40:00+00:00"},
        {"action":"RECOMMENDED","executed_at_utc":"2026-10-15T10:00:00Z"},
        {"action":"OPEN","executed_at_utc":"2026-10-15T23:10:00Z"},
        {"action":"CLOSE","executed_at_utc":"2026-10-16T00:10:00Z"},
    ])
    assert dates==("2026-10-14","2026-10-15","2026-10-16")
    with pytest.raises(ValueError):
        distinct_qualifying_activity_dates([{"action":"OPEN","executed_at_utc":"2026-10-14T12:00:00"}])


def test_exact_position_max_limits_do_not_authorize_orders():
    assert within_official_position_cap("OANDA:XAUUSD",75) is True
    assert within_official_position_cap("OANDA:XAUUSD",75.00001) is False
    assert within_official_position_cap("CAPITALCOM:XAUUSD",1) is False
    assert within_official_position_cap("BINANCE:BTCUSDT",1) is False
    assert within_official_position_cap("OANDA:XAUUSD",0) is False
    assert within_official_position_cap("OANDA:XAUUSD",float("inf")) is False


def test_research_metadata_cannot_be_silently_upgraded(tmp_path):
    source=Path("research_inputs/CONTEST_THE_LEAP_COMMODITIES_OCT2026.json")
    initial=json.loads(source.read_text())
    for field,value in [
        ("trading_authority","PAPER_AUTO"),
        ("owner_registration_confirmed",True),
        ("strategy_promoted",True),
        ("notification_route_enabled",True),
        ("no_email",False),
    ]:
        altered=json.loads(json.dumps(initial))
        altered[field]=value
        f=tmp_path/"altered.json"
        f.write_text(json.dumps(altered))
        with pytest.raises(ValueError):
            load_october_commodities_intake(f)
