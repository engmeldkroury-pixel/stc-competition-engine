# STC Trendilo Multi-Timeframe Frozen Confirmation — Run 1

Date: 2026-09-24  
Workflow run: 35947248551  
Status: SUCCESS

## Scope

The two wave-two 15m Trendilo frozen survivors were tested on independent exact-provider timeframes:

- CAPITALCOM:BTCUSD
- CME_MINI:MJY1!

Timeframes:
- 5m
- 30m
- 1h
- 2h derived only from exact 1h
- 4h
- 1D

The same exact frozen method was retained. Insufficient history fails closed.

## Main result

### CME_MINI:MJY1! — Trendilo is now MULTITF_CONFIRMED

The same Trendilo component independently passed final frozen confirmation on:

- 15m — prior wave-two survivor.
- 5m — new same-component support.
- 30m — new same-component support.

5m Trendilo:
- TEST: 29 trades, expectancy 0.225R, PF 1.39.
- FORWARD: 27 trades, expectancy 0.255R, PF 1.51.
- Frozen: 25 trades, expectancy 0.244R, PF 1.43, DD 3.84R.

30m Trendilo:
- TEST: 22 trades, expectancy 0.250R, PF 1.50.
- FORWARD: 23 trades, expectancy 0.238R, PF 1.41.
- Frozen: 18 trades, expectancy 0.162R, PF 1.27, DD 4.16R.

This advances the MJY Trendilo research records to MULTITF_CONFIRMED. It does **not** grant live authority.

### CAPITALCOM:BTCUSD — Trendilo remains SHADOW

BTCUSD Trendilo did not independently pass another tested timeframe.

Two different components did pass:

- 5m — endpoint Nadaraya-Watson non-repainting.
- 1D — Hull Suite.

These are new independent SHADOW candidates. They are not supporting Trendilo evidence.

BTCUSD 5m endpoint Nadaraya-Watson:
- TEST: 21 trades, expectancy 0.303R, PF 1.61.
- FORWARD: 17 trades, expectancy 0.234R, PF 1.47.
- Frozen: 15 trades, expectancy 0.426R, PF 2.02, DD 2.08R.

BTCUSD 1D Hull:
- TEST: 74 trades, expectancy 0.103R, PF 1.21.
- FORWARD: 75 trades, expectancy 0.265R, PF 1.58.
- Frozen: 64 trades, expectancy 0.151R, PF 1.33, DD 11.16R.

## Additional reconfirmation

MJY 5m Squeeze Momentum passed again:
- TEST: 109 trades, expectancy 0.094R, PF 1.16.
- FORWARD: 105 trades, expectancy 0.390R, PF 1.81.
- Frozen: 97 trades, expectancy 0.238R, PF 1.45, DD 5.65R.

It was already a SHADOW candidate and remains research-only.

## Registry update

After this run:
- total research registry records: 16;
- MJY Trendilo 15m/5m/30m: MULTITF_CONFIRMED;
- BTCUSD Trendilo 15m: SHADOW;
- BTCUSD 5m endpoint Nadaraya-Watson: SHADOW;
- BTCUSD 1D Hull: SHADOW;
- live_authority=false for every record.

## Authority boundary

No live A+ threshold, risk control, competition rule, or broker execution path changed.

MULTITF_CONFIRMED is still a research state. The next promotion condition requires sufficient positive shadow observations under the formal registry rules.
