# STC v1.1 MTF Production Activation

Purpose: restore the live A+ gate inputs that are currently missing from the active legacy production alerts.

## Why this is required
The active production alerts currently deliver the 26 competition symbols, but the live decision cards show:
- confirmation_1h=unavailable
- trend_2h=unavailable
- trend_4h=unavailable
- trend_1m=unavailable
- family_evidence=unavailable

The A+ gate correctly fails closed when those required confirmations are missing. Do not weaken the gate to compensate.

## Keep legacy production alerts running during parallel acceptance
Do NOT stop these until all six v1.1 feeds pass one full parallel cycle with HTTP 200 and correct symbol counts:
- 5662088915 — STC CAPITAL 10-SYMBOL 15m PROD v0.7.1
- 5664752419 — STC AMP A 8-SYMBOL 15m PROD v0.3 FIX
- 5664684004 — STC AMP B 8-SYMBOL 15m PROD v0.3

## Create these six fresh TradingView indicator alerts

### Capital A
- Pine file: tradingview/STC_CAPITAL_MTF_FEED_A.pine
- Indicator: STC Capital MTF Feed A v1.1 Family Breadth
- Scheduler chart: CAPITALCOM:BTCUSD
- Chart timeframe: 15m
- Alert condition: Any alert() function call
- Suggested alert name: STC CAPITAL MTF A v1.1 PROD
- Symbols emitted:
  - CAPITALCOM:BTCUSD
  - CAPITALCOM:ETHUSD
  - CAPITALCOM:DOGEUSD
  - CAPITALCOM:EURUSD
  - CAPITALCOM:AUDUSD

### Capital B
- Pine file: tradingview/STC_CAPITAL_MTF_FEED_B.pine
- Indicator: STC Capital MTF Feed B v1.1 Family Breadth
- Scheduler chart: CAPITALCOM:BTCUSD
- Chart timeframe: 15m
- Alert condition: Any alert() function call
- Suggested alert name: STC CAPITAL MTF B v1.1 PROD
- Symbols emitted:
  - CAPITALCOM:USDZAR
  - CAPITALCOM:XAUUSD
  - CAPITALCOM:XAGUSD
  - CAPITALCOM:SPX500
  - CAPITALCOM:NAS100

### AMP A
- Pine file: tradingview/STC_AMP_MTF_FEED_A.pine
- Indicator: STC AMP MTF Feed A v1.1 Family Breadth
- Scheduler chart: CME_MINI:MES1!
- Chart timeframe: 15m
- Alert condition: Any alert() function call
- Suggested alert name: STC AMP MTF A v1.1 PROD
- Symbols emitted:
  - CME_MINI:MES1!
  - CME_MINI:MNQ1!
  - CBOT_MINI:MYM1!
  - CME_MINI:M2K1!

### AMP B
- Pine file: tradingview/STC_AMP_MTF_FEED_B.pine
- Indicator: STC AMP MTF Feed B v1.1 Family Breadth
- Scheduler chart: CME_MINI:MES1!
- Chart timeframe: 15m
- Alert condition: Any alert() function call
- Suggested alert name: STC AMP MTF B v1.1 PROD
- Symbols emitted:
  - NYMEX:MCL1!
  - NYMEX:MNG1!
  - COMEX_MINI:MGC1!
  - COMEX_MINI:SIL1!

### AMP C
- Pine file: tradingview/STC_AMP_MTF_FEED_C.pine
- Indicator: STC AMP MTF Feed C v1.1 Family Breadth
- Scheduler chart: CME_MINI:MES1!
- Chart timeframe: 15m
- Alert condition: Any alert() function call
- Suggested alert name: STC AMP MTF C v1.1 PROD
- Symbols emitted:
  - CME_MINI:M6E1!
  - CME_MINI:M6B1!
  - CME_MINI:MJY1!
  - CME_MINI:M6A1!

### AMP D
- Pine file: tradingview/STC_AMP_MTF_FEED_D.pine
- Indicator: STC AMP MTF Feed D v1.1 Family Breadth
- Scheduler chart: CME_MINI:MES1!
- Chart timeframe: 15m
- Alert condition: Any alert() function call
- Suggested alert name: STC AMP MTF D v1.1 PROD
- Symbols emitted:
  - CME:MBT1!
  - CME:MET1!
  - CBOT:ZN1!
  - CBOT:ZB1!

## Alert settings
For each alert:
- use the existing STC webhook URL already used by the verified production alerts;
- Webhook only is sufficient;
- mobile push/popup can remain off;
- do not enable automatic broker execution;
- do not disable Safe Mode or Kill Switch;
- do not paste tokens or webhook secrets into chat.

## Acceptance test
After all six alerts are created:
1. Keep old production alerts active.
2. Wait for one confirmed 15m cycle.
3. Verify:
   - Capital A emits exactly 5 events.
   - Capital B emits exactly 5 events.
   - AMP A emits exactly 4 events.
   - AMP B emits exactly 4 events.
   - AMP C emits exactly 4 events.
   - AMP D emits exactly 4 events.
   - every webhook delivery returns HTTP 200.
   - no alert self-stops or reports study_error.
   - the Hostinger snapshot no longer reports missing 1h/2h/4h/family evidence on fresh cards.
4. Only after acceptance may legacy alert retirement be considered.

## Execution boundary
Even after v1.1 acceptance:
- A card becomes actionable only if the existing A+ quality gate passes and a locked plan exists.
- Human approval remains mandatory.
- Order entry remains manual.
- Safe Mode/Kill Switch stay enabled until owner intentionally changes them.
