# ACCOUNT CREATION.docx — Implementation Results

Source: `/home/zaidh/frappe-bench/ACCOUNT CREATION.docx` (2,117,246 bytes, 15 embedded
screenshots, read in full including images). The file was never modified; a copy was
extracted to a scratch directory for inspection.

## The two defects behind "this button does not work"

The document circles three buttons: **+ New Supplier**, **Add New Lead**,
**New Quotation**. Both root causes were found by clicking them in a real browser.

### 1. The banner decoration swallowed the click

`.rug-banner::after` is an absolutely positioned decorative circle. Pages that place
their action inside `.rug-banner-actions` are safe, because that wrapper carries
`z-index: 1`. `UniversalListPage` renders the create button as a **direct child** of
the banner, so the circle painted on top of it.

The button reported `disabled: false`, `visibility: visible`, `pointerEvents: auto`,
a real 126×38 box — and did nothing, because `document.elementFromPoint` at its
centre returned `rug-banner`, not the button.

That is exactly why Suppliers, Leads, Quotations and Purchase Orders were dead while
Warehouses worked: Warehouses uses `PriorityTreePage`, which wraps its buttons.

**Fix:** page-header pseudo-elements are now `pointer-events: none`, and a bare
action inside a banner is raised above the decoration.

### 2. No operator role could create a Supplier

Stock ERPNext v15 restricts Supplier and Supplier Group to `Purchase Master Manager`.
The selling side is not symmetric — `Sales User` can create a Customer:

| DocType | Roles with create |
|---|---|
| Customer | Sales Master Manager, **Sales User** |
| Supplier | Purchase Master Manager *(only)* |

So the button was hidden from Purchase User / Purchase Manager entirely, and for
Administrator it led to a form nobody else could save.

**Fix:** `patches/grant_buying_operator_permissions.py` mirrors the selling side on
the buying side. Idempotent, applied by `bench migrate`.

## Button audit result

`frontend/e2e/button_audit.mjs` clicks each page's create button in Chromium and
asserts it reaches a form with fields. It reports *why* a button is unusable
(disabled / covered / hidden) rather than just timing out.

| Page | Before | After |
|---|---|---|
| Suppliers | covered by banner | PASS → `/purchases/suppliers/new` |
| Leads | covered by banner | PASS → `/crm/leads/new` |
| Quotations | covered by banner | PASS → `/sales/quotations/new` |
| Purchase Orders | covered by banner | PASS → `/purchases/orders/new` |
| Sales Orders | PASS | PASS |
| Delivery Notes | PASS | PASS |
| Customers | PASS | PASS |
| Products | PASS | PASS |
| Warehouses | PASS | PASS |
| Payment Entries | n/a | SKIP — by design |

**9/9 clickable (was 5/9).** Payment Entry has no generic "new": payments are created
through typed routes (`/finance/payments/receive|pay|internal-transfer/new`) so the
account and direction are never ambiguous.

## Other document requirements

| # | Requirement | Result |
|---|---|---|
| 2 | Customer's Price List auto-selected; cart reprices | Working. `get_cart_pricing` and (fixed earlier this session) `create_draft_sales_order` both resolve the customer's Price Category |
| 3 | Price Category shows only selling Price Lists | Already correct — options filtered to `{enabled: 1, selling: 1}`, so Standard Buying cannot appear |
| 4 | Actual / Reserved / Available-to-Sell | Working; shown on Smart Sales and product cards |
| 5 | Out-of-stock blocking, backend recheck | Working; server rechecks inside order creation |
| 6 | Permission-based header Quick Create | Already implemented, and stronger than asked: it drops any entry whose route does not resolve, so a dead menu item cannot appear |
| 7 | FIFO with batch splitting | Implemented earlier this session via ERPNext's own allocator |
| 8 | Purchase Order data and workflow | Implemented earlier this session |
| 9 | Simplified Product / Customer forms | Product and Customer quick-entry forms already exist with the business field set |
| 10 | Henderson Analysis kept separate | Verified separate — it has **no** presence in any operational module. The page itself does not exist |
| — | Red "select a customer" banner | Added |
| — | Carton Qty on the product card | Added; explicitly does not gate under-carton orders |
| — | Dashboard: no greeting, no emoji, Sales shortcut | Done |

## Evidence

- Backend suite: **561 tests, 0 failures, 6 environmental skips**
- New tests this task: 13 (`test_buying_operator_permissions` 5,
  `test_smart_sales_requirements` 8)
- Frontend production build: clean
- Browser matrix: **162/162** across 1920/1440/1024/768/390/360, zero console errors
- Button audit: **9/9**
- Secret scan: clean
- `site1.local`: fingerprint unchanged
  (`f51fedb5a9ac68e27b1515daee5cdf2f90490a22c07925960dd0acb4d123d9c3`)
