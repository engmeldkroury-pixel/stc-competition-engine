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
