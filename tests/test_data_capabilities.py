from app.data_capabilities import get_capability, validate_provider_mapping


def test_capital_xau_capability_uses_local_indicator_fallback():
    c = get_capability("CAPITALCOM:XAUUSD")
    assert c.verified is True
    assert c.ohlcv is True
    assert c.native_technicals is False
    assert c.local_technicals_from_ohlcv is True
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
