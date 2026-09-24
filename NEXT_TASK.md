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
- Repository is still private.
- Branch stc-competition-mode-20260924 exists from main 126febe8a414caa89b445e80afa6d548ea72e5af.
- Competition branch adds a Capital-only opportunity gate and keeps manual approval/manual execution.
- Latest-live replay on the new baseline logic produced:
  - EURUSD SHORT quality 83/100 -> PASS;
  - XAUUSD SHORT quality 80/100 -> PASS;
  - XAGUSD SHORT quality 75/100 -> BLOCK.
- /process serverless endpoint now drains multiple batches per invocation on the branch.

## NEXT EXECUTABLE WORK
1. Complete branch verification and inspect full diff.
2. Open PR for stc-competition-mode-20260924.
3. Run CI if capacity permits; if private Actions remains blocked, make a safe public-runner decision only after secret/history review.
4. Merge only after verification evidence is adequate.
5. Deploy the merged serverless processor and confirm /health and /process behavior.
6. Confirm Telegram/notification path emits a competition opportunity when a fresh locked plan exists.
7. Keep TradingView order entry manual; no broker/order automation.
8. After go-live, monitor opportunity frequency and false-positive rate without changing thresholds after one trade.
9. Continue research tasks only after the competition runtime path is no longer blocked.

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
