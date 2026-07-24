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
- Commits created:
  - `9fc727b` chore: audit + resumable mission state
  - `524d01f` feat: customer-first Smart Sales (pricing, stock gating, reservation retry)
  - `9d4dbdc` test: FIFO valuation verification
- Working tree: clean after each commit. No pre-existing unrelated changes were
  touched (there were none at mission start).

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

Regression: `test_wholesale_credit` (7), `test_stock_action_parity` (7) still pass;
`npm run build` clean (199 modules).

## Not done this session (remaining scope — not blocked)
1. **Live 2-process reservation concurrency demo** on staging (the friendly-retry
   path has code + unit-level coverage; the 10/8/8 live parallel run was not
   re-executed this session — prior mission's Phase 4/10 demonstrated the
   over-reservation guarantee).
2. **Sale-path FIFO → COGS → Gross Profit** trace (layer valuation is verified;
   the COGS-on-delivery trace is deferred).
3. **Phase 5** — Purchase Order field-level data audit doc + end-to-end purchase
   acceptance doc (prior mission Phase 9 traced the chains live).
4. **Phase 6** — `+ Create` header menu. **Prerequisite work found:** only
   Customer, Item, Sales Order, Delivery Note, Sales Invoice, Payment Entry and 3
   Stock Entry variants have real `/new` create routes today. Supplier, PO, MR,
   RFQ, Supplier Quotation, Purchase Receipt, Purchase Invoice, User and Role need
   create routes + form pages added first, otherwise the menu would offer dead
   actions (explicitly forbidden by the brief). Not started to avoid a fake menu.
5. **Phase 7** — simplified Supplier/Product/transaction entry (Customer + User
   curated add forms already shipped in the prior batch `0d10f34`).
6. **Phase 8** — remaining access management (Role Profile surface, User Permission
   company/warehouse surface, effective-access view, session revocation,
   welcome/reset email). Password set/reset + enable/disable already shipped.
7. **Acceptance scenarios 1–11** as a scripted staging suite; **6-viewport
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
