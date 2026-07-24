# SMJ FIFO Valuation Verification

**Result: PASS (exact match).** Verified live on `staging.local` via standard
ERPNext stock controllers only — no Bin / Stock Ledger Entry / GL Entry written
directly. Reproducer: `my_store_ui/dev_scripts/fifo_verification.py`
(`bench --site staging.local execute my_store_ui.dev_scripts.fifo_verification.run`).

## Configuration
- Controlled test item `SMJ-FIFO-TEST-ITEM`, `valuation_method = FIFO`, stock item.
- Warehouse `Main Warehouse - SMJ`, company `SMJ Retail ERP` (LKR).
- The item is created fresh and fully removed (entries cancelled + deleted) after
  the run, so staging stock and valuation are left unchanged.

## Test documents (standard Material Receipt / Material Issue Stock Entries)
| Step | Voucher | Qty | Rate |
|------|---------|-----|------|
| Receipt 1 | MAT-STE-2026-00009 | 10 | 1,000 |
| Receipt 2 | MAT-STE-2026-00010 | 10 | 1,200 |
| Issue | MAT-STE-2026-00011 | 12 | FIFO |

## Expected vs actual (from Stock Ledger Entry)
FIFO consumes the oldest layer first: 10 × 1,000 + 2 × 1,200.

| Measure | Expected | Actual | Match |
|---------|----------|--------|-------|
| Outgoing valuation of the issue (Σ −`stock_value_difference`) | 12,400.00 | **12,400.00** | ✅ |
| Remaining qty (`qty_after_transaction`) | 8 | **8** | ✅ |
| Remaining stock value (`stock_value`) | 9,600.00 | **9,600.00** | ✅ |

Remaining 8 units value 9,600 = 8 × 1,200, confirming the newer (1,200) layer is
what's left after FIFO consumed the older (1,000) layer first.

## Scope notes (truthful)
- This proves FIFO layer consumption and remaining-layer valuation through the
  Stock Ledger via standard controllers.
- COGS/Gross-Profit propagation to the P&L on a *sale* (Delivery Note → Sales
  Invoice with "Update Stock" / auto stock posting) and return/cancellation repost
  behaviour are covered at the accounting layer by the prior mission's Phase 8/9
  report reconciliation; a dedicated sale-path FIFO→COGS trace remains a follow-up
  and is listed in the final report as not-yet-independently-verified this mission.
- Deliberately **not** used to silently patch the known opening-stock P&L
  classification issue documented by the prior mission.
