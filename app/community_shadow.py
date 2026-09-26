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

AMP_COMMUNITY_15M_EVIDENCE_SOURCE = (
    "github-actions:35916027610/stc-native-community-15m"
)

# Stable AMP profiles from the verified 2026-09-23 exact-provider 15m run.
# Symbols whose profile changed in later research waves (ZB/MJY/MCL) are
# intentionally excluded until their post-wave weights are reconciled.
AMP_COMMUNITY_15M_PROFILES: dict[str, dict[str, float]] = {
    "NYMEX:MNG1!": {
        "range_filter_guikroth": 1.0,
    },
    "COMEX_MINI:MGC1!": {
        "qqe_mod": 0.5698649457861664,
        "ssl_hybrid": 0.43013505421383363,
    },
    "CBOT:ZN1!": {
        "schaff_trend_cycle": 0.3704593624494359,
        "alphatrend": 0.35614555898192934,
        "qqe_mod": 0.27339507856863476,
    },
    "CME:MET1!": {
        "waddah_attar_explosion": 0.6080762173214392,
        "ut_bot_alerts": 0.39192378267856076,
    },
}

AMP_COMMUNITY_15M_PARAMETERS: dict[str, dict[str, dict[str, float | int]]] = {
    "NYMEX:MNG1!": {
        "range_filter_guikroth": {
            "sampling_period": 100,
            "range_multiplier": 2.0,
        },
    },
    "COMEX_MINI:MGC1!": {
        "qqe_mod": {
            "rsi_period": 8,
            "smoothing": 5,
            "fast_factor": 3.0,
            "slow_factor": 1.8,
            "threshold": 3.0,
            "bb_length": 40,
            "bb_mult": 0.35,
        },
        "ssl_hybrid": {
            "baseline_length": 60,
            "ssl_length": 15,
        },
    },
    "CBOT:ZN1!": {
        "schaff_trend_cycle": {
            "cycle_length": 12,
            "fast_length": 26,
            "slow_length": 50,
            "smoothing": 0.5,
        },
        "alphatrend": {
            "period": 20,
            "coefficient": 1.0,
        },
        "qqe_mod": {
            "rsi_period": 8,
            "smoothing": 5,
            "fast_factor": 3.0,
            "slow_factor": 1.8,
            "threshold": 3.0,
            "bb_length": 40,
            "bb_mult": 0.35,
        },
    },
    "CME:MET1!": {
        "waddah_attar_explosion": {
            "fast_length": 12,
            "slow_length": 26,
            "bb_length": 20,
            "bb_mult": 2.0,
            "sensitivity": 100.0,
            "dead_zone_atr_period": 100,
            "dead_zone_mult": 3.0,
        },
        "ut_bot_alerts": {
            "atr_period": 14,
            "key_value": 2.0,
        },
    },
}

AMP_PROFILE_RECONCILIATION_PENDING = frozenset(
    {
        "CBOT:ZB1!",
        "CME_MINI:MJY1!",
        "NYMEX:MCL1!",
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
    profile = None
    selected_parameters: dict[str, dict[str, float | int]] = {}
    evidence_source = EVIDENCE_SOURCE
    if normalized_timeframe == "15":
        if symbol in CAPITAL_COMMUNITY_15M_PROFILES:
            profile = CAPITAL_COMMUNITY_15M_PROFILES[symbol]
            selected_parameters = CAPITAL_COMMUNITY_15M_PARAMETERS.get(symbol, {})
        elif symbol in AMP_COMMUNITY_15M_PROFILES:
            profile = AMP_COMMUNITY_15M_PROFILES[symbol]
            selected_parameters = AMP_COMMUNITY_15M_PARAMETERS.get(symbol, {})
            evidence_source = AMP_COMMUNITY_15M_EVIDENCE_SOURCE
    supplied = dict(component_signals or {})

    if profile is None:
        status = (
            "PROFILE_RECONCILIATION_PENDING"
            if normalized_timeframe == "15"
            and symbol in AMP_PROFILE_RECONCILIATION_PENDING
            else "NO_VALIDATED_COMMUNITY_PROFILE"
            if normalized_timeframe == "15"
            and symbol in CAPITAL_NO_VALIDATED_COMMUNITY_PROFILE
            else "NO_RESEARCH_PROFILE_FOR_SYMBOL_TIMEFRAME"
        )
        return {
            "status": status,
            "symbol": symbol,
            "timeframe": normalized_timeframe,
            "evidence_source": evidence_source,
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
        "evidence_source": evidence_source,
        "expected_components": list(profile),
        "normalized_weights": dict(profile),
        "selected_parameters": dict(selected_parameters),
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
