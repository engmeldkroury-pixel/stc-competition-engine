# STC Public / Private Security Boundary

This repository is intentionally public. It contains source code, tests, research logic, deployment templates, schemas, and non-secret project documentation.

## Never store here

Do not commit any real value for:

- GitHub personal access tokens or API tokens;
- `STC_WORKER_TOKEN`, `STC_TRIGGER_TOKEN`, owner/operator bearer tokens;
- Telegram bot tokens or chat IDs;
- database usernames, passwords, DSNs, connection strings, dumps, or backups;
- private keys, certificates, cookies, sessions, or browser profiles;
- live account credentials or broker credentials;
- private operator state that identifies account balances, fills, positions, or notification recipients.

## Approved private locations

### GitHub Actions

Runtime values used by GitHub Actions must be stored in **GitHub Actions Secrets** and referenced only through `${{ secrets.NAME }}`.

Current secret contract includes at minimum:

- `STC_WORKER_TOKEN`

If a future workflow needs a private endpoint or additional credential, add it as a GitHub Secret rather than hard-coding it.

### Hostinger

The real `config.php` must remain **outside `public_html`** and outside this repository. It may contain:

- database credentials;
- `worker_api_token`;
- `owner_api_token`;
- Telegram bot token and chat ID;
- notification email addresses;
- other server-only runtime secrets.

The public `hostinger_patch/` directory contains implementation code and placeholders only.

### Vercel / other serverless runtimes

Use provider Environment Variables / Secrets for:

- `STC_BRIDGE_URL` when the endpoint itself should be private;
- `STC_WORKER_TOKEN`;
- `STC_TRIGGER_TOKEN`;
- any future external API credential.

## Runtime/private data

Live account state, positions, approvals, notification delivery records, and webhook results belong in the private runtime database. Public SQL migrations may define schemas, but real database contents must never be committed.

## Exposure response

If a real secret is ever committed:

1. Treat it as compromised immediately.
2. Rotate/revoke the credential first.
3. Remove it from the current tree.
4. Rewrite Git history only when necessary and with an explicit recovery plan.
5. Re-scan the repository before restoring normal operation.

Deleting a secret only from the latest commit is not enough because Git history can retain it.
