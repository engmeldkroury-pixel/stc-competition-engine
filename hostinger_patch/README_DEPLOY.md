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
