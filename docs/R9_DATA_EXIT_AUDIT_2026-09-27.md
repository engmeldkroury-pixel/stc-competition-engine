# R9 - data integrity, actual-fill reconciliation and controlled exit research

## Start checkpoint
- Owner requests continuous development with concrete progress messages and durable history.
- Starting main: cd55750821131aff446eb7bf2f2c88cd518251e2.
- R8 PR190 already accepted; post-merge CI36344826384 has completed successfully (critical and full).
- Isolated branch: stc-r9-data-exit-audit-20260927.
- Status: IN PROGRESS, not a completed strategy optimization.
- No broker/approval/account/stop/target or notification changes authorized by this research batch.

## Confirmed research limitations to address
- R8 historical reader selected latest5000 signal-created rows; no complete-market-history claim was valid.
- Rejected/accepted hypotheses were replayed only on validated signal rows. Need separate source selection gaps from upstream unobserved intervals.
- Unresolved exits have no fixed-horizon valuation in R8, making settled-only policy means incomparable.
- Latest screenshot versus STC ledger difference USD195.23 remains unresolved. Do not fabricate fills, infer a close timestamp from order placement, or refresh equity from stale evidence.

## Batch plan and acceptance
1. Read-only bounded wider history and normalized validated seeds/bars; preserve source hashes and availability metadata, never raw credentials or account tables in artifacts.
2. Verify naturally persisted post-R8 frozen seeds and report exact provenance/quarantine counts.
3. Add conservative coverage/conflict reconciliation with no interpolation or provider substitution.
4. Add explicit fixed-horizon mark-to-market research values and compare exit policies on the same nonoverlapping cohort, separating censoring and ambiguity.
5. Test causal boundaries, LONG/SHORT symmetry, duplicate conflicts, positive finite data, costs and no live promotion.
6. Preserve the existing live84, Boolean, monthly, ATRgeometry and0.005risk. No change is justified by synthetic tests alone.

## Reference
TradingView official strategy documentation, accessed2026-09-27: https://www.tradingview.com/pine-script-docs/concepts/strategies/ . OHLC does not uniquely reveal intrabar order; gap fills and same-bar ambiguity must not be treated as exact observed executions.
