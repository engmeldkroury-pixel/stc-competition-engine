# STC current checkpoint - 27 September 2026

Checkpoint ID: **STC-R8-FINAL-20260927**. Read this before historical PROJECT_STATE/NEXT_TASK sections.

## Accepted code and evidence
- Core R8 PR190 is merged: `9a1c32e09fc43a5eff02fd3f6094581440b2aedc`.
- Exact tested/merged tree: `befe7ecccd184a0f4283b56af4eca1dbd562f6fc`.
- PR CI `36343737101`: critical SUCCESS; full **536 passed / 1 warning**, 972.44s. The warning is Starlette/httpx test-client deprecation. No tests removed.
- Post-merge main CI `36344826384` is a separate repeat and was still running when this checkpoint was prepared. Do not confuse its status with completed PR acceptance.
- Production readback `36344826332`: SUCCESS, **2026-09-27T19:34:12Z**.
- Historical evidence `36344024376`: SUCCESS; artifact `10939992635`.
- Historical report SHA256: `550260e4e7f1005021992eecb70734ec47d73a2d20f59dfe811bb8b7290cc3fe`.

## What R8 actually changes
Inert frozen research seeds preserve pre-gate LONG/SHORT hypotheses, exact rejection clauses and original geometry. Causal replay begins at the next full observable open inside the frozen envelope. It evaluates independent single-target alternatives1/1.5/2/2.5 plannedR, actual-fillR, gap stops, same-bar ambiguity and costs. Missing paths stay censored. Pre-stop excursions and post-stop rebounds are separate. Rejected signals still have no executable locked plan.

Live84/Boolean/monthly/ATRgeometry/0.005risk and manual-execution-only authority are unchanged. No broker, account, approval, stop, target or notification write occurred. No HostingerPHP replacement is required for this Python-core change. Workers checking out main can use the accepted code; **a new natural frozen seed persisted in production has not yet been observed**. Do not overstate rollout verification.

## Production readback, not independent broker confirmation
- STC records two Capital positions OPEN: NAS100 LONG7.7, entry30416.071, stop30319.1; SPX500 LONG40, entry7737.25, stop7716.
- Both management states are HOLD because `signal_history_stale`; last history2026-09-25T20:30:00Z. This is a no-new-decision fallback, not a fresh market recommendation to hold.
- Rotation candidates null; active Capital opportunities empty.
- Capital and AMP account states remain ineligible `initial_profile_seed` values, not owner-attested current equity. Screenshot values were not used to reopen sizing.
- Telegram configured=true; STCemailconfigured=false. GitHub account email preferences were not changed.
- STC records Capital realizedP/L **-3370.87 / four qualifying days**. Screenshot shows **-3566.10 / five days**. Difference **-195.23USD** is unresolved; screenshot BTC trade alone has visible netloss140.8432USD. Do not invent missing fills or fees.

## Actual research findings and limits
- Latest5000 of9630 matching signal records;26symbols (10Capital16AMP),15m. Snapshot2026-09-27T19:21:20Z.
- 1947directional hypotheses:936Capital1011AMP, all LEGACY_RECONSTRUCTED_GEOMETRY, not original frozen plans or executed trades.
- 1416censored /508no-entry /23complete32-bar windows. Only10 exact known gate quadrants in that snapshot;1937unknown.
- 23same simulated paths reached1R then stopped before2.5R, including5BTCand5ETH. This motivates testing an exit policy, not setting universal1Rtargets.
- Outcome-independent nonoverlap leaves142entered observations,141censored/1complete. Cross-asset dependence remains.
- Report cost0.02R is a proxy. VisibleBTCtrade commissions alone are approximately0.063819R; add realistic cost sensitivity, do not present settled-only means as unbiased expectancy.
- Read `docs/R8_HISTORY_RESULTS_2026-09-27.md` for details.

## Candidate data source found, not yet integrated
A read-only TradingView connector probe returned550bars for CAPITALCOM:BTCUSD15m, first2026-09-22T00:15:00Z, last2026-09-27T19:30:00Z. The tool warns of delayed data and excluded sessions. The latest bar must be checked for closure. Provider/time/session/overlap reconciliation is still required; none of these bars was merged into the validated report.

## Exact next batch: R9 data/fill reconciliation and controlled exits
1. Observe a natural post-merge frozen seed and validate its receipt/hash; no synthetic trade events.
2. Validate candidate historical bars against stored same-provider OHLC, closed-bar cutoffs and sessions. Separate dataset-selection gaps from upstream feed gaps. Preserve immutable manifests; never interpolate trading paths.
3. Reconcile broker executed fills/fees/timestamps with original plans and STC's realized ledger. Missing original plan IDs for manual_external positions must stay explicit.
4. Add fixed-horizon marks for unresolved exits, then compare1/1.5/2/2.5singleTP and current versus volatility/structure-aware stops on the SAME nonoverlapping entry cohort.
5. Freeze chronological purged train/validation/holdout splits; compare costs, expectancy, drawdown, opportunity frequency and asset/timeframe differences. No live promotion or win probability without adequate OOS evidence.
6. Continue Boolean/84/monthly/filter ablation, asset-specific strategy and AMP work from the existing master ledger; do not restart R1-R8.

Research-only exporter/cohortdiagnostic code is on `research/r8-history-evidence-20260927`, implementation checkpoint `50d4b9ee8f481711a7ace66707621bc633b210d9`. Extra research tests are separate from the accepted core536-test count. Documentation append helper is research-branch-only and must not be deployed as runtime code.

## Owner action / safety
No upload or account refresh is required to use the accepted engineering update. Do not interpret this checkpoint as a new trade recommendation. Complete broker history or a current owner-confirmed account snapshot may later be needed to reconcile every executed trade and restore eligible sizing; neither is silently inferred from an old screenshot.
