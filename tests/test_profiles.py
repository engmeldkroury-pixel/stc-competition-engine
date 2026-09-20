from app.competition_profiles import AMP_LIMITS, CAPITAL_AFRICA_LIMITS, PROFILES


def test_two_active_profiles_present():
    assert set(PROFILES) == {"amp-futures-sep-2026", "capital-africa-sep-2026"}


def test_amp_core_rules():
    p = PROFILES["amp-futures-sep-2026"]
    assert p.initial_balance_usd == 250_000
    assert p.min_trading_days == 5
    assert p.first_prize_usd == 10_000
    assert p.max_transactions_per_minute_allowed == 59
    assert p.leverage_by_asset_class["futures"] == 20
    assert AMP_LIMITS["CME_MINI:MNQ1!"] == 500
    assert AMP_LIMITS["CME_MINI:NQ1!"] == 100
    assert AMP_LIMITS["COMEX:GC1!"] == 100


def test_capital_africa_core_rules():
    p = PROFILES["capital-africa-sep-2026"]
    assert p.initial_balance_usd == 100_000
    assert p.min_trading_days == 3
    assert p.first_prize_usd == 3_000
    assert p.commission_rate == 0.0001
    assert p.leverage_by_asset_class["forex"] == 25
    assert p.leverage_by_asset_class["crypto"] == 1
    assert CAPITAL_AFRICA_LIMITS["CAPITALCOM:XAUUSD"] == 75
    assert CAPITAL_AFRICA_LIMITS["CAPITALCOM:NAS100"] == 10
