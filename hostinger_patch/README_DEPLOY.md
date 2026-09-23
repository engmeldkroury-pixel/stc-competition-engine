# STC Hostinger durable approval patch

This additive patch keeps the existing TradingView bridge files unchanged. It adds durable runtime controls and owner approval audit state. It never places an order.

## Upload/add
- `cloud_control.php`
- `runtime_control.php`
- `approval.php`

Do not replace `webhook.php`, `claim.php`, `ack.php`, `inbox.php`, or `_bootstrap.php` for this batch.

## Database
Run `migrations/001_cloud_approval.sql` once against the same database already used by `stc_webhook_events`.

The migration is fail-closed: the singleton runtime row starts with both `safe_mode=1` and `kill_switch=1`.

## Private config prerequisite
Add one separate secret to the existing `config.php` outside `public_html`:

```php
'owner_api_token' => 'GENERATE_A_SEPARATE_LONG_RANDOM_SECRET',
```

Do not reuse `worker_api_token`, GitHub dispatch credentials, or database credentials. Never place the real value in GitHub or chat.

## First production check
1. Upload the three PHP files.
2. Run the SQL migration.
3. Add `owner_api_token` privately.
4. GET `/runtime_control.php` with the owner bearer token.
5. Confirm both `safe_mode` and `kill_switch` are still true.
6. Do not disable either control until the cloud endpoints and one blocked approval attempt have been verified.

`approval.php` records only `approved`, `blocked`, or `rejected` owner decisions and always returns `execution=manual_only`. It contains no broker/order endpoint.


## Owner console add-on

After the durable approval patch is already deployed and verified, upload these two additive files:

- `operator_snapshot.php`
- `operator.php`

No additional SQL migration is required.

Open `/operator.php` and enter the existing private owner token for the current browser session. The page does not persist the token.

The console can:
- read the latest authoritative analyzed signal for each Capital.com competition symbol;
- display the immutable locked plan when one exists;
- display durable approval and runtime-control state;
- submit a human approve/reject decision through the existing `approval.php`;
- turn Safe Mode / Kill Switch on or off through the existing `runtime_control.php`.

The console cannot place, modify, or close an order. After a signal is approved, order entry remains manual in the competition platform.

For an approve action, the owner must enter the current TradingView price. The console supplies a fresh UTC observation timestamp and `market_status=open`; the existing server-side approval contract still rejects stale evidence, a price outside the envelope, Safe Mode, Kill Switch, WAIT signals, expired signals, or signals superseded by a newer event.


## Portfolio Supervisor add-on

After the owner console is deployed, this additive batch adds durable manual position tracking, owner-synced competition equity, position sizing, and portfolio-management advice.

Upload these files to the same `public_html` directory:

- `portfolio_control.php`
- `position.php`
- `account_state.php`
- updated `operator_snapshot.php`
- updated `operator.php`

Then run once:

- `migrations/002_portfolio_supervisor.sql`

Deployment order matters:
1. Run the SQL migration first.
2. Upload `portfolio_control.php`, `position.php`, and `account_state.php`.
3. Replace `operator_snapshot.php`.
4. Replace `operator.php`.
5. Keep Safe Mode and Kill Switch ON.
6. Refresh the owner console and confirm both competition tabs still load.

The new account-state rows are seeded from the known competition initial balances:
- Capital.com Africa: USD 100,000
- AMP Futures: USD 250,000

The seeded risk fraction is an STC provisional configuration of 0.50% per new trade. It is not an official competition risk limit. The owner console can update equity and the configured risk fraction manually because the verified STC integration has no broker-account read access.

Position records are created only after the owner confirms the fill already occurred manually in the competition platform. The ledger supports:
- OPEN after a confirmed manual fill;
- STOP_UPDATE after the stop is changed manually;
- PARTIAL after a manual partial close;
- CLOSE after a manual full close.

The API never sends broker orders. Stop updates that widen risk are rejected.

Portfolio Supervisor actions are decision support only:
- `HOLD`
- `PROTECT`
- `PARTIAL_TAKE_PROFIT`
- `EXIT_NOW`

Anti-churn rule: a stronger opportunity alone cannot force rotation. The current thesis must first degrade, including two consecutive strong opposite closed-bar signals when reversal is the reason, and a same-competition locked opportunity must be materially stronger before it is surfaced as a rotation candidate.


## Actionable mobile/email notification add-on

This batch is additive and never sends broker orders.

Upload:
- `notification_control.php`
- `notification.php`
- updated `operator.php`

Run once:
- `migrations/003_notifications.sql`

Add only the channels you want to the private `config.php` outside `public_html`.

Telegram:
```php
'telegram_bot_token' => 'CHANGE_ME_TELEGRAM_BOT_TOKEN',
'telegram_chat_id' => 'CHANGE_ME_TELEGRAM_CHAT_ID',
```

Email backup:
```php
'notification_email' => 'owner@example.com',
'notification_from_email' => 'stc@example.com',
```

Do not commit real tokens or addresses into GitHub and do not paste a bot token into chat.

The GitHub worker calls `notification.php` after durable ingestion. Notification failures are fail-soft and cannot turn a successfully ingested market event into a failed trading signal.

Server notification policy:
- NEW locked LONG/SHORT plan: notify.
- WAIT signal: do not notify.
- Raw 15-minute feed bar: do not notify.
- Open-position management action `HOLD`: do not notify.
- `PROTECT`, `PARTIAL_TAKE_PROFIT`, or `EXIT_NOW`: notify when the de-duplicated management state changes.

