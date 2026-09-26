from __future__ import annotations

from typing import Mapping


CAPITAL_EVIDENCE_SOURCE = "research_benchmarks/community_corrected_full26_20260924.json"
AMP_EVIDENCE_SOURCE = "github_actions:35964596933/wave3-combined"

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

AMP_COMMUNITY_15M_PROFILES: dict[str, dict[str, float]] = {
    "NYMEX:MCL1!": {
        "ssl_hybrid": 0.21132177101758742,
        "qqe_mod": 0.18665429587529245,
        "chandelier_exit_everget": 0.1681999714994004,
        "range_filter_guikroth": 0.12746426014806664,
        "ut_bot_alerts": 0.1118849249414745,
        "schaff_trend_cycle": 0.10967817623990596,
        "squeeze_momentum_lazybear": 0.08479660027827253,
    },
    "NYMEX:MNG1!": {
        "range_filter_guikroth": 1.0,
    },
    "COMEX_MINI:MGC1!": {
        "qqe_mod": 0.5698649457861664,
        "ssl_hybrid": 0.43013505421383363,
    },
    "CME_MINI:MJY1!": {
        "wavetrend_crosses": 0.29313954752232735,
        "schaff_trend_cycle": 0.2580276321516121,
        "waddah_attar_explosion": 0.2570035403438741,
        "trendilo": 0.19182927998218638,
    },
    "CME:MET1!": {
        "waddah_attar_explosion": 0.6080762173214392,
        "ut_bot_alerts": 0.39192378267856076,
    },
    "CBOT:ZN1!": {
        "schaff_trend_cycle": 0.3704593624494359,
        "alphatrend": 0.35614555898192934,
        "qqe_mod": 0.27339507856863476,
    },
    "CBOT:ZB1!": {
        "range_filter_guikroth": 0.2320986383034729,
        "chandelier_exit_everget": 0.2063520940279631,
        "waddah_attar_explosion": 0.18337368787086122,
        "qqe_mod": 0.13019654494176194,
        "ssl_hybrid": 0.12469713822952401,
        "halftrend_everget": 0.12328189662641696,
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

AMP_COMMUNITY_15M_PARAMETERS: dict[str, dict[str, dict[str, float | int]]] = {
    "NYMEX:MCL1!": {
        "ssl_hybrid": {"baseline_length": 100, "ssl_length": 20},
        "qqe_mod": {
            "rsi_period": 6,
            "smoothing": 5,
            "fast_factor": 2.5,
            "slow_factor": 1.61,
            "threshold": 2.0,
            "bb_length": 50,
            "bb_mult": 0.35,
        },
        "chandelier_exit_everget": {"period": 14, "multiplier": 2.0},
        "range_filter_guikroth": {"sampling_period": 50, "range_multiplier": 2.0},
        "ut_bot_alerts": {"atr_period": 10, "key_value": 1.5},
        "schaff_trend_cycle": {
            "cycle_length": 12,
            "fast_length": 26,
            "slow_length": 50,
            "smoothing": 0.5,
        },
        "squeeze_momentum_lazybear": {"length": 20, "bb_mult": 2.0, "kc_mult": 1.5},
    },
    "NYMEX:MNG1!": {
        "range_filter_guikroth": {"sampling_period": 100, "range_multiplier": 2.0},
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
        "ssl_hybrid": {"baseline_length": 60, "ssl_length": 15},
    },
    "CME_MINI:MJY1!": {
        "wavetrend_crosses": {
            "channel_length": 14,
            "average_length": 21,
            "signal_length": 4,
        },
        "schaff_trend_cycle": {
            "cycle_length": 12,
            "fast_length": 26,
            "slow_length": 50,
            "smoothing": 0.5,
        },
        "waddah_attar_explosion": {
            "fast_length": 12,
            "slow_length": 26,
            "bb_length": 20,
            "bb_mult": 2.0,
            "sensitivity": 100.0,
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
        "ut_bot_alerts": {"atr_period": 14, "key_value": 2.0},
    },
    "CBOT:ZN1!": {
        "schaff_trend_cycle": {
            "cycle_length": 12,
            "fast_length": 26,
            "slow_length": 50,
            "smoothing": 0.5,
        },
        "alphatrend": {"period": 20, "coefficient": 1.0},
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
    "CBOT:ZB1!": {
        "range_filter_guikroth": {"sampling_period": 100, "range_multiplier": 3.0},
        "chandelier_exit_everget": {"period": 14, "multiplier": 3.0},
        "waddah_attar_explosion": {
            "fast_length": 20,
            "slow_length": 40,
            "bb_length": 20,
            "bb_mult": 2.0,
            "sensitivity": 150.0,
            "dead_zone_atr_period": 100,
            "dead_zone_mult": 3.7,
        },
        "qqe_mod": {
            "rsi_period": 6,
            "smoothing": 5,
            "fast_factor": 3.0,
            "slow_factor": 1.61,
            "threshold": 3.0,
            "bb_length": 50,
            "bb_mult": 0.35,
        },
        "ssl_hybrid": {"baseline_length": 60, "ssl_length": 15},
        "halftrend_everget": {"amplitude": 5},
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

AMP_NO_VALIDATED_COMMUNITY_PROFILE = frozenset(
    {
        "CME_MINI:MES1!",
        "CME_MINI:MNQ1!",
        "CBOT_MINI:MYM1!",
        "CME_MINI:M2K1!",
        "COMEX_MINI:SIL1!",
        "CME_MINI:M6E1!",
        "CME_MINI:M6B1!",
        "CME_MINI:M6A1!",
        "CME:MBT1!",
    }
)

COMMUNITY_15M_PROFILES = {
    **CAPITAL_COMMUNITY_15M_PROFILES,
    **AMP_COMMUNITY_15M_PROFILES,
}

COMMUNITY_15M_PARAMETERS = {
    **CAPITAL_COMMUNITY_15M_PARAMETERS,
    **AMP_COMMUNITY_15M_PARAMETERS,
}


def _normalize_timeframe(timeframe: str) -> str:
    value = str(timeframe).strip().lower()
    return "15" if value in {"15", "15m"} else value


def _evidence_source_for(symbol: str) -> str:
    if symbol in AMP_COMMUNITY_15M_PROFILES or symbol in AMP_NO_VALIDATED_COMMUNITY_PROFILE:
        return AMP_EVIDENCE_SOURCE
    return CAPITAL_EVIDENCE_SOURCE


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
        COMMUNITY_15M_PROFILES.get(symbol)
        if normalized_timeframe == "15"
        else None
    )
    supplied = dict(component_signals or {})
    evidence_source = _evidence_source_for(symbol)

    if profile is None:
        has_known_no_profile = (
            normalized_timeframe == "15"
            and (
                symbol in CAPITAL_NO_VALIDATED_COMMUNITY_PROFILE
                or symbol in AMP_NO_VALIDATED_COMMUNITY_PROFILE
            )
        )
        status = (
            "NO_VALIDATED_COMMUNITY_PROFILE"
            if has_known_no_profile
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
        "selected_parameters": dict(COMMUNITY_15M_PARAMETERS.get(symbol, {})),
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
