from __future__ import annotations

from .competition_profiles import AMP_CORE_FEED_SYMBOLS, CAPITAL_AFRICA_LIMITS
from .data_capabilities import CAPABILITIES


def build_readiness(runtime_control: dict) -> dict:
    competition_symbols = set(CAPITAL_AFRICA_LIMITS)
    amp_core_symbols = set(AMP_CORE_FEED_SYMBOLS)
    verified_symbols = {s for s, c in CAPABILITIES.items() if c.verified}
    direct_quote_symbols = sorted(s for s, c in CAPABILITIES.items() if c.direct_quote)
    fallback_quote_symbols = sorted(s for s, c in CAPABILITIES.items() if not c.direct_quote)

    capability_complete = competition_symbols.issubset(verified_symbols)
    amp_core_capability_complete = amp_core_symbols.issubset(verified_symbols)
    historical_context_capable = capability_complete and all(
        CAPABILITIES[s].ohlcv and CAPABILITIES[s].local_technicals_from_ohlcv
        for s in competition_symbols
    )
    amp_core_historical_context_capable = amp_core_capability_complete and all(
        CAPABILITIES[s].ohlcv and CAPABILITIES[s].local_technicals_from_ohlcv
        for s in amp_core_symbols
    )
    analysis_ready = historical_context_capable and amp_core_historical_context_capable
    execution_api_available = any(CAPABILITIES[s].execution_write for s in competition_symbols)

    blockers: list[str] = []
    if not capability_complete:
        blockers.append("capital_capability_matrix_incomplete")
    if not analysis_ready:
        blockers.append("analysis_capability_incomplete")
    if not amp_core_capability_complete:
        blockers.append("amp_core_capability_matrix_incomplete")
    if not amp_core_historical_context_capable:
        blockers.append("amp_core_historical_context_incomplete")
    if not historical_context_capable:
        blockers.append("historical_context_capability_incomplete")
    if runtime_control.get("kill_switch"):
        blockers.append("kill_switch_active")
    if runtime_control.get("safe_mode"):
        blockers.append("safe_mode_active")

    return {
        "analysis_ready": analysis_ready,
        "historical_context_capable": historical_context_capable,
        "historical_context_required": True,
        "historical_window_trading_days": 252,
        "historical_context_timeframe": "1D",
        "historical_context_policy": "previous_confirmed_daily_bar",
        "approval_runtime_ready": not blockers,
        "execution_mode": "manual_only",
        "automatic_execution_available": execution_api_available,
        "human_approval_required": True,
        "runtime_control": runtime_control,
        "capital_symbols_total": len(competition_symbols),
        "capital_symbols_verified": len(verified_symbols & competition_symbols),
        "amp_core_symbols_total": len(amp_core_symbols),
        "amp_core_symbols_verified": len(verified_symbols & amp_core_symbols),
        "amp_core_historical_context_capable": amp_core_historical_context_capable,
        "direct_quote_capability_symbols": direct_quote_symbols,
        "runtime_quote_evidence_required_for_all_approvals": True,
        "independent_quote_or_owner_confirmation_symbols": fallback_quote_symbols,
        "blockers": blockers,
        "note": (
            "Static readiness does not prove that the market is open, that a live quote is "
            "currently available, or that the latest v0.7 historical context has been observed "
            "in a production event. Approval still requires fresh trusted runtime evidence."
        ),
    }
