# STC Corrected Community Research — Full 26-Symbol Completion

Date: 2026-09-24  
Status: research evidence only — no live authority

## Completion

The corrected 20-component community matrix is now complete across all 26 competition symbols using the existing 5,000-bar exact-provider TradingView 15-minute research windows.

Evidence:
- corrected run: 35969652488 (17 completed symbols);
- retry run: 35987607069 (9/9 deferred symbols completed successfully);
- retry combined artifact: 10803236399;
- retry combined artifact digest: `sha256:dd7462c6cf70ad05c150f9acae5b981fa64f05133e4cbed017ba26bc05119798`.

## Final findings

- Native STC validated 15m strategies: **0/26**.
- Community profile-ready symbols: **13/26**.
- Official Lorentzian classification: **3/26** validated:
  - CAPITALCOM:USDZAR — robust score 44.3006;
  - CBOT:ZB1! — robust score 23.2508;
  - NYMEX:MCL1! — robust score 15.8644.
- VuManChu Cipher B: **0/26**.
- QQE + SSL + WAE composite: **0/26**.

These results reject the idea of one universal "best composite indicator". The evidence supports symbol-specific ensembles only.

## Capital.com 15m research profiles

| Symbol | Validated components and normalized research weights |
|---|---|
| BTCUSD | RSI Kernel Optimized 100.00% |
| DOGEUSD | Range Filter 60.06%; Schaff Trend Cycle 39.94% |
| ETHUSD | SSL Hybrid 100.00% |
| EURUSD | Trendilo 100.00% |
| NAS100 | HalfTrend 100.00% |
| USDZAR | Lorentzian 28.79%; Nadaraya-Watson endpoint 23.41%; AlphaTrend 17.88%; Supertrend 17.72%; UT Bot 12.19% |
| AUDUSD | No validated community component |
| SPX500 | No validated community component |
| XAGUSD | No validated community component |
| XAUUSD | No validated community component |

Capital profile-ready coverage is **6/10**.

## Live-integration gap

The live production feed currently emits nine generic evidence families, not the exact selected component states above. The runtime calibration registry also contains no promoted records.

Therefore the research weights above are **not** currently applied as live component weights. Mapping a component such as Trendilo to generic momentum, or HalfTrend to generic trend, would falsely claim that different algorithms are equivalent.

The correct next engineering step is:
1. carry exact selected component state into the live/shadow payload;
2. verify Pine/live parity against the Python research adapters;
3. accumulate shadow observations;
4. only then allow owner-controlled promotion of symbol/timeframe-specific weights.

No live risk, sizing, competition gate, approval, or execution authority is changed by this evidence package.
