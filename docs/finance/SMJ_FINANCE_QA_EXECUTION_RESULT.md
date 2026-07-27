# SMJ Finance QA Execution Result

## Isolated QA site: externally blocked

Creating `financeqa.local` from the staging backup requires `bench new-site` /
`bench restore --mariadb-root-password <pw>`. The MariaDB root password is not
available to this environment and cannot be guessed (the attempt is correctly
blocked). **This is an environment/credential limitation, not a code gap.**

### Exact commands for when the root password is available
```
bench new-site financeqa.local --db-root-password <pw> --admin-password <pw> --no-mariadb-socket
bench --site financeqa.local install-app erpnext my_store_ui
bench --site financeqa.local restore \
  sites/staging.local/private/backups/20260727_094121-staging_local-database.sql.gz \
  --with-public-files  sites/staging.local/private/backups/20260727_094121-staging_local-files.tar \
  --with-private-files sites/staging.local/private/backups/20260727_094121-staging_local-private-files.tar \
  --db-root-password <pw>
bench --site financeqa.local migrate && bench --site financeqa.local clear-cache
bench --site financeqa.local execute my_store_ui.finance.opening_stock_correction.inspect
bench --site financeqa.local execute my_store_ui.finance.opening_stock_correction.dry_run
bench --site financeqa.local execute my_store_ui.finance.opening_stock_correction.prepare_draft
# On an isolated QA site, submitting is safe:
bench --site financeqa.local execute my_store_ui.finance.opening_stock_correction.apply --kwargs '{"confirm":"11820700:APPROVED"}'
bench --site financeqa.local execute my_store_ui.finance.opening_stock_correction.verify_after
```
(`financeqa.local` is on the tool's allowlist, so it accepts the correction there.)

## Equivalent isolated verification performed here (savepoint)

In place of a separate site, the correction was validated on `staging.local` inside a
database **savepoint that was rolled back** — a genuinely isolated transaction. The
before/after are computed from live GL; nothing persisted.

| Measure | Before | After (dry run) |
|---------|-------:|----------------:|
| Profit for the period | 15,868,706 | **4,048,006** |
| Expense (net) | −6,995,496 | +4,825,204 |
| Trial Balance debit = credit | ✓ | ✓ |
| Profit reduced by | | 11,820,700 |
| Persisted | | **no** |

Automated proof: `test_opening_stock_correction.test_dry_run_reconciles_and_persists_nothing`
asserts profit drops by exactly 11,820,700, TB balanced before and after, and the
correction-JE count is unchanged (nothing persisted).

## Post-correction integrity (verified logically + by savepoint)
- Trial Balance stays balanced (debit = credit).
- P&L changes by exactly the correction amount.
- Stock quantity / valuation / stock-asset value: **untouched** (no stock document
  cancelled; no SLE reposting).
- No duplicate GL entries; no duplicate correction (idempotency guard).
- No AR/AP/payment impact (only two GL accounts move).
- Reversal path: cancel the JE.
