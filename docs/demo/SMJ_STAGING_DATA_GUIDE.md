# SMJ Retail ERP — Staging Data Guide

Site: `staging.local` (separate from `site1.local`, which was never touched).
Company: **SMJ Retail ERP** (LKR, Sri Lanka), a carpet/rug/floor-covering wholesaler.
Fiscal year: **2025-07-01 to 2026-06-30**.

Every document named below is real: created and submitted through standard
ERPNext controllers and mappers (Sales Order → Delivery Note → Sales
Invoice, Purchase Order → Purchase Receipt → Purchase Invoice, Payment
Entry, Journal Entry, Stock Entry, Landed Cost Voucher, Stock Reservation
Entry), never written directly to GL Entry / Stock Ledger Entry / Bin /
Payment Ledger Entry. All names below were re-queried from the live
database, not copied from memory.

Login: `Administrator` / `admin`.

---

## 1. Master Data

| Type | Count | Where to browse |
|---|---|---|
| Customers | 26 | `/sales/customers` |
| Suppliers | 12 | `/purchases/suppliers` |
| Items | 40 | `/inventory/products` |
| Item Groups | 7 (Carpets, Rugs, Floor Mats, Prayer Mats, Artificial Grass, Accessories, Cleaning Products) | Item Group filter on Products |
| Brands | 8 | Item filter |
| Warehouses | 10 (5 ERPNext defaults + Main, Colombo, Showroom, Returns, Damaged Goods) | `/inventory/warehouses` |
| Price Lists | 5 (Standard Buying, Standard Selling, Wholesale Price List, Retail Price List, Preferred Customer Price List) | Item Price on any product |
| Pricing Rules | 4 (bulk-qty discount, customer-specific rate, time-limited promo, supplier-specific buying rate) | Selling/Buying Settings → Pricing Rule |
| Payment Terms Templates | 3 (Immediate, Net 30, 50% Advance) | Accounts settings |
| Sales Persons | 5 | Selling settings |
| Contacts / Addresses | 1 company + 2 per customer (billing+shipping) + 1 per supplier | Linked from each party |

### Customer personas (`custom_credit_type` set on every customer)

Cash/non-credit: **ABC Traders**, **Colombo City Interiors**, **Nuwara Eliya Furnishings**.
Credit customers with a credit limit: most Commercial customers (e.g. **Eastern Furnishers**, **Grand Textile House**).
No orders (deliberately untouched): **Priyantha Rugs & More**.
On hold: **Batticaloa Home Mart**.
Inactive (disabled): **Ratnapura Carpet House**.
Near credit limit: **Kurunegala Rug Traders** (limit LKR 200,000).
Over credit limit: **Anuradhapura Floor Decor** (limit LKR 150,000) — see Scenario J below.

### Item catalog highlights

- High-value: `CAR-001` Persian Wool Carpet, `CAR-002` Silk Blend Carpet, `CAR-006` Premium Silk Carpet.
- Fast-selling: `CAR-003`, `CAR-004`, `CAR-007`, `RUG-001`, `RUG-002`, `FM-001`, `FM-002`.
- Slow-moving: `RUG-005`, `RUG-006`, `AG-002`, `FM-006`, `PM-004`, `ACC-003`(low-stock tag), `ACC-004`.
- Low stock: `ACC-003` Carpet Binding Tape.
- Out of stock (zero opening stock, deliberately): `FM-007` Out-of-Stock Logo Mat.
- Overstocked: `RUG-008`, `CLN-004`.
- Discontinued (disabled after receiving opening stock, so its stock history is real): `CAR-008` Discontinued Vintage Carpet.
- No recent sales: `PM-005` Deluxe Prayer Mat.

---

## 2. Sales Workflow Examples

