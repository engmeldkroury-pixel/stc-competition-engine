# NEXT TASK

Updated: 2026-09-22

## Active objective
Find a robust same-entry-timeframe strategy for competition use without weakening sample, OOS, forward, stability or risk gates.

## Current research architecture
- 17 research strategy families.
- Exact-provider TradingView OHLCV.
- No-lookahead historical features.
- Train / OOS test / forward validation.
- Exact-timeframe runtime calibration only.
- Research-only MTF confirmation layer across 1H / 2H / 4H / 1D / 1M.
- MTF policies: MAJORITY, TREND_WEIGHTED, STRICT.
- research_mode=mtf_compare selectively tests only the strongest adequately sampled 15m candidates.

## Completed evidence
- NO_VALIDATED_STRATEGY / no live 15m calibration: XAUUSD, MES, EURUSD, NAS100, MNQ, XAGUSD, MCL, MGC, SPX500, M2K.
- BTCUSD: 1D trend_pullback research is validated on the original strategy set, but n=49 is below probability-calibration floor and 15m is not validated. Informational only.
- Do not promote any higher-TF result into 15m runtime.

## Active batches
- research/strategy-v2-xau-mnq-20260922 — 17-strategy re-screen of XAUUSD + MNQ.
- research/strategy-v2-btc-mcl-20260922 — 17-strategy re-screen of BTCUSD + MCL.
- research/eth-m6e-screen-e-20260922 — ETHUSD + M6E screening.

## Next automatic actions
1. Read each active run when complete.
2. Extract per-timeframe diagnostics and 15m candidates.
3. Launch mtf_compare only for promising 15m candidates.
4. Compare MTF policies by OOS/forward robustness and trade-retention.
5. Run full feature calibration only for a genuinely VALIDATED same-timeframe candidate.
6. Update PROJECT_STATE.md after every accepted research result.

## Production safeguards
- Safe Mode and Kill Switch remain enabled.
- Manual approval and manual execution remain mandatory.
- Verified legacy TradingView production alerts remain the rollback baseline.
- Six v1.1 MTF Family Breadth Pine feeds are code-ready but not yet the active TradingView alert snapshots.

## Owner dependency
None now. Owner intervention is required only when a later step needs fresh TradingView indicator alerts, private Telegram credentials, or verified manual competition position/trade input.
