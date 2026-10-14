"""Fail-closed preregistration eligibility gate for TradingView Paper contests.

Research eligibility alone never authorizes registration, strategy promotion,
live/paper execution, account access or owner notifications.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "research_inputs"
    / "STC_OFFICIAL_CONTEST_DISCOVERY_20261014.json"
)


@dataclass(frozen=True)
class ContestIntake:
    contest_id: str
    result: str
    reason: str
    registration_deadline_utc: datetime
    end_utc: datetime
    rules_url: str
    paper_orders_authorized: bool = False
    notifications_authorized: bool = False


def _required_utc(value: Any, key: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"Unverified or non-UTC {key}")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Malformed {key}") from exc
    if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
        raise ValueError(f"Invalid {key} timezone")
    return stamp


def _load(path: str | Path | None = None) -> tuple[dict, ...]:
    data = json.loads(Path(path or DEFAULT_SOURCE).read_text(encoding="utf-8"))
    if data.get("purpose") != "RESEARCH_DISCOVERY_ONLY_NOT_REGISTRATION_OR_TRADE_AUTHORITY":
        raise ValueError("Competition data is not research-only")
    if data.get("registered_owner_accounts_verified") is not False:
        raise ValueError("Unverified account cannot be automatically registered")
    records = data.get("contests")
    if not isinstance(records, list) or not records:
        raise ValueError("No official contest records")
    result = []
    ids = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid contest record")
        cid = record.get("competition_id")
        if not isinstance(cid, str) or not cid or cid in ids:
            raise ValueError("Duplicate or malformed contest id")
        ids.add(cid)
        url = record.get("rules_url")
        if (
            not isinstance(url, str)
            or not url.startswith("https://www.tradingview.com/the-leap/")
            or not url.endswith("/rules/")
        ):
            raise ValueError("Official TradingView rules URL required")
        start = _required_utc(record.get("start_utc"), "start_utc")
        end = _required_utc(record.get("end_utc"), "end_utc")
        deadline = _required_utc(record.get("registration_close_utc"), "registration_close_utc")
        if not (start < end and deadline <= end):
            raise ValueError("Inconsistent contest schedule")
        if record.get("owner_registration_confirmed") is not False:
            raise ValueError("No owner registration is verified at intake")
        if record.get("strategy_research_only") is not True:
            raise ValueError("Unapproved contest strategy")
        rule = record.get("residence_rule")
        if not isinstance(rule, dict) or rule.get("type") not in (
            "ALLOWLIST_ONLY", "EXCLUSION_LIST_REQUIRES_LEGAL_CONFIRMATION",
        ):
            raise ValueError("Undefined territory eligibility policy")
        codes = rule.get("iso_country_codes")
        if (
            not isinstance(codes, list)
            or not codes
            or len(codes) != len(set(codes))
            or any(not isinstance(code, str) or len(code) != 2 or code != code.upper()
                   for code in codes)
        ):
            raise ValueError("Malformed country code register")
        result.append(record)
    return tuple(result)


def evaluate_contest_intake(
    contest_id: str,
    legal_residence_iso2: str,
    *,
    now_utc: datetime | None = None,
    source_path: str | Path | None = None,
) -> ContestIntake:
    """Validate an explicit legal-residence input; never infer user's residency."""
    if (
        not isinstance(legal_residence_iso2, str)
        or len(legal_residence_iso2) != 2
        or not legal_residence_iso2.isalpha()
        or legal_residence_iso2 != legal_residence_iso2.upper()
    ):
        raise ValueError("Explicit ISO 3166-1 alpha-2 legal residence required")
    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Timezone-aware current time required")
    now = now.astimezone(timezone.utc)
    records = _load(source_path)
    match = next((r for r in records if r["competition_id"] == contest_id), None)
    if match is None:
        raise KeyError(f"Contest is not in verified official rules registry: {contest_id}")
    deadline = _required_utc(match["registration_close_utc"], "registration_close_utc")
    end = _required_utc(match["end_utc"], "end_utc")
    rules = match["residence_rule"]
    countries = set(rules["iso_country_codes"])
    if (
        rules["type"] == "ALLOWLIST_ONLY"
        and legal_residence_iso2 not in countries
    ) or (
        rules["type"] == "EXCLUSION_LIST_REQUIRES_LEGAL_CONFIRMATION"
        and legal_residence_iso2 in countries
    ):
        result = "INELIGIBLE_TERRITORY"
        reason = "Official contest restrictions exclude this legal residence"
    elif now >= end:
        result = "CONTEST_ENDED"
        reason = "Competition period ended"
    elif now >= deadline:
        result = "REGISTRATION_CLOSED"
        reason = "Official registration period ended; owner entry was not confirmed"
    else:
        result = "OWNER_ELIGIBILITY_CONFIRMATION_REQUIRED"
        reason = (
            "Preliminary country screening only; verify full legal rules, owner "
            "identity, account enrollment and source before any activation"
        )
    return ContestIntake(
        contest_id=contest_id,
        result=result,
        reason=reason,
        registration_deadline_utc=deadline,
        end_utc=end,
        rules_url=match["rules_url"],
    )
