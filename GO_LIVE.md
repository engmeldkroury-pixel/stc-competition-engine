# STC Capital.com Competition Go-Live

Status: software path verified; final owner-console deployment and runtime activation require owner action.

## Already verified

- TradingView Pine: `STC Capital Multi Feed v0.7.1 Historical Context`.
- Active production alert: `5662088915`.
- Scheduler: `CAPITALCOM:BTCUSD`, 15 minutes.
- Exactly 10 Capital.com competition symbols emitted per confirmed cycle.
- Webhook deliveries observed with HTTP 200.
- Hostinger persistence verified.
- GitHub worker batches verified with 10/10 ingested and zero rejects/failures.
- Historical context verified on all 10 symbols.
- `historical_regime` and `blended_technical` verified in durable results.
- Immutable locked trade plan verified on an actionable signal.
- Old single-symbol XAUUSD fallback alert is paused, not deleted.
- CI is green on main.

## Owner console files to deploy

Upload these two files from `hostinger_patch/` to the existing STC `public_html` directory:

- `operator_snapshot.php`
- `operator.php`

No new SQL migration is required because the durable approval/runtime-control migration is already deployed.

Do not replace the existing bridge files.

## First owner-console check

1. Open `https://stc.feama.site/operator.php`.
2. Enter the existing private owner token in the page. Do not paste the token into chat.
3. Click Refresh.
4. Confirm the page shows:
   - the latest Capital.com symbols;
   - runtime Safe Mode and Kill Switch;
   - latest recommendation and score;
   - locked Entry / Stop / TP1 / TP2 when a plan exists;
   - durable approval status.
5. Keep Safe Mode and Kill Switch ON during this check.

## Activation boundary

The owner console contains an explicit button to disable Safe Mode and Kill Switch. Do not use it until the owner intentionally chooses to make manual approvals available.

Disabling controls does not place an order. It only removes the runtime block on a fresh owner approval.

## Manual approval flow

For a LONG or SHORT card with a locked plan:

1. Read the current price directly from the Capital.com competition chart in TradingView.
2. Enter that current price in the owner console.
3. Click Approve.
4. Server-side approval still rejects the request if:
   - Safe Mode is active;
   - Kill Switch is active;
   - the signal expired;
   - a newer signal exists;
   - the price is outside the locked approval envelope;
   - the evidence timestamp is stale;
   - the market is not confirmed open;
   - the recommendation is WAIT.
5. If approved, the console can show manual execution readiness briefly.
6. Enter any competition order manually in TradingView. STC does not place the order.

## Emergency stop

At any time, use the owner console button:

`SAFE + KILL ON`

This prevents further approvals. It does not close an existing position automatically.

## Important architecture rule

- Pine chart zones are technical chart visuals.
- The backend `locked_trade_plan` is the authoritative STC plan.
- A newer bar never silently reprices an older locked plan; it creates a new plan identity.
- Historical context is used for analysis, never as an execution-time quote.
- Automatic broker/order execution remains unavailable by design.
