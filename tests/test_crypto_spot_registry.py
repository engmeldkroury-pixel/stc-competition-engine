from app.crypto_spot_registry import load_crypto_spot_registry


def test_crypto_spot_registry_loads_spot_only_assets():
    registry = load_crypto_spot_registry()

    assert registry.mode == "SPOT_ONLY"
    assert registry.constraints["futures"] is False
    assert registry.constraints["leverage"] is False
    assert registry.constraints["shorting"] is False

    assert [x.asset for x in registry.research_assets] == [
        "BTC",
        "ETH",
        "SOL",
        "TRB",
        "GALA",
        "YGG",
        "NOT",
    ]


def test_crypto_spot_registry_exact_pairs():
    registry = load_crypto_spot_registry()

    assert registry.by_pair("BTCUSDT").asset == "BTC"
    assert registry.by_asset("ETH").pair == "ETHUSDT"
