# SMJ Retail ERP — Phase 6 Workspace Audit Summary (all 18)

**Date:** 2026-07-18 · **Method:** real Linux-native Playwright Chromium
(see `docs/ui/SMJ_BROWSER_VERIFICATION.md`). Every row below is
`browser_verified`: actually rendered, actually measured, not inferred.

| # | Workspace | Route (real, registry-sourced) | Buttons | Links | Tables | Mobile overflow (390×844) | Status |
|---|---|---|---|---|---|---|---|
| 1 | Home | `/home` | 15 | 41 | 1 | None | browser_verified |
| 2 | Smart Sales | `/smart-sales` | 54 | 15 | 0 | None | browser_verified |
| 3 | Customers | `/sales/customers` | 60 | 14 | 1 | None | browser_verified |
| 4 | Items | `/inventory/products` | 59 | 14 | 1 | None | browser_verified |
| 5 | Sales Orders | `/sales/orders` | 61 | 14 | 1 | None | browser_verified |
| 6 | Delivery Notes | `/sales/delivery-notes` | 61 | 14 | 1 | None | browser_verified |
| 7 | Sales Invoices | `/sales/invoices` | 60 | 14 | 1 | None | browser_verified |
| 8 | Payment Entries | `/finance/payments` | 59 | 14 | 1 | None | browser_verified |
| 9 | Wholesale Transaction Register | `/sales/transactions` | 28 | 15 | 1 | None | browser_verified |
| 10 | Suppliers | `/generated/supplier` | 24 | 16 | 1 | None | browser_verified |
| 11 | Purchase Orders | `/purchases/orders` | 26 | 16 | 1 | None | browser_verified |
| 12 | Purchase Receipts | `/purchases/receipts` | 26 | 16 | 1 | None | browser_verified |
| 13 | Purchase Invoices | `/purchases/invoices` | 26 | 16 | 1 | None | browser_verified |
| 14 | Stock Entries | `/inventory/stock-entries` | 24 | 16 | 1 | None | browser_verified |
| 15 | Stock Reconciliation | `/inventory/reconciliations` | 25 | 16 | 1 | None | browser_verified |
| 16 | Accounts and Banking | `/finance` | 21 | 59 | 0 | None | browser_verified |
| 17 | Reports | `/reports` | 12 | 191 | 0 | None | browser_verified |
| 18 | Administration | `/admin` | 19 | 54 | 0 | None | browser_verified |

All 18 workspaces: 0 buttons/links/tables count is only expected for
dashboard-style pages (Smart Sales, Accounts and Banking, Reports,
Administration) that present cards/charts/dropdowns rather than a
tabular list — confirmed intentional by inspecting each page's actual
component composition, not treated as a defect by default.

## Routing correction made during this audit

Workspaces 9, 11–15 (Wholesale Transaction Register, Purchase Orders,
Purchase Receipts, Purchase Invoices, Stock Entries, Stock
Reconciliation) initially redirected to `/retail-erp/not-found` in the
first audit pass due to an incorrect route guess. Fixed by reading the
real routes from
`my_store_ui/services/priority_registry.py`'s `CANONICAL_ROUTE_BY_DOCTYPE`
and `SPECIAL_ROUTES` tables (not guessed a second time). Full detail:
`docs/ui/SMJ_BROWSER_VERIFICATION.md`.

## What each row's "browser_verified" status actually covers

- Real HTTP navigation with a real authenticated session cookie
- Final URL confirmed to match the intended workspace (not a
  not-found/redirect)
- Zero console errors, zero page errors, zero failed/5xx requests
- Zero horizontal overflow at all 6 required viewports (only 390×844 shown
  in this summary table for brevity; full 6-viewport data in
  `docs/ui/evidence/runtime/2026-07-17T22-07-20-504Z/results.json`)
- Real screenshot captured at every viewport (curated desktop+mobile pairs
  committed; full set generated locally during the run)

## What this summary does NOT individually cover per workspace

Full click-through of every button/filter/action on every one of the 18
workspaces (108 distinct list/detail/form surfaces) was not exhaustively
performed — that would require many hours of scripted interaction beyond
what a single verification pass can cover. What WAS deeply verified
(real clicks, not just presence): Home's full interaction set (see
`SMJ_HOME_BROWSER_EVIDENCE.md`) and Sales Orders' list→detail→back flow,
pagination, and filter presence (see `SMJ_BROWSER_VERIFICATION.md`).

Checked precisely (not assumed) which other workspaces share Sales
Orders' exact component implementation, by reading
`frontend/src/router/routes.js`: **Customers, Items, Delivery Notes,
Sales Invoices, and Payment Entries** all route through the identical
shared `EntityListPage`/`EntityFormPage`/`EntityDetailPage` components
(parameterized only by `entityKey`) — for these 5, Sales Orders' verified
interaction behavior is `source_verified` by direct code inspection, not
`browser_verified` individually.

**Suppliers** uses a *different* shared engine
(`UniversalListPage`/`/generated/:feature`), and **Purchase
Orders/Receipts/Invoices and Stock Entries/Reconciliation** use a
*third* shared engine (`PriorityRoutePage`/the clean-route pattern).
Both were independently interaction-tested (row click → detail → back),
not assumed identical to Sales Orders:

- **Suppliers** (`UniversalListPage` engine): row click navigated to a
  real detail page
  (`/generated/supplier/Island%20Cleaning%20Supplies%20Co`), back button
  returned cleanly to the list. 6 filter controls found, 0 pagination
  controls (consistent with only 12 total suppliers — no pagination
  needed). `browser_verified`.
- **Purchase Orders** (`PriorityRoutePage` engine): row click navigated
  to a real detail page (`/purchases/orders/PUR-ORD-2026-00067`), back
  button returned cleanly. 2 pagination controls, 4 filter controls
  found. `browser_verified`. Purchase Receipts, Purchase Invoices,
  Stock Entries, and Stock Reconciliation share this exact same
  `PriorityRoutePage` component (confirmed via
  `frontend/src/router/routes.js`'s shared route definition), so this
  result is `source_verified` for those 4 by direct code inspection,
  not independently `browser_verified` each.

Evidence: `docs/ui/evidence/runtime/other-engines-2026-07-17T22-45-*/`.

**Net result: all three component engines used across the 18 workspaces
(EntityListPage, UniversalListPage, PriorityRoutePage) now have at least
one real, browser-verified row-click→detail→back interaction test.** No
engine in this app was left completely untested at the interaction
level.
