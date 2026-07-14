# Full Feature Parity — Blockers and Approval Proposals

Every P0 wholesale capability requires an approval gate that the master prompt
itself says to stop for (schema/Custom Field, site-config, new DocType, package,
or destructive change). None of these were executed. Each is proposed below with
enough detail to approve or amend.

---

## URGENT MAPPING MISSION (2026-07-14) — remaining batches, not schema-gated

These are NOT approval-gated (no schema/custom field/destructive change needed) —
they are genuinely unbuilt engineering work that this mapping pass did not reach.
Listed here per the mission's own rule: "When a specialised action cannot safely
be implemented now, map it to a truthful blocked or unavailable state with
evidence... do not stop the full mission." Registry status for all of these
remains honestly `unavailable_with_reason`, not faked to `internal`/`not_required`.
They are the entirety of `required_but_missing = 367` in
`docs/full-parity/corrected_production_parity_audit.json`.

| Batch | Scope | Status | Detail |
|---|---|---|---|
| 7 | Stock document actions | **DONE** (pass 2, commit c2f95fa) | Purchase Receipt→Purchase Return/LCV, Material Request→Stock Entry added to `MAPPED_ACTIONS` |
| 8 | Accounts document actions | **DONE** (pass 2, commit c2f95fa) | Purchase Invoice→Debit Note, Journal Entry→Reverse Journal Entry added |
| 13 | Platform administration | **DONE** (pass 2, commit 0dcc9a0) | 45 DocTypes → `internal`, 9 print formats credited via their routed report |
| 14 | POS Awesome / external apps | **DONE** (pass 2, commits 393c45a, 6a3d661) | 23 entries classified: 2 `not_required` (Mpesa/Kenya), 18 `external_app_adapter` |
| 10 | Special finance adapters (Bank Reconciliation Tool, Payment Reconciliation, GL/Trial Balance/P&L/Balance Sheet interactive drill-down, Budgets, Accounting Dimensions, Process Period Closing Voucher, Process Statement Of Accounts, Process Subscription) | **Still open** | Genuinely unbuilt UI/adapter code; the underlying reports route (Batch 1/2), but a real interactive reconciliation/drill-down adapter is separate work. Build dedicated Vue adapter components per SPECIAL_ROUTES-style pattern (see `/finance/bank-reconciliation`, `/finance/payment-reconciliation`, which are route stubs only) |
| 11 | Special stock adapters (Serial and Batch Bundle picker UI, barcode workflows, Stock Ledger/Ageing views, Transit Warehouse, reorder tools, Pick List→Delivery Note/Stock Entry) | **Still open** | Genuinely unbuilt. Pick List's `create_delivery_note`/`create_stock_entry` were investigated in pass 2 and deliberately NOT force-fit into the generic `MAPPED_ACTIONS` pattern — `create_delivery_note` can create multiple Delivery Notes per call and may save internally; `create_stock_entry` takes a JSON-serialized Pick List, not a docname. Both break the simple get_mapped_doc→insert() pattern; need a dedicated adapter, not a registry credit |
| 12 | Purchasing/imports (Blanket Order, Drop Shipping, Supplier Statements/Performance, **Import Shipment**) | **Still open** | Genuinely unbuilt. Import Shipment likely needs a new Custom DocType field set for wholesale import tracking — stays `blocked` pending a schema-change approval gate identical to GATE 1-3 above; the rest is ordinary generic/special_adapter work |

Remaining `required_but_missing = 327` (down from 367 after pass 1, 846 in
the first buggy computation). None of the still-open items block anything
else - each was left `unavailable_with_reason`
with real evidence and the mission continued through every other batch, per the
"do not stop because one feature is blocked" rule.

---

## GATE 1 — Enable stock reservation + reservation policy  (P0)

**Why blocked:** `Stock Settings.enable_stock_reservation = 0` is a global
site-config change (approval required), and the reservation *policy* (expiry
window, backorder handling, partial-reservation rules, per-warehouse behaviour)
is a business decision, not derivable from code.

