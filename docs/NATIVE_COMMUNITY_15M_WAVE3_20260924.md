# STC Reconciled Wave 3 Community Benchmark — 26 Symbols

Workflow run: 35964596933 — SUCCESS.

Scope: 26 competition symbols × 5,000 exact-provider TradingView 15m bars.

This run was generated after PR #124 repaired the frozen HalfTrend / Trendilo / Nadaraya component contracts. Any earlier Wave-3 benchmark is superseded.

## Headline

- Research-ready community profiles: **13/26** (prior baseline: 10/26).
- Incremental profile symbols: **CAPITALCOM:BTCUSD, CAPITALCOM:EURUSD, CAPITALCOM:NAS100**.
- Lost profile symbols vs prior baseline: **none**.
- Native STC 15m strategies remained at 0 validated symbols under the existing robustness gates.

## Cross-symbol validated community counts

| Component | Validated | Rate | Avg robust score |
|---|---:|---:|---:|
| ssl_hybrid | 4/26 | 15.4% | 32.80 |
| range_filter_guikroth | 4/26 | 15.4% | 30.91 |
| qqe_mod | 4/26 | 15.4% | 27.67 |
| schaff_trend_cycle | 4/26 | 15.4% | 20.61 |
| waddah_attar_explosion | 3/26 | 11.5% | 35.91 |
| ut_bot_alerts | 3/26 | 11.5% | 24.21 |
| chandelier_exit_everget | 2/26 | 7.7% | 46.99 |
| halftrend_everget | 2/26 | 7.7% | 31.64 |
| alphatrend | 2/26 | 7.7% | 22.62 |
| trendilo | 2/26 | 7.7% | 19.59 |
| nadaraya_watson_endpoint_nonrepaint | 1/26 | 3.8% | 33.62 |
| wavetrend_crosses | 1/26 | 3.8% | 30.26 |
| rsi_kernel_optimized_flux | 1/26 | 3.8% | 28.60 |
| supertrend_kivanc | 1/26 | 3.8% | 27.62 |
| squeeze_momentum_lazybear | 1/26 | 3.8% | 14.53 |
| hull_suite | 0/26 | 0.0% | 0.00 |
| qqe_ssl_wae_composite | 0/26 | 0.0% | 0.00 |
| optimized_trend_tracker | 0/26 | 0.0% | 0.00 |

## New Wave-3 components
- halftrend_everget: 2/26 validated; avg validated score 31.64.
- trendilo: 2/26 validated; avg validated score 19.59.
- nadaraya_watson_endpoint_nonrepaint: 1/26 validated; avg validated score 33.62.
- rsi_kernel_optimized_flux: 1/26 validated; avg validated score 28.60.

## Boundary
- Research only; no live A+ or risk change.
- These are development OOS/forward results, not final frozen confirmation.
- New survivors must pass the untouched final holdout before SHADOW eligibility.