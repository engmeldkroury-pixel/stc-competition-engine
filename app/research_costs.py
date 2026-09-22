from __future__ import annotations

from dataclasses import dataclass

from .asset_classification import strategy_asset_class
from .competition_profiles import get_profile


# Conservative research-only market-friction assumptions. They are not claims
# about a broker's live bid/ask spread. They model spread/slippage as a small
# fraction of ATR and are deliberately explicit so calibration can be audited.
ASSET_ROUND_TRIP_ATR_FRICTION = {
    "forex": 0.030,
    "rates": 0.030,
    "indices": 0.035,
    "metals": 0.040,
    "energy": 0.050,
    "crypto": 0.070,
}


@dataclass(frozen=True)
class ResearchCostEstimate:
    symbol: str
    competition_id: str
    asset_class: str
    commission_rate: float
    commission_price_units: float
    assumed_market_friction_atr_fraction: float
    market_friction_price_units: float
    total_price_units: float
    total_r: float
    note: str


def competition_id_for_symbol(symbol: str) -> str:
    if symbol.startswith("CAPITALCOM:"):
        return "capital-africa-sep-2026"
    return "amp-futures-sep-2026"


def estimate_research_cost_r(
    symbol: str,
    *,
    reference_price: float,
    atr: float,
    planned_risk_per_unit: float,
) -> ResearchCostEstimate:
    if reference_price <= 0 or atr < 0 or planned_risk_per_unit <= 0:
        raise ValueError("research cost inputs must be positive")

    competition_id = competition_id_for_symbol(symbol)
    profile = get_profile(competition_id)
    asset_class = strategy_asset_class(symbol)
    friction_fraction = ASSET_ROUND_TRIP_ATR_FRICTION.get(asset_class, 0.04)

    # The profile commission is modeled on both opening and closing notional.
    # Futures profile commission is currently zero under the stored competition
    # rules; the ATR friction still prevents a zero-cost backtest assumption.
    commission_price_units = 2.0 * profile.commission_rate * reference_price
    market_friction_price_units = friction_fraction * atr
    total_price_units = commission_price_units + market_friction_price_units
    total_r = min(0.50, total_price_units / planned_risk_per_unit)

    return ResearchCostEstimate(
        symbol=symbol,
        competition_id=competition_id,
        asset_class=asset_class,
        commission_rate=profile.commission_rate,
        commission_price_units=commission_price_units,
        assumed_market_friction_atr_fraction=friction_fraction,
        market_friction_price_units=market_friction_price_units,
        total_price_units=total_price_units,
        total_r=total_r,
        note=(
            "Research-only conservative transaction-cost proxy. Live spread/slippage "
            "must still be checked at manual execution time."
        ),
    )
