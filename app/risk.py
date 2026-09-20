from __future__ import annotations

from .competition_profiles import get_profile
from .models import (
    CompetitionEligibilityRequest,
    CompetitionEligibilityResult,
    OrderValidationRequest,
    OrderValidationResult,
)


def validate_order(req: OrderValidationRequest) -> OrderValidationResult:
    profile = get_profile(req.competition_id)
    reasons: list[str] = []

    max_position = profile.max_open_position.get(req.symbol)
    projected = req.current_open_quantity + req.requested_quantity

    if max_position is None:
        reasons.append("Symbol is not allowed by the selected competition profile")
    elif projected > max_position + 1e-12:
        reasons.append(
            f"Projected open position {projected:g} exceeds official maximum {max_position:g}"
        )

    if req.transactions_last_60s >= profile.max_transactions_per_minute_allowed:
        reasons.append(
            "Submitting another transaction would reach or exceed the competition prohibition threshold"
        )

    if req.risk_amount > req.account_equity * req.max_risk_fraction:
        reasons.append(
            f"Risk amount {req.risk_amount:.2f} exceeds configured risk fraction "
            f"{req.max_risk_fraction:.2%} of equity"
        )

    remaining = max(0, profile.max_transactions_per_minute_allowed - req.transactions_last_60s)
    return OrderValidationResult(
        allowed=not reasons,
        reasons=reasons or ["Order proposal satisfies current competition and configured risk checks"],
        max_position=max_position,
        projected_position=projected,
        rate_limit_remaining=remaining,
        requires_human_approval=True,
    )


def competition_eligibility(req: CompetitionEligibilityRequest) -> CompetitionEligibilityResult:
    profile = get_profile(req.competition_id)
    remaining = max(0, profile.min_trading_days - req.qualifying_trading_days)
    return CompetitionEligibilityResult(
        eligible_by_days=remaining == 0,
        days_remaining=remaining,
        competition_score=req.realized_pnl,
        note="Official ranking uses realized P/L; unrealized P/L is excluded until positions are closed or auto-closed at competition end.",
    )