**Proposal:**
- Enable `enable_stock_reservation` on an approved site.
- Use ERPNext's standard `Stock Reservation Entry` against `Sales Order`
  (no custom stock ledger writes; controllers own all stock movement).
- Available to Sell = `Bin.actual_qty − reserved_qty` computed from standard
  `Stock Reservation Entry`, surfaced read-only in `api.get_bootstrap` /
  Smart Sales. Vue never writes Bin or Stock Ledger Entry.
- Add an allowlisted reserve/unreserve service that calls standard controller
  methods, with row-level locking to make the concurrency test hold
  (10 available, two 8-unit reservations → never 16).

**Business questions to confirm:** reservation expiry duration; whether backorders
are allowed and how; partial-reservation default; which warehouses participate.

**Tests required (on an approved test site):** concurrent double-reservation,
partial delivery/cancel/return release, expiry release, warehouse permissions,
Stock Ledger unchanged until Delivery Note submit.

---

## GATE 2 — Customer Credit/Non-Credit Custom Fields  (P0)

**Why blocked:** requires **Custom Field** creation on `Customer` (approval
checkpoint). Currently zero credit fields and zero `Customer Credit Limit` rows.

**Proposed Custom Fields (via fixtures, reviewable, reversible):**
- `Customer.custom_credit_customer` (Check) — Credit vs Non-Credit selector.
- Reuse standard `Customer.credit_limits` child table for the individual limit
  and `Customer Credit Limit.bypass_credit_limit_check` — do not reinvent.
- Reuse standard `payment_terms` for credit period.
- `Customer.custom_allow_delivery_before_payment` (Check, permlevel-restricted).

**Server enforcement (no Vue arithmetic for official balances):**
- Outstanding/overdue/available-credit read from standard ERPNext
  (`get_customer_outstanding`, Accounts Receivable), surfaced read-only.
- A server-side delivery gate on Sales Order → Delivery Note that blocks or
  requires manager approval when over-limit / overdue, using standard credit
  controller checks.
- Credit-limit changes recorded via standard Version history + a required
  override reason; role-restricted.

**Business questions:** overdue policy (block vs warn); who may override; whether
to use ERPNext's built-in credit-limit block or a stricter custom gate.

---

## GATE 3 — Wholesale Transaction ID / Register Custom Fields  (P0)

**Why blocked:** requires **Custom Fields** on Sales Order, Delivery Note,
Sales Invoice, Payment Entry, Pick List, Packing Slip, Stock Reservation Entry.

**Proposal:**
- Add `custom_wholesale_transaction_id` (Data, indexed) to the above doctypes.
- Atomic `TRX-YYYY-000001` generator (server-owned naming helper; each document
  keeps its own naming series).
- Propagate the TRX id through standard mapped-document hooks (no ledger edits).
- `/retail-erp/sales/transactions` read-only register: one row per TRX, links to
  every related document, permission-controlled financial columns, CSV export,
  timeline. All data read from ERPNext; no shadow store.

**Note:** a read-only register that groups existing documents by their native
links (DN←SO, SI←DN, PE.references) is possible *without* custom fields and could
ship first as an interim view; the shared TRX id still needs the fields above.

---

## GATE 4 — Test execution environment  (P0 for evidence)

**Why blocked:** `bench --site site1.local run-tests --app my_store_ui` fails —
`allow_tests` is disabled. Enabling it mutates site config (approval required).

**Proposal:** provision a separate approved test/staging site, or approve
`set-config allow_tests true` on a non-production site, plus deterministic
single-role test users (Sales, Stock, Purchase, Accounts, managers, restricted
company/warehouse). Until then, 100 existing tests remain unrun this mission and
all lifecycle/permission features stay `implemented_unverified`.

---

## GATE 5 — Browser / real-interface verification  (P0 for evidence)

**Why blocked:** no Chrome/Chromium/Edge/Firefox/Playwright/Cypress/Selenium
present; installing system packages requires approval.

