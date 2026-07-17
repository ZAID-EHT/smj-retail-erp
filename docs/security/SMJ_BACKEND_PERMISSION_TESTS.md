# SMJ Retail ERP — Backend Permission Enforcement Tests

**Date:** 2026-07-18 · **Site:** staging.local

This is the proof-of-enforcement layer behind `SMJ_ROLE_PERMISSION_MATRIX.md`.
`frappe.has_permission()` tells you what the *config* says; these tests
prove ERPNext's ORM actually **rejects the write at the document level**,
which is what protects the business even if a UI check were ever missing
or a request came directly through the REST API.

Method: for each test, impersonate the real test user via
`frappe.set_user()`, attempt a genuine `doc.insert()` (no
`ignore_permissions`), and record whether ERPNext's own `PermissionError`
fires. Immediately followed by `frappe.set_user("Administrator")` cleanup.

## Results

| # | Test | Expected | Actual | Verdict |
|---|---|---|---|---|
| 1 | Restricted user (no roles) attempts to create a Sales Order | Blocked | `PermissionError` raised | ✅ PASS |
| 2 | Sales User attempts to create a Purchase Order (cross-department) | Blocked | `PermissionError` raised | ✅ PASS |
| 3 | Sales User attempts to create their own Sales Order (in-scope) | Allowed | Document inserted successfully | ✅ PASS |
| 4 | Purchase User attempts to create a Payment Entry (Accounts territory) | Blocked | `PermissionError` raised | ✅ PASS |
| 5 | Restricted user attempts to create a new User record | Blocked | `PermissionError` raised | ✅ PASS |
| 6 | Stock User attempts to create a Journal Entry (Accounts territory) | Blocked | `PermissionError` raised | ✅ PASS |

Raw output (verbatim from the test run):
```
REAL_WRITE_ATTEMPTS_JSON_START
{
  "restricted_user_create_sales_order": "BLOCKED (PermissionError): ",
  "sales_user_create_purchase_order": "BLOCKED (PermissionError): ",
  "sales_user_create_own_sales_order": "SUCCEEDED",
  "purchase_user_create_payment_entry": "BLOCKED (PermissionError): ",
  "restricted_user_create_user": "BLOCKED (PermissionError): ",
  "stock_user_create_journal_entry": "BLOCKED (PermissionError): "
}
REAL_WRITE_ATTEMPTS_JSON_END
```

## Why this matters more than the `has_permission()` matrix alone

`frappe.has_permission()` is a query against `DocPerm`/`User Permission`
config — it is possible (in a badly-built custom app) for a controller to
skip calling it and just call `.insert(ignore_permissions=True)`
unconditionally, silently bypassing security regardless of what the
matrix says. These 6 tests instead called the real `.insert()` method
with default arguments (`ignore_permissions` not set, defaults to
`False`), which forces Frappe's `PermissionError` check to run inside the
ORM itself — the same code path every REST API request and every UI
action goes through. All 6 rejected/allowed exactly as the matrix
predicted, meaning **the config and the actual enforcement agree** — no
drift between "what the Role Permission Manager says" and "what the
system actually does."

## Test hygiene

- All 10 test users (`smj.*.test@smjretail.local`) were created via a
  real `frappe.get_doc({"doctype": "User", ...}).insert(ignore_permissions=True)`
  call (as Administrator, the only account permitted to create users —
  this is the one place `ignore_permissions=True` is appropriate, since
  it is the setup step itself, not the test being measured).
- The one document that *did* get created (test #3's Sales Order) was
  deleted again by Administrator immediately after the test, before the
  next test ran.
- All 10 test users were deleted at the end of the batch
  (`cleanup_users()`, confirmed via `USERS_REMOVED` listing all 10
  emails). `staging.local`'s user list returned to just `Administrator`
  afterward.
- Reusable test script:
  `apps/my_store_ui/my_store_ui/dev_scripts/security_matrix_test.py`.
