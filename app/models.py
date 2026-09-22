from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Bar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @model_validator(mode="after")
    def validate_ohlc(self):
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be >= open, close, and low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be <= open, close, and high")
        return self


class TechnicalAnalysisRequest(BaseModel):
    symbol: str
    bars: list[Bar] = Field(min_length=60, max_length=5000)


class TechnicalAnalysisResult(BaseModel):
    symbol: str
    latest_close: float
    ema20: float
    ema50: float
    rsi14: float
    atr14: float
    macd: float
    macd_signal: float
    momentum_10: float
    technical_score: float
    regime: Literal["bullish", "bearish", "mixed"]


class HistoricalRegimeResult(BaseModel):
    symbol: str
    timeframe: Literal["1D"] = "1D"
    bars_used: int
    latest_close: float
    ema50: float
    ema200: float
    rsi14: float
    atr14: float
    high_252: float
    low_252: float
    momentum_20: float
    momentum_63: float
    momentum_126: float
    momentum_252: float
    volatility_20: float
    regime_score: float = Field(ge=-1.0, le=1.0)
    regime: Literal["bullish", "bearish", "mixed"]


class FactorScores(BaseModel):
    technical: float = Field(ge=-1.0, le=1.0)
    news: float = Field(default=0.0, ge=-1.0, le=1.0)
    macro: float = Field(default=0.0, ge=-1.0, le=1.0)
    volatility_quality: float = Field(default=0.0, ge=-1.0, le=1.0)
    liquidity_quality: float = Field(default=0.0, ge=-1.0, le=1.0)


class SignalEvaluationRequest(BaseModel):
    competition_id: str
    symbol: str
    factors: FactorScores


class SignalEvaluationResult(BaseModel):
    signal_id: str
    competition_id: str
    symbol: str
    composite_score: float
    recommendation: Literal["LONG", "SHORT", "WAIT"]
    confidence: float
    requires_human_approval: bool = True
    reasons: list[str]


class OrderValidationRequest(BaseModel):
    competition_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    requested_quantity: float = Field(gt=0)
    current_open_quantity: float = Field(default=0.0, ge=0)
    transactions_last_60s: int = Field(default=0, ge=0)
    account_equity: float = Field(gt=0)
    risk_amount: float = Field(default=0.0, ge=0)
    max_risk_fraction: float = Field(default=0.02, gt=0, le=1)


class OrderValidationResult(BaseModel):
    allowed: bool
    reasons: list[str]
    max_position: float | None
    projected_position: float
    rate_limit_remaining: int
    requires_human_approval: bool = True


class CompetitionEligibilityRequest(BaseModel):
    competition_id: str
    qualifying_trading_days: int = Field(ge=0)
    realized_pnl: float
    unrealized_pnl: float = 0.0


class CompetitionEligibilityResult(BaseModel):
    eligible_by_days: bool
    days_remaining: int
    competition_score: float
    note: str


class ProviderMappingCheckRequest(BaseModel):
    requested_symbol: str
    candidate_symbol: str
    allow_cross_provider: bool = False


