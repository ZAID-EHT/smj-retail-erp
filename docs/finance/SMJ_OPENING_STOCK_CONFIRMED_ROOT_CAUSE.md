# SMJ Opening-Stock — Confirmed Root Cause (voucher-level)

Confirmed on `staging.local`, 2026-07-27, via `dev_scripts/confirm_root_cause.py`
(read-only). Company `SMJ Retail ERP`.

## Single root cause

Opening inventory was booked with three **Material Receipt Stock Entries** whose
difference account is the **Expense** account `Stock Adjustment - SMJ`. Each debits
`Stock In Hand` (asset) and **credits `Stock Adjustment`** (expense), so the opening
inventory value lands on the Profit and Loss statement as negative expense, inflating
profit.

| Voucher | Type | Posting date | Credit → Stock Adjustment | Against | is_opening | Cancelled |
|---------|------|--------------|--------------------------:|---------|:----------:|:---------:|
| MAT-STE-2026-00001 | Stock Entry | 2025-07-01 | 9,186,100 | Stock In Hand | No | No |
| MAT-STE-2026-00002 | Stock Entry | 2025-07-01 | 1,487,100 | Stock In Hand | No | No |
| MAT-STE-2026-00003 | Stock Entry | 2025-07-01 | 1,147,500 | Stock In Hand | No | No |
| **Opening total** | | | **11,820,700** | | | |

## Account classification (why it hits the P&L)

| Account | root_type | account_type | report_type |
|---------|-----------|--------------|-------------|
| Stock Adjustment - SMJ | **Expense** | Stock Adjustment | **Profit and Loss** |
| Opening Balance Equity - SMJ | Equity | Equity | Balance Sheet |
| Temporary Opening - SMJ | Asset | Temporary | Balance Sheet |

A credit to a **Profit and Loss** expense account reduces expense and inflates profit.
The offset belongs on the **Balance Sheet** — `Opening Balance Equity` is the correct
target (`Temporary Opening` is an Asset and would unbalance the sheet once the fake
profit is removed).

## Ruled-out secondary causes

| Candidate | Finding |
|-----------|---------|
| Opening Invoices (Sales/Purchase, is_opening=Yes) | **0** |
| Manual Journal Entry on Stock Adjustment | **0** |
| Stock Reconciliations on Stock Adjustment | 2, small (1,980 + 10,000), in-period 2025-08 / 2026-07 — **not** part of the opening artifact |
| `is_opening` flag on the opening Stock Entries | **No** (they are plain material receipts) |
| Duplicate opening stock | none (three distinct receipts) |
| Wrong fiscal-year classification | posting date 2025-07-01, correctly in the opening period |

**Conclusion:** one root cause, one correction (reclassify 11,820,700 from Stock
Adjustment to Opening Balance Equity). No stock document needs cancelling.
