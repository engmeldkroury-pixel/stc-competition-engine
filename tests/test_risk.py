from app.models import CompetitionEligibilityRequest, OrderValidationRequest
from app.risk import competition_eligibility, validate_order


def order(**overrides):
    data = dict(
        competition_id="capital-africa-sep-2026",
        symbol="CAPITALCOM:XAUUSD",
        side="BUY",
        requested_quantity=10,
        current_open_quantity=0,
        transactions_last_60s=0,
        account_equity=100_000,
        risk_amount=500,
        max_risk_fraction=0.02,
    )
    data.update(overrides)
    return OrderValidationRequest(**data)


def test_valid_order_allowed():
    r = validate_order(order())
    assert r.allowed is True
    assert r.max_position == 75
    assert r.requires_human_approval is True


def test_position_limit_rejected():
    r = validate_order(order(requested_quantity=10, current_open_quantity=70))
    assert r.allowed is False
    assert any("exceeds official maximum" in x for x in r.reasons)


def test_unknown_symbol_rejected():
    r = validate_order(order(symbol="CAPITALCOM:UNKNOWN"))
    assert r.allowed is False
    assert any("not allowed" in x for x in r.reasons)


def test_rate_limit_blocks_60th_transaction():
    r = validate_order(order(transactions_last_60s=59))
    assert r.allowed is False
    assert any("prohibition threshold" in x for x in r.reasons)


def test_configured_risk_limit_blocks_excess():
    r = validate_order(order(risk_amount=2501, max_risk_fraction=0.02))
    assert r.allowed is False
    assert any("Risk amount" in x for x in r.reasons)


def test_score_is_realized_pnl_only():
    r = competition_eligibility(
        CompetitionEligibilityRequest(
            competition_id="capital-africa-sep-2026",
            qualifying_trading_days=2,
            realized_pnl=1234.5,
            unrealized_pnl=99999,
        )
    )
    assert r.competition_score == 1234.5
    assert r.eligible_by_days is False
    assert r.days_remaining == 1


def test_amp_requires_five_days():
    r = competition_eligibility(
        CompetitionEligibilityRequest(
            competition_id="amp-futures-sep-2026",
            qualifying_trading_days=4,
            realized_pnl=0,
        )
    )
    assert not r.eligible_by_days
    assert r.days_remaining == 1
