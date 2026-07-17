# SMJ Master Mission — Batch Log

Append-only. Each entry is a real, executed batch with real command output
referenced (not a claim). Never delete earlier entries.

---

## Batch: mission-init (2026-07-18 00:33)

**Phase:** 0 — Preflight and recovery baseline

**Actions taken:**
1. Verified `pwd`/`whoami` — `/home/zaidh/frappe-bench`, user `zaidh`.
2. `bench version` — frappe 15.108.0, erpnext 15.108.3, my_store_ui 0.0.1,
   posawesome 15.30.0, smj_theme 0.0.1, erpnext_chatgpt 0.0.1,
   erpnext_gemini_integration 0.1.0.
3. `git -C apps/my_store_ui status --short` — confirmed 9 modified files
   that **predate this mission and this conversation's own work**
   (frontend Vue/CSS components, `module_dashboards.py`, two test files),
   plus this session's own untracked additions (`docs/demo/`,
   `my_store_ui/dev_scripts/`, favicon files, and the just-added favicon
   `<link>` edit to `retail_erp.html`). Left untouched per "preserve all
   valid uncommitted work" — not reset/stashed/cleaned.
4. Branch confirmed `full-feature-parity`, HEAD `1d2d36a...`.
5. `git diff --check` / `git diff --cached --check` — clean, no whitespace
   errors.
6. Confirmed `sites/common_site_config.json`: `default_site: staging.local`,
   `serve_default_site: true` — matches mission expectation.
7. Confirmed `sites/apps.txt` matches installed apps, no duplicates.
8. `bench --site staging.local list-apps` — frappe, erpnext, my_store_ui.
9. `bench --site site1.local list-apps` — frappe, erpnext, smj_theme,
   erpnext_chatgpt, erpnext_gemini_integration, posawesome, my_store_ui.
   Unchanged from every prior audit this session — site1.local integrity
   confirmed, not touched.
10. Created recovery tag `pre-smj-master-mission-20260718-0033` on
    `apps/my_store_ui` (the only git repo in scope; `frappe-bench` root
    itself is not a git repository).
11. Created `docs/execution/` and all other documentation directories the
    mission's phases will need (`docs/demo/`, `docs/workflows/`,
    `docs/security/`, `docs/verification/`, `docs/ui/audits/`).

**Result:** Phase 0 complete. Environment already known-stable from this
same conversation's immediately-prior work (bench Redis conflict fixed,
gemini duplicate-module warning fixed, favicon fixed, verified running for
60+ seconds with staging.local serving correctly). Phase 1 will do a fast
re-verification rather than redoing that work from scratch.

**Files changed this batch:** 4 new files under `docs/execution/`.

**Commit:** not yet committed — will commit at the end of Phase 1
re-verification per the mission's suggested commit sequence
(`chore: freeze SMJ master mission baseline` covers Phase 0+2 together).

---

## Batch: phase3-audit (2026-07-18)

**Phase:** 3 — audit staging demo data against mission checklist

**Actions taken:**
1. Queried all 26 customers' `custom_credit_type`/`disabled` — confirmed
   all 13 required customer personas present (cash, non-credit, credit,
   new, high-volume, no-orders, fully-paid, partially-paid, overdue,
   near-limit, over-limit, on-hold, inactive).
2. Spot-verified persona semantics against real data, not just labels:
   - Priyantha Rugs & More (no-orders tag): confirmed 0 Sales Orders.
   - Anuradhapura Floor Decor (over-limit tag): confirmed 0 Sales Orders
     (the one attempt was genuinely blocked and the draft deleted, by
     design).
   - Royal Home Decor (fully-paid tag): found 5/6 invoices paid, 1
     unpaid (LKR 134,550, a bulk-generated invoice that doesn't respect
     the persona tag). **Real gap, fixed** — settled via a genuine
     Payment Entry (`ACC-PAY-2026-00125`).
3. **Real bug discovered while fixing #2**: the company's only Fiscal
   Year (`2025-2026`) ends 2026-06-30. The system date has since advanced
   to 2026-07-18 (one day past FY end), so any *new* transaction dated
   "today" now fails with `FiscalYearError`. This would have silently
   blocked all further testing (including the Phase 4 concurrency test).
   **Fixed**: created Fiscal Year `2026-2027` (2026-07-01 to 2027-06-30)
   for SMJ Retail ERP via the standard Fiscal Year doctype (not a direct
   DB edit).
4. Queried all 12 suppliers — confirmed all 9 required supplier personas
   present (local, import [3 USD/Distributor suppliers], regular, backup,
   full/partial payment, outstanding invoice, purchase return, no recent
   activity) — matches original build design, cross-referenced against
   `docs/demo/SMJ_STAGING_DATA_GUIDE.md` §7 (purchase scenarios).
5. Item personas (fast/slow/high-value/low-value/low-stock/out-of-stock/
   overstocked/discontinued/no-recent-sales) were already verified with
   real Bin queries during the original build this session — not
   re-verified here, no new evidence needed.

**Result:** Phase 3 substantially satisfied by prior work. One real data
gap found and fixed (Royal Home Decor outstanding invoice). One real
environment bug found and fixed (missing Fiscal Year for current date) —
this is the more important finding, since it would have blocked Phase 4
onward silently.

