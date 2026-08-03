# SMJ Sales Team Integration — Mission State

## Repository position at start

| Item | Value |
|---|---|
| Bench | `/home/zaidh/frappe-bench` |
| App | `apps/my_store_ui` |
| Branch | `full-feature-parity` |
| Starting commit | `65ecf4bc5d903a308feb9818c4c05ab0a02b4e43` |
| Starting release tag | `v1.0.0-rc8` |
| Recovery tag | `pre-smj-sales-team-integration-20260803-1813` (already present at HEAD from the preceding session; not overwritten) |
| Test site | `staging.local` |
| Protected site | `site1.local` |

### Worktree at start

Tracked files were clean. Four untracked paths were carried in from the preceding
session and are genuine work in progress, so they were kept rather than cleaned:

```
my_store_ui/dev_scripts/audit_sales_team_model.py
my_store_ui/my_store_ui/doctype/retail_sales_team/__init__.py
my_store_ui/my_store_ui/doctype/retail_sales_team_member/__init__.py
my_store_ui/my_store_ui/doctype/retail_sales_team_snapshot/
```

The two `__init__.py` files belong to doctypes whose `.json`/`.py` were already
committed — they were simply missed by the previous `git add`. Committing them is a
correctness fix, not new work: without them the doctype packages are not importable
from a fresh clone.

## Backup

```
sites/staging.local/private/backups/20260803_182238-staging_local-database.sql.gz      2.4 MiB
sites/staging.local/private/backups/20260803_182238-staging_local-files.tar           10.0 KiB
sites/staging.local/private/backups/20260803_182238-staging_local-private-files.tar   10.0 KiB
sites/staging.local/private/backups/20260803_182238-staging_local-site_config_backup.json
```

Backups are inside `sites/`, which is outside the app repository. Nothing from the
backup is committed.

## site1.local fingerprint (read-only)

Taken before any change, to be repeated at the end.

```
{"Batch": 0, "Customer": 3, "Delivery Note": 0, "GL Entry": 44, "Item": 11,
 "Payment Entry": 5, "Purchase Invoice": 6, "Purchase Order": 10,
 "Purchase Receipt": 0, "Sales Invoice": 7, "Sales Order": 7,
 "Stock Ledger Entry": 17, "User": 3}
SHA f51fedb5a9ac68e27b1515daee5cdf2f90490a22c07925960dd0acb4d123d9c3
MATCHES_BASELINE True
```

## Baseline reproduction

| Check | Reported | Measured |
|---|---|---|
| Focused Sales Team backend tests | 37/37 | 37/37 in 7.9 s |
| Full backend suite | 673, 0 failures | see log |
| Frontend build | passes | see log |
| Browser matrix | 210/210 viewport checks | see log |

Measured results and any drift are recorded in
`SMJ_SALES_TEAM_INTEGRATION_LOG.md`.
