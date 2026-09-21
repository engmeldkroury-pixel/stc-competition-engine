from __future__ import annotations

from dataclasses import asdict, dataclass

from .competition_profiles import AMP_CORE_FEED_SYMBOLS


@dataclass(frozen=True)
class SymbolCapability:
    symbol: str
    provider: str
    verified: bool
    symbol_search: bool
    ohlcv: bool
    native_technicals: bool
    local_technicals_from_ohlcv: bool
    news: bool
    economic_calendar_context: bool
    direct_quote: bool
    alerts_read: bool
    alert_log_read: bool
    execution_account_read: bool
    execution_write: bool
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        data = asdict(self)
        data["technical_path"] = (
            "native_mcp"
            if self.native_technicals
            else "local_from_ohlcv"
            if self.ohlcv and self.local_technicals_from_ohlcv
            else "unsupported"
        )
        return data


def _capital(
    symbol: str,
    *,
    symbol_search: bool,
    native_technicals: bool,
    direct_quote: bool,
    news: bool = False,
    extra_notes: tuple[str, ...] = (),
) -> SymbolCapability:
    notes = [
        "Exact-provider CAPITALCOM OHLCV was live-verified on 2026-09-20 for both 15m and 1h intervals.",
        "TradingView MCP OHLCV carries an explicit delayed-data notice; never use the latest OHLCV close as an execution-time quote.",
        "Execution account read/write is not provided by the verified TradingView MCP path; human approval and manual execution remain mandatory.",
        "Do not silently substitute another provider for Capital.com execution context.",
    ]
    if native_technicals:
        notes.append("Native TradingView technical rating was verified on both 15m and 1h for this exact provider/symbol.")
    else:
        notes.append("Native TradingView technical rating returned no technicals; use local indicators from exact-provider OHLCV for research/context.")
    if direct_quote:
        notes.append("Streaming direct quote was verified through get_symbol_data with update_mode=streaming.")
    else:
        notes.append("Direct quote via get_symbol_data was unavailable in the verified smoke test; approval must fail closed until an execution-time quote is independently verified.")
    notes.extend(extra_notes)
    return SymbolCapability(
        symbol=symbol,
        provider="CAPITALCOM",
        verified=True,
        symbol_search=symbol_search,
        ohlcv=True,
        native_technicals=native_technicals,
        local_technicals_from_ohlcv=True,
        news=news,
        economic_calendar_context=True,
        direct_quote=direct_quote,
        alerts_read=True,
        alert_log_read=True,
        execution_account_read=False,
        execution_write=False,
        notes=tuple(notes),
    )


def _amp_core(symbol: str) -> SymbolCapability:
    return SymbolCapability(
        symbol=symbol,
        provider=provider_of(symbol),
        verified=True,
        symbol_search=True,
        ohlcv=True,
        native_technicals=False,
        local_technicals_from_ohlcv=True,
        news=False,
        economic_calendar_context=True,
        direct_quote=False,
        alerts_read=True,
        alert_log_read=True,
        execution_account_read=False,
        execution_write=False,
        notes=(
            "Exact-provider 15m and 1D OHLCV were live-verified on 2026-09-21 for this AMP core-feed symbol.",
            "400 daily bars were returned for one-year historical context.",
            "TradingView OHLCV is analysis/context data, not execution-time quote evidence.",
            "No broker/execution-account read/write API is available through the verified TradingView MCP path.",
            "Human approval and manual competition order entry remain mandatory.",
        ),
    )


CAPABILITIES: dict[str, SymbolCapability] = {
    "CAPITALCOM:BTCUSD": _capital(
        "CAPITALCOM:BTCUSD", symbol_search=False, native_technicals=False, direct_quote=False
    ),
    "CAPITALCOM:ETHUSD": _capital(
        "CAPITALCOM:ETHUSD", symbol_search=False, native_technicals=False, direct_quote=False
    ),
    "CAPITALCOM:DOGEUSD": _capital(
        "CAPITALCOM:DOGEUSD", symbol_search=True, native_technicals=False, direct_quote=False
    ),
    "CAPITALCOM:EURUSD": _capital(
        "CAPITALCOM:EURUSD", symbol_search=True, native_technicals=True, direct_quote=True, news=True,
        extra_notes=("News retrieval was live-verified for the exact Capital.com EURUSD symbol on 2026-09-20.",),
    ),
    "CAPITALCOM:AUDUSD": _capital(
        "CAPITALCOM:AUDUSD", symbol_search=True, native_technicals=True, direct_quote=True
    ),
    "CAPITALCOM:USDZAR": _capital(
        "CAPITALCOM:USDZAR", symbol_search=True, native_technicals=True, direct_quote=True
    ),
    "CAPITALCOM:XAUUSD": _capital(
        "CAPITALCOM:XAUUSD", symbol_search=True, native_technicals=False, direct_quote=False, news=True,
        extra_notes=(
            "Owner-run TradingView MCP smoke test on 2026-09-19 verified symbol search, OHLCV, news, economic calendar, alerts list, and alert log.",
        ),
    ),
    "CAPITALCOM:XAGUSD": _capital(
        "CAPITALCOM:XAGUSD", symbol_search=True, native_technicals=False, direct_quote=False
    ),
    "CAPITALCOM:SPX500": _capital(
        "CAPITALCOM:SPX500", symbol_search=False, native_technicals=False, direct_quote=False
    ),
    "CAPITALCOM:NAS100": _capital(
        "CAPITALCOM:NAS100", symbol_search=False, native_technicals=False, direct_quote=False
    ),
    **{symbol: _amp_core(symbol) for symbol in AMP_CORE_FEED_SYMBOLS},
}


def provider_of(symbol: str) -> str:
    return symbol.split(":", 1)[0].upper() if ":" in symbol else ""


def get_capability(symbol: str) -> SymbolCapability:
    if symbol in CAPABILITIES:
        return CAPABILITIES[symbol]
    return SymbolCapability(
        symbol=symbol,
        provider=provider_of(symbol),
        verified=False,
        symbol_search=False,
        ohlcv=False,
        native_technicals=False,
        local_technicals_from_ohlcv=False,
        news=False,
        economic_calendar_context=False,
        direct_quote=False,
        alerts_read=False,
        alert_log_read=False,
        execution_account_read=False,
        execution_write=False,
        notes=("Capability has not yet been verified for this exact provider/symbol pair.",),
    )


def validate_provider_mapping(requested_symbol: str, candidate_symbol: str, allow_cross_provider: bool = False) -> tuple[bool, str]:
    requested_provider = provider_of(requested_symbol)
    candidate_provider = provider_of(candidate_symbol)
    if not requested_provider or not candidate_provider:
        return False, "Both symbols must include an explicit provider prefix such as CAPITALCOM:XAUUSD."
    if requested_provider == candidate_provider:
        return True, "Provider preserved."
    if allow_cross_provider:
        return True, "Cross-provider mapping explicitly allowed by caller; result must remain labeled as non-execution reference data."
    return False, f"Silent provider switch blocked: {requested_provider} -> {candidate_provider}."
