# Community Pine Parity Reference — 2026-09-24

The authoritative Python reference streams were generated from the same staged exact-provider TradingView 15-minute datasets used by the corrected community benchmark.

- Workflow run: 35992849854
- Research head: `dc40a5d530609156d17b64e5c2fc637c52f21f19`
- Combined artifact: 10804853153
- Artifact digest: `sha256:e0357abc68949b88d5554e636cb376f70c004bac7fb8e4da213cb1a33c67cce7`
- Each dataset contains 5,000 bars.
- The fixture builder remains reproducible on branch `research/native-community-15m-20260923`.
- These fixtures have no live authority.

| Symbol | Component | Reference events |
|---|---|---:|
| BTCUSD | RSI Kernel Optimized | 252 |
| DOGEUSD | Range Filter | 149 |
| DOGEUSD | Schaff Trend Cycle | 609 |
| ETHUSD | SSL Hybrid | 210 |
| EURUSD | Trendilo | 225 |
| NAS100 | HalfTrend | 133 |
| USDZAR | Lorentzian Classification | 47 |
| USDZAR | Nadaraya-Watson endpoint | 76 |
| USDZAR | AlphaTrend | 363 |
| USDZAR | Supertrend | 142 |
| USDZAR | UT Bot | 383 |

## Promotion gate

A Pine implementation is not accepted because it has the same indicator name or parameters. For each selected symbol/component it must reproduce the Python reference event timestamps and values on the frozen dataset, subject only to an explicitly documented and independently reviewed parity tolerance.

Until that check passes:
- `community_component_shadow.live_authority=false`;
- community weights do not enter setup quality;
- community weights do not enter risk, sizing or approval;
- the existing live competition gate remains authoritative.
