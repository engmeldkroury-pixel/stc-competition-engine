from __future__ import annotations

from typing import Mapping


# Research-only profiles from corrected 26-symbol exact-provider 15m evidence.
# Source runs: 35969652488 + retry 35987607069.
# These weights have NO live authority until exact Pine/Python component parity
# and owner-controlled promotion are separately verified.
CAPITAL_15M_COMPONENT_PROFILES: dict[str, dict[str, float]] = {
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


def build_component_shadow_snapshot(
    symbol: str,
    timeframe: str,
    signals: Mapping[str, float] | None,
) -> dict:
    """Evaluate exact community-component state as shadow evidence only.

    This function intentionally cannot influence the live competition gate.
    A weighted score is emitted only when every validated component for the
    exact symbol/timeframe profile is present.
    """
    if str(timeframe) != "15":
        return {
            "status": "NO_VALIDATED_PROFILE",
            "symbol": symbol,
            "timeframe": str(timeframe),
            "complete": False,
            "weighted_score": None,
            "expected_components": [],
            "missing_components": [],
            "unexpected_components": sorted((signals or {}).keys()),
            "signals_used": {},
            "weights_used": {},
            "live_authority": False,
            "affects_live_gate": False,
            "note": "No validated exact-component profile for this symbol/timeframe.",
        }

    weights = CAPITAL_15M_COMPONENT_PROFILES.get(symbol)
    if weights is None:
        return {
            "status": "NO_VALIDATED_PROFILE",
            "symbol": symbol,
            "timeframe": str(timeframe),
            "complete": False,
            "weighted_score": None,
            "expected_components": [],
            "missing_components": [],
            "unexpected_components": sorted((signals or {}).keys()),
            "signals_used": {},
            "weights_used": {},
            "live_authority": False,
            "affects_live_gate": False,
            "note": "Research found no validated community component profile for this Capital symbol.",
        }

    expected = set(weights)
    provided = dict(signals or {})
    matched = sorted(expected.intersection(provided))
    missing = sorted(expected.difference(provided))
    unexpected = sorted(set(provided).difference(expected))
    used = {component: float(provided[component]) for component in matched}
    complete = not missing

    score = None
    if complete:
        score = sum(used[component] * weights[component] for component in weights)
        score = max(-1.0, min(1.0, float(score)))

    return {
        "status": "COMPLETE_SHADOW" if complete else "AWAITING_EXACT_COMPONENTS",
        "symbol": symbol,
        "timeframe": str(timeframe),
        "complete": complete,
        "weighted_score": score,
        "expected_components": sorted(expected),
        "missing_components": missing,
        "unexpected_components": unexpected,
        "signals_used": used,
        "weights_used": dict(weights),
        "live_authority": False,
        "affects_live_gate": False,
        "note": (
            "Exact component research weights are shadow-only. "
            "They do not alter LONG/SHORT/WAIT, sizing, approval, or execution."
        ),
    }
