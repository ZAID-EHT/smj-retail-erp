# SMJ Retail ERP — Demo Walkthrough

A step-by-step tour of `staging.local` using real, seeded documents. Log in
as `Administrator` / `admin`. Every name below is a real document verified
against the live database — see `SMJ_STAGING_DATA_GUIDE.md` for the full
reference and route conventions.

1. **View the Home dashboard** — `/home`. Live KPI cards, sales trend,
   payment collection donut, top categories, stock overview, low-stock
   alerts, all backed by real seeded transactions.
2. **Open a customer** — `/sales/customers/Eastern Furnishers`. A Credit
   Customer with a LKR 800,000 limit, contact, billing + shipping address.
3. **Check that customer's credit status** — from the customer detail page
   (or `my_store_ui.wholesale.credit.get_customer_credit_status`), see real
   outstanding balance vs. credit limit, computed live from ERPNext data.
4. **Open an item** — `/inventory/products/CAR-001`. Persian Wool Carpet:
   material, size/colour, brand, purchase/retail/wholesale price, reorder
   level, default supplier and warehouse.
5. **Check stock for that item** — same detail page, or `/inventory/stock-entries`
   filtered by item — see actual quantity on hand in Main Warehouse.
6. **Open the quotation** — `/sales/quotations/SAL-QTN-2026-00001` for
   Jaffna Home Essentials.
7. **Follow it to its Sales Order** — `/sales/orders/SAL-ORD-2026-00018`,
   converted from the quotation above via the real `make_sales_order` mapper.
8. **Look at the stock reservation example** — `/sales/orders/SAL-ORD-2026-00020`
   (Wijesekara Home Textiles) and the linked Stock Reservation Entries
   `MAT-SRE-2026-00001` / `MAT-SRE-2026-00002` — created and then released
   through the real reservation API.
9. **Open a Delivery Note** — `/sales/delivery-notes/MAT-DN-2026-00017`,
   delivering the quotation-derived Sales Order above.
10. **Open the final Sales Invoice** — `/sales/invoices/ACC-SINV-2026-00017`,
    LKR 13,970, paid in full.
11. **View its Payment Entry** — `/finance/payments/ACC-PAY-2026-00019`.
12. **Check the General Ledger impact** — open the Sales Invoice's linked
    accounting ledger (Debtors debited on invoice, credited on payment;
    Sales account credited; Cost of Goods Sold posted from the Delivery
    Note) — every entry traces back to one of these three documents.
13. **Open a supplier** — `/purchases/suppliers/Ceylon Weave Mills`.
14. **Follow Purchase Order → Receipt → Invoice** —
    `/purchases/orders/PUR-ORD-2026-00001` →
    `/purchases/receipts/MAT-PRE-2026-00001` →
    `/purchases/invoices/ACC-PINV-2026-00001` (LKR 263,200, the full MR→RFQ→
    Supplier Quotation→PO→PR→PI→Payment procurement cycle).
15. **View a stock transfer** — `/inventory/stock-entries/MAT-STE-2026-00004`,
    Main Warehouse → Showroom Warehouse.
16. **View a return** — Delivery Note `MAT-DN-2026-00018` (return, `is_return=1`)
    against the original delivery `MAT-DN-2026-00013`.
17. **View the Credit Note** — `/sales/invoices/ACC-SINV-2026-00018`, the
    return Sales Invoice issued against `ACC-SINV-2026-00013` (Eastern
    Furnishers) — negative amounts, left as available customer credit.
18. **View a Debit Note** — `/purchases/invoices/ACC-PINV-2026-00005`, the
    return Purchase Invoice against `ACC-PINV-2026-00002` (Ceylon Weave
    Mills), paired with return Purchase Receipt `MAT-PRE-2026-00007`.
19. **Check receivables** — Accounts Receivable / customer outstanding
    report; total outstanding across all Sales Invoices is real and
    non-zero (mix of unpaid, partially paid, fully paid).
20. **Check payables** — Accounts Payable / supplier outstanding report;
    same for Purchase Invoices.
21. **Check stock reports** — Stock Balance / Stock Ledger reports show
    real quantity and valuation movement across all warehouses, including
    the Landed Cost Voucher's valuation change on `PM-003` / `CAR-002`.
22. **Check Profit and Loss** — real income/expense figures driven entirely
    by the seeded Sales and Purchase Invoices plus the three Journal
    Entries (`ACC-JV-2026-00001/2/3`).
23. **Check Balance Sheet** — reflects the LKR 5,000,000 opening capital
    injection, ending inventory value, receivables and payables.
24. **Check Cash Flow** — driven by the real Payment Entries, including the
    Internal Transfer (`ACC-PAY-2026-00023`, Bank → Petty Cash) and the
    unallocated advance (`ACC-PAY-2026-00025`).
25. **Check the transaction register / recent transactions widget** — on
    `/home` or a module dashboard, confirm Sales Invoices, Purchase
    Orders and Delivery Notes all appear with real customers/suppliers
    and amounts, not placeholder data.

## Two things worth trying on purpose

- **The blocked over-limit order**: try creating a new Sales Order for
  **Anuradhapura Floor Decor** (credit limit LKR 150,000) for more than
  that amount and submit it — you should see ERPNext's real credit-limit
  validation fire, the same way it did when this dataset was built.
- **The overdue invoice**: open `/sales/invoices/ACC-SINV-2026-00019`
  (Galle Textile Traders) — due date 2025-08-15, still unpaid, genuinely
  overdue against today's date.
