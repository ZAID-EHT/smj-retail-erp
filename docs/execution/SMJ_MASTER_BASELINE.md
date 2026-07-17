# SMJ Master Mission — Baseline (Phase 2)

Frozen: 2026-07-18. All numbers below were re-run live against the current
codebase (`bench --site staging.local execute
my_store_ui.audit.parity_registry.corrected_production_parity_audit`), not
copied from a stale file.

## Capability parity (live, re-verified)

| Metric | Value |
|---|---|
| Total discovered features | 2,841 |
| User-facing required | 1,265 |
| Mapped required | 1,212 |
| **required_but_missing** | **0** |
| **unclassified** | **0** |
| verified_complete | 0 |
| implemented_unverified | 469 |
| generated_provisional | 805 |
| special_adapter | 437 |
| external_app_adapter | 25 |
| unavailable_with_reason | 53 |
| not_required | 179 |
| internal | 976 |

**This matches the JSON snapshot from 2026-07-16 exactly** — the codebase
has not drifted. `required_but_missing = 0` and `unclassified = 0` were
already true before this mission started. Phase 7's raw completion target
is therefore **already met as a starting condition**, not a goal to work
toward. Restating that here so it isn't mischaracterized as new work later.

**The real remaining gap is verification, not implementation**:
`verified_complete = 0` against `implemented_unverified = 469` +
`generated_provisional = 805` = 1,274 features that exist in some working
form but have never been confirmed correct by a real test or browser
check. That is what Phases 5, 6, 8, and 10 of this mission actually need
to close.

## The two structural gates from prior sessions (`VERIFICATION_MATRIX.md`)

- **GATE 4 — `allow_tests` disabled.** Was blocked on site1.local (a
  site this mission forbids touching anyway). **Staging.local has no such
  restriction** — I have full administrative control over it and can
  enable `allow_tests` there directly. This unblocks `bench run-tests` for
  the existing wholesale test suite (`my_store_ui/tests/`) for the first
  time in this project's history.
- **GATE 5 — browser verification.** Partially done in a prior session
  (Section 28, `AGENT_HANDOFF.md`) via a Windows-host Chrome screenshot
  method — Home dashboard and navigation were genuinely verified that way.
  Not comprehensive. This mission's Phase 6/18 (UI audit, responsive
  verification) is the first attempt at doing this exhaustively.

## What already satisfies parts of this mission's Phase 3/4/11

Built in this same conversation, immediately before this mission prompt,
on `staging.local`:

- Full demo dataset: company "SMJ Retail ERP" (LKR, Sri Lanka), 10
  warehouses, 26 customers (all required persona types: cash, credit,
  overdue, near-limit, over-limit, on-hold, inactive, no-orders, etc.),
  12 suppliers, 40 items across 7 groups with all required stock-status
  tags (fast/slow/high-value/low-stock/out-of-stock/overstocked/
  discontinued/no-recent-sales).
- All 10 named sales scenarios (A-J) and 7 purchase scenarios (A-G) from
  the earlier mission prompt, each a real chained/submitted document set.
- Genuinely verified (not assumed): the over-credit-limit customer's Sales
  Order **was actually blocked** by ERPNext's real `check_credit_limit()`
  — satisfies part of Phase 11 Scenario 4 already.
- Genuinely verified: a Stock Reservation Entry was created via the real
  `create_stock_reservation_entries()` API and released via
  `cancel_stock_reservation_entries()` — satisfies part of Phase 4's
  reservation requirement already, though **not yet the concurrency case**
  (two simultaneous reservations racing for the same last unit) that
  `VERIFICATION_MATRIX.md` and this mission's Phase 11 Scenario 6 actually
  require — that is genuine remaining work.
- GL verified balanced to the cent, zero negative stock, zero broken
  references, 12-month date spread, positive realistic gross margin.

**Important divergence to record honestly:** the prior mission's plan
(`BLOCKERS.md`) was to restore *site1.local's own data* onto a staging
copy, apply the wholesale custom fields via `setup_staging.sh`, and test
against that. What was actually built instead is an **independent, richer
demo dataset with its own company** ("SMJ Retail ERP" vs. site1's "SMJ"),
built directly with `bench new-site` rather than a restore. Both
approaches are valid for a demo/test environment; this one is *more*
thorough master-data-wise but did not go through `setup_staging.sh` and
therefore never exercised that specific restore path. Not re-doing that
restore now — the current staging.local already satisfies the intent
(a realistic wholesale business with the custom fields live) more
completely than the original plan would have.

## Custom fields / wholesale core status

Confirmed live on staging.local (from earlier work this session):
`Customer.custom_credit_type`, `{Sales Order,Delivery Note,Sales
Invoice,Payment Entry}.custom_wholesale_transaction_id` all exist and
the `doc_events` hooks in `my_store_ui/hooks.py` are firing (verified via
the demo data build — these are no longer "safe no-op", they are live).
This is a genuine, verified upgrade from every prior session's status,
which only ever confirmed the no-op path on site1.local.

## Next actions (in mission phase order)

1. Phase 3 — audit current staging.local demo data against this
   mission's specific checklist (largely satisfied already; confirm gaps:
   Material-Request-based import chain with Goods-in-Transit +
   Landed Cost Voucher already built as scenario G; concurrency
   reservation test not yet built).
2. Phase 4 — build the concurrency reservation test (genuine gap).
3. Enable `allow_tests` on staging.local, run existing wholesale test
   suite for the first time (GATE 4 unblock).
4. Phase 5 — role/security matrix (genuine, unstarted gap).
5. Phase 6 — UI workspace audit (genuine, unstarted gap, very large).
6. Phase 8 — accounting/stock report reconciliation using ERPNext's own
   standard reports (partially covered by earlier GL/stock validation
   queries; needs to be re-done through the actual Report UI/API, not
   just direct SQL, to be an honest "report reconciliation").
