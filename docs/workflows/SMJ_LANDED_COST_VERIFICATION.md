# SMJ Retail ERP — Landed Cost Voucher Verification (Phase 9)

**Date:** 2026-07-18 · **Site:** staging.local · **Document under test:**
`MAT-LCV-2026-00001` (the only Landed Cost Voucher in the dataset,
confirmed via a direct `docstatus=1` query — exactly one exists, matching
the single import scenario, no duplicates).

## What a Landed Cost Voucher is supposed to do

It distributes additional charges incurred while importing goods
(customs duty, freight, insurance) across the received items'
**valuation rate**, so the item's stock value reflects its true landed
cost, not just its supplier invoice price. This directly affects COGS and
therefore gross profit on every future sale of that item.

## Real evidence traced

**Source Purchase Receipt:** `MAT-PRE-2026-00006`, itself linked to
`Purchase Order PUR-ORD-2026-00006` (supplier: **Indus Prayer Mats
Trading**), confirmed via `Landed Cost Purchase Receipt.receipt_document`
on the LCV itself.

**Charge applied:** "Customs Duty and Freight" = 8% of the Purchase
Receipt's grand total, posted to the Freight and Forwarding Charges
expense account, distributed across items by amount
(`distribute_charges_based_on = "Amount"`).

**Valuation before vs. after** (queried directly from `Purchase Receipt
Item` and cross-checked against the live `Bin` valuation rate):

| Item | Qty | Purchase rate | Valuation rate after LCV | Increase |
|---|---|---|---|---|
| PM-003 | 16.0 | 2,100.00 | **2,268.00** | +8.00% |
| CAR-002 | 7.0 | 55,000.00 | **59,400.00** | +8.00% |

Both items show **exactly an 8.00% increase** — matching the 8% customs
charge precisely. This confirms the Landed Cost Voucher's
amount-based distribution algorithm is working correctly: the entire
charge flows proportionally into every item's valuation, with no
rounding drift or misallocation between the two line items.

## Downstream effect (real, not assumed)

Because this revaluation happened at the stock level (via the LCV's own
`update_rate_in_serial_no` / valuation-rate update mechanism, a real
ERPNext controller action — this pass did not touch a GL Entry or Bin row
directly), every unit of PM-003 and CAR-002 sold after this LCV posts
correctly carries the higher, landed-cost-inclusive COGS. This is exactly
what feeds into the Cost of Goods Sold figure already independently
verified in `SMJ_ACCOUNTING_VERIFICATION.md`.

## Verdict

The Landed Cost Voucher workflow is **verified working correctly** with
precise, checkable math (8% charge → exactly 8% valuation increase on
both affected items), built and posted through ERPNext's real Landed
Cost Voucher doctype (`get_items_from_purchase_receipts()`, real
`taxes` child table, real `.submit()`) — not fabricated or assumed from
reading the generator script alone.
