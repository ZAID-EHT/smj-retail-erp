# SMJ Fresh-Install Acceptance

## Status: code complete; physical fresh-site run environment-blocked

The first-time setup code path (detection → company creation → CoA + price lists +
checklist) is implemented and verified against the real ERPNext Company controller in
a rolled-back savepoint (`test_setup_wizard`). What could not be done here is a run on
a *physically empty* site, because creating one needs the MariaDB root password
(unavailable; documented in FINAL_READINESS_BLOCKERS).

## Reproducing on a fresh site (owner steps)

```
bench new-site freshsetup.local --db-root-password <pw> --admin-password <pw>
bench --site freshsetup.local install-app erpnext my_store_ui
bench --site freshsetup.local browse   # open /retail-erp
```

Expected:
1. With no Company, opening `/retail-erp` routes to `/retail-erp/setup`.
2. `get_setup_status().setup_required` is `true`.
3. A System Manager creates the company; the checklist flips to done and
   `ready_for_transactions` becomes true.
4. Chart of Accounts, default warehouses and the four Price Lists exist.
