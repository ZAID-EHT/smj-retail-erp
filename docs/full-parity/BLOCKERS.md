# Full Feature Parity — Blockers and Approval Proposals

Every P0 wholesale capability requires an approval gate that the master prompt
itself says to stop for (schema/Custom Field, site-config, new DocType, package,
or destructive change). None of these were executed. Each is proposed below with
enough detail to approve or amend.

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
