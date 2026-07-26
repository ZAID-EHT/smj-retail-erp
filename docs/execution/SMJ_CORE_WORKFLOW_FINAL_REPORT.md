# SMJ Core Wholesale Workflow — Final Report

Recovery and completion mission, **2026-07-26**. Supersedes the 2026-07-24 interim
report (whose commit pointers and "remaining" list are now out of date).

## What this mission was

A previous session stopped mid-work and left **valid-looking but entirely unverified**
code in the working tree. This mission recovered it, verified every line against a
live site and a real browser, fixed what was wrong, and committed it.

Nothing was discarded, reset or rewritten from scratch.

| | |
|---|---|
| Starting branch | `full-feature-parity` |
| Starting commit | `e9e71e2` |
| Final commit | `f7c7cbe` |
| Recovery tag | `pre-smj-phase78-recovery-20260726-1740` |
| Backup | `20260726_174038-staging_local-*` |
| Final worktree | clean |

## Verified totals

| | Result |
|---|---|
| Backend tests | **142 green** across 12 modules — 0 failures, 0 errors |
| Frontend build | clean, **204 modules** |
| Browser matrix | **60/60 checks, 0 problems**, six viewports |
| Acceptance scenarios | 9 Verified, 2 Partly verified |
| Staging cleanliness | 0 `Item Price` rows, no residual test users |

## The six defects the previous session left behind

Three were invisible to the test suite and were only found by probing the live site
or driving a real browser.

| # | Defect | How it was found | Severity |
|---|--------|------------------|----------|
| 1 | Item Price sync **broke product creation for `Item Manager`** — `Item Price` is master data in stock ERPNext v15, and the suite runs as Administrator, which bypasses permission checks | permission probe | High |
| 2 | `Wholesale Price List` left `buying=1`, so the marked-up wholesale rate was selectable as a **purchase cost** | schema probe | Medium |
| 3 | Email status queried `Email Account.disabled`, **which does not exist** — `OperationalError 1054` on every call, taking 4 tests down | test run | High |
| 4 | **Self-lockout possible** — Frappe protects only Administrator/Guest, so a System Manager could disable their own account or drop their own System Manager role | source audit | High |
| 5 | Access Control was a **dead route** at all six viewports — absent from the server-side `ROUTE_REGISTRY` | browser matrix | High |
| 6 | Optional route groups returned **HTTP 500** — `unquote(None)` raises; latent for any future optional group | browser matrix | Medium |

All six are fixed, each with regression coverage.

## Phase 7 — Item Price synchronisation

Products created through the Retail ERP stored prices only in `custom_*` fields, so
ERPNext's pricing engine never saw them: site-wide `Item Price` count was **0**.

`save_entity_form` now mirrors purchase, wholesale and retail prices into standard
`Item Price` documents. Mapping settled from data, not guessed:

| Item field | Price List | Required flag |
|---|---|---|
| `custom_purchase_price` | Buying Settings → `Standard Buying` | `buying` |
| `custom_wholesale_price` | `Wholesale Price List` | `selling` |
| `custom_retail_price` | `Retail Price List` (23 of 26 customers default to it) | `selling` |

Proof it works: `test_synced_price_is_visible_to_the_pricing_engine` asserts
`get_item_details` returns the synced retail rate.

Behaviour: updates rather than duplicating; deletes a cleared price; adopts legacy
`NULL`-UOM rows; converges duplicates; **never** touches a batch-, party- or
other-UOM-specific price; refuses to write a price the engine could never apply; and
gates on `Item Price` permissions before the first write, failing atomically.

**14 tests.** Detail: `docs/ui/SMJ_SIMPLIFIED_ENTRY_FORMS.md`.

## Phase 8 — Access management

Backend (`access_management.py`) plus the first UI for it at `/admin/access-control`
— before this it was reachable only over the raw API with no frontend reference.

Five sections: Effective Access, User Permissions, Roles, Role Profiles, Email
Delivery. User/Role/Role Profile **CRUD was not rebuilt** — it already exists at
`/admin/users`, `/admin/roles`, `/admin/role-profiles`, so the screen links to it.

Every access decision is made server-side for the target user via
`frappe.has_permission(..., user=…)`; a test asserts the report cannot drift from the
permission engine. No endpoint uses `ignore_permissions`. Restrictions are standard
`User Permission` documents against a fixed DocType allowlist.

**28 tests.** Detail: `docs/security/SMJ_USER_ROLE_ACCESS_MODEL.md`.

## Acceptance scenarios

Full matrix in `docs/workflows/SMJ_CORE_ACCEPTANCE_SCENARIOS.md`.

- **Verified (9):** 1, 2, 3, 4, 7, 8, 9, 10, 11
- **Partly verified (2):** 5 (live two-process demo not re-run; unit-level retry
  coverage exists), 6 (six-step reservation trace covered across two modules rather
  than one continuous sequence)

Scenario 11 asserts login through `User.find_by_credentials` — the same function
`LoginManager.authenticate` uses — so "login refused when disabled" is a real
assertion, not a restatement of the `enabled` flag.

## Browser verification

Linux-native Playwright Chromium, located through `chromium.executablePath()` —
never a guessed path, never Windows Chrome — and always closed through the Playwright
API. No process was killed by name.

| Viewport | Result |
|---|---|
| 1920×1080 | 10/10 |
| 1440×900 | 10/10 |
| 1024×768 | 10/10 |
| 768×1024 | 10/10 |
| 390×844 | 10/10 |
| 360×800 | 10/10 |

Checked per route: HTTP status, dead routes, horizontal overflow, console and page
errors, and that no stored secret reaches the DOM.

## Staging changes made

One, applied only after re-verifying it was safe: `Wholesale Price List`
`buying` 1 → 0. Zero Item Prices, customers, suppliers, customer groups and
purchasing documents referenced it. Applied by
`dev_scripts/fix_wholesale_price_list_selling_only.py`, which re-checks every one of
those and **refuses to act** if any is non-zero.

`site1.local` was never touched.

## Remaining, stated plainly

**External setup (cannot be done from this repository):**
- No outgoing `Email Account` on staging, so welcome/reset emails cannot be
  delivered. Onboarding uses an administrator-set password. The UI says so.
  See `docs/security/SMJ_EMAIL_ONBOARDING_STATUS.md`.

**Ordinary remaining development:**
- Scenario 5 live two-process concurrency demo.
- Scenario 6 as one continuous Actual/Reserved/Available trace.
- Role-by-role denial breadth for Purchase/Stock/Accounts users against the access
  endpoints (the single System Manager gate is already exercised by the Sales User
  case).
- Product form field gaps: Colour, Purchase/Selling UOM, Default Warehouse, Reorder
  Level, Safety Stock, Published — some need a Custom Field or child-table support.

## Production readiness

The core wholesale spine, pricing, stock gating, FIFO, purchasing, quick create,
simplified entry forms and access management are implemented, verified on staging and
browser-checked. The one genuine gap to production is **email configuration**, which
is an infrastructure task, not a code defect.
