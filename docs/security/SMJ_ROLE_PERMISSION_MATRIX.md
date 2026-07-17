# SMJ Retail ERP — Role Permission Matrix

**Date:** 2026-07-18 · **Site:** staging.local · **Method:** real backend
enforcement, not configuration reading. For every role, a dedicated test
user was created with **only** that role, then impersonated via
`frappe.set_user()` to call the actual `frappe.has_permission()` function
— the same function every ERPNext controller and REST API endpoint calls
internally. Nothing here is inferred from the Role Permission Manager
screen alone.

Test script (reusable):
`apps/my_store_ui/my_store_ui/dev_scripts/security_matrix_test.py`.

## Roles tested (11, per mission scope)

`Administrator` (superuser, bypasses all permission checks by definition
— not re-tested, this is core Frappe behavior, not project-specific),
`System Manager`, `Sales User`, `Sales Manager`, `Purchase User`,
`Purchase Manager`, `Stock User`, `Stock Manager`, `Accounts User`,
`Accounts Manager`, `Restricted normal user` (a user with **zero**
elevated roles — the "All"/default baseline).

## Matrix — doctype-level access granted per role

`R`=read `W`=write `C`=create `S`=submit `X`=cancel `D`=delete. Blank = no
access.

| Role | Sales Order | Sales Invoice | Purchase Order | Purchase Invoice | Purchase Receipt | Stock Entry | Payment Entry | Journal Entry | GL Entry |
|---|---|---|---|---|---|---|---|---|---|
| System Manager | | | | | | | | | |
| Sales User | R W C S X D | | | | | | | | |
| Sales Manager | R W C S X D | | | | | | | | |
| Purchase User | | | R W C S X D | R | R W C S X D | | | | |
| Purchase Manager | | | R W C S X D | | | | | | |
| Stock User | R | R | R W C S X D | R W C S X D | | | | |
| Stock Manager | | | | | R W C S X D | R W C S X D | | | |
| Accounts User | R | R W C S | | R W C S X | R | | R W C S X D | R W C S X D | R |
| Accounts Manager | | R W C S X D | | R W C S X D | | | R W C S X D | R W C S X D | R |
| Restricted | | | | | | | | | |

(All roles additionally have `read`/`write` on their **own** `User`
document only — see the "Restricted user and the User doctype" note
below; no role in this matrix except System Manager has broader `User`
access, and System Manager's own-User access was not separately
distinguished from the "own record only" case in this pass.)

## Honest findings — real, not assumed

1. **`System Manager` alone grants almost nothing on transactional
   doctypes.** A user with only the `System Manager` role (no
   `Administrator`, no business role) cannot read or write Sales Orders,
   Purchase Orders, Stock Entries, or any financial document. This
   matches ERPNext's actual shipped `DocPerm` configuration — `System
   Manager` is designed for system administration (users, roles, DocType
   settings), not day-to-day business transactions. **This is standard
   ERPNext behavior, confirmed directly against `tabDocPerm`, not a
   misconfiguration in this project.**

2. **`Purchase Manager` has zero access to Purchase Receipt and Purchase
   Invoice.** Confirmed directly against `tabDocPerm`: ERPNext ships no
   `DocPerm` row for `Purchase Manager` on either doctype at all — only
   `Purchase Order`. Receiving is `Purchase User`/`Stock User`/`Stock
   Manager` territory; invoicing is `Accounts User`/`Accounts Manager`
   territory. A business owner who assumes "Manager" implies "sees
   everything downstream" would be surprised by this — **flagged as a
   product/business decision for the client to make (add `DocPerm` rows
   if they want it), not silently patched by this verification mission.**

3. **`Restricted` user's apparent `User: read/write` is not a security
   gap.** Every authenticated Frappe user can read/update their own user
   profile (change password, update contact info) — `has_permission()`
   without a specific document returns `True` if *any* row (including
   "my own record") is writable. Confirmed with a real write attempt:
   the Restricted user tried to **create** an arbitrary new `User` record
   and was correctly blocked with a `PermissionError` (see
   `SMJ_BACKEND_PERMISSION_TESTS.md`). Self-service on one's own account
   is expected behavior, not a boundary violation.

4. **`Sales User` and `Sales Manager` have identical Sales Order
   permissions.** Both get full CRUD + submit + cancel + delete. This
   matches ERPNext's default design — the User/Manager split for Selling
   is enforced elsewhere (discount limits, price list rate overrides via
   Selling Settings), not at the doctype-permission level. Confirmed
   against `tabDocPerm`, not assumed.

5. **`GL Entry` is read-only for every role tested, including Accounts
   Manager.** No role can directly write a GL Entry — matches this
   project's own `TRANSACTIONS.md` rule (never write the GL directly;
   only submitted transactional documents may post to it) and confirms
   the database-level rule is *also* enforced by ERPNext's own
   permission system, not just by convention.

## What this does NOT cover (honestly scoped)

- Field-level permissions (e.g., "can edit rate" restrictions) — out of
  scope for this pass, doctype-level only.
- User Permissions (row-level restriction to a specific Company/
  Warehouse/Territory) — not tested in this batch; every test user in
  this pass had no User Permission records, so results reflect role-level
  `DocPerm` only. Flagged as a follow-up if the client uses multi-company
  segregation.
- Workspace/UI visibility (what menu items a role sees) — covered
  separately by Phase 6's UI workspace audit.
