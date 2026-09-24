from __future__ import annotations

from typing import Mapping


EVIDENCE_SOURCE = "research_benchmarks/community_corrected_full26_20260924.json"

CAPITAL_COMMUNITY_15M_PROFILES: dict[str, dict[str, float]] = {
    "CAPITALCOM:BTCUSD": {
        "rsi_kernel_optimized_flux": 1.0,
    },
    "CAPITALCOM:DOGEUSD": {
        "range_filter_guikroth": 0.6006253304227808,
        "schaff_trend_cycle": 0.3993746695772193,
    },
    "CAPITALCOM:ETHUSD": {
        "ssl_hybrid": 1.0,
    },
    "CAPITALCOM:EURUSD": {
        "trendilo": 1.0,
    },
    "CAPITALCOM:NAS100": {
        "halftrend_everget": 1.0,
    },
    "CAPITALCOM:USDZAR": {
        "lorentzian_classification": 0.2879042371321771,
        "nadaraya_watson_endpoint_nonrepaint": 0.2341137461419382,
        "alphatrend": 0.1788421855683715,
        "supertrend_kivanc": 0.1771992492416492,
        "ut_bot_alerts": 0.12194058191586397,
    },
}

CAPITAL_NO_VALIDATED_COMMUNITY_PROFILE = frozenset(
    {
        "CAPITALCOM:AUDUSD",
        "CAPITALCOM:SPX500",
        "CAPITALCOM:XAGUSD",
        "CAPITALCOM:XAUUSD",
    }
)


def _normalize_timeframe(timeframe: str) -> str:
    value = str(timeframe).strip().lower()
    return "15" if value in {"15", "15m"} else value


def build_community_component_shadow(
    symbol: str,
    timeframe: str,
    component_signals: Mapping[str, float] | None,
) -> dict:
    """Build research-only community-component evidence.

    This function deliberately has no trade-decision authority. It may expose a
    symbol/timeframe-specific weighted score only when every component selected
    by the frozen research profile is present in the payload.
    """
    normalized_timeframe = _normalize_timeframe(timeframe)
    profile = (
        CAPITAL_COMMUNITY_15M_PROFILES.get(symbol)
        if normalized_timeframe == "15"
        else None
    )
    supplied = dict(component_signals or {})

    if profile is None:
        status = (
            "NO_VALIDATED_COMMUNITY_PROFILE"
            if normalized_timeframe == "15"
            and symbol in CAPITAL_NO_VALIDATED_COMMUNITY_PROFILE
            else "NO_RESEARCH_PROFILE_FOR_SYMBOL_TIMEFRAME"
        )
        return {
            "status": status,
            "symbol": symbol,
            "timeframe": normalized_timeframe,
            "evidence_source": EVIDENCE_SOURCE,
            "expected_components": [],
            "normalized_weights": {},
            "observed_signals": {},
            "missing_components": [],
            "unexpected_components_ignored": sorted(supplied),
            "complete": False,
            "weighted_score": None,
            "live_authority": False,
            "used_in_quality_gate": False,
            "used_in_risk": False,
            "used_in_approval": False,
        }

    expected = set(profile)
    observed = {
        name: float(value)
        for name, value in supplied.items()
        if name in expected
    }
    missing = sorted(expected - set(observed))
    unexpected = sorted(set(supplied) - expected)
    complete = not missing
    weighted_score = (
        sum(profile[name] * observed[name] for name in profile)
        if complete
        else None
    )

    return {
        "status": (
            "COMPLETE_SHADOW_EVIDENCE"
            if complete
            else "AWAITING_COMPONENT_SIGNALS"
            if not supplied
            else "INCOMPLETE_SHADOW_EVIDENCE"
        ),
        "symbol": symbol,
        "timeframe": normalized_timeframe,
        "evidence_source": EVIDENCE_SOURCE,
        "expected_components": list(profile),
        "normalized_weights": dict(profile),
        "observed_signals": observed,
        "missing_components": missing,
        "unexpected_components_ignored": unexpected,
        "complete": complete,
        "weighted_score": weighted_score,
        "live_authority": False,
        "used_in_quality_gate": False,
        "used_in_risk": False,
        "used_in_approval": False,
    }
