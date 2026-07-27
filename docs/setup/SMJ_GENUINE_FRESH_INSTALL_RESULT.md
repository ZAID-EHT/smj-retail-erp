# SMJ Genuine Fresh-Install Result

## Status: script complete + statically validated; live run credential-blocked

A genuine zero-business-data site run requires `bench new-site` with the **MariaDB
root password**, which is unavailable in this environment (and guessing is blocked).
This is an environment/credential limitation, not a code gap.

## What was done

- **`scripts/verify_fresh_install.sh`** created and statically validated:
  - `bash -n` syntax check: **passed**.
  - Refusal guardrails proven: refuses `staging.local` (exit 3) and `site1.local`
    (exit 3); refuses any already-existing site; requires the site name; requires a
    MariaDB root password (never echoed); restores the original default site on exit
    via a trap; does **not** auto-delete the site.
- The setup-flow code it exercises is already verified by `test_setup_wizard` (6
  tests), including full company creation via the standard controller in a savepoint.

## What the script does when run with credentials

1. Create a fresh empty site + install `erpnext` and `my_store_ui`, migrate.
2. `get_setup_status` → confirm `setup_required = true` (no company).
3. `create_company` (standard controller builds CoA, cost center, warehouses, price
   lists) → first company.
4. `create_company` again → second company (multi-company).
5. `get_setup_status` → confirm setup complete.

## Owner steps to close the live gap
```
scripts/verify_fresh_install.sh freshrelease.local
# (prompts for the MariaDB root password; never echoed)
```
Then, in the browser, confirm `/retail-erp` redirects to `/retail-erp/setup` on the
empty site, complete the wizard, add master data, and run a Sales/Purchase order.

## Company separation
Enforced by ERPNext User Permissions (verified at mechanism level in
`test_role_denial_matrix` and the access model). A dedicated two-company end-to-end
separation test belongs on this fresh site and is listed as ordinary remaining
verification (needs the site).
