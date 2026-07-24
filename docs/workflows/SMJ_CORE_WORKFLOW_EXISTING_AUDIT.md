# SMJ Core Wholesale Workflow — Existing-Feature Audit

Audit of what already exists before implementing, so working code is repaired,
not duplicated. Source paths are repo-relative.

## Smart Sales (Phase 1 / 3)
- **Frontend**: `frontend/src/pages/priority/SmartSalesPage.vue`. Loads catalogue via
  `getSmartSales` (→ `my_store_ui.api.get_bootstrap`), searches customers, holds a
  local `cart` reactive. Shows Actual / Reserved / Available KPIs and per-card
  Actual/Reserved.
- **Backend**: `my_store_ui/api.py`
  - `get_bootstrap` — permission-filtered catalogue; prices from `Item Price` by
    `price_list`; stock from `Bin` (`actual_qty`, `reserved_stock`); computes
    `available_to_sell = actual - reserved`. Sound and permission-safe.
  - `search_customers` — permission-checked Customer search.
  - `create_draft_sales_order` — creates a **standard draft** Sales Order, ignores
    browser rates (ERPNext fetches rates on insert), idempotent via `request_id`.

### Gaps / defects
| # | Requirement | Existing | Gap | Fix |
|---|-------------|----------|-----|-----|
| 1 | Customer required before product add (req 1,11,12) | `add(item)` always enabled; `get_bootstrap` takes no customer | Not enforced | Gate cart on `customer`; disable add/qty/submit until selected |
| 2 | Customer's correct prices load automatically (req 3-6) | price list is default/manual, not customer's | Not customer-specific | `get_bootstrap(customer=…)` derives `Customer.default_price_list`; add per-item pricing-engine endpoint |
| 3 | Backend rechecks stock on placement (req 12,13) | `create_draft_sales_order` inserts without availability check | Missing | Recheck available-to-sell per line, reject over-available |
| 4 | Pricing source display (Phase 2) | card shows a single `rate` | No source/discount/rule info | Return rate + price_list_rate + source per item add |

## Pricing (Phase 2)
- `get_bootstrap` reads `Item Price` directly by `price_list` + `selling=1`.
- **No** use of `Customer.default_price_list`; **no** Pricing Rule application.
- ERPNext authoritative engine `erpnext.stock.get_item_details.get_item_details(args)`
  is available and applies Price List + Pricing Rules given `customer`, `price_list`,
  `company`, `qty`, `transaction_type="selling"`. This is the correct engine to use —
  no pricing logic is duplicated in Vue.

## Stock & Reservation (Phase 3)
- `my_store_ui/wholesale/reservation.py`:
  - `get_stock_availability` — read-only Actual/Reserved/Available per item+warehouse.
  - `reserve_sales_order` — reserves for a **submitted** SO via the standard engine
    `create_stock_reservation_entries()`, after `_lock_bins()` (SELECT … FOR UPDATE)
    to serialise concurrent reservations. **Correctly prevents over-reservation.**
  - `unreserve_sales_order`, `release_expired_reservations` (scheduled).
- **Gap**: the losing side of a concurrent reservation race raises a raw
  `QueryDeadlockError` (500) — reqs 14 + Scenario 5 want a bounded retry + friendly
  message. Reservation is decoupled from draft-SO creation (correct: draft SOs do not
  reserve in ERPNext); the availability *gate* at draft time is advisory UX, the hard
  guarantee is at reservation/submit time.

## Credit (already implemented — do not duplicate)
- `my_store_ui/wholesale/credit.py` → `get_customer_credit_status` (used by
  `SmartSalesPage` via `services/wholesale.js`). Prior mission (Phase 4) verified the
  credit delivery gate across 4 decision branches.

## User / Role / Access (Phase 8 — partly done this session already)
- `universal/api.py` already has (committed as `0d10f34`): write-only `new_password`
  set/reset, writable `enabled` toggle, create-by-username, curated
  `simple_create_fields`/`simple_create_required` add forms, `Password` input type.
- Remaining: Role Profile management surface, User Permission (company/warehouse)
  management surface, effective-access view, session revocation, welcome/reset email
  actions, admin polish, and a fresh backend access test report.

## Purchasing (Phase 5)
- Prior mission (Phase 9) traced full domestic MR→…→Payment and import/landed-cost
  chains via live documents. PO renders through the universal form engine. This
  mission still needs the field-level PO metadata audit doc + explicit acceptance doc.

## Henderson Analysis
- Separate management-report area. **Not** touched by these operational requirements.
