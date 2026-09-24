# STC Reconciled Wave-3 Native vs Community 15m Benchmark

Date: 2026-09-24

## Evidence source
- GitHub Actions run: 35964596933
- Source commit: 8edb3edef2c26e6348e989d5b95632f50b803327
- Scope: 26 competition symbols
- History: 5,000 exact-provider TradingView 15m bars per symbol
- Community components: 18
- Native STC strategies: same symbol/timeframe windows
- Parameter choice: TRAIN only; TEST and FORWARD untouched
- Ensemble: redundancy-aware family normalization

## Result
- Native STC strategies validated on 15m: **0/26 symbols**.
- Community research profile ready: **13/26 symbols**.
- Prior verified 14-component benchmark: **10/26** profile-ready.
- Incremental coverage from the reconciled wave-3 pool: **+3 symbols**:
  - CAPITALCOM:BTCUSD — top component: RSI Kernel Optimized (causally delayed).
  - CAPITALCOM:EURUSD — top component: Trendilo.
  - CAPITALCOM:NAS100 — top component: HalfTrend.

## New/reconciled component evidence
- HalfTrend: 2/26 validated — NAS100 and ZB1!.
- Trendilo: 2/26 validated — EURUSD and MJY1!.
- Endpoint Nadaraya-Watson non-repaint: 1/26 validated — USDZAR.
- RSI Kernel Optimized with delayed pivot confirmation: 1/26 validated — BTCUSD.

## Cross-symbol leaderboard
| Component | Validated / 26 | Avg robust score on validated symbols |
|---|---:|---:|
| SSL Hybrid | 4 | 32.80 |
| Range Filter | 4 | 30.91 |
| QQE MOD | 4 | 27.67 |
| Schaff Trend Cycle | 4 | 20.61 |
| Waddah Attar Explosion | 3 | 35.91 |
| UT Bot | 3 | 24.21 |
| Chandelier Exit | 2 | 46.99 |
| HalfTrend | 2 | 31.64 |
| AlphaTrend | 2 | 22.62 |
| Trendilo | 2 | 19.59 |
| Endpoint Nadaraya-Watson non-repaint | 1 | 33.62 |
| WaveTrend | 1 | 30.26 |
| RSI Kernel Optimized | 1 | 28.60 |
| SuperTrend | 1 | 27.62 |
| Squeeze Momentum | 1 | 14.53 |
| Hull Suite | 0 | 0 |
| QQE+SSL+WAE composite | 0 | 0 |
| Optimized Trend Tracker | 0 | 0 |

## Control interpretation
- No component receives live authority from this benchmark.
- Failed OOS/FORWARD components retain zero deployable research weight on that symbol/timeframe.
- The results reinforce symbol-specific weighting: the same component does not generalize uniformly across the 26-symbol universe.
- This run started before PR #125 merged, so **official Lorentzian Classification is not included**. Lorentzian requires a fresh exact-data run.
