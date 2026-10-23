# STC Crypto Spot 16 — Pre-Registered Multi-Timeframe Strategy Research V2
Version: 2.0.0 | 2026-10-15 | SOURCE LOCK BEFORE NEW DATA | RESEARCH + MANUAL PAPER PREPARATION ONLY

## Owner hard limits
- Exactly original 16 pairs: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, ADAUSDT, AVAXUSDT, TRBUSDT, GALAUSDT, YGGUSDT, NOTUSDT, NEOUSDT, OPUSDT, ARBUSDT, SUIUSDT, INJUSDT; primary seven research order BTC, ETH, SOL, TRB, GALA, YGG, NOT.
- Binance public SPOT market data research only, exact pair source and status; no exchange account connection or inference of owner exchange/fees. Do not substitute other venues silently.
- Long-only cash spot (BUY then SELL owned quantity). Futures=false; leverage=false; short=false; real-money authorization=false; orders to Binance/TradingView API=false. No email or old contest notifications; manual owner only when and if a candidate truly passes independent promotion and owner approves.
- Competition preparation is a DIFFERENT rules- and calendar-specific module: no strategy or past contest account automatically carried to the next TradingView event, and no automatic registration/trades.

## Source acquisition, integrity, and eligibility
- Fetch Binance /api/v3/exchangeInfo (exact SPOT permission + TRADING symbol) and public /api/v3/klines; never create API key or POST.
- Required 15m, 1h, 4h, 1d closed series. For time-depth, up to 4,000 most recent fully closed 15m; 1,000 fully closed 1h/4h/1d, with timestamps and volume preserved. Min 900 closed bars each required, else pair STATUS DATA_INSUFFICIENT / NO SIGNAL. Close time must precede independent UTC clock at download and each open time must agree with configured interval. No forward-filled gaps, silent pair mapping, synthetic closes, nonfinite prices or duplicate timestamps.
- Keep raw cached market data immutable with SHA256 and source retrieval metadata. Distinguish exchange suspension from missing candles. Signal uses prior completed bars only, and all higher-timeframe filters are AS-OF LAST CLOSED high-timeframe bar, never future value.
- Avoid trading/paper entry on symbol not verified as TRADING Spot with required filters. Even TRADING today does not prove symbol available on owner's future chosen exchange.
- Existing last 1d NOTUSDT archive lacked min 900 bars as of Oct13; if still short do NOT waive this gate.

## Exactly three locked, LONG-ONLY research hypotheses (no parameter search)
A. MTF_TREND_PULLBACK: 1d EMA50 > EMA200 and last daily close > EMA200; 4h EMA20 > EMA50 and close > EMA50; 1h close > EMA50, ADX14 >= 18; closed 15m candle tagged EMA20, closes back above EMA20 but no more than 0.8 ATR14 above; candle green and volume > median of prior 20 volumes.
B. MTF_BOUNDED_BREAKOUT: same daily + 4h bullish rules; 1h close > EMA20 and ADX14 >= 18; 15m close crosses above previous 20 highs, volume >= 1.2 x median prior 20 volumes, close no more than 1.5 ATR14 beyond 15m EMA20.
C. MTF_RANGE_RECOVERY: daily close > EMA200, 4h close > EMA50; 1h ADX14 <= 18; previous 15m close below previous lower Bollinger(20,2), current candle closes back inside lower band, RSI14 <48, 15m candle green; volume > prior20 median.
D. WAIT/NO TRADE baseline.
No bearish short or leverage variant. No per-pair profitability cherry-picking. Do not promote on lucky low-trade series.

## Fixed execution simulation
- Historical signal ONLY at 15m fully closed candle; simulated entry at immediate next 15m OPEN (not live claim); one open per pair/family at a time, no shortcut for absence of user/manual fill confirmation.
- Initial stop = entry minus 1.8 * ATR14(15m) as observed at signal bar; target = entry plus 2.0 R (except range 1.5 R). Never widen the stop or average down. Maximum 48 future 15m candles (12h) or censor when gap appears; intrabar TP/SL collision = SL first. Trading may be skipped entirely.
- Round-trip cost/slippage stress per side 5/15/30 basis points of entry and exit prices as hypothetical total friction (unknown owner venue fee/tier). Paper sizing proposal: max 0.5% of hypothetical account equity at risk, max 5% notional per individual trade, aggregate concurrent worst-case risk <=2% of equity; no BTC-correlated independent trades assumed.
- Research train first 60%, embargo 48 x 15m, retrospective historic test remaining 40% (not untouched prospective); minimum 900 closed source bars each TF. Count first time historical trade sample and report how often ZERO trades or non-positive expected outcome.
- Entry after owner 5/10/15m delay requires NEW market quote and original immutable TTL; new order may not be approved from 15m OHLC alone. Freshness, actual fills, protective orders and liquidity must be verified separately.

## Promotion/production gates
- Code and data quality + independent deterministic QA; net positive credible expectancy and drawdown (not merely one good symbol) across market regimes and fees; train vs walk-forward plus true FUTURE, untouched forward evidence; owner's real Paper Trading execution fill/stop confirmations, delayed entry experiments; next competition rule eligibility and score handled independently.
- A strategy that fails ANY gate is RESEARCH/HOLD or REJECT, not approved for Telegram actionable trading or real orders.
- This project may implement validators/simulator/paper-only report generator now without enabling Hostinger production signal issuance, notifier or exchange writes. Existing 60-second Hostinger scheduler must remain read-only and stable.