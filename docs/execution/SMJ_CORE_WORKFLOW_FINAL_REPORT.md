# SMJ Core Wholesale Workflow — Final Report (session of 2026-07-24)

This report is **truthful about scope**. The mission spans eight phases plus
acceptance scenarios and a full browser matrix. This session completed and
**verified** the security/correctness-critical spine (customer-first sales,
customer-specific pricing, server-side stock gating, reservation concurrency UX)
and FIFO valuation. The remaining phases are genuine remaining work — not
externally blocked — and are listed explicitly so the next session can resume.

## Repository
- Starting branch / commit: `full-feature-parity` @ `e15c37e`
- Final commit: `9d4dbdc`
- Recovery tag: `pre-smj-core-workflow-20260724-1140`
- Final commit: `5a67ec2`
- Commits created (7):
  - `9fc727b` chore: audit + resumable mission state
  - `524d01f` feat: customer-first Smart Sales (pricing, stock gating, reservation retry)
  - `9d4dbdc` test: FIFO valuation verification
  - `b47c880` docs: mission state + interim report
  - `8811341` feat: permission-aware Quick Create (+ Create) header menu
  - `07e3447` feat: curated Supplier add form + simplified-entry state (Phase 7)
  - `5a67ec2` test: reservation bounded retry-on-deadlock + friendly message
- Working tree: clean after each commit. No pre-existing unrelated changes were
  touched (there were none at mission start).
- Verified totals: **59 backend tests green** (test_smart_sales_core 5,
  test_frontend_layout 9, test_quick_create 4, test_universal_frontend 24,
  test_reservation_retry 3, test_wholesale_credit 7, test_stock_action_parity 7) +
  FIFO dev-script exact + frontend build clean (201 modules).

## Verified this session (with evidence)
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Customer required before product add / cart / submit (1, 11, 12) | ✅ Done | `SmartSalesPage.vue` gating + `test_frontend_layout.test_smart_sales_enforces_customer_first_and_stock_gating` |
| Out-of-stock badge + add blocked (10, 11) | ✅ Done | product-card `outOfStock()` guard + badge; frontend regression test |
| Customer's prices load automatically / different customers differ (2–5) | ✅ Done | `get_bootstrap(customer)` → `Customer.default_price_list`; `test_smart_sales_core` (bootstrap + isolation) |
| Cart reprices on customer change (6) | ✅ Done | `get_cart_pricing` + `repriceCart()`; uses ERPNext `get_item_details` |
| Customer-specific Pricing Rule applied (Phase 2) | ✅ Done | `test_smart_sales_core.test_cart_pricing_applies_customer_pricing_rule` |
| Pricing source displayed (Phase 2) | ✅ Done | per-line `source` (pricing_rule / customer_price_list / price_list) in cart |
| Backend rechecks stock on placement; over-available rejected (12, 13) | ✅ Done | `create_draft_sales_order` recheck; `test_smart_sales_core` out-of-stock rejection |
| Concurrency friendly conflict / bounded retry (14) | ✅ Done | `reserve_sales_order` retry-on-deadlock (1213/1205) + friendly message |
| FIFO layer valuation + remaining layer (15–17) | ✅ Done | `SMJ_FIFO_VERIFICATION.md`: 12,400 exact, remaining 9,600 exact |

| Concurrency friendly bounded-retry (14, Scenario 5) | ✅ Done | `test_reservation_retry` (3) — deterministic 1213/1205 retry + friendly error |
| `+ Create` permission-aware header menu (Phase 6) | ✅ Done | `test_quick_create` (4) — 22 real routes, no dead actions, role-filtered; `SMJ_QUICK_CREATE_MENU.md` |
| Curated Supplier add form; Customer/Item already sectioned (Phase 7) | ✅ Done | `test_universal_frontend` (24); `SMJ_SIMPLIFIED_ENTRY_FORMS.md` |

Regression: `test_wholesale_credit` (7), `test_stock_action_parity` (7) pass;
`npm run build` clean (201 modules). **59 backend tests green total.**

### Phase 6 update
Initially reported as prerequisite-blocked, but the universal form engine
(`/generated/:feature/new`) provides **real** create routes for 22 doctypes — the
menu now offers Customer/Quotation/Sales Order/Delivery Note/Sales Invoice/Payment
Entry, Supplier/Material Request/RFQ/Supplier Quotation/Purchase Order/Purchase
Receipt/Purchase Invoice, Item/Stock Entry/Stock Reconciliation/Warehouse, User/Role,
Journal Entry/Contact/Address — every one route-resolved (no dead actions), filtered
by create permission. Role Profile is correctly omitted (no create route).

## Confirmed defect (documented, not auto-fixed — needs a decision)
- **Item pricing stored only in custom fields**: `form_api._apply_item_pricing`
  writes wholesale/retail to `custom_*` fields, not standard `Item Price` records,
  so those prices are invisible to the pricing engine (and Smart Sales). Fix needs a
  price-list mapping decision (no `Wholesale Price List` on staging). See
  `SMJ_SIMPLIFIED_ENTRY_FORMS.md` + blockers.

## Not done this session (remaining scope — not blocked)
1. **Live 2-process reservation concurrency demo** against the new wrapper (retry is
   unit-verified; prior mission ran the live 10/8/8 against the pre-retry path).
2. **Sale-path FIFO → COGS → Gross Profit** trace (layer valuation verified).
3. **Phase 5** — Purchase Order field-level data audit + end-to-end purchase
   acceptance docs (prior mission Phase 9 traced the chains live).
4. **Phase 7 pricing fix** — item-price → `Item Price` sync (needs mapping decision).
5. **Phase 8** — remaining access management (Role Profile surface, User Permission
   company/warehouse surface, effective-access view, session revocation,
   welcome/reset email). Password set/reset + enable/disable already shipped.
6. **Acceptance scenarios 1–11** as a scripted staging suite; **6-viewport
   Playwright matrix** for the new Smart Sales UI.

## Safety confirmations
- All writes were to `staging.local`; a full backup was taken first
  (`20260724_114030-*`). `site1.local` business data was not modified.
- No `ignore_permissions=True` in any endpoint; all pricing/stock/reservation goes
  through standard ERPNext controllers (`get_item_details`,
  `create_stock_reservation_entries`, Stock Entry). No direct GL/SLE/Bin/outstanding
  writes; no Vue-side valuation.
- No sudo / killall / pkill / taskkill / Windows Chrome; no credentials committed.

## One-line status
The core wholesale security/correctness spine (customer-first, customer pricing,
stock gating, reservation concurrency UX) and FIFO valuation are **implemented and
verified**; the remaining phases are unfinished scope, honestly enumerated above,
resumable from the mission-state files.
