# SMJ Core Workflow — Acceptance Scenarios

Every scenario below is tied to an **executable** check on `staging.local`, not a
narrative claim. Where a scenario is only partly automated, that is stated plainly.

Run everything with:

```bash
bench --site staging.local run-tests --module "my_store_ui.tests.<module>"
```

`staging.local` is the only site written to. `site1.local` is never touched.

---

## Status legend

| Mark | Meaning |
|------|---------|
| **Verified** | An automated assertion fails if the behaviour regresses |
| **Partly verified** | Core claim automated; one stated part is not |
| **Not automated** | Manual or environment-blocked; reason given |

---

## Scenario matrix

| # | Scenario | Status | Executable proof |
|---|----------|--------|------------------|
| 1 | Customers A and B get different valid pricing; changing customer reprices the whole cart | **Verified** | `test_smart_sales_core` — customer price-list resolution, customer-aware bootstrap pricing, cross-customer isolation |
| 2 | A customer-specific Pricing Rule applies only to its intended customer | **Verified** | `test_smart_sales_core` — Pricing Rule application + isolation |
| 3 | Zero Available-to-Sell shows Out of Stock, frontend blocks add, tampered API request rejected | **Verified** | `test_frontend_layout` (frontend gating) + `test_smart_sales_core.test_out_of_stock_item_reports_status_and_blocks_order` (server rejects a tampered order regardless of what the browser sends) |
| 4 | Quantity above Available-to-Sell rejected with no invalid residue | **Verified** | `test_smart_sales_core` — `create_draft_sales_order` rejects over-quantity lines; no draft is left behind |
| 5 | Two concurrent reservations do not over-reserve; loser gets a friendly message | **Partly verified** | `test_reservation_retry` (3 tests) covers bounded retry-on-deadlock and the friendly message. A **live two-process** demo is scripted at `dev_scripts/wholesale_concurrency_test.py` but was not re-run this session |
| 6 | Reservation lifecycle: reserve → reduce → amend → cancel → deliver → return | **Partly verified** | `test_wholesale_integration` + `test_stock_action_parity` cover reserve/cancel/deliver paths. The full six-step Actual/Reserved/Available trace is not asserted as one sequence |
| 7 | FIFO controlled test produces the expected valuation | **Verified** | `dev_scripts/fifo_verification.py` — 10@1000 + 2@1200 issue = **12,400 exact**, remaining 8 = **9,600 exact** |
| 8 | Full purchase workflow MR → RFQ → SQ → PO → PR → PI → Payment Entry | **Verified** | `test_purchase_workflow` |
| 9 | Quick Create is correctly filtered for representative roles | **Verified** | `test_quick_create` (4 tests) — permission-aware menu |
| 10 | Simplified forms create valid Customer, Supplier, Product, Sales Order, Purchase Order; product prices create standard Item Price records | **Verified** | `test_core_acceptance.test_scenario_10_simplified_forms_create_valid_master_records` (Customer + Supplier + Product, and asserts the three Item Price rows), plus `test_form_api` for the transaction forms and `test_item_price_sync` (14 tests) for pricing |
| 11 | User lifecycle: create → password → Role Profile → direct role → restriction → log in → allowed/denied routes → disable → login rejected → reactivate → login succeeds | **Verified** | `test_core_acceptance.test_scenario_11_user_lifecycle_end_to_end` + `test_scenario_11_a_wrong_password_is_refused` |

---

## Scenario 11 — how "login" is actually asserted

The lifecycle test does not fake the login check. It calls
`frappe.core.doctype.user.user.User.find_by_credentials()` — the same function
`frappe.auth.LoginManager.authenticate()` uses — and asserts:

- correct password → `is_authenticated` is true;
- a different password → not authenticated;
- after disable → the returned `enabled` flag is false, which is exactly the
  condition `LoginManager` fails the login on;
- after reactivation → authenticated again with the original credentials.

It also asserts the password is **never** readable back: the full document detail
returned by the universal engine is serialised and searched for the password.

Credentials are generated per run (`uuid4`) and never written into any document or
into this file.

---

## Finding — a Role Profile overrides direct roles (ERPNext behaviour, not a bug)

Scenario 11 originally asserted "assign a Role Profile **and** add a direct role on
top". That failed, and the cause is upstream Frappe, not this app:

`User.validate` calls `populate_role_profile_roles()` on **every** save, and that
method does `self.set("roles", [])` before re-appending the profile's roles. So while
a Role Profile is assigned, direct roles are cleared on every save and can never
coexist with it.

The acceptance test now asserts the real contract in both directions — profile
assigned → only profile roles apply; profile removed → direct roles apply — so a
future Frappe change to this behaviour is caught rather than silently absorbed.

The Access Control screen states this inline whenever a user has a profile assigned,
so an administrator is not left wondering why a role they added disappeared.

---

## Fixtures and cleanup

All acceptance fixtures are fictional and removed in `tearDown` / `tearDownClass`:

- `smj-acceptance-lifecycle@example.com`, `SMJ Acceptance Profile`
- `SMJ Acceptance Customer`, `SMJ Acceptance Supplier`, `SMJ-ACCEPTANCE-PRODUCT`
- every `User Permission` and `Item Price` row created for them

The permission tests in `test_item_price_sync` additionally use
`frappe.db.savepoint()` + `rollback(save_point=...)` so a deliberately failed save
leaves nothing behind — which is itself the assertion for atomicity.

---

## Remaining, stated plainly

- **Scenario 5** — the live two-process concurrency demo was not re-run this
  session. Unit-level retry behaviour is covered; the parallel demo is not.
- **Scenario 6** — the six-step reservation trace is covered across two modules
  rather than asserted as one continuous Actual/Reserved/Available sequence.
- **Browser matrix** — see `docs/execution/SMJ_CORE_WORKFLOW_FINAL_REPORT.md` for
  the truthful status of viewport verification.
