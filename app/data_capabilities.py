from __future__ import annotations

from dataclasses import asdict, dataclass


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


CAPABILITIES: dict[str, SymbolCapability] = {
    "CAPITALCOM:XAUUSD": SymbolCapability(
        symbol="CAPITALCOM:XAUUSD",
        provider="CAPITALCOM",
        verified=True,
        symbol_search=True,
        ohlcv=True,
        native_technicals=False,
        local_technicals_from_ohlcv=True,
        news=True,
        economic_calendar_context=True,
        direct_quote=False,
        alerts_read=True,
        alert_log_read=True,
        execution_account_read=False,
        execution_write=False,
        notes=(
            "Owner-run TradingView MCP smoke test on 2026-09-19 verified symbol search, OHLCV, news, economic calendar, alerts list, and alert log.",
            "TradingView MCP technical-rating/screener technical fields returned no technicals/no data for this Capital.com CFD symbol.",
            "OHLCV may be delayed; do not treat the latest OHLCV close as an execution-time live quote without a freshness check.",
            "Do not silently substitute OANDA or another provider for Capital.com execution context.",
        ),
    ),
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
