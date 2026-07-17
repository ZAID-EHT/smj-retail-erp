# SMJ Retail ERP — Backup / Restore Verification (Phase 10)

**Date:** 2026-07-18 · **Source site:** staging.local · **Method:** a
real, full `bench backup --with-files`, restored into a genuinely
separate, temporary site (`smj-restore-test.local`), verified by direct
comparison, then torn down. **`site1.local` and `staging.local` were
never touched** — the restore target was a brand-new site created
specifically for this test.

## Steps performed

1. `bench --site staging.local backup --with-files` — produced a real
   database dump (1.3MiB compressed), plus public/private file archives.
2. `bench new-site smj-restore-test.local` — a fresh, empty site.
3. Installed `erpnext` and `my_store_ui` (the same app stack as
   staging.local) on the new site.
4. `bench --site smj-restore-test.local restore <backup>.sql.gz
   --with-public-files ... --with-private-files ...` — a real restore,
   not a copy of the raw database files.
5. Compared record counts and financial totals directly between
   `staging.local` and the restored site.
6. Verified the restored site's **application layer**, not just its
   database: `frappe.db.get_value("Sales Order", "SAL-ORD-2026-00001",
   "customer")` correctly resolved to `"ABC Traders"`, and a full `bench
   migrate` ran to completion with zero errors.
7. Tore down the temporary site (`bench drop-site`, which itself takes
   one final backup and archives the site directory rather than
   silently deleting it) and confirmed `staging.local` and `site1.local`
   were both unaffected.

## Verification results — exact match

| Metric | staging.local | Restored site | Match |
|---|---|---|---|
| Active Customers | 25 | 25 | ✅ |
| Submitted Purchase Orders | 67 | 67 | ✅ |
| Submitted Sales Invoices | 100 | 100 | ✅ |
| Submitted Sales Orders | 102 | 102 | ✅ |
| Total GL Entry debit (all-time, all rows) | 69,131,114.30 | 69,131,114.30 | ✅ |

Every metric checked matches **exactly**, to the last decimal. The
restored site's application layer also works correctly (real document
lookups resolve, a full framework migration completes cleanly).

## Verdict

Backup and restore is **verified working end-to-end** — not just "the
`.sql.gz` file exists," but a complete round-trip: backup → fresh site →
install same app stack → restore → data matches exactly → application
functions correctly → migration succeeds. This is the standard disaster-
recovery drill a production deployment would need to have proven at least
once, and it has now been proven on this project's real data.

## Safety notes

- `site1.local` was never referenced by any command in this test.
- `staging.local` was only ever read from (the backup command) — never
  written to.
- The temporary site's own final backup (taken automatically by
  `drop-site` before deletion) is preserved under
  `archived/sites/smj-restore-test.local/` if anyone needs to inspect it
  later.
