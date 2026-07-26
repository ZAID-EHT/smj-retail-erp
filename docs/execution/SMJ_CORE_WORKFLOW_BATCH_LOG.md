# SMJ Core Wholesale Workflow — Batch Log

Append-only log of logical batches. Newest at the bottom.

## Batch 0 — Preflight & audit (2026-07-24)
- Confirmed branch `full-feature-parity` @ `e15c37e`, clean tree.
- Confirmed both sites exist. `staging.local` = frappe+erpnext+my_store_ui only
  (clean isolated test site). `site1.local` carries the full app stack + business data.
- Created recovery tag `pre-smj-core-workflow-20260724-1140`.
- Took full `staging.local` backup (`--with-files`); DB 1.3 MiB (lean test site).
- Audited Smart Sales (`SmartSalesPage.vue`, `api.py`), reservation
  (`wholesale/reservation.py`), credit (`wholesale/credit.py`).
- Recorded four confirmed defects (see mission-state JSON `defects_found`).

## Batch 1 — Core spine (Phases 1-3), commit 524d01f (2026-07-24)
- Customer-first Smart Sales: catalogue/add/qty/submit gated on selected customer;
  out-of-stock badge + disabled add; "Select a customer to begin the order".
- Customer-specific pricing: `get_bootstrap(customer=…)` prices against the
  customer's own selling Price List; new `get_cart_pricing` uses ERPNext
  `get_item_details` (Item Price + Pricing Rules) to reprice the cart + return
  per-line stock status. No pricing logic in Vue.
- Server-side stock recheck in `create_draft_sales_order` (reject over-available).
- `reserve_sales_order` bounded retry-on-deadlock + friendly message.
- Tests: test_smart_sales_core (5) PASS; test_frontend_layout (8, +1 new) PASS;
  regression suites test_wholesale_credit (7), test_stock_action_parity (7) PASS;
  frontend build clean.
- Recorded pre-existing staging search.py failure (not ours) in BLOCKERS.

## Batch 2 — FIFO verification (Phase 4), commit 9d4dbdc (2026-07-24)
- Controlled FIFO test on staging via standard Stock Entries: outgoing 12,400 exact,
  remaining 8 @ 9,600 exact. Doc: SMJ_FIFO_VERIFICATION.md. Fixtures cleaned up.

## Batch 3 — Quick Create menu (Phase 6), commit 8811341 (2026-07-24)
- get_quick_create_actions: 22 real create routes from the universal registry,
  permission-filtered, grouped; QuickCreateMenu.vue (teleport, search, keyboard,
  focus return, mobile). test_quick_create (4) PASS incl. no-dead-route check.

## Batch 4 — Simplified entry (Phase 7), commit 07e3447 (2026-07-24)
- Supplier curated add form via universal engine; verified Customer/Item already
  sectioned in form_schemas.py. Recorded item-pricing-in-custom-fields defect.
  test_universal_frontend (24) PASS.

## Batch 5 — Reservation retry (Phase 3 / Scenario 5), commit 5a67ec2 (2026-07-24)
- Deterministic verification of bounded retry-on-deadlock + friendly message.
  test_reservation_retry (3) PASS. Doc SMJ_RESERVATION_CONCURRENCY_RESULT.md.

## Final regression (2026-07-24): 59 backend tests green across 7 modules; FIFO
## dev-script exact; frontend build clean (201 modules).

---

## Batch: Phase 7/8 recovery and completion (2026-07-26)

Started from `e9e71e2` with unverified code in the worktree. Tag
`pre-smj-phase78-recovery-20260726-1740`; backup `20260726_174038-staging_local-*`.

| Step | Outcome |
|------|---------|
| Worktree inventory | 3 modified + 4 untracked files; nothing unrelated touched |
| Verified reported staging change | `Wholesale Price List` selling=1 confirmed; **buying still 1** — corrected to 0 after re-checking 0 references |
| Phase 7 test run | 7 green as-written; probing then found the `Item Manager` permission defect the suite could not catch |
| Phase 7 hardening | permission pre-flight, duplicate convergence, legacy NULL-UOM adoption → **14 tests** |
| Phase 8 first run | **4 errors** — `Email Account.disabled` does not exist (OperationalError 1054) |
| Phase 8 fixes | real email schema, manager gate, removed mid-request commits, self-lockout guard → **28 tests** |
| Phase 8 frontend | `/admin/access-control`, 5 sections + `search_users`; CRUD deliberately not duplicated |
| Acceptance | scenarios 10 and 11 automated (**3 tests**); all 11 mapped in a matrix |
| Browser matrix (1st run) | **29 failures** — Access Control dead at every viewport |
| Root cause | route absent from server-side `ROUTE_REGISTRY`; then a latent `unquote(None)` 500 on the optional group |
| Browser matrix (final) | **60/60, 0 problems**, six viewports |
| Full regression | **142 backend tests green**, 12 modules, 0 failures |
| Cleanup | 0 `Item Price` rows, no residual test users |

Commits: `ba2e1dc`, `0667a5d`, `eec512b`, `4a42f42`, `2862160`, `ea92d16`, `f7c7cbe`.
