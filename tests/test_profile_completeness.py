from app.competition_profiles import AMP_LIMITS, CAPITAL_AFRICA_LIMITS


def test_amp_profile_has_expected_full_symbol_count():
    # Official Sep-2026 AMP rules list 94 symbols in the competition.
    assert len(AMP_LIMITS) == 94


def test_africa_profile_has_ten_symbols():
    assert len(CAPITAL_AFRICA_LIMITS) == 10
