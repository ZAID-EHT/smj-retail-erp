# SMJ User and Access — Test Report

Recorded 2026-07-26 on `staging.local`. Every number below is a real run, not an
estimate. Model: `SMJ_USER_ROLE_ACCESS_MODEL.md`.

## Backend totals

| Module | Tests | Result |
|--------|------:|--------|
| `test_item_price_sync` | 14 | OK |
| `test_access_management` | 28 | OK |
| `test_core_acceptance` | 3 | OK |
| `test_standalone_frontend` | 12 | OK |
| `test_universal_frontend` | 24 | OK |
| `test_form_api` | 14 | OK |
| `test_frontend_layout` | 9 | OK |
| `test_quick_create` | 4 | OK |
| `test_navigation_search` | 11 | OK |
| `test_smart_sales_core` | 5 | OK |
| `test_purchase_workflow` | 7 | OK |
| `test_create_routes` | 11 | OK |
| **Total** | **142** | **0 failures, 0 errors** |

Frontend build: clean, **204 modules**.
Browser matrix: **60/60 checks, 0 problems**, across six viewports.

## What is actually proven about access

### Denial

| Claim | Test |
|-------|------|
| A non-manager is rejected by **every** access endpoint, whatever the browser sends | `test_non_manager_cannot_reach_any_endpoint` (9 endpoints) |
| The user directory is manager-only | `test_user_directory_is_manager_only` |
| Email status is manager-only | `test_email_status_is_not_readable_by_a_non_manager` |
| An arbitrary DocType cannot be used as a restriction | `test_restriction_doctype_is_allowlisted` |
| A restriction value that does not exist is refused | `test_restriction_rejects_a_value_that_does_not_exist` |
| Protected accounts cannot have sessions revoked | `test_protected_accounts_cannot_have_sessions_revoked` |
| A wrong password is refused | `test_scenario_11_a_wrong_password_is_refused` |
| Pricing a product without `Item Price` rights is refused, atomically | `test_pricing_a_product_without_item_price_rights_is_refused_atomically` |

### Non-leakage

| Claim | Test |
|-------|------|
| The user directory returns no password, hash, salt, reset key, API key or secret | `test_user_directory_never_returns_credentials` |
| Email status returns no credential or SMTP field | `test_email_status_never_returns_credentials` |
| A set password is never readable back through the document API | `test_scenario_11_user_lifecycle_end_to_end` (serialises the whole detail response) |
| No secret reaches the rendered DOM | browser matrix, every route × every viewport |

### Correctness of the access report

| Claim | Test |
|-------|------|
| Effective access is evaluated backend-side for the **target** user | `test_effective_access_is_backend_evaluated_for_the_target_user` |
| The report cannot drift from `frappe.has_permission` | `test_effective_access_matches_frappe_has_permission` |
| Restrictions are standard `User Permission` documents | `test_restrictions_use_standard_user_permission_documents` |
| Role counts are real, from `Has Role` | `test_role_overview_reports_real_counts_and_risk` |
| Role grants come from `DocPerm` | `test_role_permission_summary_comes_from_docperm` |

### Self-lockout

| Claim | Test |
|-------|------|
| A manager cannot disable their own account | `test_a_manager_cannot_disable_their_own_account` |
| A manager cannot remove their own System Manager role | `test_a_manager_cannot_remove_their_own_system_manager_role` |
| A manager can still disable a **different** user | `test_a_manager_may_still_disable_a_different_user` |

### Lifecycle

`test_scenario_11_user_lifecycle_end_to_end` runs create → set password → assign
Role Profile → direct role → company and warehouse restriction → verify login →
allowed vs denied documents → disable → **login refused** → reactivate → login
succeeds. Login is asserted through `User.find_by_credentials`, the same function
`LoginManager.authenticate` uses.

## Honest gaps

- **Role-by-role denial breadth.** Denial is proven for a Sales User and for an Item
  Manager. Purchase User / Stock User / Accounts User are *not* separately asserted
  against the access endpoints; the gate is a single `System Manager` check, so the
  Sales User case exercises the same code path, but the broader matrix in
  `SMJ_ROLE_PERMISSION_MATRIX.md` predates this session and was not re-run.
- **Session revocation** is asserted to zero the active count; it is not asserted
  from a second live browser session.
- **Two-process concurrency** (Scenario 5) has unit-level coverage only this session.
