"""Jurisdiction and deadline gates for prize-eligible TradingView contests."""
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from app.competition_intake_gate import evaluate_contest_intake


def test_geographically_restricted_open_phillip_nova_is_not_eligible_for_egypt():
    decision = evaluate_contest_intake(
        "phillip-nova-oct-2026", "EG",
        now_utc=datetime(2026, 10, 14, tzinfo=timezone.utc),
    )
    assert decision.result == "INELIGIBLE_TERRITORY"
    assert decision.paper_orders_authorized is False
    assert decision.notifications_authorized is False
    assert decision.rules_url.endswith("phillip-nova-october-2026/rules/")


@pytest.mark.parametrize("residence", ["MY", "SG", "ID"])
def test_phillip_nova_allowlist_only_needs_additional_legal_owner_checks(residence):
    result = evaluate_contest_intake(
        "phillip-nova-oct-2026", residence,
        now_utc=datetime(2026, 10, 14, tzinfo=timezone.utc),
    )
    assert result.result == "OWNER_ELIGIBILITY_CONFIRMATION_REQUIRED"
    assert result.paper_orders_authorized is False


def test_closed_commodities_registration_must_not_be_revived():
    result = evaluate_contest_intake(
        "tradingview-commodities-oct-2026", "EG",
        now_utc=datetime(2026, 10, 14, 12, tzinfo=timezone.utc),
    )
    assert result.result == "REGISTRATION_CLOSED"


def test_predeadline_commodities_egypt_is_not_automatically_eligible():
    result = evaluate_contest_intake(
        "tradingview-commodities-oct-2026", "EG",
        now_utc=datetime(2026, 10, 13, 12, tzinfo=timezone.utc),
    )
    assert result.result == "OWNER_ELIGIBILITY_CONFIRMATION_REQUIRED"
    assert result.paper_orders_authorized is False


def test_at_exact_registration_close_is_closed():
    result = evaluate_contest_intake(
        "tradingview-commodities-oct-2026", "EG",
        now_utc=datetime(2026, 10, 14, 8, tzinfo=timezone.utc),
    )
    assert result.result == "REGISTRATION_CLOSED"


def test_expired_competition_not_eligible_even_if_owner_missed_deadline():
    result = evaluate_contest_intake(
        "tradingview-commodities-oct-2026", "EG",
        now_utc=datetime(2026, 10, 20, 8, tzinfo=timezone.utc),
    )
    assert result.result == "CONTEST_ENDED"


def test_unknown_contest_and_inferred_residence_rejected():
    with pytest.raises(KeyError):
        evaluate_contest_intake("unverified-contest", "EG")
    for country in ["", "egypt", "eg", "E", "E1"]:
        with pytest.raises(ValueError):
            evaluate_contest_intake("phillip-nova-oct-2026", country)


def test_malformed_rules_cannot_silently_grant_permission(tmp_path):
    original = json.loads(
        (Path(__file__).parents[1] / "research_inputs" / "STC_OFFICIAL_CONTEST_DISCOVERY_20261014.json")
        .read_text(encoding="utf-8")
    )
    for key, value in [
        ("owner_registration_confirmed", True),
        ("strategy_research_only", False),
        ("registration_close_utc", "2026-10-20 08:00:00"),
        ("rules_url", "https://untrusted.example/rules/"),
        ("residence_rule", {"type": "ALLOWLIST_ONLY", "iso_country_codes": ["EG", "EG"]}),
    ]:
        data=json.loads(json.dumps(original))
        data["contests"][0][key]=value
        filepath=tmp_path/"altered.json"
        filepath.write_text(json.dumps(data))
        with pytest.raises(ValueError):
            evaluate_contest_intake(
                "tradingview-commodities-oct-2026", "EG",
                source_path=filepath,
            )


def test_all_research_records_never_authorize_trades():
    for contest in ["phillip-nova-oct-2026", "tradingview-commodities-oct-2026"]:
        for residence in ["EG", "MY", "SG", "ID"]:
            result=evaluate_contest_intake(
                contest, residence,
                now_utc=datetime(2026, 10, 14, tzinfo=timezone.utc),
            )
            assert result.paper_orders_authorized is False
            assert result.notifications_authorized is False