The owner console Notifications tab shows whether Telegram/email are configured and provides a harmless test button. Browser notifications remain independent and can work alongside both server channels.


## High-impact macro approval gate

Upload:
- `macro_control.php`
- updated `approval.php`
- updated `operator_snapshot.php`
- updated `operator.php`

No SQL migration is required for this gate.

Default source:
- Forex Factory weekly JSON export served from `https://nfs.faireconomy.media/ff_calendar_thisweek.json`.

Default STC policy:
- enabled;
- cached for 10 minutes;
- high-impact events only;
- block new approvals from 45 minutes before through 30 minutes after a relevant high-impact event;
- fail closed if the external calendar becomes unavailable;
- existing open positions are not auto-closed because of the calendar.

Optional private `config.php` overrides:
```php
'macro_calendar_enabled' => true,
'macro_calendar_url' => 'https://nfs.faireconomy.media/ff_calendar_thisweek.json',
'macro_calendar_cache_seconds' => 600,
'macro_calendar_timeout_ms' => 1800,
'macro_blackout_before_minutes' => 45,
'macro_blackout_after_minutes' => 30,
'macro_calendar_fail_closed' => true,
```

The calendar gate is event-risk control, not a directional macro forecast. Signal reasons still state that a live directional macro factor is unavailable until a separate verified source exists.


## Active-opportunity lifecycle and clearer order-entry UX

This patch changes only decision-support behavior and presentation. It does not add broker execution.

Replace these deployed files after CI passes:
- `operator_snapshot.php`
- `operator.php`
- `portfolio_control.php`
- `notification_control.php`

The Python worker code also changes `app/approval.py`; deploy by merging to `main` so GitHub Actions uses the updated worker automatically.

Behavior after deployment:
- LONG/SHORT opportunities are considered active only until the locked plan expiry.
- Expired LONG/SHORT plans disappear automatically from opportunity lists, including between the 30-second server refreshes.
- WAIT remains visible only as a current signal, not an opportunity.
- Times are rendered in the browser's local timezone in a short human-readable form.
- The countdown updates every second.
- The card shows a planned order type based on the latest confirmed 15-minute close.
- Entering the current TradingView price recalculates the manual order type before approval.
- Browser notifications can fire for already-active unseen opportunities immediately after notification permission is granted.
- Server Telegram/email notifications skip expired plans and include ACTIVE time-left plus order type.

Validity is anchored to the TradingView bar close rather than the later GitHub worker processing time. The Pine feed sends the bar-open timestamp, so STC derives the close time from the feed timeframe before calculating plan expiry. This prevents a delayed worker from extending an old opportunity artificially.
## Current production file manifest

When deploying the current Owner Console / Portfolio Supervisor / Notifications build to a fresh or partially updated Hostinger site, keep these PHP files together in the same deployed directory:

- `cloud_control.php`
- `runtime_control.php`
- `approval.php`
- `macro_control.php`
- `portfolio_control.php`
- `position.php`
- `account_state.php`
- `notification_control.php`
- `notification.php`
- `operator_snapshot.php`
- `operator.php`

Required additive migrations, once per database:
- `migrations/001_cloud_approval.sql`
- `migrations/002_portfolio_supervisor.sql`
- `migrations/003_notifications.sql`

A partial deployment can leave the HTML shell visible while authenticated data calls fail. In particular, the current `operator_snapshot.php` requires `macro_control.php`, `portfolio_control.php`, and the portfolio/account tables.

## Historical competition activity backfill

The Owner Console can import:
- a position that is still open, preserving its original open timestamp; or
- a past position that is already closed, preserving original open/close timestamps.

Historical closed imports are ledger/audit operations only. They never send broker orders. If the owner supplies the actual realized P/L from the competition platform, STC stores that value as the authoritative owner-platform record; otherwise STC calculates an estimate from entry/exit/quantity using its verified contract-value model.

Qualification-day progress uses the original recorded open and close dates plus any recorded partial-close dates, so importing older trades does not incorrectly turn today's import date into the historical trading day.


## General Lab durable research queue

This additive batch connects the Owner Console General Lab tab to a durable research-request queue. It does not place orders and it cannot grant live trading authority.

Run once:
- `migrations/004_general_lab_queue.sql`

Upload:
- `general_lab.php`
- updated `operator.php`

The endpoint reuses the existing private owner/worker bearer tokens. No new secret is introduced.

Behavior:
- Saving General Lab symbols creates one durable research request per symbol.
- Provider-qualified symbols such as `CAPITALCOM:XAUUSD` enter `WAITING_FOR_EXACT_HISTORY`.
- Bare symbols such as `XAUUSD` enter `WAITING_FOR_SYMBOL_RESOLUTION` until an authorized exact-data worker resolves the TradingView provider symbol.
- An authorized worker can claim the request and later store a research-only result.
- Completed results are forced to `live_authority=false` and `promotion_required=true`.
- The Owner Console shows queue/running/evaluated/failed state and compact research results.
- No alternate history provider may be substituted silently if exact-provider data is unavailable.

The hosted PHP queue does not itself have access to ChatGPT's TradingView MCP. Automatic historical evaluation therefore requires an authorized exact-provider data worker/connector to claim queued requests, fetch exact TradingView history, run the STC research engine, and submit the result.
