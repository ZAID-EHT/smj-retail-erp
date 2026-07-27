# SMJ System Health & Operations

Route: `/retail-erp/admin/system` (System Manager only). Backend:
`my_store_ui/system_operations.py`. Regression: `test_system_operations` (5 tests).

## Safety design

Every endpoint is **read-only** and **fixed-purpose**. There is:
- **no arbitrary shell execution**,
- **no database credential exposure** (asserted: the site db_password never appears
  in any response),
- **no absolute-path exposure** (backup files are shown by basename only; asserted
  no `/home/` or `/private/` in output),
- **no web-based restore** (documented as a server-only operation).

## What it shows

| Section | Fields |
|---------|--------|
| Health | database connected, Redis connected, scheduler enabled, Error Log 24h trend, failed background jobs |
| Readiness | developer mode, maintenance mode, scheduler, pending migrations, company count, first-time-setup flag, email configured, app versions |
| Backups | count, latest age (hours), last 10 backup files (basename, size, created) |
| Errors | Error Log counts by source over 7 days (counts only, no tracebacks/PII) |

## Findings surfaced on staging (2026-07-27)

- Database ✓ connected, Redis ✓ connected.
- **Scheduler is DISABLED** on staging — a production-readiness item (enable it in
  production so reservation expiry and other scheduled jobs run).
- Email delivery not configured (see `docs/email/SMJ_EMAIL_SETUP.md`).
- No pending migrations; developer mode off; 1 company (setup complete).
