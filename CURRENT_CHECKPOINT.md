## R10 forward/AMP extension checkpoint - 2026-09-28
Core frozen Capital R10 PR192 merged at f9f04f8022088f9327f5af646891a49eb77dc361 after CI36375341815: full582passed/1warning; critical309passed/1warning. No live strategy promotion.
Second research batch builds causal forward evaluation with exact protocol identity, gap/conflict fail-closed handling, and a statistical evidence gate that cannot auto-promote.
Capital frozen rule does NOT transfer robustly to30m/1h and does NOT transfer to the aggregate AMP universe at realistic cost proxies. Do not claim MTF or cross-market edge.
AMP family audit rejects index/rates/FX/metals/energy under tested rules. Only MBT/MET crypto futures retained a frozen research hypothesis:15m,ADX>=30,EMA20/50/200 anti-chase trend pullback,stop2ATR,target2R,horizon32,not-before2026-09-28T04:15Z. Official competition rules directly allow CME:MBT1! and CME:MET1!, max25 open each.
Historical AMP-crypto cost stress stays positive0-5bps, but holdout is only14 trades/6 days and already inspected. Day-block bootstrap CI crosses zero. Capital inspected holdout24 trades/8days also has a bootstrap CI crossing zero. Neither candidate is statistically established or live-authorized.
Forward evidence gate rejects mixed cost scenarios, duplicates and protocol mismatches; CENSORED is never scored as a win/loss; chronology is used for drawdown; even a passing result is human-review-only.
Second branch: research/r10-forward-amp-crypto-20260928. Local combined R10 tests currently25passed. Full GitHub CI is still required before merge.

## R10 strategy-shadow checkpoint - 2026-09-28
Owner reports all executed competition trades losing so far. R10 tested stop/target-only fixes, uniform trend/chase, pullback/reclaim/breakout, mean reversion, per-asset/timeframe static selection and naive walk-forward switching. These were NOT robust and are rejected for live promotion. Do not restart these searches blindly.
Historical accepted directional cases were materially more extended than rejected cases, supporting a late/chasing-entry hypothesis but not proving gate causality. Stop widening did not solve the accepted-plan problem.
The first historically stable parameter region found uses a direct session/regime model: 15m, London/New York overlap, ADX trend vs range separation, anti-chase pullback in trend and z-score extreme fade in range. Neighborhood/cost/session stress was materially more stable than prior families, but the historical holdout was inspected during development and is now contaminated for further selection.
Frozen forward candidate: research_inputs/R10_REGIME_SESSION_FROZEN_PROTOCOL.json; no earlier than 2026-09-28T12:00:00Z; session12-17UTC; trendADX>=30; rangeADX<=20; neutral=>WAIT; initial stop1.5ATR; single target2R;32-bar horizon. It is RESEARCH ONLY, live_authorized=false, execution=none.
Historical stress for frozen candidate, 12-17UTC: at2bps train n68 mean+0.227R PF1.451; validation n27 +0.209R PF1.378; already-inspected holdout n24 +0.379R PF1.744. At5bps these were +0.063/+0.093/+0.205R. Nearby session windows remained positive historically. These are hypothesis-generation results, NOT a promised or independently forward-validated edge.
Local verification: R10-only10passed; focused R10+R8-outcome+trade-plan75passed. Branch research/r10-regime-session-shadow-20260928. Live84/Boolean/monthly/risk0.005/current open stops and manual execution unchanged.
Next: full GitHub CI, then collect prospective frozen signals without retuning; stratify by symbol/day and use realistic costs. No live promotion until prospective evidence supports it. Zero additional paid infrastructure remains a hard constraint.



## Persistent runtime direction - 2026-09-28
Owner does not want Work or Opera as runtime dependencies. Continue with R10-PERSISTENT-BRIDGE: STC as an owner-controlled always-on service; TradingView server-side alert webhooks for signal ingress; durable queue/database and Telegram/manual approval; official broker/feed API adapters where available; and a self-hosted persistent Playwright/Chromium collector only as a fail-closed reconciliation fallback when no account API exists. Do not depend on ChatGPT session lifetime. Do not auto-trade. Preserve adapter separation and health monitoring.
# STC latest checkpoint - R9

## R9 accepted evidence checkpoint - 2026-09-27T20:30:40.269361+00:00
Core PR191 merged at 2a3b8aecae6bc53e1b5222c658e2a300500c3d2f; critical and full CI36347047903 succeeded. This is tested research infrastructure, not a promoted profitable strategy. No live gates, initial ATR stops, risk0.005, positions, broker actions, equity freshness or notifications changed.
Corrected read36347045013, artifact10940971609: all9639matching signal rows admitted,206late decisions retained as expired, zero receipt/source/seed/plan quarantine. Three naturally persisted R8 frozen seeds verified. Dataset08979d9c931fe3f1d799ae76afb15ce01682ac989662c5fd041264f860d227a3;3519hypotheses and170original plans.
Fixed-horizon same-cohort analysis:249selected,73valued/176unknown. Protection research36347455391 succeeded; none of the tested shorter targets, breakeven or trailing variants justified promotion. All are exploratory counterfactuals, not owner trades or an untouched holdout.
Exact BTCprice overlays restored27observed missing candles in research only after35and143zero-disagreement overlap checks. Supplement94781fc1057c4c44b7a6d96df69f517ed1d376d243fe651be85f494d8975a665 has75commonlyvalued/174unknown. MNQarchive112overlaps/27disagreements was NOT merged. Do not average or rank differing cohorts as measured improvement.
The195.23USD screenshot/ledger delta equals prior documented54.39residual plus visibleBTC140.8432loss to displayed cents. Old residual remains unattributed; no trade imported without exact close time/identity. Closest BTCplan hasTP85189.5655 versus screenshot85500; source linkage is tentative only.
Details:docs/R9_RESULTS_2026-09-27.md. Additional experiments and price-overlay tooling remain on research/r9-protection-20260927, not live runtime code. Future protocol is registered, not evaluated or scheduled; preserve purge/embargo and no-retuning boundaries.

## R10 next executable batch after R9
Read the latest CURRENT_CHECKPOINT first; do not restart R1-R9.
1. Investigate MNQsource close discrepancies and remaining source/quote timing gaps. Current-source bar confirmation versus host-chart confirmation is a hypothesis to test, not a proven cause. Do not change live Pine feeds without verified source parity and compilation/runtime tests.
2. Run controlled entry-timing and volatility/structure-aware initial-stop experiments on the same entry opportunities, maintaining monetary risk and realistic fee/spread exposure. Existing open stops must not be widened for recovery.
3. Preserve and expand natural frozen-seed capture. Historical accepted/rejected reconstructed hypotheses are not independent executed trades. Separate asset, timeframe, competition and gate strata.
4. Complete execution-to-plan reconciliation only with exact fill/close identifiers and timestamps. Opera browser read failed as disconnected in this session. No Capital.com API account is required; previous project history parks that optional route.
5. For prospective protocol evidence from2026-09-28T00:00Z, purge training windows overlapping evaluation and apply a horizon-sized embargo when fitting/tuning. Do not retune on the evaluation data. No automated promotion or win probability.
No owner upload or account refresh is needed to use this engineering update. No fresh trade recommendation is issued.


--- Prior checkpoint history preserved below ---

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
