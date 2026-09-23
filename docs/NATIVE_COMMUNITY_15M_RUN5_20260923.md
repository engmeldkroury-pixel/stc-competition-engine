# STC Native vs Community 15m Benchmark — Run 5

Date: 2026-09-23

GitHub Actions run: `35916027610` — 26/26 symbol jobs completed successfully and the combine job passed.

## Scope

- 26 competition symbols.
- 5,000 exact-symbol TradingView 15m bars per symbol.
- 14 implemented community research components per symbol.
- Native STC strategy matrix evaluated on the same symbol windows.
- Community parameters selected on TRAIN only and frozen for TEST/FORWARD.
- Research only; no A+ gate, risk rule, or live weight was changed.

## Main result

- Native STC 15m strategies that passed every strict robustness gate: **0**.
- Symbols with at least one validated community component: **10/26**.
- Symbols with no validated native or community component: **16/26**.
- This supports symbol-specific weighting and rejects the idea of one universal indicator stack.

## Community cross-symbol benchmark

| Indicator | Validated symbols | Rate | Avg robust score on validated trials |
|---|---:|---:|---:|
| ssl_hybrid | 4/26 | 15.4% | 32.80 |
| range_filter_guikroth | 4/26 | 15.4% | 30.91 |
| qqe_mod | 4/26 | 15.4% | 27.67 |
| schaff_trend_cycle | 4/26 | 15.4% | 20.61 |
| waddah_attar_explosion | 3/26 | 11.5% | 35.91 |
| ut_bot_alerts | 3/26 | 11.5% | 24.21 |
| chandelier_exit_everget | 2/26 | 7.7% | 46.99 |
| alphatrend | 2/26 | 7.7% | 22.62 |
| wavetrend_crosses | 1/26 | 3.8% | 30.26 |
| supertrend_kivanc | 1/26 | 3.8% | 27.62 |
| squeeze_momentum_lazybear | 1/26 | 3.8% | 14.53 |
| hull_suite | 0/26 | 0.0% | 0.00 |
| qqe_ssl_wae_composite | 0/26 | 0.0% | 0.00 |
| optimized_trend_tracker | 0/26 | 0.0% | 0.00 |

## Validated symbol profiles

### CAPITALCOM:DOGEUSD
- range_filter_guikroth: research weight 60.1%, robust score 23.23, test trades 24, forward trades 35.
- schaff_trend_cycle: research weight 39.9%, robust score 13.48, test trades 66, forward trades 72.

### CAPITALCOM:ETHUSD
- ssl_hybrid: research weight 100.0%, robust score 39.10, test trades 42, forward trades 27.

### CAPITALCOM:USDZAR
- alphatrend: research weight 37.4%, robust score 23.48, test trades 46, forward trades 45.
- supertrend_kivanc: research weight 37.1%, robust score 27.62, test trades 27, forward trades 28.
- ut_bot_alerts: research weight 25.5%, robust score 19.00, test trades 65, forward trades 67.

### CBOT:ZB1!
- range_filter_guikroth: research weight 25.7%, robust score 51.08, test trades 32, forward trades 24.
- chandelier_exit_everget: research weight 25.7%, robust score 51.05, test trades 42, forward trades 34.
- waddah_attar_explosion: research weight 20.3%, robust score 37.31, test trades 23, forward trades 20.
- qqe_mod: research weight 14.4%, robust score 23.63, test trades 52, forward trades 49.
- ssl_hybrid: research weight 13.8%, robust score 22.31, test trades 39, forward trades 36.

### CBOT:ZN1!
- schaff_trend_cycle: research weight 37.0%, robust score 22.94.
- alphatrend: research weight 35.6%, robust score 21.76.
- qqe_mod: research weight 27.3%, robust score 15.30.

### CME:MET1!
- waddah_attar_explosion: research weight 60.8%, robust score 45.01.
- ut_bot_alerts: research weight 39.2%, robust score 25.06.

### CME_MINI:MJY1!
- wavetrend_crosses: research weight 36.3%, robust score 30.26.
- schaff_trend_cycle: research weight 31.9%, robust score 25.53.
- waddah_attar_explosion: research weight 31.8%, robust score 25.39.

### COMEX_MINI:MGC1!
- qqe_mod: research weight 57.0%, robust score 30.12, test trades 39, forward trades 38.
- ssl_hybrid: research weight 43.0%, robust score 20.70.

### NYMEX:MCL1!
- ssl_hybrid: research weight 21.1%, robust score 49.10, test trades 23, forward trades 17.
- qqe_mod: research weight 18.7%, robust score 41.61, test trades 45, forward trades 42.
- chandelier_exit_everget: research weight 16.8%, robust score 42.93, test trades 50, forward trades 68.
- range_filter_guikroth: research weight 12.7%, robust score 25.03, test trades 47, forward trades 50.
- ut_bot_alerts: research weight 11.2%, robust score 28.56, test trades 53, forward trades 63.
- schaff_trend_cycle: research weight 11.0%, robust score 20.48, test trades 70, forward trades 64.
- squeeze_momentum_lazybear: research weight 8.5%, robust score 14.53, test trades 73, forward trades 84.

### NYMEX:MNG1!
- range_filter_guikroth: research weight 100.0%, robust score 24.30, test trades 44, forward trades 49.

## Zero-pass symbols

`CAPITALCOM:AUDUSD`, `CAPITALCOM:BTCUSD`, `CAPITALCOM:EURUSD`, `CAPITALCOM:NAS100`, `CAPITALCOM:SPX500`, `CAPITALCOM:XAGUSD`, `CAPITALCOM:XAUUSD`, `CBOT_MINI:MYM1!`, `CME:MBT1!`, `CME_MINI:M2K1!`, `CME_MINI:M6A1!`, `CME_MINI:M6B1!`, `CME_MINI:M6E1!`, `CME_MINI:MES1!`, `CME_MINI:MNQ1!`, `COMEX_MINI:SIL1!`

## Decision

- Keep all zero-pass components at zero research weight.
- Do not weaken native gates merely because no native 15m strategy passed.
- Continue expanding causal community candidates and deeper/multi-timeframe history.
- Keep research weights shadow-only until frozen confirmation and explicit promotion.
- Continue using redundancy-aware family normalization before any ensemble promotion.
