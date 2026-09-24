# STC Community Indicator 15m Benchmark — 26 Symbols

Date: 2026-09-23

Scope: 10 Capital.com Africa symbols + 16 AMP Futures symbols; 5,000 exact-provider TradingView 15m bars per symbol.

Method: parameters selected on the first 60% only; frozen for 20% test and 20% forward. Entry is next-bar open. Stop = 1.5 ATR, target = 2R, max hold = 16 bars, round-trip cost = 0.04R, and same-bar stop/target assumes stop first.

A validation pass requires minimum sample sizes, positive OOS and forward expectancy, minimum profit factors, controlled drawdown, and no severe forward degradation.

## Cross-symbol leaderboard

| Rank | Indicator | Validated symbols | Validation rate | Avg robust score* | Avg test exp R* | Avg forward exp R* |
|---:|---|---:|---:|---:|---:|---:|
| 1 | range_filter_guikroth | 4/26 | 15.4% | 30.54 | 0.212 | 0.223 |
| 2 | ut_bot_alerts | 3/26 | 11.5% | 24.17 | 0.089 | 0.170 |
| 3 | schaff_trend_cycle | 3/26 | 11.5% | 22.96 | 0.097 | 0.173 |
| 4 | chandelier_exit_everget | 2/26 | 7.7% | 46.99 | 0.367 | 0.339 |
| 5 | wavetrend_crosses | 2/26 | 7.7% | 23.00 | 0.106 | 0.134 |
| 6 | supertrend_kivanc | 1/26 | 3.8% | 27.62 | 0.173 | 0.150 |
| 7 | squeeze_momentum_lazybear | 1/26 | 3.8% | 14.47 | 0.119 | 0.053 |
| 8 | hull_suite | 0/26 | 0.0% | 0.00 | 0.000 | 0.000 |

\* Averages are over validated symbol/timeframe trials only; zero-pass trials are not hidden in the JSON.

## Per-symbol validated leaders

### CAPITALCOM:BTCUSD
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:ETHUSD
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:DOGEUSD
- range_filter_guikroth: score 21.86, test expectancy 0.201R, forward expectancy 0.128R, test PF 1.44, forward PF 1.22.

### CAPITALCOM:EURUSD
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:AUDUSD
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:USDZAR
- supertrend_kivanc: score 27.62, test expectancy 0.173R, forward expectancy 0.150R, test PF 1.43, forward PF 1.34.
- ut_bot_alerts: score 19.02, test expectancy 0.064R, forward expectancy 0.107R, test PF 1.13, forward PF 1.21.
- wavetrend_crosses: score 15.75, test expectancy 0.058R, forward expectancy 0.020R, test PF 1.14, forward PF 1.05.

### CAPITALCOM:XAUUSD
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:XAGUSD
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:SPX500
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CAPITALCOM:NAS100
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME_MINI:MES1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME_MINI:MNQ1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CBOT_MINI:MYM1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME_MINI:M2K1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### NYMEX:MCL1!
- chandelier_exit_everget: score 42.93, test expectancy 0.411R, forward expectancy 0.179R, test PF 2.14, forward PF 1.45.
- ut_bot_alerts: score 28.32, test expectancy 0.119R, forward expectancy 0.192R, test PF 1.25, forward PF 1.42.
- range_filter_guikroth: score 24.93, test expectancy 0.160R, forward expectancy 0.135R, test PF 1.33, forward PF 1.27.
- schaff_trend_cycle: score 20.41, test expectancy 0.133R, forward expectancy 0.114R, test PF 1.30, forward PF 1.24.

### NYMEX:MNG1!
- range_filter_guikroth: score 24.30, test expectancy 0.107R, forward expectancy 0.154R, test PF 1.21, forward PF 1.32.

### COMEX_MINI:MGC1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### COMEX_MINI:SIL1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME_MINI:M6E1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME_MINI:M6B1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME_MINI:MJY1!
- wavetrend_crosses: score 30.26, test expectancy 0.154R, forward expectancy 0.247R, test PF 1.33, forward PF 1.61.
- schaff_trend_cycle: score 25.53, test expectancy 0.107R, forward expectancy 0.274R, test PF 1.20, forward PF 1.56.

### CME_MINI:M6A1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME:MBT1!
- No community indicator passed the full 15m OOS+forward validation gate in this run.

### CME:MET1!
- ut_bot_alerts: score 25.17, test expectancy 0.083R, forward expectancy 0.210R, test PF 1.16, forward PF 1.39.

### CBOT:ZN1!
- schaff_trend_cycle: score 22.94, test expectancy 0.052R, forward expectancy 0.129R, test PF 1.13, forward PF 1.30.

### CBOT:ZB1!
- range_filter_guikroth: score 51.08, test expectancy 0.380R, forward expectancy 0.474R, test PF 1.94, forward PF 2.22.
- chandelier_exit_everget: score 51.05, test expectancy 0.323R, forward expectancy 0.499R, test PF 1.77, forward PF 2.15.

## Interpretation boundary

- This is research evidence, not a live trade instruction.
- A popular indicator that failed OOS/forward validation gets zero research weight for that symbol/timeframe.
- A strong indicator on one symbol does not inherit weight on another symbol.
- Community results remain shadow/research-only until frozen confirmation and explicit promotion.