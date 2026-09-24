# STC Native vs Community 15m Benchmark — 26 Symbols

Workflow run: 35916027610 — SUCCESS.

Scope: 26 competition symbols, 5,000 exact-provider TradingView 15m bars per symbol.

Important: this is research evidence only. It does not change the live A+ gate or authorize trades.

## Headline result

- Native STC strategies validated on 15m in this exact run: **0**.
- Symbols with at least one validated community component: **10/26**.
- Therefore the current native 15m strategy layer remains unvalidated, while some community components show symbol-specific OOS+forward evidence.

## Community leaderboard

| Indicator | Validated symbols | Rate | Avg validated robust score |
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

## Symbols with research profiles

- CAPITALCOM:DOGEUSD: top component **range_filter_guikroth**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- CAPITALCOM:ETHUSD: top component **ssl_hybrid**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- CAPITALCOM:USDZAR: top component **alphatrend**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- CBOT:ZB1!: top component **range_filter_guikroth**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- CBOT:ZN1!: top component **schaff_trend_cycle**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- CME:MET1!: top component **waddah_attar_explosion**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- CME_MINI:MJY1!: top component **wavetrend_crosses**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- COMEX_MINI:MGC1!: top component **qqe_mod**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- NYMEX:MCL1!: top component **ssl_hybrid**; community share 1.000; native status NO_VALIDATED_STRATEGY.
- NYMEX:MNG1!: top component **range_filter_guikroth**; community share 1.000; native status NO_VALIDATED_STRATEGY.

## Native result

Every native 15m strategy family in this run remained at zero validated symbols under the current robustness gates. This does not prove the concepts are useless; it means no native 15m trial met the existing OOS/forward acceptance standard on these same windows.

## Interpretation

- Keep weights symbol-specific and timeframe-specific.
- Zero-pass components receive zero deployable research weight.
- Community popularity/reviews never add score.
- Family redundancy normalization is required so several correlated trend/momentum components do not fake independent consensus.
- Further promotion requires frozen confirmation and then explicit live-authority approval.