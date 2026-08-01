# SMJ Wholesale Operations — Blockers and External Requirements

Only genuine external requirements are recorded here. Unfinished development is
never classified as external.

## External requirements (owner action needed)

| # | Requirement | Owner action | Blocks |
|---|---|---|---|
| 1 | Opening-stock financial correction | Accountant approval before submitting the guarded correction (`finance/opening_stock_correction.py`) | Carried over from the finance mission; not re-opened by this mission |
| 2 | Real SMTP credentials | Owner supplies outgoing mail account | Email delivery of statements/receipts only; all document generation is verified without it |

## Environment limitations (not defects)

| # | Limitation | Effect |
|---|---|---|
| 1 | staging.local has a single Company (`SMJ Retail ERP`) | `test_cross_company_warehouse_denied` skips; cross-company denial is covered instead by suites that create their own second company |
