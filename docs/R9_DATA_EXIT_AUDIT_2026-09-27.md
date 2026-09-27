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


## R9 accepted evidence checkpoint - 2026-09-27T20:30:40.269361+00:00
Core PR191 merged at 2a3b8aecae6bc53e1b5222c658e2a300500c3d2f; critical and full CI36347047903 succeeded. This is tested research infrastructure, not a promoted profitable strategy. No live gates, initial ATR stops, risk0.005, positions, broker actions, equity freshness or notifications changed.
Corrected read36347045013, artifact10940971609: all9639matching signal rows admitted,206late decisions retained as expired, zero receipt/source/seed/plan quarantine. Three naturally persisted R8 frozen seeds verified. Dataset08979d9c931fe3f1d799ae76afb15ce01682ac989662c5fd041264f860d227a3;3519hypotheses and170original plans.
Fixed-horizon same-cohort analysis:249selected,73valued/176unknown. Protection research36347455391 succeeded; none of the tested shorter targets, breakeven or trailing variants justified promotion. All are exploratory counterfactuals, not owner trades or an untouched holdout.
Exact BTCprice overlays restored27observed missing candles in research only after35and143zero-disagreement overlap checks. Supplement94781fc1057c4c44b7a6d96df69f517ed1d376d243fe651be85f494d8975a665 has75commonlyvalued/174unknown. MNQarchive112overlaps/27disagreements was NOT merged. Do not average or rank differing cohorts as measured improvement.
The195.23USD screenshot/ledger delta equals prior documented54.39residual plus visibleBTC140.8432loss to displayed cents. Old residual remains unattributed; no trade imported without exact close time/identity. Closest BTCplan hasTP85189.5655 versus screenshot85500; source linkage is tentative only.
Details:docs/R9_RESULTS_2026-09-27.md. Additional experiments and price-overlay tooling remain on research/r9-protection-20260927, not live runtime code. Future protocol is registered, not evaluated or scheduled; preserve purge/embargo and no-retuning boundaries.
