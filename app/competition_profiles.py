from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

UTC = timezone.utc


@dataclass(frozen=True)
class CompetitionProfile:
    competition_id: str
    name: str
    start_utc: datetime
    end_utc: datetime
    registration_close_utc: datetime
    initial_balance_usd: float
    min_trading_days: int
    first_prize_usd: float
    max_transactions_per_minute_allowed: int
    scoring_basis: str
    commission_rate: float
    leverage_by_asset_class: Mapping[str, float]
    max_open_position: Mapping[str, float]
    source_url: str

    @property
    def allowed_symbols(self) -> tuple[str, ...]:
        return tuple(self.max_open_position.keys())


AMP_LIMITS = {
    "CME_MINI:MES1!": 500.0,
    "CME_MINI:MNQ1!": 500.0,
    "CBOT_MINI:MYM1!": 500.0,
    "CME_MINI:M2K1!": 500.0,
    "CME_MINI:ES1!": 100.0,
    "CME_MINI:NQ1!": 100.0,
    "CBOT_MINI:YM1!": 100.0,
    "CME_MINI:RTY1!": 100.0,
    "CME_MINI:EMD1!": 25.0,
    "CME:MNK1!": 5.0,
    "CME:NKD1!": 10.0,
    "CME:BTC1!": 1.0,
    "CME:MBT1!": 25.0,
    "CME:ETH1!": 1.0,
    "CME:MET1!": 25.0,
    "CME:SOL1!": 1.0,
    "CME:MSL1!": 5.0,
    "CME:XRP1!": 1.0,
    "CME:MXP1!": 5.0,
    "CME:6A1!": 25.0,
    "CME:6B1!": 25.0,
    "CME:6C1!": 25.0,
    "CME:6E1!": 25.0,
    "CME:6J1!": 25.0,
    "CME:6N1!": 25.0,
    "CME:6S1!": 25.0,
    "CME_MINI:NES1!": 10.0,
    "CME_MINI:NNQ1!": 10.0,
    "CME_MINI:N2K1!": 10.0,
    "CBOT_MINI:NDOW1!": 10.0,
    "CME_MINI:E71!": 10.0,
    "CME_MINI:J71!": 5.0,
    "CME_MINI:M6A1!": 25.0,
    "CME_MINI:M6B1!": 10.0,
    "CME_MINI:MCD1!": 10.0,
    "CME_MINI:M6E1!": 25.0,
    "CME_MINI:MJY1!": 5.0,
    "CME_MINI:MSF1!": 5.0,
    "NYMEX:CL1!": 100.0,
    "NYMEX_MINI:QM1!": 10.0,
    "NYMEX:MCL1!": 100.0,
    "NYMEX:NG1!": 25.0,
    "NYMEX_MINI:QG1!": 5.0,
    "NYMEX:MNG1!": 10.0,
    "NYMEX:RB1!": 25.0,
    "NYMEX:HO1!": 25.0,
    "COMEX:GC1!": 100.0,
    "COMEX_MINI:QO1!": 10.0,
    "COMEX_MINI:MGC1!": 100.0,
    "COMEX:1OZ1!": 25.0,
    "COMEX:HG1!": 25.0,
    "COMEX_MINI:QC1!": 5.0,
    "COMEX_MINI:MHG1!": 25.0,
    "COMEX:SI1!": 25.0,
    "COMEX_MINI:QI1!": 5.0,
    "COMEX_MINI:SIL1!": 10.0,
    "COMEX:SIC1!": 10.0,
    "NYMEX:PL1!": 25.0,
    "CBOT:UB1!": 100.0,
    "CBOT:MWN1!": 5.0,
    "CBOT:TN1!": 100.0,
    "CBOT:MTN1!": 5.0,
    "CBOT:Z3N1!": 10.0,
    "CBOT:ZB1!": 100.0,
    "CBOT_MINI:30Y1!": 1.0,
    "CBOT:ZF1!": 100.0,
    "CBOT_MINI:5YY1!": 1.0,
    "CBOT:ZN1!": 100.0,
    "CBOT_MINI:10Y1!": 5.0,
    "CBOT:ZQ1!": 25.0,
    "CBOT:ZT1!": 100.0,
    "CBOT_MINI:2YY1!": 1.0,
    "CME:SR11!": 25.0,
    "CME:SR31!": 100.0,
    "CBOT:ZC1!": 25.0,
    "CBOT_MINI:XC1!": 5.0,
    "CBOT_MINI:MZC1!": 5.0,
    "CBOT:ZW1!": 25.0,
    "CBOT_MINI:XW1!": 5.0,
    "CBOT_MINI:MZW1!": 5.0,
    "CBOT:ZS1!": 25.0,
    "CBOT_MINI:XK1!": 5.0,
    "CBOT_MINI:MZS1!": 5.0,
    "CBOT:ZL1!": 25.0,
    "CBOT_MINI:MZL1!": 5.0,
    "CBOT:ZM1!": 25.0,
    "CBOT_MINI:MZM1!": 5.0,
    "CBOT:ZO1!": 5.0,
    "CBOT:ZR1!": 5.0,
    "CME:DC1!": 5.0,
    "CME:LBR1!": 5.0,
    "CME:GF1!": 10.0,
    "CME:HE1!": 25.0,
    "CME:LE1!": 25.0,
}

