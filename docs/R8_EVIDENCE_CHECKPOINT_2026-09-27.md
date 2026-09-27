# R8 - acceptance and evidence checkpoint

## 2026-09-27 initial verification
- PR #190 source implementation; transfer-helper workflow 36343326058 succeeded with pinned dependencies. All transfer helpers removed from PR final diff.
- CI 36343419807 critical passed; full still in progress at this checkpoint.
- First production GET-only report run 36343409127 failed before any data was evaluated. No performance or source-coverage conclusion may be inferred.
- Existing read_cloud_snapshot contract explicitly permits only limit 1..100. Initial runner requested 1000; corrected default/workflow maximum to 100 and added four reader-contract tests. Exact initial HTTP status was withheld by the first diagnostic, so do not assert the server rejection cause until reverified.
- Local engine + reader-contract regressions: 63 passed. No tests disabled; full PR CI must run on the new head.
- No worker/owner credential contents are printed. No source raw inbox is exported. No account/equity/position/approval/notification writes.

## Screenshot-specific stop/target observation
The visible BTC long entry fill is 84,564.60, stop order 84,300, canceled target 85,500. Relative to the actual entry fill, these displayed levels imply about 3.535R before costs, not automatically 2.5 actual-fill R. This alone does NOT prove an STC plan mismatch: the original frozen signal/envelope must be matched to this filled trade. Entry fill slippage/entry-zone position can change fill-R while planned-R stays fixed.
The visible stop fill was 84,299.80. The shown price loss plus entry/exit commissions is USD 140.8432, excluding any unshown costs.

## Open acceptance items
1. Complete full CI for latest PR head.
2. Obtain the first successful bounded production outcome report; explicitly retain incomplete/censored states.
3. Merge only after acceptance, then verify production readback and next natural frozen-seed capture.
4. Next quantitative work: non-overlapping symbol/timeframe exit/ATR ablation with frozen holdout and explicit cost sensitivity. No live parameter promotion from screenshots or synthetic tests.
