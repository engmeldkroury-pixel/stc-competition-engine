"""Read-only arithmetic reconciliation. Never fabricate fills or ledger imports."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def money(value: str) -> Decimal:
    if not isinstance(value, str):
        raise ValueError('decimal_string_required')
    try:
        d = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError('invalid_decimal') from exc
    if not d.is_finite():
        raise ValueError('nonfinite_decimal')
    return d


def reconcile_visible_trade(*, ledger_realized: str, platform_realized: str,
                            previously_documented_residual: str, side: str,
                            quantity: str, entry_price: str, exit_price: str,
                            entry_commission: str, exit_commission: str) -> dict:
    if side not in {'LONG', 'SHORT'}:
        raise ValueError('invalid_side')
    q,e,x,fee1,fee2 = map(money, (quantity,entry_price,exit_price,entry_commission,exit_commission))
    if min(q,e,x) <= 0 or min(fee1,fee2) < 0:
        raise ValueError('invalid_fill_values')
    ledger,platform,residual = map(money,(ledger_realized,platform_realized,previously_documented_residual))
    gross = (x-e)*q*(1 if side=='LONG' else -1)
    net = gross-fee1-fee2
    explained = ledger+residual+net
    remaining = platform-explained
    return dict(schema='stc-visible-fill-reconciliation-v1', research_only=True, execution='none',
                ledger_write_allowed=False, independent_broker_confirmation=False,
                assumed_point_value='1', gross_price_pnl=str(gross), visible_commissions=str(fee1+fee2),
                visible_net_pnl=str(net), prior_residual=str(residual),
                ledger_plus_prior_residual_plus_visible_trade=str(explained),
                remaining_rounding_difference=str(remaining),
                matches_displayed_cents=explained.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)==platform.quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                limitations=['Historical screenshot arithmetic only; no current equity attestation.',
                             'Previously documented residual remains unattributed, not invented as a new trade.',
                             'Assumes one USD price-point value per unit for this evidenced instrument.',
                             'Unknown financing or other charges are not inferred.',
                             'Exact execution identifiers, close time and ledger idempotency remain prerequisites for import.'])