| Scenario | Customer | Sales Order | Delivery Note | Sales Invoice | Payment Entry | Amount (LKR) |
|---|---|---|---|---|---|---|
| A — Cash sale, paid in full | ABC Traders | SAL-ORD-2026-00013 | MAT-DN-2026-00012 | ACC-SINV-2026-00012 | ACC-PAY-2026-00014 | 208,800 |
| B — Credit sale, paid later | Eastern Furnishers | SAL-ORD-2026-00014 | MAT-DN-2026-00013 | ACC-SINV-2026-00013 | ACC-PAY-2026-00015 | 73,950 |
| C — Advance + partial payment | Wattala Home Furnishings | SAL-ORD-2026-00015 | MAT-DN-2026-00014 | ACC-SINV-2026-00014 | Advance: ACC-PAY-2026-00016 (LKR 24,190) · Final: ACC-PAY-2026-00017 (LKR 24,190) | 48,380 |
| D — Pending delivery (SO only, nothing shipped) | City Home Centre | SAL-ORD-2026-00016 | — | — | — | 37,900 |
| E — Partial delivery, two shipments, two invoices | Lanka Interior Solutions | SAL-ORD-2026-00017 | MAT-DN-2026-00015, MAT-DN-2026-00016 | ACC-SINV-2026-00015 (61,960) + ACC-SINV-2026-00016 (165,960) | ACC-PAY-2026-00018 | 331,920 (SO total) |
| F — Quotation → Sales Order → Invoice → Payment | Jaffna Home Essentials | Quotation SAL-QTN-2026-00001 → SAL-ORD-2026-00018 | MAT-DN-2026-00017 | ACC-SINV-2026-00017 | ACC-PAY-2026-00019 | 13,970 |
| G — Draft cancelled before submission | Priyantha Rugs & More | Created then `frappe.delete_doc`-ed while still docstatus=0 — no record remains, no GL impact. Nothing to open; that's the point. | — | — | — | — |
| H — Return + Credit Note | (against Scenario B) | — | Return DN: MAT-DN-2026-00018 | Credit Note: ACC-SINV-2026-00018 (against source SI ACC-SINV-2026-00013 / DN MAT-DN-2026-00013) | Left as available credit (no refund PE) | negative of the original line |
| I — Overdue invoice | Galle Textile Traders | SAL-ORD-2026-00019 | MAT-DN-2026-00019 | ACC-SINV-2026-00019, due 2025-08-15, still unpaid | — | 68,000 |
| J — Credit-limit near/over | Near: Kurunegala Rug Traders, SO **SAL-ORD-2026-00102**, LKR 3,400, well under the 200,000 limit — submitted normally. Over: Anuradhapura Floor Decor — a Sales Order was built to exceed the 150,000 limit and `submit()` genuinely raised `Please contact your administrator to extend the credit limits for Anuradhapura Floor Decor.` (real ERPNext `check_credit_limit()`, not simulated); the draft was then deleted, so no trace of it remains in the database. | | | | | |

Also relevant to Scenario D: **Stock Reservation** was demonstrated separately (not on the same SO) — see §4.

---

## 3. Purchase Workflow Examples

