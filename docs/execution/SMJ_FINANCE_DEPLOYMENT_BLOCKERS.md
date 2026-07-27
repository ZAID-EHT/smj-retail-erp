# SMJ Finance / Deployment — Blockers

## External requirements (not code defects)

### Accountant sign-off — opening-stock reclassification posting
- The correction is prepared as a **draft** Journal Entry; submitting it on staging
  or production requires accountant approval of the account and amount.
- Owner step: review `docs/finance/SMJ_ACCOUNTANT_CORRECTION_PACKAGE.md`, then run
  `correct_opening_stock_pnl.apply` (or the finance/ package apply) with the signed
  confirmation.

### MariaDB root password — QA / fresh-install sites
- `bench new-site financeqa.local` / `freshrelease.local` need `--mariadb-root-password`.
  Unavailable and not guessable. Mitigated: savepoint simulation + static-validated
  `scripts/verify_fresh_install.sh`.

### SMTP credentials — email delivery
- No outgoing Email Account. Onboarding uses admin-set passwords. Owner supplies SMTP.

### Hetzner credentials / DNS / registry / git push
- Deployment package is prepared but not deployed; requires server + DNS + registry
  credentials and git push access.

### Client UAT
- Requires real business participation.