class TradingViewWebhook(BaseModel):
    event_id: str | None = None
    event: str = "bar_close"
    competition_id: str
    symbol: str
    timeframe: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    ema20: float
    ema50: float
    rsi14: float
    atr14: float
    macd: float
    macd_signal: float
    volume_ratio: float = 1.0
    confirm_timeframe: str | None = None
    confirm_time: datetime | None = None
    confirm_close: float | None = None
    confirm_ema20: float | None = None
    confirm_ema50: float | None = None
    confirm_ema200: float | None = None
    confirm_rsi14: float | None = None
    confirm_atr14: float | None = None
    confirm_macd: float | None = None
    confirm_macd_signal: float | None = None
    confirm_volume_ratio: float | None = None
    history_timeframe: str | None = None
    history_time: datetime | None = None
    history_close: float | None = None
    history_ema50: float | None = None
    history_ema200: float | None = None
    history_rsi14: float | None = None
    history_atr14: float | None = None
    history_high_252: float | None = None
    history_low_252: float | None = None
    history_momentum_20: float | None = None
    history_momentum_63: float | None = None
    history_momentum_126: float | None = None
    history_momentum_252: float | None = None
    history_volatility_20: float | None = None

    @model_validator(mode="after")
    def validate_confirmation_context(self):
        names = (
            "confirm_timeframe",
            "confirm_time",
            "confirm_close",
            "confirm_ema20",
            "confirm_ema50",
            "confirm_ema200",
            "confirm_rsi14",
            "confirm_atr14",
            "confirm_macd",
            "confirm_macd_signal",
            "confirm_volume_ratio",
        )
        values = [getattr(self, name) for name in names]
        present = [value is not None for value in values]
        if any(present) and not all(present):
            raise ValueError("confirmation context must be complete or absent")
        if all(present):
            if str(self.confirm_timeframe).lower() not in {"60", "1h"}:
                raise ValueError("confirmation context timeframe must be 60/1h")
            if not 0 <= self.confirm_rsi14 <= 100:
                raise ValueError("confirm_rsi14 must be between 0 and 100")
            if self.confirm_atr14 < 0 or self.confirm_volume_ratio < 0:
                raise ValueError("confirmation quality values must be non-negative")
        return self

    @model_validator(mode="after")
    def validate_history_context(self):
        names = (
            "history_timeframe",
            "history_time",
            "history_close",
            "history_ema50",
            "history_ema200",
            "history_rsi14",
            "history_atr14",
            "history_high_252",
            "history_low_252",
            "history_momentum_20",
            "history_momentum_63",
            "history_momentum_126",
            "history_momentum_252",
            "history_volatility_20",
        )
        values = [getattr(self, name) for name in names]
        present = [value is not None for value in values]
        if any(present) and not all(present):
            raise ValueError("historical context must be complete or absent")
        if all(present):
            if self.history_timeframe != "1D":
                raise ValueError("historical context timeframe must be 1D")
            if self.history_high_252 < self.history_low_252:
                raise ValueError("history_high_252 must be >= history_low_252")
            if not self.history_low_252 <= self.history_close <= self.history_high_252:
                raise ValueError("history_close must be within the 252-day range")
            if not 0 <= self.history_rsi14 <= 100:
                raise ValueError("history_rsi14 must be between 0 and 100")
            if self.history_atr14 < 0 or self.history_volatility_20 < 0:
                raise ValueError("historical volatility values must be non-negative")
        return self


class TradeEvent(BaseModel):
    competition_id: str
    symbol: str
    event: Literal["OPEN", "CLOSE"]
    side: Literal["LONG", "SHORT"]
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    event_time: datetime
    trade_id: str | None = None
    realized_pnl_delta: float = 0.0


class TradeEventResult(BaseModel):
    trade_id: str
    recorded: bool
    status: Literal["OPEN", "CLOSED"]
    competition_id: str
    symbol: str
    realized_pnl_total: float
    qualifying_trading_days: int

class ExecutionEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=8, max_length=128)
    source: Literal["tradingview_mcp_direct_quote", "owner_platform_confirmation", "broker_session_status"]
    competition_id: str | None = None
    symbol: str
    provider: str
    observed_at_utc: datetime
    quote_price: float | None = Field(default=None, gt=0)
    update_mode: str | None = None
    market_status: Literal["open", "closed", "unknown"] = "unknown"
    details: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_observed_at_timezone(self):
        if self.observed_at_utc.tzinfo is None:
            raise ValueError("observed_at_utc must include timezone information")
        return self


class ApprovalRevalidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_signal_score: float = Field(ge=-1.0, le=1.0)
    current_market_state_hash: str
    current_rule_version: str = "stc-rule-v1"
    news_block: bool = False
    volatility_ratio: float = Field(default=1.0, gt=0)
    quote_evidence_id: str = Field(min_length=8, max_length=128)
    market_evidence_id: str = Field(min_length=8, max_length=128)
    kill_switch: bool = False
    safe_mode: bool = False
