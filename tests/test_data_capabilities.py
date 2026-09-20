from app.competition_profiles import CAPITAL_AFRICA_LIMITS
from app.data_capabilities import CAPABILITIES, get_capability, validate_provider_mapping


def test_all_capital_competition_symbols_have_verified_capability_records():
    assert set(CAPITAL_AFRICA_LIMITS) == set(CAPABILITIES)
    for symbol in CAPITAL_AFRICA_LIMITS:
        c = get_capability(symbol)
        assert c.verified is True
        assert c.provider == "CAPITALCOM"
        assert c.ohlcv is True
        assert c.local_technicals_from_ohlcv is True
        assert c.execution_account_read is False
        assert c.execution_write is False


def test_native_technical_and_streaming_quote_subset_is_exact():
    native = {s for s, c in CAPABILITIES.items() if c.native_technicals}
    streaming = {s for s, c in CAPABILITIES.items() if c.direct_quote}
    expected = {"CAPITALCOM:EURUSD", "CAPITALCOM:AUDUSD", "CAPITALCOM:USDZAR"}
    assert native == expected
    assert streaming == expected
    for symbol in expected:
        assert get_capability(symbol).to_dict()["technical_path"] == "native_mcp"


def test_capital_xau_capability_uses_local_indicator_fallback():
    c = get_capability("CAPITALCOM:XAUUSD")
    assert c.verified is True
    assert c.ohlcv is True
    assert c.native_technicals is False
    assert c.local_technicals_from_ohlcv is True
    assert c.direct_quote is False
    assert c.to_dict()["technical_path"] == "local_from_ohlcv"


def test_unavailable_native_technicals_remain_local_fallback():
    for symbol in {
        "CAPITALCOM:BTCUSD", "CAPITALCOM:ETHUSD", "CAPITALCOM:DOGEUSD",
        "CAPITALCOM:XAUUSD", "CAPITALCOM:XAGUSD", "CAPITALCOM:SPX500", "CAPITALCOM:NAS100",
    }:
        c = get_capability(symbol)
        assert c.native_technicals is False
        assert c.to_dict()["technical_path"] == "local_from_ohlcv"


def test_unknown_symbol_is_not_assumed_supported():
    c = get_capability("CAPITALCOM:UNKNOWN")
    assert c.verified is False
    assert c.ohlcv is False
    assert c.to_dict()["technical_path"] == "unsupported"


def test_silent_provider_switch_is_blocked():
    allowed, reason = validate_provider_mapping("CAPITALCOM:XAUUSD", "OANDA:XAUUSD")
    assert allowed is False
    assert "Silent provider switch blocked" in reason


def test_same_provider_mapping_is_allowed():
    allowed, _ = validate_provider_mapping("CAPITALCOM:XAUUSD", "CAPITALCOM:XAUUSD")
    assert allowed is True
