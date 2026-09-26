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

CAPITAL_COMMUNITY_15M_PARAMETERS: dict[str, dict[str, dict[str, float | int]]] = {
    "CAPITALCOM:BTCUSD": {
        "rsi_kernel_optimized_flux": {
            "rsi_period": 21,
            "pivot_length": 12,
            "bandwidth": 6.0,
            "min_samples": 12,
            "dominance_ratio": 1.35,
        },
    },
    "CAPITALCOM:DOGEUSD": {
        "range_filter_guikroth": {
            "sampling_period": 100,
            "range_multiplier": 3.0,
        },
        "schaff_trend_cycle": {
            "cycle_length": 12,
            "fast_length": 26,
            "slow_length": 50,
            "smoothing": 0.5,
        },
    },
    "CAPITALCOM:ETHUSD": {
        "ssl_hybrid": {
            "baseline_length": 60,
            "ssl_length": 15,
        },
    },
    "CAPITALCOM:EURUSD": {
        "trendilo": {
            "smoothing": 1,
            "lookback": 50,
            "alma_offset": 0.85,
            "alma_sigma": 6.0,
            "band_multiplier": 1.0,
        },
    },
    "CAPITALCOM:NAS100": {
        "halftrend_everget": {
            "amplitude": 5,
        },
    },
    "CAPITALCOM:USDZAR": {
        "lorentzian_classification": {},
        "nadaraya_watson_endpoint_nonrepaint": {
            "window": 500,
            "bandwidth": 8.0,
            "multiplier": 3.0,
            "deviation_length": 499,
        },
        "alphatrend": {
            "period": 20,
            "coefficient": 1.0,
        },
        "supertrend_kivanc": {
            "atr_period": 14,
            "multiplier": 3.0,
        },
        "ut_bot_alerts": {
            "atr_period": 14,
            "key_value": 1.5,
        },
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
            "selected_parameters": {},
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
        "selected_parameters": dict(CAPITAL_COMMUNITY_15M_PARAMETERS.get(symbol, {})),
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


FROZEN_COMPETITION_15M_PROFILES: dict[str, dict[str, float]] = {
    # Capital.com final-unseen survivors in the current shadow registry.
    "CAPITALCOM:BTCUSD": {"trendilo": 1.0},
    "CAPITALCOM:USDZAR": {"supertrend_kivanc": 1.0},
    "CAPITALCOM:XAUUSD": {"range_filter_guikroth": 1.0},
    # AMP Futures final-unseen survivors on the currently deployed 16-symbol feed.
    "CBOT:ZB1!": {"range_filter_guikroth": 1.0},
    "NYMEX:MCL1!": {"ssl_hybrid": 1.0},
    "CME_MINI:MJY1!": {
        "alphatrend": 1.0 / 3.0,
        "waddah_attar_explosion": 1.0 / 3.0,
        "trendilo": 1.0 / 3.0,
    },
}

FROZEN_COMPETITION_15M_PARAMETERS: dict[str, dict[str, dict[str, float | int]]] = {
    "CAPITALCOM:BTCUSD": {
        "trendilo": {
            "smoothing": 1,
            "lookback": 50,
            "alma_offset": 0.85,
            "alma_sigma": 6.0,
            "band_multiplier": 1.25,
        },
    },
    "CAPITALCOM:USDZAR": {
        "supertrend_kivanc": {"atr_period": 14, "multiplier": 3.0},
    },
    "CAPITALCOM:XAUUSD": {
        "range_filter_guikroth": {"sampling_period": 100, "range_multiplier": 2.0},
    },
    "CBOT:ZB1!": {
        "range_filter_guikroth": {"sampling_period": 100, "range_multiplier": 3.0},
    },
    "NYMEX:MCL1!": {
        "ssl_hybrid": {"baseline_length": 100, "ssl_length": 20},
    },
    "CME_MINI:MJY1!": {
        "alphatrend": {"period": 20, "coefficient": 1.0},
        "waddah_attar_explosion": {
            "fast_length": 12,
            "slow_length": 26,
            "sensitivity": 100.0,
            "bb_length": 20,
            "bb_mult": 2.0,
            "dead_zone_atr_period": 100,
            "dead_zone_mult": 3.0,
        },
        "trendilo": {
            "smoothing": 1,
            "lookback": 50,
            "alma_offset": 0.85,
            "alma_sigma": 6.0,
            "band_multiplier": 1.25,
        },
    },
}


def build_frozen_competition_component_support(
    symbol: str,
    timeframe: str,
    component_signals: Mapping[str, float] | None,
) -> dict:
    """Build exact final-unseen component support for competition decisions.

    This layer is intentionally separate from the broader community-shadow
    research profile. It contains only components that survived the sealed
    final holdout and are present in the current shadow registry.

    The returned object does not place orders and does not bypass competition
    risk/approval controls. It is suitable only as a secondary direction input
    after the live Pine payload reproduces the exact confirmed-bar semantics.
    """
    normalized_timeframe = _normalize_timeframe(timeframe)
    profile = (
        FROZEN_COMPETITION_15M_PROFILES.get(symbol)
        if normalized_timeframe == "15"
        else None
    )
    supplied = dict(component_signals or {})

    if profile is None:
        return {
            "status": "NO_FROZEN_COMPETITION_PROFILE",
            "symbol": symbol,
            "timeframe": normalized_timeframe,
            "evidence_source": "research/community_shadow_registry.json",
            "expected_components": [],
            "normalized_weights": {},
            "selected_parameters": {},
            "observed_signals": {},
            "missing_components": [],
            "unexpected_components_ignored": sorted(supplied),
            "complete": False,
            "weighted_score": None,
            "decision_support_eligible": False,
            "live_authority": False,
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
        "status": "COMPLETE_FROZEN_SUPPORT" if complete else "AWAITING_FROZEN_COMPONENT_SIGNALS",
        "symbol": symbol,
        "timeframe": normalized_timeframe,
        "evidence_source": "research/community_shadow_registry.json",
        "expected_components": list(profile),
        "normalized_weights": dict(profile),
        "selected_parameters": dict(FROZEN_COMPETITION_15M_PARAMETERS[symbol]),
        "observed_signals": observed,
        "missing_components": missing,
        "unexpected_components_ignored": unexpected,
        "complete": complete,
        "weighted_score": weighted_score,
        "decision_support_eligible": complete,
        "live_authority": False,
    }