CAPITAL_AFRICA_LIMITS = {
    "CAPITALCOM:BTCUSD": 0.5,
    "CAPITALCOM:ETHUSD": 15.0,
    "CAPITALCOM:DOGEUSD": 500_000.0,
    "CAPITALCOM:EURUSD": 800_000.0,
    "CAPITALCOM:AUDUSD": 1_200_000.0,
    "CAPITALCOM:USDZAR": 800_000.0,
    "CAPITALCOM:XAUUSD": 75.0,
    "CAPITALCOM:XAGUSD": 5_000.0,
    "CAPITALCOM:SPX500": 40.0,
    "CAPITALCOM:NAS100": 10.0,
}


PROFILES: dict[str, CompetitionProfile] = {
    "amp-futures-sep-2026": CompetitionProfile(
        competition_id="amp-futures-sep-2026",
        name="The Leap by AMP Futures — September 2026",
        start_utc=datetime(2026, 9, 1, 8, 0, tzinfo=UTC),
        end_utc=datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
        registration_close_utc=datetime(2026, 9, 23, 8, 0, tzinfo=UTC),
        initial_balance_usd=250_000.0,
        min_trading_days=5,
        first_prize_usd=10_000.0,
        max_transactions_per_minute_allowed=59,
        scoring_basis="realized_pnl_closed_positions",
        commission_rate=0.0,
        leverage_by_asset_class={"futures": 20.0},
        max_open_position=AMP_LIMITS,
        source_url="https://www.tradingview.com/the-leap/amp-futures-september-2026/rules/",
    ),
    "capital-africa-sep-2026": CompetitionProfile(
        competition_id="capital-africa-sep-2026",
        name="The Leap by Capital.com Africa — September 2026",
        start_utc=datetime(2026, 9, 16, 8, 0, tzinfo=UTC),
        end_utc=datetime(2026, 10, 2, 8, 0, tzinfo=UTC),
        registration_close_utc=datetime(2026, 9, 23, 8, 0, tzinfo=UTC),
        initial_balance_usd=100_000.0,
        min_trading_days=3,
        first_prize_usd=3_000.0,
        max_transactions_per_minute_allowed=59,
        scoring_basis="realized_pnl_closed_positions",
        commission_rate=0.0001,
        leverage_by_asset_class={"forex": 25.0, "crypto": 1.0, "other": 10.0},
        max_open_position=CAPITAL_AFRICA_LIMITS,
        source_url="https://www.tradingview.com/the-leap/capitalcom-africa-september-2026/rules/?source=individual_landing_page",
    ),
}


def get_profile(competition_id: str) -> CompetitionProfile:
    try:
        return PROFILES[competition_id]
    except KeyError as exc:
        raise KeyError(f"Unknown competition profile: {competition_id}") from exc