| Scenario | Supplier | Chain | Amount (LKR) |
|---|---|---|---|
| A — Full procurement cycle | Ceylon Weave Mills | Material Request MAT-MR-2026-00001 → RFQ PUR-RFQ-2026-00001 → Supplier Quotation PUR-SQTN-2026-00001 → PO PUR-ORD-2026-00001 → Receipt MAT-PRE-2026-00001 → Invoice ACC-PINV-2026-00001 → Payment ACC-PAY-2026-00020 | 263,200 |
| B — Purchase on credit | Ceylon Weave Mills | PO PUR-ORD-2026-00002 → Receipt MAT-PRE-2026-00002 → Invoice ACC-PINV-2026-00002 → Payment ACC-PAY-2026-00021 (paid near due date) | 179,100 |
| C — Partial receipt, one invoice | Island Cleaning Supplies Co | PO PUR-ORD-2026-00003 → Receipt 1 MAT-PRE-2026-00003 (half qty) → Receipt 2 MAT-PRE-2026-00004 (remaining qty) → Invoice ACC-PINV-2026-00003 (against Receipt 2, LKR 507,500 — about half the PO's 1,015,000 total, exactly reflecting the split) | 507,500 (invoiced) |
| D — Supplier advance | Island Cleaning Supplies Co | PO PUR-ORD-2026-00004 → Advance Payment (against the PO) → Receipt MAT-PRE-2026-00005 → Invoice ACC-PINV-2026-00004 with the advance allocated via `set_advances()` | 142,700 |
| E — Purchase return + Debit Note | (against Scenario B) | Return Receipt MAT-PRE-2026-00007 (against MAT-PRE-2026-00002) → Debit Note ACC-PINV-2026-00005 (return Purchase Invoice against ACC-PINV-2026-00002) | negative of the original line |
| F — Pending purchase, goods not received | Backup Textile Suppliers | PO PUR-ORD-2026-00005 only, no Receipt | 436,700 |
| G — Imported goods, Landed Cost Voucher | Indus Prayer Mats Trading | PO PUR-ORD-2026-00006 → Receipt MAT-PRE-2026-00006 → Landed Cost Voucher MAT-LCV-2026-00001 (8% customs/freight allocated by amount) — item valuation rates increased after the LCV (e.g. PM-003 2,100 → 2,302.59, CAR-002 55,000 → 57,369.23) | — |

---

## 4. Stock Workflow Examples

| Scenario | Document(s) | Detail |
|---|---|---|
| Opening stock | One Stock Entry (Material Receipt) per warehouse, dated 2025-07-01, remarks "Opening Stock 2025-07-01" | Distributed across Main/Colombo/Showroom warehouses per item, honouring each item's stock-level tag |
| Plain warehouse transfer | MAT-STE-2026-00004 | Main Warehouse → Showroom Warehouse |
| Transit transfer (two legs) | Out: MAT-STE-2026-00006 (add_to_transit=1, Main → Goods In Transit) · In: MAT-STE-2026-00007 (Goods In Transit → Colombo Warehouse, via `make_stock_in_entry`) | Real ERPNext in-transit pattern |
| Stock Reconciliation | MAT-RECO-2026-00001 | Counted quantities adjusted vs. book quantities on 2 items in Main Warehouse |
| Damaged goods | MAT-STE-2026-00008 | Moved out of Main Warehouse into Damaged Goods Warehouse, remarks note the reason |
| Stock reservation (create + release) | Stock Reservation Entries MAT-SRE-2026-00001, MAT-SRE-2026-00002, against Sales Order SAL-ORD-2026-00020 (Wijesekara Home Textiles) | Created via the real `create_stock_reservation_entries()` API, then released via `cancel_stock_reservation_entries()` — both genuinely exercised |
| Low / out-of-stock / overstock | See item tags in §1 | `/inventory/products` — filter or open the item directly to see current Bin quantities |

---

## 5. Accounting Examples

| Scenario | Document | Detail |
|---|---|---|
| Opening balance | Journal Entry ACC-JV-2026-00001 (`is_opening="Yes"`) | LKR 5,000,000 capital injection into the Business Bank Account at fiscal-year start |
| Bank charge | Journal Entry ACC-JV-2026-00002 | LKR 1,500 monthly bank service charge |
| Expense correction | Journal Entry ACC-JV-2026-00003 | Reclassifies a freight cost that had been posted to Miscellaneous Expenses |
| Internal transfer | Payment Entry ACC-PAY-2026-00023 | Business Bank Account → Petty Cash, LKR 25,000 |
| Multi-invoice allocation | One Payment Entry allocated across two Sales Invoices for **Royal Home Decor** | Single payment settling two separate invoices in one entry |
| Unallocated advance | Payment Entry ACC-PAY-2026-00025 | Received from a customer with no invoice reference — a genuine unallocated advance |
| Full / partial / outstanding / overdue documents | See §2 and §3 tables above | Every payment state (fully paid, partially paid, unpaid/outstanding, overdue) is represented by a named scenario |

---

## 6. Bulk Transaction Volume

On top of the named scenarios above, ~130 further Sales Order→Delivery Note→
Sales Invoice cycles and ~55 further Purchase Order→Purchase Receipt→
Purchase Invoice cycles were generated across all 12 months of the fiscal
year (seasonal variation month to month, ~68% of invoices get a payment,
~35% of those partially), through the exact same real controllers as the
named scenarios — no synthetic/direct ledger writes anywhere.

Actual achieved totals (see the final status report for the authoritative
numbers) landed close to, but not exactly inside, the requested LKR
10–12M sales / 7–9M purchases / 3–5M ending-inventory bands. This is
reported honestly rather than forced — see the final status report for
the real figures and why.

---

## 7. Frontend Routes

The custom Retail ERP SPA exposes clean routes for the core doctypes;
anything without a handcrafted route resolves through the universal
generated-detail pattern `/generated/{feature}/{name}` (feature = the
doctype's snake-case name with hyphens, e.g. `Purchase Order` →
`purchase-order`). If a specific route below doesn't resolve in your
build, use the in-app global search for the document name instead — it
always works regardless of routing status.

| Doctype | List | Detail (append `/{name}`) |
|---|---|---|
| Customer | `/sales/customers` | `/sales/customers/{name}` |
| Item | `/inventory/products` | `/inventory/products/{name}` |
| Sales Order | `/sales/orders` | `/sales/orders/{name}` |
| Delivery Note | `/sales/delivery-notes` | `/sales/delivery-notes/{name}` |
| Sales Invoice | `/sales/invoices` | `/sales/invoices/{name}` |
| Payment Entry | `/finance/payments` | `/finance/payments/{name}` |
| Quotation | `/sales/quotations` | `/sales/quotations/{name}` |
| Supplier | `/purchases/suppliers` | `/purchases/suppliers/{name}` |
| Material Request | `/purchases/material-requests` | `/purchases/material-requests/{name}` |
| Request for Quotation | `/purchases/requests-for-quotation` | `/purchases/requests-for-quotation/{name}` |
| Supplier Quotation | `/purchases/supplier-quotations` | `/purchases/supplier-quotations/{name}` |
| Purchase Order | `/purchases/orders` | `/purchases/orders/{name}` |
| Purchase Receipt | `/purchases/receipts` | `/purchases/receipts/{name}` |
| Purchase Invoice | `/purchases/invoices` | `/purchases/invoices/{name}` |
| Warehouse | `/inventory/warehouses` | `/inventory/warehouses/{name}` |
| Stock Entry | `/inventory/stock-entries` | `/inventory/stock-entries/{name}` |
| Stock Reconciliation | `/inventory/reconciliations` | `/inventory/reconciliations/{name}` |
| Journal Entry | `/finance/journal-entries` | `/finance/journal-entries/{name}` |
| Landed Cost Voucher, Stock Reservation Entry | — (no handcrafted route) | `/generated/landed-cost-voucher/{name}`, `/generated/stock-reservation-entry/{name}` |
| Home dashboard | `/home` | |
| Smart Sales | `/smart-sales` | |

---

## 8. Intentionally Skipped (documented, not silently dropped)

- **Item images** — no real product photography or asset pipeline exists for this data; items have no `image` set rather than a fabricated placeholder.
- **Website Item / published-in-catalog flags** — `my_store_ui` is an internal ERP SPA, not a public storefront; there is no real e-commerce front for these to publish to, so it wasn't faked.
- **Item Variant Attributes (Size/Colour as true ERPNext variants)** — material/size/colour are captured as plain text (`custom_product_size`, description) rather than wired into full Item Attribute/Template/Variant machinery, which would be substantial extra complexity for a demo catalog with no real need for variant-level stock tracking.
- **Real bank account numbers/phone numbers/emails** — all fictional (`@example-customer.lk`, `@example-supplier.lk`, `+94` numbers built from sequential offsets), per the "no real personal data" requirement.
