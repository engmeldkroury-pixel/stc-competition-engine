# NEXT TASK

Updated: 2026-09-24 12:xx EEST

## CONTROLLING PROJECT
STC.

## CURRENT URGENT PRIORITY
Capital.com Africa September 2026 competition acceleration without automatic order execution.

## VERIFIED CURRENT STATE
- TradingView Capital MTF feed is firing every confirmed 15m cycle and webhooks return HTTP 200.
- Official leaderboard snapshot: rank 1 +38.08%; rank 60 +11.02%.
- Competition ends 2026-10-02 08:00 UTC and ranks by realized P/L.
- GitHub Actions quota/capacity is an external runtime blocker for private-repository workflows.
- Repository is still private; owner has authorized public visibility for non-critical code.
- PR #140 is merged as 403db181e9ce43772b95215a8187f0dfcf0a4f78; Capital-only competition mode is now on main.
- PR #141 is merged as d7664ec2492d36cdd6eb713b9e0769d387a77a54; Telegram/email now accepts COMPETITION_OPPORTUNITY plans in source.
- Latest-live replay on the new baseline logic produced:
  - EURUSD SHORT quality 83/100 -> PASS;
  - XAUUSD SHORT quality 80/100 -> PASS;
  - XAGUSD SHORT quality 75/100 -> BLOCK.
- /process serverless endpoint now drains multiple batches per invocation on main.
- Live Hostinger notification file and serverless deployment still require runtime deployment/verification.

## NEXT EXECUTABLE WORK
1. Change repository visibility to Public in GitHub Settings so standard GitHub-hosted Actions can run without the exhausted private-minutes allowance.
2. Immediately confirm the new STC CI and STC Process Bridge Events jobs actually start with non-null steps.
3. Deploy the merged serverless processor and hostinger_patch/notification_control.php to the live runtimes.
4. Trigger/process a fresh Capital cycle and confirm a COMPETITION_OPPORTUNITY locked plan is persisted.
5. Confirm Telegram delivery status is sent, not skipped, for that fresh plan.
6. Keep TradingView order entry manual; no broker/order automation.
7. Monitor opportunity frequency and false-positive rate without changing thresholds after one trade.
8. Continue research tasks after the competition runtime path is operational.

## PUBLIC/PRIVATE REPOSITORY DECISION
Owner authorizes public visibility for non-critical code and accepts strategy visibility.
Do not expose:
- credentials/tokens/secrets;
- private owner/admin material;
- any secret-bearing historical commit.
Current screening is incomplete for full Git history, so repository visibility has not yet changed.

## LIVE BOUNDARY
- human approval/manual execution only;
- no automatic broker/order execution;
- quality score is not win probability;
- public leaderboard returns are descriptive, not evidence that STC can reproduce them;
- do not promise a competition win.
