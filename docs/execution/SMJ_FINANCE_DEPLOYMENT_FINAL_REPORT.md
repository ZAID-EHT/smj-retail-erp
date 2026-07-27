# SMJ Finance / Fresh-Install / Deployment — Final Report

Date 2026-07-27. Branch `full-feature-parity`. Start `13b3da1` (v1.0.0-rc2).
Final `4e374c9`. New tag `v1.0.0-rc3`. Recovery tag
`pre-smj-finance-deployment-20260727-0941`. Backup `20260727_094121-staging_local-*`.

## Finance verification (authoritative, from the ledger)
- The "impossible" reported figure **4,048,825,204 exists nowhere in the repo** — a
  concatenation of corrected profit 4,048,**006** and corrected expense 4,**825,204**.
- Profit before correction: **15,868,706**. Overstatement: **11,820,700**.
  Corrected profit: **4,048,006** (arithmetic check passes). Trial Balance balanced.
- Single root cause (voucher-level): 3 Material Receipt Stock Entries
  (MAT-STE-2026-00001/2/3) crediting the Expense account Stock Adjustment.

## Correction package
- `my_store_ui/finance/opening_stock_correction.py`: inspect / dry_run /
  prepare_draft / verify_after / apply.
- Correction: Dr Stock Adjustment 11,820,700 / Cr Opening Balance Equity 11,820,700,
  dated 2025-07-01.
- Guardrails: allowlisted sites only, site1.local refused; refuses wrong company /
  vouchers / amount / already-applied / unbalanced-TB; idempotent; reversible.
- Dry-run (savepoint) reconciles exactly; **apply is NOT run** — requires
  `confirm='11820700:APPROVED'` (accountant sign-off). 5 tests green.

## Fresh install
- `scripts/verify_fresh_install.sh` — static-validated, refuses protected/existing
  sites, never echoes the root password, restores the default site. Live run blocked
  (MariaDB root); setup code covered by `test_setup_wizard` (6 tests).

## SMTP
- Email admin System-Manager-gated, never returns/logs a credential (4 tests).
  Real SMTP is external; production checklist provided.

## Hetzner deployment package
- `deployment/`: pinned apps.json, compose.yaml (10 services; DB/Redis unpublished;
  frontend localhost-bound), Caddy TLS override, .env.example (secrets git-ignored),
  8 scripts (all `bash -n` clean). Compose statically valid. Live deploy external.

## Testing
- Backend: **338 tests, 0 failures** (42 modules + the correction module's 5).
- Frontend build clean. Browser: **90/90**, six viewports.
- Secret scan: clean. Migrations clean.

## Safety
- `site1.local` fingerprint identical to the Phase 0 baseline — **untouched**.
- No direct ledger edits; correction is a standard (draft) JE. No permission bypass.
- No credentials committed. No Windows Chrome; browser via Playwright API; no
  process killed by name. Backups recorded.

## Regression fixed
- The prior mission's warehouse-disabling cleanup had broken 5 test modules; the three
  empty test warehouses were re-enabled (they cannot be hard-deleted due to
  cancelled-SLE history).

## Verdict
**Code and deployment package are technically verified; financial posting,
infrastructure credentials and UAT remain external.**
