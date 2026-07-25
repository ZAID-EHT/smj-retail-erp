# SMJ Purchasing — End-to-End Acceptance (Phase 5)

**Executed:** 2026-07-25 on `staging.local`. **Result: 14/14 steps PASS.**

Reproduce:

```bash
bench --site staging.local execute my_store_ui.dev_scripts.purchase_workflow_verification.run
# add --kwargs "{'keep': 1}" to leave the documents in place for inspection
```

Every step goes through a standard ERPNext controller (`make_request_for_quotation`,
`make_supplier_quotation_from_rfq`, `make_purchase_order`, `make_purchase_receipt`,
`make_purchase_invoice`, `get_payment_entry`, `make_return_doc`,
`get_items_from_purchase_receipts`). **No Stock Ledger Entry, GL Entry, Payment
Ledger Entry or Bin row was written directly.**

## Fixtures (fictional, staging-only)

| Record | Value |
|--------|-------|
| Company | `SMJ Retail ERP` (LKR, FIFO) |
| Supplier | `SMJ Purchase Test Supplier` |
| Item | `SMJ-PURCHASE-TEST-ITEM` (stock item, UOM `Nos`) |
| Warehouse | `Main Warehouse - SMJ`, transit `Goods In Transit - SMJ` |
| Order | 20 Nos @ 500 = 10,000 |

## Results

| # | Step | Document | Outcome |
|---|------|----------|---------|
| 1 | Material Request (Purchase) | `MAT-MR-2026-00002` | created, submitted |
| 2 | MR → Request for Quotation | `PUR-RFQ-2026-00002` | supplier attached, submitted |
| 3 | RFQ → Supplier Quotation | `PUR-SQTN-2026-00002` | grand total **10,000** |
| 4 | SQ → Purchase Order | `PUR-ORD-2026-00068` | qty **20**, total **10,000**, `supplier_quotation` = `PUR-SQTN-2026-00002`, `material_request` = `MAT-MR-2026-00002` |
| 5 | PO → Payment Entry (supplier advance) | `ACC-PAY-2026-00126` | `advance_paid` = **2,000** on the PO |
| 6 | PO → Purchase Receipt (partial) | `MAT-PRE-2026-00069` | received **12/20**, `per_received` = **60%** |
| 7 | PO → Purchase Receipt (remainder) | `MAT-PRE-2026-00070` | remaining qty defaulted to **8**, `per_received` = **100%** |
| 8 | PR → Purchase Invoice (partial billing) | `ACC-PINV-2026-00067` | total **6,000**, outstanding **6,000**, PO `per_billed` = **60%** |
| 9 | PI → Payment Entry (partial) | `ACC-PAY-2026-00127` | paid **3,000**, invoice outstanding **3,000** (payable retained) |
| 10 | PR → Purchase Return | `MAT-PRE-2026-00071` | `is_return=1`, qty **−2** |
| 11 | PI → Debit Note | `ACC-PINV-2026-00068` | `is_return=1`, total **−6,000** |
| 12 | PR → Landed Cost Voucher | `MAT-LCV-2026-00002` | freight **800** applied to receipt valuation |
| 13 | Goods In Transit transfer | `MAT-STE-2026-00009` | 3 Nos → `Goods In Transit - SMJ` |
| 14 | PO cancellation + amendment | `PUR-ORD-2026-00069` → `PUR-ORD-2026-00069-1` | cancelled, amended, amendment status `To Receive and Bill`, still mappable to a Purchase Receipt |

## What each requirement maps to

| Requirement | Covered by | Evidence |
|-------------|-----------|----------|
| Normal local purchase | 1–4, 6–8 | full MR→PO→PR→PI chain |
| Partial receipt | 6 | 12 of 20, `per_received` 60% |
| Multiple receipts | 6 + 7 | two receipts closing to 100% |
| Partial billing | 8 | 6,000 of 10,000, `per_billed` 60% |
| Supplier advance | 5 | `advance_paid` 2,000 |
| Partial payment | 9 | 3,000 of 6,000 |
| Outstanding payable | 9 | invoice outstanding 3,000 after payment |
| Purchase return | 10 | `is_return=1`, −2 qty |
| Debit Note | 11 | `is_return=1`, −6,000 |
| Imported goods / Goods in Transit | 13 | transit warehouse transfer |
| Landed Cost Voucher | 12 | 800 freight applied |
| Cancellation | 14 | PO cancelled |
| Amendment | 14 | amended doc submitted and mappable |
| Full and partial quantities preserved | 6, 7 | remainder auto-defaulted to 8 |
| Source references preserved | 4 | `supplier_quotation` + `material_request` on the PO row |

## Cleanup

All 17 created documents were cancelled and deleted newest-first by `cleanup()`;
the fixture Supplier and Item were removed too. Verified: cleanup completed with no
errors, so `staging.local` is back to its pre-run state. `site1.local` was never
touched.

## Notes

- Steps run sequentially and each commits, so a failure is reported per step and the
  chain continues rather than aborting — the script prints a per-step PASS/FAIL table.
- The reusable read-only assertions (field exposure, mapping registry, submittable /
  amendable, canonical route) are in `my_store_ui/tests/test_purchase_workflow.py`
  (**7 tests green**) so they run in the normal suite without writing documents.
- Field-level audit: `SMJ_PURCHASE_ORDER_DATA_AUDIT.md` (**PASS, no gaps**).
