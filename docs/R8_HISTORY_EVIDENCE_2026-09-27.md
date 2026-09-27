# R8 evidence coverage follow-up

Initial authenticated inbox report run 36343734257 succeeded, but returned 100 old rows covering 21 September 2026 only. Two invalid rows quarantined. Seven directional legacy-reconstructed observations: six censored, one no-entry, zero settled outcomes for any R threshold. This is not evidence of profitability or the recent stop-out causes.

This evidence-only branch adds a CLI reader, not a web endpoint. It uses the already-authorized Hostinger SSH connection, an InnoDB consistent READ ONLY transaction, and SELECT queries only against the event log. Latest 5000 matching Capital/AMP signal records are projected onto the minimum research fields while preserving source payload/receipt integrity. Total matching/selected counts, ID boundaries and truncation are recorded. No account or position tables are read or written. Raw source is temporary on the runner, not a public artifact, and is removed afterward. Production PHP files are never replaced.

Local projection/lint/safety tests: 3 passed. Full R8 CI remains separately gated in PR190. This branch itself is not a strategy promotion and is not merged into main at creation.

Transaction semantics source: MariaDB official documentation, START TRANSACTION WITH CONSISTENT SNAPSHOT and READ ONLY (retrieved 2026-09-27): https://mariadb.com/docs/server/ha-and-performance/standard-replication/enhancements-for-start-transaction-with-consistent-snapshot

Next: verify read-only history run; inspect actual coverage, censoring, receipt integrity and gate/provenance groups before claiming any result. Do not treat overlapping signal observations as independent executed trades or a calibrated win rate.
