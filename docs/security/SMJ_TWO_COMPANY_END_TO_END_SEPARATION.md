# SMJ Two-Company End-to-End Data Separation

Regression: `test_two_company_separation` (8 tests, green). Runs entirely in a
savepoint that is rolled back — staging is untouched.

## Setup
Two fictional companies (`SMJ Company A Test <hash>` / `SMJ Company B Test <hash>`),
each created via the standard Company controller (full Chart of Accounts), plus a
company-specific warehouse, customer and submitted Sales Order. Three users:
- **User A** — `User Permission` on Company A (apply to all doctypes)
- **User B** — `User Permission` on Company B
- **Manager** — permitted for both

## Verified separations

| Check | Result |
|-------|--------|
| User A reads Company A Sales Order | allowed |
| User A reads Company B Sales Order | **denied** (`has_permission` false) |
| User B reads Company A Sales Order | **denied** |
| User A warehouse list | Company B warehouse **absent** |
| Manager reads both companies' orders | allowed |
| App export path (User A) | Company B warehouse **not in export** |
| Company A order + Company B warehouse | **rejected** by the standard controller |
| Direct doc API read of Company B doc by User A | **PermissionError** |

## Why this holds
Separation is enforced by ERPNext's own permission engine via `User Permission` on
Company (applied to all company-scoped doctypes), not by app code. `frappe.get_list`
and `frappe.has_permission` respect it, and so does the app's `data_management`
export (which uses `get_list`). Invalid mixed-company documents are rejected by the
standard transaction controllers.

## Cleanup
The savepoint is rolled back in `tearDownClass`, with an explicit belt-and-braces
delete of the fictional companies/users. Verified: no test companies, users,
warehouses, transactions or permissions remain.
