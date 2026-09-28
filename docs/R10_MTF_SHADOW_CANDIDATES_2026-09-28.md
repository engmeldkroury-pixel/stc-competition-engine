# R10 MTF shadow candidates - 28 September 2026

## Status
Research/shadow only. No live promotion, no broker action, no risk increase. The existing live strategy remains unchanged.

## Why R10 changed direction
Broad single-timeframe and asset-agnostic variants failed to show robust positive expectancy after costs. Asset-specific single-timeframe variants that looked positive on train/validation generally failed the untouched holdout. This is explicit anti-overfit evidence.

## Causal MTF test contract
- Source: TradingView official connector, exact CAPITALCOM symbols.
- Base entry timeframe: 15m.
- Higher-timeframe confirmation: only fully CLOSED 1h/4h bars were eligible at each 15m decision time.
- Candidate families: pullback, reclaim, momentum.
- Sessions: all / EU+US / US.
- Initial stops: 1.2 / 1.5 / 1.8 ATR.
- Targets: 1.5 / 2 / 2.5 R.
- Entry gap cap: 0.25 or 0.5 ATR.
- Cost proxy for selection: 2 bps round-trip price notional converted to R.
- Chronological split: first 60% train, next 20% validation, final 20% untouched historical holdout.
- Selection required positive train AND validation expectancy with PF >= 1.05. Holdout was not used for selection.
- Same-position blocking prevents overlapping entries inside one symbol while a modeled trade is active.
- Gaps through stops execute at bar open; same-bar stop/target ambiguity is conservative stop-first.
- This is historical simulation, not evidence of guaranteed future profit.

## Result across Capital competition symbols
Most symbols failed holdout or had no acceptable train+validation candidate. BTCUSD, NAS100, SPX500, XAUUSD, XAGUSD, USDZAR and the FX tests did not justify promotion.

Two candidates survived the historical holdout and were therefore frozen for forward SHADOW validation only:

### ETHUSD candidate
- family: pullback
- MTF: majority vote of 15m/1h/4h trend direction, using closed higher-timeframe bars only
- session: all
- initial stop: 1.5 ATR
- target: 1.5R
- max next-open gap: 0.25 ATR
- 2 bps split results:
  - train: n=26, mean +0.198R, PF 1.373
  - validation: n=7, mean +0.197R, PF 1.444
  - holdout: n=8, mean +0.840R, PF 4.245
- full-history stress at 2 bps:
  - 16 bars: n=46, mean +0.243R, PF 1.665
  - 32 bars: n=41, mean +0.323R, PF 1.698
  - 48 bars: n=40, mean +0.329R, PF 1.694
- 5 bps stress remained positive:
  - 16 bars +0.176R
  - 32 bars +0.255R
  - 48 bars +0.261R
- chronological 5-fold means at 2 bps / 32 bars: +0.141, +0.296, +0.022, +0.197, +0.840R.
- LIMITATION: only 8 untouched holdout trades; historical selection bias remains possible.

### DOGEUSD candidate
- family: pullback
- MTF: closed 1h direction
- session: 07:00-20:00 UTC
- initial stop: 1.2 ATR
- target: 2.5R
- max next-open gap: 0.25 ATR
- 2 bps split results:
  - train: n=41, mean +0.335R, PF 1.539
  - validation: n=13, mean +0.348R, PF 1.618
  - holdout: n=10, mean +0.249R, PF 1.400
- full-history stress at 2 bps:
  - 16 bars: n=65, mean +0.178R, PF 1.300
  - 32 bars: n=64, mean +0.324R, PF 1.532
  - 48 bars: n=64, mean +0.293R, PF 1.469
- 5 bps stress remained positive:
  - 16 bars +0.098R
  - 32 bars +0.244R
  - 48 bars +0.213R
- chronological 5-fold means at 2 bps / 32 bars: +0.511, -0.064, +0.491, +0.348, +0.249R.
- LIMITATION: one fold is slightly negative and only 10 untouched holdout trades.

## Promotion boundary
These candidates are NOT live strategies yet. They may enter forward-shadow observation only.
Do not raise risk, do not auto-execute, and do not retune on forward outcomes.
A later human review should require an independent forward sample large enough to be meaningful, realistic cost/slippage, and continued positive expectancy/PF without unacceptable drawdown before any live promotion is considered.

## Ongoing validation
An hourly condition-watch has been created to check new naturally frozen signals and forward-shadow evidence without retuning or auto-promotion. It notifies only on material evidence, failures, source-integrity problems, or when enough new independent evidence exists for review.
