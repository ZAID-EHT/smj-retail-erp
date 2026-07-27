# Opening-Stock P&L Overstatement — Root Cause

Audited on `staging.local`, 2026-07-27 (read-only), confirming the issue reported in
`docs/verification/SMJ_ACCOUNTING_VERIFICATION.md` is still present with the same
magnitude. Audit script: `dev_scripts/audit_opening_stock.py`.

## The defect

Three opening-stock **Stock Entries** dated `2025-07-01`
(`MAT-STE-2026-00001/2/3`) posted the opening inventory value as a **credit to
`Stock Adjustment - SMJ`**:

| Voucher | Date | Credit to Stock Adjustment |
|---------|------|---------------------------:|
| MAT-STE-2026-00001 | 2025-07-01 | 9,186,100 |
| MAT-STE-2026-00002 | 2025-07-01 | 1,487,100 |
| MAT-STE-2026-00003 | 2025-07-01 | 1,147,500 |
| **Opening total** | | **11,820,700** |

(Two later Stock Reconciliations add 11,980 more, for a Stock Adjustment net credit
of 11,832,680; only the 11,820,700 opening portion is the artifact being corrected.)

## Why it inflates profit

`Stock Adjustment - SMJ` is charted under **Expense** (root_type = Expense,
Direct Expenses → Stock Expenses). A **credit** to an expense account is negative
expense, which **increases** reported profit. Confirmed live:

| P&L line | As reported (before correction) |
|----------|--------------------------------:|
| Income | 8,873,210 |
| Expense (net) | **−6,995,496** (negative — impossible for a real expense total) |
| **Profit for the period** | **15,868,706** |

The negative expense total is the tell: the 11.82M opening-stock credit is
masquerading as this year's trading result.

## What it should have been

Opening inventory is not this year's profit — it is the owner's opening
contribution. It should net through the **Balance Sheet / Equity**, not the P&L. The
standard ERPNext pattern books opening stock against a balance-sheet account
(`Temporary Opening`, then cleared to opening equity), leaving the Income Statement
untouched.

## One root cause, not several

There is a single root cause: the opening Stock Entries' difference account was the
Expense `Stock Adjustment` instead of a balance-sheet account. The later Stock
Reconciliations (11,980) are ordinary in-period adjustments and are **not** part of
the correction.

## Correction target available

The company already has an **`Opening Balance Equity - SMJ`** account (root_type =
Equity) — the textbook-correct home for an opening-balance offset. See
`SMJ_OPENING_STOCK_CORRECTION_PLAN.md`.
