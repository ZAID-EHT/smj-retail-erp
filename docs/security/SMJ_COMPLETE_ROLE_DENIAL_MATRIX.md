# Complete Role-Denial and Privilege-Escalation Matrix

Verified on `staging.local`, 2026-07-26. Regression: `test_role_denial_matrix`
(7 tests, green). Extends the single-role denial in `test_access_management` to
every representative role.

## Principle

The security boundary is the **server-side endpoint gate**, not menu hiding. Every
check below calls the access-management endpoint **directly** as the role — as a
tampered browser would — and asserts the server refuses.

## Roles exercised

Sales User, Sales Manager, Purchase User, Purchase Manager, Stock User,
Stock Manager, Accounts User, Accounts Manager, Item Manager (all created as
fictional staging users), plus a disabled user, a System Manager, and a victim
account. All removed afterwards.

## Endpoints tested per role

`get_user_access_overview`, `search_users`, `get_role_overview`,
`get_role_permission_summary`, `get_role_profile_overview`,
`get_role_profile_change_impact`, `get_restriction_options`,
`set_user_restrictions`, `revoke_user_sessions`, `get_email_configuration_status`.

## Results

| Check | Roles | Result |
|-------|-------|--------|
| Direct call to every endpoint | all 9 non-manager roles | **PermissionError** — 9 roles × 10 endpoints all denied |
| Payload manipulation (`user=self`, unknown DocType) | Accounts Manager | denied — the gate runs before any allowlist logic |
| Escalate a victim to System Manager via the universal save path | Sales Manager | denied — cannot reach `update_document` for User; victim never gained the role |
| Disabled user authenticates | disabled | refused (`enabled=0`, which `LoginManager` fails on) |
| Enabled user authenticates | Sales User | allowed (correct password) |
| System Manager reaches the endpoints | System Manager | allowed |
| Denied response leaks target user data | Stock User → view Administrator | message contains no email, no `Administrator` |

## What this proves

- **Menu hiding is not the security boundary** — the same endpoints a hidden menu
  would call are refused at the server for every unauthorised role.
- **Payload manipulation does not create access** — forging the target user or an
  arbitrary DocType still hits `PermissionError`.
- **No privilege escalation** — a Sales Manager cannot grant System Manager to
  another user; the universal User save path is unreachable without the role.
- **Disabled users cannot authenticate**, and **protected accounts stay protected**
  (from `test_access_management`: Administrator/Guest cannot be disabled or have
  sessions revoked).
- **Self-lockout is prevented** (from `test_access_management`: a manager cannot
  disable their own account or drop their own System Manager role).
- **Denied responses do not leak private user information.**

## Coverage notes (honest)

- Company/Warehouse/Printing/Data-Import/Financial-config endpoints are covered by
  their own phases' permission tests (Phases 8–12) and the universal engine's
  per-DocType `frappe.has_permission` checks, not re-listed here.
- The universal generated CRUD (Users/Roles/Role Profiles at `/admin/*`) is System
  Manager gated in `universal/registry.py`, enforced server-side on every
  create/update/delete.
