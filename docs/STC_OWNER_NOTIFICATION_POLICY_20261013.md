# STC owner notification policy — 2026-10-13

- The STC owner disabled **all STC email**. No Gmail reads/sends/replies are authorized; do not reactivate `mail()` or route portfolio/alerts to email.
- Telegram is permitted for **new actionable and materially urgent paper-only** event/position recommendations for an eligible contest or distinct Crypto Spot Lab; not periodic health/heartbeat noise.
- Two Sep 2026 competitions have officially ended: `amp-futures-sep-2026` at `2026-09-30T12:00:00Z` and `capital-africa-sep-2026` at `2026-10-02T08:00:00Z`.
- Both are archived for notification purposes. Drop outdated entries *before recording/delivery* and also guard old signal/portfolio notification producers. Keep immutable execution and paper-position history for human reconciliation; never fabricate a close order.
- Do not globally stop Hostinger `cron_kick.php`: that is a shared queued webhook processor, not the direct notification sender.
- Six old TradingView contest alerts were separately paused through official TradingView account tools, then re-listed inactive on Oct 13. A standalone unnamed XAUUSD alert was not altered without proof it belongs to the ended contests.
- `stc_notification_suppression_reason` consults server-side registered contest end times, and suppresses these two historic contest IDs after expiry. Every *new* competition must have a verified registered lifecycle/end time before activation; automatic retirement beyond these two requires further generic lifecycle implementation.
- The notification-only Hostinger hotfix workflow must not be triggered until PR CI is green. It updates only `notification_control.php`, validates the remote contest rule helper, preserves a restorable remote copy, checks PHP syntax and verifies file SHA.
- Deployment is not certified until the remote job succeeds and separate production readback verifies no old email/Telegram messages. Do not infer that creating or merging this PR silences production.
- No broker/account/position writes or automatic trading are part of this release.
