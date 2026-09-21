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
