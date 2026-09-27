# R9 research engine acceptance contract

Research-only modules; no live threshold/ATR/risk changes, broker actions, ledger writes or account refresh.

- `outcome_dataset.py`: validate authenticated source receipts, exact provider/timeframe, closed-bar cutoff, envelope prices, frozen seed hashes AND source semantics. Reject noncanonical NaN/Inf snapshots. Conflicting duplicate events and same-time OHLC are quarantined, not silently preferred. Export normalized bars, seeds, receipt hashes and original locked-plan identities only; no raw payloads/accounts/credentials.
- `exit_policy_audit.py`: compare fixed single-TP alternatives 1/1.5/2/2.5 planned R. A COMPLETE path whose target never triggers gets an explicitly labeled terminal mark, NOT a fictitious broker fill. Partial paths remain unknown. Intrabar double touches retain lower/upper bounds; gap stops use the open. Use identical eligible IDs across all policies and cost sensitivities. Select earliest nonoverlapping full-horizon occupancy before considering results. Do not turn common-cohort statistics into unbiased global expectancy or a calibrated win probability.
- `execution_reconciliation.py`: exact-decimal screenshot arithmetic. The latest observed delta is explained by the earlier documented -54.39 residual plus visible BTC net -140.8432, to displayed cents. This is NOT evidence of the remaining fee/trade attribution or a verified close timestamp. Ledger writes remain disallowed.
- `export_r9_history.php`: CLI-only consistent READ ONLY transaction, upper bound12000 rows, status-count inventory, no account tables or permanent server files.
- `run_r9_audit.py`: network-free local consumer; raw input remains temporary. Manifest hashes are actual emitted file SHA256, dataset identity has a separate canonical hash. Exported original plans are research records, not an approval.

## Deliberate limitations
History remains signal-derived, not guaranteed complete exchange ticks. Unknown gaps are not assumed sessions. External OHLC reconciliation never auto-merges or silently substitutes provider. Terminal marks exclude realistic bid/ask trigger effects and use explicit cost proxies. Adaptive-stop experiments, unseen holdout validation and exact broker fill linkage remain separate tasks. Do not call this a winning strategy or change live parameters from these diagnostics.

## Rollback
Remove/revert the research-only files and CI entry. No database migration, account edit or Hostinger PHP replacement is needed.
