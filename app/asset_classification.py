from __future__ import annotations


STRATEGY_ASSET_CLASS = {
    # Capital.com
    "CAPITALCOM:BTCUSD": "crypto",
    "CAPITALCOM:ETHUSD": "crypto",
    "CAPITALCOM:DOGEUSD": "crypto",
    "CAPITALCOM:EURUSD": "forex",
    "CAPITALCOM:AUDUSD": "forex",
    "CAPITALCOM:USDZAR": "forex",
    "CAPITALCOM:XAUUSD": "metals",
    "CAPITALCOM:XAGUSD": "metals",
    "CAPITALCOM:SPX500": "indices",
    "CAPITALCOM:NAS100": "indices",
    # AMP futures core
    "CME_MINI:MES1!": "indices",
    "CME_MINI:MNQ1!": "indices",
    "CBOT_MINI:MYM1!": "indices",
    "CME_MINI:M2K1!": "indices",
    "NYMEX:MCL1!": "energy",
    "NYMEX:MNG1!": "energy",
    "COMEX_MINI:MGC1!": "metals",
    "COMEX_MINI:SIL1!": "metals",
    "CME_MINI:M6E1!": "forex",
    "CME_MINI:M6B1!": "forex",
    "CME_MINI:MJY1!": "forex",
    "CME_MINI:M6A1!": "forex",
    "CME:MBT1!": "crypto",
    "CME:MET1!": "crypto",
    "CBOT:ZN1!": "rates",
    "CBOT:ZB1!": "rates",
}


def strategy_asset_class(symbol: str) -> str:
    try:
        return STRATEGY_ASSET_CLASS[symbol]
    except KeyError as exc:
        raise KeyError(f"Unclassified strategy symbol: {symbol}") from exc
