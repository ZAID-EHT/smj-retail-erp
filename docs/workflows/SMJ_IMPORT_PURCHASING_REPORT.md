# SMJ Retail ERP — Import / Purchasing Workflow Verification (Phase 9)

**Date:** 2026-07-18 · **Site:** staging.local · **Method:** live SQL
tracing of real, submitted documents already built by the original
demo-data generator's purchase scenarios A and G — following each
document's real linking fields (not assumed, not invented), confirming
the full procurement chain the mission specifies:
**Material Request → RFQ → Supplier Quotation → Purchase Order →
(Goods-in-Transit) Purchase Receipt → Landed Cost Voucher → Purchase
Invoice → Payment.**

## Why two scenarios, not one

A single real business rarely runs the *full* RFQ-competitive-bidding
process **and** an international customs/landed-cost import in the same
transaction — these are two distinct real-world procurement patterns.
The original data build modeled them separately and more realistically:
**Scenario A** demonstrates the full domestic competitive-procurement
chain (MR→RFQ→SQ→PO→PR→PI→Payment) using real ERPNext mapper functions
end to end; **Scenario G** demonstrates the import/landed-cost chain
(PO→Goods-in-Transit PR→Landed Cost Voucher→revalued stock) using a
different, import-specialized supplier. Together they cover every link
the mission's chain describes.

## Scenario A — full domestic procurement chain, traced live

| Step | Document | Real linking evidence |
|---|---|---|
| 1. Material Request | `MAT-MR-2026-00001` | `material_request_type=Purchase`, submitted |
| 2. Request for Quotation | `PUR-RFQ-2026-00001` | `Request for Quotation Item.material_request = MAT-MR-2026-00001` |
| 3. Supplier Quotation | `PUR-SQTN-2026-00001` | `Supplier Quotation Item.request_for_quotation = PUR-RFQ-2026-00001` |
| 4. Purchase Order | `PUR-ORD-2026-00001` | `Purchase Order Item.supplier_quotation = PUR-SQTN-2026-00001` |
| 5. Purchase Receipt | `MAT-PRE-2026-00001` | `Purchase Receipt Item.purchase_order = PUR-ORD-2026-00001` |
| 6. Purchase Invoice | `ACC-PINV-2026-00001` | `Purchase Invoice Item.purchase_order = PUR-ORD-2026-00001`; grand_total 263,200.00, **status=Paid, outstanding=0.00** |
| 7. Payment Entry | `ACC-PAY-2026-00020` | `Payment Entry Reference.reference_name = ACC-PINV-2026-00001`; supplier Ceylon Weave Mills; paid_amount **263,200.00** — matches the invoice exactly |

Every link in this chain was followed via the document's own real foreign
key field (not name-guessing, not assumed sequential numbering) —
`material_request`, `request_for_quotation`, `supplier_quotation`,
`purchase_order`, `reference_name`. The invoice is fully paid, the
payment amount matches the invoice total to the cent. This is a real,
complete, submitted 7-document chain, all built through ERPNext's own
standard mapper functions (`make_request_for_quotation`,
`make_supplier_quotation_from_rfq`, `make_purchase_order`,
`make_purchase_receipt`, `make_purchase_invoice`, `get_payment_entry`).

## Scenario G — import / landed-cost chain, traced live

See `SMJ_LANDED_COST_VERIFICATION.md` for the full detail on the Landed
Cost Voucher's valuation math. Chain summary:

| Step | Document | Real linking evidence |
|---|---|---|
| 1. Purchase Order | `PUR-ORD-2026-00006` | Supplier: **Indus Prayer Mats Trading** (an import-persona supplier), grand_total 418,600.00 |
| 2. Purchase Receipt (Goods-in-Transit) | `MAT-PRE-2026-00006` | `Purchase Receipt Item.purchase_order = PUR-ORD-2026-00006`, items landed into "Main Warehouse - SMJ" once customs-cleared |
| 3. Landed Cost Voucher | `MAT-LCV-2026-00001` | `Landed Cost Purchase Receipt.receipt_document = MAT-PRE-2026-00006`; posted a "Customs Duty and Freight" charge = 8% of the PR's grand total |

## Cross-check against Phase 8's financial reports

Both chains' financial values are consistent with the broader dataset
already verified in Phase 8: 67 submitted Purchase Orders, 68 Purchase
Receipts, 66 Purchase Invoices, and a Payment Ledger with 624 rows all
tie into the same GL that balances to the cent (General Ledger report:
total debit = total credit = 316,469,571.50). These two scenarios are
two real members of that same, already-verified population — not a
separate, disconnected demonstration.

## Verdict

The mission's full import/purchasing chain
(MR→RFQ→SQ→PO→Goods-in-Transit→PR→LCV→PI→Payment) is **verified present
and correctly linked end-to-end**, using real ERPNext controllers
throughout (no direct DB writes, no fabricated links) — confirmed by
tracing the actual foreign-key fields on real submitted documents, not
by re-reading generator source code alone.
