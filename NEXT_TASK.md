# NEXT TASK

Updated: 2026-09-24 00:50 EEST

## CONTROLLING PROJECT
STC.

## AUTHORITATIVE CONTINUITY
Read first:
- docs/STC_ADAPTIVE_RESEARCH_MASTER_LEDGER.md
- PROJECT_STATE.md

Owner instruction: continue from repository state without requiring the owner to restate the strategy program after a new chat.

## VERIFIED COMPLETE
- Native STC strategy matrix exists.
- 14 implemented community/composite research adapters exist.
- Train-only tuning + OOS TEST + FORWARD exists.
- Exact 85/15 final frozen holdout exists and fails closed on insufficient history.
- Redundancy-aware family normalization exists.
- 26-symbol 15m native/community benchmark archived.
- Final unseen 15m confirmation archived.
- Multi-timeframe frozen scan archived.
- 10 research-only SHADOW records exist.
- Protected serverless endpoints exist:
  - POST /research/general-lab/plan
  - POST /research/general-lab/evaluate
  - GET /research/shadow-candidates
- community_indicator_live_authority=false.

## ACTIVE WORK
Finish the General Lab runtime bridge.

Required behavior when owner adds/saves a General Lab symbol:
1. persist the symbol in the existing local General Lab list;
2. automatically build/show the STC research plan for that symbol;
3. show any existing SHADOW records for the symbol;
4. create/show a research request status;
5. if exact-provider OHLCV is not available, show WAITING_FOR_EXACT_HISTORY and fail closed;
6. once exact-provider series is supplied by an authorized worker/connector, call the existing research evaluation engine;
7. display a compact result: validated native strategies, validated community components, frozen/shadow status, and no live authority.

## DATA-SOURCE BLOCKER
The hosted STC server cannot call ChatGPT TradingView MCP directly by ticker.
Do not substitute another provider silently.
Full one-click historical evaluation requires an authorized exact-provider worker/connector or supplied exact series.

## RESEARCH CONTINUATION
After the General Lab bridge:
1. causal/repaint-safe audit and implementation priority:
   - Lorentzian Classification;
   - HalfTrend;
   - VuManChu Cipher B;
   - Trendilo;
   - Nadaraya-Watson non-repainting mode;
   - other high-use practical open-source composites found by review;
2. run exact-provider frozen benchmark before any research weight;
3. extend 5m/30m/1h/2h/4h/1D only when evidence floor is met;
4. accumulate shadow/live outcomes, but recalibrate only on frozen batches/windows.

## NON-NEGOTIABLE
- no lookahead;
- no repainting evidence unless explicit non-repainting mode is verified;
- no cross-symbol weight inheritance;
- no popularity/review-based trading weights;
- no live A+ or risk-rule weakening;
- no automatic broker execution;
- no provider substitution.
