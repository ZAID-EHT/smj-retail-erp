# SMJ First-Time Setup Wizard

Route: `/retail-erp/setup` (any authenticated user can view; company creation is
System Manager gated). Backend: `my_store_ui/setup_wizard.py`. Tests:
`test_setup_wizard` (6, green).

## Detection

`get_setup_status()` reports `setup_required = (Company count == 0)` plus a readiness
checklist (Company, Chart of Accounts, Fiscal Year, Warehouses, Price Lists, Taxes,
Opening Stock, Users). Detection is readable by any authenticated user so the SPA can
route a fresh install to `/setup`; only a System Manager sees the create form and can
submit it.

## Company creation

`create_company()` uses the **standard ERPNext Company controller**, which itself
builds the Chart of Accounts, root cost center and default accounts on insert — no
ledger row is hand-written. It then ensures the four Price Lists the wholesale
workflow needs exist (Standard Selling, Standard Buying, Retail, Wholesale) and makes
the first company the global default. The whole operation is atomic (no mid-request
commit), so a failure rolls back cleanly.

Verified: `test_create_company_builds_coa_and_price_lists` creates a full company in a
savepoint, asserts the CoA and price lists exist, then rolls back — leaving staging
untouched.

## Environment limitation — physically fresh site

The mission asked for a separate `freshsetup.local` site tested from zero data.
Creating it needs the MariaDB root password, which is unavailable here (see
`docs/execution/SMJ_FINAL_READINESS_BLOCKERS.md`). Instead the empty-system code path
is exercised against the real Company controller in a savepoint. **Owner step to fully
close this:** create `freshsetup.local` with the root password, open
`/retail-erp/setup`, and confirm the redirect + wizard against a genuinely empty site.

## Setup routes (SPA)

`/setup`, `/setup/company`, `/setup/accounts`, `/setup/warehouses`, `/setup/pricing`,
`/setup/taxes`, `/setup/printing`, `/setup/users`, `/setup/opening-data`,
`/setup/review` all resolve to the wizard (the `:step` param is open-ended).
