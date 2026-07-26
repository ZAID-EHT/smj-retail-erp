# SMJ User, Role and Access Model

How access is decided in the SMJ Retail ERP, and where each decision is enforced.
Companion documents: `SMJ_ROLE_PERMISSION_MATRIX.md` (which role gets what),
`SMJ_USER_ACCESS_TEST_REPORT.md` (what is proven), `SMJ_EMAIL_ONBOARDING_STATUS.md`.

## Principle

**Every access decision is made by the ERPNext permission engine on the server, for
the target user.** Nothing is inferred from frontend state, and no endpoint in this
app uses `ignore_permissions=True`.

The Access Control screen reports `frappe.has_permission(doctype, ptype, user=…)`,
`frappe.get_roles(user)` and `get_user_permissions(user)` — the same functions the
rest of ERPNext obeys. A regression test asserts the report cannot drift from
`frappe.has_permission`.

## Enforcement layers

| Layer | Enforces | Where |
|-------|----------|-------|
| Route guard (server) | which SPA routes a session may open | `services/frontend_routes.py` → `standalone.authorize_frontend_route` |
| Endpoint gate | System Manager for every access-management call | `access_management._require_user_manager` |
| DocType permission | read/create/write/submit/… per role | ERPNext `DocPerm`, via `frappe.has_permission` |
| User Permission | which *records* a user may see | standard `User Permission` documents |
| Field gating | which fields are readable/writable | `universal/api.py` `SUPPORTED_FIELD_TYPES`, `SPECIAL_WRITABLE_FIELDS`, `WRITE_ONLY_INPUT_FIELDS` |

The route guard is a **usability** boundary, not the security boundary: opening a
URL directly still fails at the endpoint gate and the DocType permission. That is
asserted — a non-manager calling every endpoint directly is rejected regardless of
what the browser sends.

## Where each capability lives

User, Role and Role Profile **CRUD** is served by the universal generated engine at
`/admin/users`, `/admin/roles`, `/admin/role-profiles`, all gated to System Manager
in `universal/registry.py`. The Access Control screen at `/admin/access-control`
adds what the CRUD pages cannot show and deliberately does not duplicate them:

| Surface | Route | Backed by |
|---------|-------|-----------|
| Effective Access | `/admin/access-control/access` | `get_user_access_overview` |
| User Permissions | `/admin/access-control/restrictions` | `get_restriction_options`, `set_user_restrictions` |
| Roles | `/admin/access-control/roles` | `get_role_overview`, `get_role_permission_summary` |
| Role Profiles | `/admin/access-control/profiles` | `get_role_profile_overview`, `compare_role_profiles`, `get_role_profile_change_impact` |
| Email Delivery | `/admin/access-control/email` | `get_email_configuration_status` |
| User directory | (all tabs) | `search_users` |

## Passwords

- Set and reset through the **write-only** `new_password` input
  (`WRITE_ONLY_INPUT_FIELDS`): accepted on create/update, never returned on any read
  path. The acceptance suite serialises a full user detail response and asserts the
  password does not appear in it.
- No endpoint returns a password, hash, salt, reset key, API key or API secret.
  `search_users` returns an explicit allowlist of safe columns, asserted by test.
- Because no outgoing email is configured on staging, onboarding uses an
  administrator-set password rather than a welcome link — see
  `SMJ_EMAIL_ONBOARDING_STATUS.md`.

## Restrictions (User Permission)

Restrictions are written as **standard `User Permission` documents**, so ERPNext's
own permission query conditions apply everywhere — there is no parallel restriction
mechanism to keep in sync.

The restrictable DocTypes are a fixed allowlist: Company, Warehouse, Customer,
Supplier, Territory, Project, Cost Center, Sales Person. An arbitrary DocType is
rejected with a `ValidationError`, so this can never become a generic
document-writing endpoint. A value the calling administrator cannot themselves read
is refused.

## Protected accounts and self-lockout

- `Administrator` and `Guest` cannot be disabled, deleted or signed out through this
  surface. Frappe guards them too; this is an additional explicit boundary.
- **A manager cannot lock themselves out.** They cannot disable their own account,
  and cannot remove their own System Manager role — including when the role would be
  lost by switching Role Profile. Frappe itself does *not* prevent this; the guard is
  ours, in `universal/api._guard_self_lockout`, and it still allows administering
  other users.

## Role Profiles override direct roles

`User.validate` calls `populate_role_profile_roles()` on every save, which clears
`roles` and re-applies the profile's. While a Role Profile is assigned, a direct role
cannot coexist with it. This is upstream Frappe behaviour, asserted in both
directions by the acceptance suite, and stated inline on the Access Control screen so
an administrator is not left wondering why a role they added disappeared.

## Item Price is master data

`Item Price` is restricted to `Sales Master Manager` and `Purchase Master Manager` in
stock ERPNext v15. `Item Manager` can create an Item but not price one. The product
form therefore gates on the exact `Item Price` permissions a save needs and fails
with a message naming those roles, rather than bypassing the check. An unpriced
product still saves. See `docs/ui/SMJ_SIMPLIFIED_ENTRY_FORMS.md`.
