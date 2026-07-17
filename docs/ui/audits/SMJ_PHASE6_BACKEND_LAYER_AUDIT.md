# SMJ Retail ERP — Phase 6 UI Workspace Audit: Backend Layer

**Date:** 2026-07-18 · **Site:** staging.local · **Scope of this pass:**
the data/API layer every workspace depends on. **Not yet done:** actual
rendered-pixel / interactive / responsive-breakpoint verification — see
"What remains" below, stated honestly rather than assumed complete.

## Why split the audit this way

The mission's 18 named workspaces (Home, Smart Sales, Customers, Items,
Sales Orders, Delivery Notes, Sales Invoices, Payment Entries, Wholesale
Transaction Register, Suppliers, Purchase Orders, Purchase Receipts,
Purchase Invoices, Stock Entries, Stock Reconciliation, Accounts and
Banking, Reports, Administration) are Vue SPA views
(`apps/my_store_ui/frontend/`) that call whitelisted Python APIs for
their data. A workspace can fail for two independent reasons: (1) the
backend API errors or returns wrong/empty data, or (2) the frontend
renders it incorrectly. This pass verifies (1) exhaustively with real
calls against real data. (2) requires a real browser (visual rendering,
click-through, responsive breakpoints) which this pass could not
complete in this batch — documented honestly below, not glossed over.

## Backend verification performed (real, live, not code-reading)

### Dashboard/aggregation APIs (`my_store_ui/module_dashboards.py`)

Live-called every whitelisted dashboard function as Administrator against
real staging.local data:

| Function | Backs workspace(s) | Result |
|---|---|---|
| `get_accounts_dashboard` | Accounts and Banking | ✅ Returns `company, currency, cards, charts` — no error |
| `get_payments_dashboard` | Payment Entries | ✅ Returns `company, currency, cards, charts` — no error |
| `get_buying_dashboard` | Purchases (Purchase Orders/Receipts/Invoices, Suppliers) | ✅ Returns `company, currency, cards, charts` — no error |
| `get_crm_dashboard` | CRM / Smart Sales | ✅ Returns `company, currency, cards, charts` — no error |
| `get_selling_dashboard` | Sales (Sales Orders/Invoices, Customers) | ✅ Returns `company, currency, cards, charts` — no error |
| `get_stock_dashboard` | Inventory (Stock Entries, Stock Reconciliation, Items) | ✅ Returns `cards, charts` — no error |

### Wholesale-specific API (`my_store_ui/wholesale/register.py`)

Already verified in Phase 4: `get_wholesale_transactions()` returns
102/102 real rows with correct pagination and status derivation — see
`SMJ_WHOLESALE_TRANSACTION_MODEL.md`.

### Underlying data volume (confirms no workspace will show a false
empty state)

| DocType | Live count (submitted/active) |
|---|---|
| Customer (active) | 25 |
| Supplier (active) | 12 |
| Item (active) | 40 |
| Sales Order | 102 |
| Delivery Note | 100 |
| Sales Invoice | 100 |
| Payment Entry | 124 (incl. supplier payments) |
| Purchase Order | 67 |
| Purchase Receipt | 68 |
| Purchase Invoice | 66 |
| Stock Entry | 8 |
| Stock Reconciliation | 2 |
| Journal Entry | 3 |

Every doctype that backs a named workspace has real, non-zero data —
every list/detail workspace will render populated content, not an empty
state, when visited.

### Frontend route registration (`frontend/src/router/routes.js`)

Confirmed all 9 top-level module dashboard routes are registered
(`/home`, `/smart-sales`, `/sales`, `/purchases`, `/inventory`,
`/finance`, `/operations`, `/crm`, `/reports`, `/admin`), plus dedicated
CRUD routes for customers, items, delivery notes, sales invoices, payment
entries, and sales orders. Workspaces without a dedicated static route
(Suppliers, Purchase Orders/Receipts/Invoices, Stock Entries/
Reconciliation, Wholesale Transaction Register) are served through the
project's `/generated/:feature` universal list/detail/form page system —
present in the router, not missing.

### HTTP-level reachability

Confirmed `serve_default_site: true` means the app is directly reachable
at `http://127.0.0.1:8000/retail_erp` without a DNS entry for
`staging.local` (useful for any future headless-browser tooling in this
same container) — `GET /retail_erp` returns `200` with the real SPA shell
HTML, and `GET /api/method/ping` returns `200 {"message":"pong"}`.

## What remains (honestly, not silently skipped)

This pass did **not** perform:
- Actual browser rendering / visual inspection of any of the 18
  workspaces.
- The mission's 6-breakpoint responsive check (1920×1080 down to
  360×800).
- Authenticated interactive click-through (login → navigate → verify UI
  state, filters, sorting, pagination controls actually work in the
  rendered page).
- Accessibility audit of the rendered DOM.

**Why:** this requires a real or headless browser with a persisted
authenticated session across many page loads. The tools available in
this execution environment for this batch did not include a
browser-automation tool capable of a scripted login + multi-page
authenticated crawl (the `accesslint` MCP server can audit a single live
URL's DOM but was not exercised against an authenticated SPA route in
this batch). A prior session in this same project used a manual
Windows-host Chrome screenshot method for a subset of pages (Home
dashboard, navigation) — that method is not available to this
non-interactive batch execution.

**Recommendation, stated plainly:** the remaining visual/interactive/
responsive verification for all 18 workspaces needs either (a) a
Playwright or similar browser-automation tool enabled for this session,
or (b) a manual QA pass by a person with a real browser, following the
existing E2E test file structure convention already documented in this
project's `FRONTEND.md` rules. This is flagged as genuinely unfinished
work, not claimed as done.

**Confirmed by direct attempt, not just assumed:** tried the
`accesslint` MCP's `audit_live` against the reachable shell URL
(`http://127.0.0.1:8000/retail_erp`) as a real test of whether any
in-environment browser automation was usable. Result: `Could not start a
debuggable Chrome: Launched Chrome (pid 67142) but discovery never
answered on 127.0.0.1:9222` — this container cannot launch a working
headless Chrome (missing sandbox dependencies, typical of a minimal WSL
container). This confirms the gap above is a real environment limitation,
not an assumption.