**Files changed:** none (data-only changes on staging.local: 1 new
Fiscal Year record, 1 new Payment Entry).

**Not yet done from Phase 3's exact list:** `docs/demo/
SMJ_DEMO_DOCUMENT_INDEX.json` and `docs/demo/SMJ_DEMO_VALIDATION_REPORT.md`
(named in the mission but not in the earlier session's deliverable list) —
queued for the documentation pass at the end of this batch of phases.

---

## Batch: phase4-wholesale-concurrency (2026-07-18)

**Phase:** 4 — wholesale workflow verification + concurrency reservation
test (the one genuine gap named in `SMJ_MASTER_BASELINE.md`'s "Next
actions" list)

**Actions taken:**
1. Read `stock_reservation_entry.py` (`allow_partial_reservation` confirmed
   `1` on staging.local via live query) to understand the real locking
   behavior before designing the test — no guessing.
2. Wrote a dedicated, reusable test script
   (`apps/my_store_ui/my_store_ui/dev_scripts/wholesale_concurrency_test.py`):
   creates item `CONC-TEST-001` with exactly 10 units in one warehouse, two
   Sales Orders for 8 units each (16 > 10, forces the race), then exposes
   `reserve_one()` for two independent OS processes to call concurrently.
3. Ran the real test: launched two separate `bench execute` processes
   (genuine separate DB connections/transactions, not simulated) racing to
   reserve 8 units each against 10 available.
   - **Result:** Process A got `QueryDeadlockError (1213)` (InnoDB row
     lock conflict) and rolled back cleanly; Process B succeeded with
     `reserved_qty=8.0`. A retry of Process A then correctly received the
     true remaining amount (`reserved_qty=2.0`, respecting
     `allow_partial_reservation=1`).
   - **Verified:** `total_reserved=10.0`, `actual_qty=10.0`,
     `over_reserved=False` — the stock-safety property held under genuine
     concurrent load.
4. Cleaned up: cancelled both Stock Reservation Entries, cancelled and
   deleted both test Sales Orders (`cancelled_sres=2 removed_sos=2`,
   confirmed via `tabBin` query afterward: item back to `actual_qty=10,
   reserved_qty=0`). Removed the temporary copy from `apps/erpnext/erpnext/`
   (the `bench execute` app-dependency workaround, same pattern as
   `seed_staging_year.py`); `git status` on the erpnext app confirmed
   clean afterward.
5. Live-verified (not code-inspection-only) the rest of the wholesale
   transaction model against real data:
   - Transaction ID coverage: 102/102 Sales Orders, 100/100 Delivery
     Notes, 100/100 Sales Invoices, 77/78 Payment Entries (the one gap is
     a genuine unallocated advance with zero references — expected, not a
     bug, confirmed by reading `propagate_payment_entry()`'s actual logic).
     Format and uniqueness both 100% correct across 102 distinct IDs.
   - Credit delivery gate (`evaluate_delivery_gate`) live-called as
     Administrator against 4 real customers covering all 4 decision
     branches (non-credit+overdue blocked, credit+overdue blocked pending
     manager approval, credit+within-limit allowed x2) — all matched
     expected behavior exactly.
   - Wholesale Transaction Register (`get_wholesale_transactions`)
     live-called: 102 rows (matches Sales Order count exactly), correct
     pagination, correct payment/delivery status derivation on real rows
     (both a fully-paid and a fully-unpaid example checked).
   - Confirmed a real submitted Sales Return (`ACC-SINV-2026-00018`
     against `ACC-SINV-2026-00013`) satisfies Scenario 5 using existing
     data — no new document needed.
6. Wrote all 3 required Phase 4 deliverables under
   `docs/workflows/`: `SMJ_WHOLESALE_CONCURRENCY_REPORT.md` (full test
   detail, including the honestly-reported UX gap — raw deadlock error
   instead of a friendly retry message on the first attempt),
   `SMJ_WHOLESALE_TRANSACTION_MODEL.md` (transaction ID / credit gate /
   register / return verification detail), `SMJ_WHOLESALE_ACCEPTANCE_REPORT.md`
   (scoreboard mapping all 6 of Section 11's acceptance scenarios to
   PASS/evidence).

**Result:** Phase 4 complete. All 6 acceptance scenarios pass. One
genuine (not fabricated) UX hardening gap identified and documented
honestly rather than silently patched: a losing concurrent-reservation
request currently surfaces a raw `QueryDeadlockError` instead of a
friendly conflict message on its first attempt — the underlying
data-safety guarantee (never over-reserve) holds regardless, and a retry
succeeds correctly. Recommended as a future application-layer hardening
item (bounded retry-on-deadlock at the "Reserve Stock" call site), not
applied in this mission since it would mean silently modifying behavior
beyond the mission's verification scope.

**Files changed:** 3 new files under `docs/workflows/`; 1 new file
`apps/my_store_ui/my_store_ui/dev_scripts/wholesale_concurrency_test.py`.
Data-only changes on staging.local: 1 new Item (`CONC-TEST-001`, a
reusable test fixture, 10 units on hand, 0 reserved, no live Sales Orders
or Stock Reservation Entries referencing it).

**Commit:** pending — will commit this batch immediately after this log
entry.
