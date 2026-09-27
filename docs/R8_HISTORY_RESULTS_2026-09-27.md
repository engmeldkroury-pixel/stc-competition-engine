# R8 historical outcome evidence - 27 September 2026

## Exact source and reproducibility
- Read-only history run: 36344024376; SUCCESS.
- Export code: 13d681d211fa5d40080902c376de25ba79567eb2.
- Artifact: 10939992635, stc-r8-history-evidence.
- Report SHA256: 550260e4e7f1005021992eecb70734ec47d73a2d20f59dfe811bb8b7290cc3fe.
- Snapshot cutoff: 2026-09-27T19:21:20Z; report evaluation cutoff 19:21:22.779957Z.
- Latest 5000 selected signal records out of 9630 matching stored signal rows. IDs 4863..9901. Truncated=true. No projection failures or receipt/identity quarantines.
- 26 exact-provider instruments: 10 Capital, 16 AMP. All this capture's base bars are 15 minutes. Most start Sep23 18:00-18:30Z; crypto extends to Sep27 19:00Z and other instruments to Friday Sep25 evening.
- No database writes, public endpoint, PHP deployment, broker action, equity refresh, approval or notification change. Raw source was temporary on the runner and deleted, not uploaded as an artifact.

## Observations, NOT executed trades
- 1947 directional hypotheses: 936 Capital and 1011 AMP.
- All 1947 are LEGACY_RECONSTRUCTED_GEOMETRY, NOT original frozen historical plans.
- 1224 have an observed entry under the next-full-open envelope rule.
- 1416 censored, 508 no-entry, only 23 complete 32-bar windows.
- Exact gates: 8 B0_Q0; 2 B1_Q0; 1937 UNKNOWN. No B1_Q1 observations in this evidence set.
- Missing-path-bar reason 1197; missing-entry-bar 212; insufficient closed bars 7. Do not interpret missing feed intervals as known market session gaps.

## Stop/target diagnostic, not a live recommendation
- On the SAME simulated paths, 23 hypotheses reached 1R and then stopped before 2.5R: 13 Capital / 10 AMP, including 5 BTCUSD and 5 ETHUSD.
- Four stopped paths later touched 2.5R in the still-observed window. They remain losses; never turn them into wins retrospectively.
- These counts overlap in time and include rejected/unclassified historical setups. They do not establish the outcome of the owner's actual filled trades or justify a universal 1R target.
- Greedy earliest-entry selection per competition/instrument, blocking the entire fixed horizon without looking at results, leaves 142 entered observations: 141 censored, 1 complete; four of these have the 1R-then-stop pattern. This demonstrates why 1947 observations are NOT 1947 independent trades.
- The settled-only mean at 1R (-0.030643 planned R, n=446) and 2.5R (-0.485835, n=292) use DIFFERENT censored populations and must NOT be ranked as unbiased expectancy. No preferred exit is selected.
- Added fee-proxy sensitivity at 0 / 0.02 / 0.05 / 0.10 planned R. This does not model spread-dependent trigger changes.
- The owner's visible BTC trade commissions alone are about 0.063819R relative to its shown initial stop distance. The initial report's 0.02R proxy is therefore not a sufficient measured-cost assumption for that trade. Do not generalize the screenshot fee to all instruments.

## Engineering status
- CLI projection/lint/safety and reader tests passed remotely in the successful history run.
- New non-overlap, paired-count, fee-sensitivity and no-promotion diagnostics plus reader/projection local selection: 12 passed.
- Additional historical exporter/diagnostic files are research-branch tools, not deployed live strategy logic. PR190 core acceptance is tracked separately.

## Decisions and next work
1. Preserve live 84/Boolean/1M/ATR geometry and 0.005 risk. Do not widen stops to recover losses.
2. Priority: reconcile missing bars against exact-provider history and session calendars, preserve their provenance, and retain original frozen seeds going forward.
3. Compare 1/1.5/2/2.5 single-TP policies and current versus volatility/structure-aware stops on the SAME entry cohort, with fixed-horizon marks for unresolved exits and realistic costs.
4. Use chronology, purging/embargo and an untouched holdout; keep Capital/AMP and asset/timeframe results separate. No probability or winner without supporting independent evidence.
5. Reconcile actual entry/stop/target fills with original plan IDs before diagnosing the screenshot's 3.535 actual-entry R as a plan mismatch.
