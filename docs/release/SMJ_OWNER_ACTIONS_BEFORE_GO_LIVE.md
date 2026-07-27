# SMJ Owner Actions Before Go-Live

Complete in this order. Each is external (needs approval or credentials).

## Action 1 — Accountant approval (finance correction)
1. Review `docs/finance/SMJ_OPENING_STOCK_CONFIRMED_ROOT_CAUSE.md`.
2. Confirm amount **LKR 11,820,700**, debit **Stock Adjustment**, credit
   **Opening Balance Equity**, posting date **2025-07-01**.
3. Review `docs/finance/SMJ_ACCOUNTANT_CORRECTION_PACKAGE.md`.
4. Approve or reject the Journal Entry (record decision).
5. Apply only after approval:
   `bench --site staging.local execute my_store_ui.finance.opening_stock_correction.apply --kwargs '{"confirm":"11820700:APPROVED"}'`
6. Verify: `...verify_after`; rerun P&L / Balance Sheet / Trial Balance / Stock Balance.
7. Save signed evidence in the evidence register.
> The financial submission is **not** executed by the delivery team.

## Action 2 — Genuine fresh-site test (needs MariaDB root)
1. Obtain the MariaDB administrative password (do not paste it into any file).
2. `scripts/verify_fresh_install.sh freshrelease.local` (prompts for the password).
3. It creates an empty site, installs apps, runs first-time setup, creates Company A
   and Company B, and verifies separation.
4. Save results in the evidence register.

## Action 3 — SMTP setup (needs SMTP credentials)
1. Create an outgoing `Email Account`: host, port, TLS/SSL, username, **write-only
   password**, `enable_outgoing`, `default_outgoing`.
2. Send a test email; test welcome + password-reset flows; check Email Queue.
3. Confirm scheduler + workers healthy; enable a scheduled report.
4. See `docs/email/SMJ_SMTP_PRODUCTION_CHECKLIST.md`.

## Action 4 — Hetzner rehearsal (needs Hetzner/registry/DNS)
Provision VPS → firewall (SSH/80/443 only) → SSH → Docker → registry login → build +
push pinned image → `deployment/scripts/preflight.sh` → create site → migrate → DNS →
HTTPS → backups → restore drill → smoke tests. See
`docs/deployment/SMJ_HETZNER_REHEARSAL_PLAN.md`.

## Action 5 — Client UAT
Run `docs/release/SMJ_CLIENT_UAT_CHECKLIST.md` with real users: login, roles,
customer/supplier/product, price lists, Smart Sales, reservation, delivery, invoice,
payment, purchasing, returns, credit/debit notes, printing, reports, multi-company,
mobile, permission denial.

## Action 6 — Final production approval
Require: accountant sign-off, correction applied, reports reconciled, fresh-site
passed, SMTP passed, HTTPS passed, backup + restore passed, UAT passed, rollback
ready, management approval.