**Impact:** no capability that depends on rendered UI, layout, focus, multi-tab
or multi-user interaction can be marked `verified_complete`. A manual browser
verification checklist is maintained in `VERIFICATION_MATRIX.md`.

---

## GATE 6 — Custom Import Shipment DocType  (P1, conditional)

**Why potentially blocked:** a consolidated Import Shipment record
(container/BoL/vessel/forwarder/ports/ETD-ETA/customs/clearing + multi-PO +
landed cost) may need a **new DocType**. First confirm standard ERPNext
`Shipment` + `Landed Cost Voucher` are insufficient.

**Proposal (only if standard is insufficient):** submit a schema checkpoint with
proposed fields, permissions, links, migration, backup and rollback before
creating anything. Landed Cost Voucher itself needs only a route/report adapter,
not schema.

---

## Non-gated work that can proceed without approval

- Generic-engine hardening for in-scope masters and reports (list/detail/form,
  filters, print) — stays `generated_provisional` until verified.
- Report/register read-only adapters that use only existing ERPNext data.
- The interim link-based transaction register (GATE 3 note) — no custom fields.

These can advance but cannot reach `verified_complete` until GATE 4/5 are open.

---

## CONSOLIDATED APPROVAL REQUEST (to unblock P0 business functionality)

Safe, non-gated route/engine work is largely exhausted (829 features implemented
in some form; ~75% of the inventory truthfully resolved). The remaining business
value is the wholesale operating model, which needs these approvals:

1. **Custom Fields (reversible fixtures)** — Credit/Non-Credit on Customer, and
   `custom_wholesale_transaction_id` on Sales Order/Delivery Note/Sales Invoice/
   Payment Entry/Pick List/Packing Slip/Stock Reservation Entry.
   - Why standard is insufficient: no standard field marks Credit vs Non-Credit or
     a shared cross-document transaction id.
   - DB effect: adds columns via Custom Field fixtures; no data migration of rows.
   - Backup: pre-change DB backup. Rollback: delete the Custom Fields (fixtures).
   - Security: `custom_allow_delivery_before_payment` at a restricted permlevel.
   - Tests: schema presence, credit gate, TRX propagation (on a test site).
2. **Enable `enable_stock_reservation`** on an approved (non-production) site, plus
   the reservation policy (expiry window, backorder rule, partial-reservation
   default). Uses standard Stock Reservation Entry only.
3. **Test environment** — `allow_tests` on a non-prod site, or a staging site, with
   single-role test users, so features can graduate past `implemented_unverified`.
4. **Browser automation** (Playwright/Chromium) install approval, for the manual
   verification checklist in VERIFICATION_MATRIX.md.

Grant any subset; each unblocks the corresponding batch independently.

---

## STAGING — remaining ENVIRONMENT blockers for the wholesale core (2026-07-14)

The wholesale core is fully implemented and committed. Two blockers are
environment-level (not code, not approval) and could not be self-resolved:

1. **MariaDB root password** — required to create the approved staging database.
   No root password in config, no passwordless sudo, and the site DB-user lacks
   CREATE privileges. Provide it (or run `bench new-site` yourself) and then run
   `apps/my_store_ui/docs/full-parity/setup_staging.sh`, which backs up, creates
   staging, restores, applies fixtures, enables reservation + allow_tests ON
   STAGING ONLY, and runs the wholesale test suite.
2. **Network access** — the npm registry is unreachable (`npm ping` times out), so
   Playwright/Chromium cannot be downloaded despite approval. Once network is
   available: `cd apps/my_store_ui/frontend && npm i -D @playwright/test &&
   npx playwright install chromium && npx playwright test e2e/wholesale.spec.js`.

What is verified now (site1 read-only, no config/schema change): Available-to-Sell
snapshot + Smart Sales display, credit status + all 7 gate rules, transaction
register on real data, route HTTP 200, transaction-id hooks safe no-op, Bin-lock
query validity, Vue build. What needs staging: applying custom fields, enabling
reservation, and running the reservation/concurrency/integration + browser tests.
