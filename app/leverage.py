from __future__ import annotations

from dataclasses import dataclass

from .competition_profiles import get_profile


@dataclass(frozen=True)
class LeverageCapacity:
    competition_id: str
    symbol: str
    asset_class: str
    official_leverage: float
    quantity: float
    notional_usd: float
    margin_required_usd: float
    margin_utilization: float
    effective_leverage_on_equity: float
    within_margin_budget: bool
    note: str


FUTURES_MULTIPLIER_USD = {
    "CME_MINI:MES1!": 5.0,
    "CME_MINI:MNQ1!": 2.0,
    "CBOT_MINI:MYM1!": 0.5,
    "CME_MINI:M2K1!": 5.0,
    "NYMEX:MCL1!": 100.0,
    "NYMEX:MNG1!": 1000.0,
    "COMEX_MINI:MGC1!": 10.0,
    "COMEX_MINI:SIL1!": 1000.0,
    "CME_MINI:M6E1!": 12500.0,
    "CME_MINI:M6B1!": 6250.0,
    "CME_MINI:MJY1!": 1250000.0,
    "CME_MINI:M6A1!": 10000.0,
    "CME:MBT1!": 0.1,
    "CME:MET1!": 0.1,
    "CBOT:ZN1!": 1000.0,
    "CBOT:ZB1!": 1000.0,
}


def asset_class_for_symbol(competition_id: str, symbol: str) -> str:
    if competition_id == "amp-futures-sep-2026":
        return "futures"
    if symbol in {"CAPITALCOM:BTCUSD", "CAPITALCOM:ETHUSD", "CAPITALCOM:DOGEUSD"}:
        return "crypto"
    if symbol in {"CAPITALCOM:EURUSD", "CAPITALCOM:AUDUSD", "CAPITALCOM:USDZAR"}:
        return "forex"
    return "other"


def notional_usd(competition_id: str, symbol: str, price: float, quantity: float) -> float:
    if price <= 0 or quantity < 0:
        raise ValueError("price must be positive and quantity non-negative")
    if competition_id == "amp-futures-sep-2026":
        multiplier = FUTURES_MULTIPLIER_USD.get(symbol)
        if multiplier is None:
            raise KeyError(f"unverified futures multiplier: {symbol}")
        return price * multiplier * quantity
    if symbol == "CAPITALCOM:USDZAR":
        return quantity
    return price * quantity


def leverage_capacity(
    competition_id: str,
    symbol: str,
    *,
    price: float,
    quantity: float,
    equity_usd: float,
    max_margin_fraction: float = 0.35,
) -> LeverageCapacity:
    if equity_usd <= 0:
        raise ValueError("equity_usd must be positive")
    if not 0 < max_margin_fraction <= 1:
        raise ValueError("max_margin_fraction must be in (0,1]")

    profile = get_profile(competition_id)
    asset_class = asset_class_for_symbol(competition_id, symbol)
    leverage = float(profile.leverage_by_asset_class[asset_class])
    gross = notional_usd(competition_id, symbol, price, quantity)
    margin = gross / leverage
    utilization = margin / equity_usd
    effective = gross / equity_usd

    return LeverageCapacity(
        competition_id=competition_id,
        symbol=symbol,
        asset_class=asset_class,
        official_leverage=leverage,
        quantity=quantity,
        notional_usd=gross,
        margin_required_usd=margin,
        margin_utilization=utilization,
        effective_leverage_on_equity=effective,
        within_margin_budget=utilization <= max_margin_fraction + 1e-12,
        note=(
            "Competition leverage is fixed by the official rules. STC controls exposure via quantity, "
            "stop risk, position caps and a margin-utilization budget; it does not set broker leverage."
        ),
    )
