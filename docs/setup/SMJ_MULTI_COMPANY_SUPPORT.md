# SMJ Multi-Company Support

After first-time setup, additional companies are created through the existing
**Administration → Companies** surface (`/retail-erp/admin/companies`), which is the
universal engine's System-Manager-gated Company CRUD, plus the setup wizard's
`create_company` for a guided path.

## What ERPNext provides (standard, not rebuilt)

- Per-company Chart of Accounts, cost centers and default accounts (built by the
  Company controller on insert).
- Per-company warehouses.
- Company-scoped reports and User Permissions (a user restricted to a company via a
  `User Permission` sees only that company's data — enforced by ERPNext's own query
  conditions, surfaced in Access Control → User Permissions).
- The company selector on Sales/Purchase transactions.

## Company separation

Data separation between companies is enforced by ERPNext's permission engine, not by
this app: a `User Permission` on Company restricts every company-scoped DocType. This
is the same mechanism verified in the role-denial matrix and acceptance suite.

## Verification status

- Company creation via the standard controller: **verified** (savepoint test).
- Multi-company selector / per-company separation: relies on standard ERPNext
  behaviour and User Permissions, which are covered by the access tests; a dedicated
  two-company end-to-end separation test on a fresh site is **environment-blocked**
  (no root password to build an isolated site) and is listed as ordinary remaining
  verification.
