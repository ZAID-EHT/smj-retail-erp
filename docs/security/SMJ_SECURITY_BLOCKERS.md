# SMJ Retail ERP — Security Blockers (Phase 5)

Per the mission's own rule ("do not classify ordinary unfinished work as
externally blocked"), this file only lists things that genuinely require
a decision or action from someone other than an autonomous coding agent.

## No genuine security blockers found

Phase 5's real backend permission tests (10 dedicated per-role test users,
`frappe.has_permission()` matrix across 9 doctypes, and 6 real `.insert()`
write-attempt tests across role boundaries) found **zero unauthorized
access** — every cross-boundary write attempt was correctly rejected by
ERPNext's own `PermissionError`, and every in-scope write attempt
correctly succeeded. See `SMJ_BACKEND_PERMISSION_TESTS.md` for the full
evidence.

## Items requiring a business decision (not a code fix)

These are not bugs. They are legitimate default ERPNext role-design
choices that the business owner should confirm match their intent before
go-live — listed here so they are not silently assumed either way.

1. **Should `Purchase Manager` be able to see Purchase Receipts and
   Purchase Invoices?** By default (confirmed against `tabDocPerm`), they
   cannot — only `Purchase Order`. If the client wants purchase managers
   to have downstream visibility, this requires adding `DocPerm` rows
   (a Role Permission Manager change, or a fixture), which is a
   deliberate business decision, not something this verification mission
   should apply unilaterally.
2. **Should `System Manager` (without `Administrator`) be granted access
   to business transactions?** By default it is not — System Manager is
   scoped to system administration only. If the client wants an IT-admin
   role that can also see sales/purchase/stock data, that also requires
   explicit `DocPerm` additions.
3. **User Permissions (row-level company/warehouse restriction) were not
   tested in this batch** — every test user had none configured. If SMJ
   Retail ERP ever becomes multi-company or multi-branch, User
   Permissions should be added and this test re-run to confirm row-level
   isolation, not just doctype-level access. Not a current gap (single
   company, single primary warehouse setup today) — flagged for the
   future.

## Environment blockers (carried forward, unrelated to security)

See `SMJ_MASTER_BLOCKERS.md` for `BLOCKER-001` (sudo overcommit) and
`BLOCKER-002` (RQ version drift) — neither affects permission enforcement,
both already documented and non-blocking.
