# NEXT TASK

Updated: 2026-09-23 23:15 EEST

## CONTROLLING PROJECT
STC — do not rename to CC/SCC in project state.

## PRIMARY OBJECTIVE
Finish the reproducible native-vs-community 15m benchmark for all 26 competition symbols on identical exact-provider TradingView history, then merge verified evidence and continue the indicator-expansion + General Lab automation roadmap.

Authoritative research ledger:
- docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md

## VERIFIED COMPLETED
- PR #101 adaptive community research foundation merged; CI 347 passed.
- PR #102 expanded indicator catalog + four extra causal adapters + train-only parameter selection merged; CI 351 passed.
- Community-only 15m benchmark completed for 26/26 competition symbols on 5,000 exact-provider bars each.
- 208 symbol-indicator community trials completed.
- 8/26 symbols had at least one community family pass OOS+forward validation.
- Research remains shadow-only: community_indicator_live_authority=false.

## ACTIVE WORK UNIT
Branch:
- research/native-community-15m-20260923

Controlling workflow:
- STC Native + Community 15m Benchmark run #5
- 26 exact-provider 15m datasets staged
- latest 14 implemented community components + native STC strategies

Already created:
- scripts/run_native_community_15m.py
- .github/workflows/stc-native-community-15m.yml

Required completion:
1. stage 15m exact TradingView OHLCV for all 26 symbols;
2. add research_native_inputs/READY to trigger workflow;
3. run native STC strategies and implemented community indicators on the same windows;
4. build per-symbol ensemble profiles;
5. compare native/community robust scores and weight shares;
6. retain zero weight for failed OOS/forward components;
7. merge verified result artifacts to main.

## COMPLETED SINCE LAST CHECKPOINT
- PR #103: General Lab research plan/evaluate endpoints + discovery wave 2 + AlphaTrend/OTT + family redundancy normalization.
- PR #104: archived first 26-symbol community benchmark evidence.
- PR #105: QQE MOD + SSL Hybrid + WAE + QQE/SSL/WAE composite adapters; CI 359 passed.

## CONTINUING RESEARCH ROADMAP
After WU-104:
1. add family-correlation/diversity penalty before any live ensemble promotion;
2. exact/repaint-safe ports in priority order:
   - Lorentzian Classification;
   - QQE MOD;
   - Optimized Trend Tracker;
   - HalfTrend;
   - SSL Hybrid;
   - AlphaTrend;
   - VuManChu Cipher B;
   - Trendilo;
   - Nadaraya-Watson non-repainting mode;
3. audit LuxAlgo SMC overlap with native STC SMC/structure families;
4. extend matrix from 15m to 5m/30m/1h/2h/4h/1D wherever history is sufficient;
5. build General Lab runtime bridge so any new Lab symbol automatically runs the same research matrix and shows a compact result;
6. accumulate live trade outcomes as new evidence, but recalibrate only on frozen evidence windows.

## NON-NEGOTIABLE RULES
- No lookahead.
- Confirmed bars only.
- Train-only tuning; test/forward remain untouched.
- Same-bar ambiguity -> stop first.
- Reviews/popularity are discovery metadata only.
- No cross-symbol weight inheritance.
- No live weight or A+ gate change from same-dataset discovery.
- No automatic trade execution.
