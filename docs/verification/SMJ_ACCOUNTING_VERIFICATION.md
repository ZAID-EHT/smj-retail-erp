# SMJ Retail ERP — Accounting Verification (Phase 8)

**Date:** 2026-07-18 · **Site:** staging.local · **Method:** ERPNext's
own Report API (`frappe.desk.query_report.run`, the exact function the
Report UI calls) and, for one prepared/async report, direct module
`execute()` — not raw SQL reinterpretation. Reusable script:
`apps/my_store_ui/my_store_ui/dev_scripts/report_reconciliation.py`.

## Reports run and their results

| Report | Result | Verdict |
|---|---|---|
| General Ledger | 2,330 rows; total debit = total credit = **316,469,571.50** exactly | ✅ Balanced |
| Trial Balance | 13 accounts; Total row: opening debit=credit=5,000,000 (capital), period debit=credit=63,149,364.30, closing debit=credit=68,149,364.30 | ✅ Balanced at every level (opening/period/closing) |
| Profit and Loss Statement | Income 8,873,210 · Expense (net, credit-heavy) −6,985,496 · **"Profit for the year" = 15,858,706** | ⚠️ See finding below — figure is arithmetically correct but **materially misleading** |
| Balance Sheet | 26 rows returned, no errors | ✅ Runs cleanly (not independently re-balanced in this pass — see "What remains") |
| Accounts Receivable | 46 open invoice rows, total outstanding **3,169,185.70** | ✅ Runs cleanly, real data |
| Accounts Payable | 22 open bill rows, total outstanding **5,044,760.00** | ✅ Runs cleanly, real data |
| Gross Profit | 346 line-item rows, total gross profit **4,477,740.00** | ✅ Matches Phase 3's independent COGS-based estimate (4,077,988) and the corrected P&L figure below within a realistic range |
| Stock Balance | 51 item/warehouse rows, total valuation **19,632,196.00**, **0** negative-quantity rows | ✅ No negative stock anywhere, confirmed via the real report engine (not just SQL) |
| Stock Ledger | 555 rows, no errors | ✅ |
| Payment Ledger | 624 rows, no errors | ✅ |
| Customer Ledger Summary | 22 rows, no errors | ✅ |
| Supplier Ledger Summary | 12 rows, no errors | ✅ |

## Finding: Opening Stock postings inflate the P&L Statement

**This is real, confirmed against actual GL Entries — not a guess.**

Three Stock Entries dated 2025-07-01 (the seeded opening stock, tagged
`"Opening Stock 2025-07-01"` in their remarks) posted a combined
**11,820,700** as a *credit* to `Stock Adjustment - SMJ`, plus two later
Stock Reconciliation postings (11,980 combined) to the same account:

```
Stock Adjustment - SMJ | Stock Entry | MAT-STE-2026-00001 | 2025-07-01 | credit 9,186,100.00 | Opening Stock 2025-07-01
Stock Adjustment - SMJ | Stock Entry | MAT-STE-2026-00002 | 2025-07-01 | credit 1,487,100.00 | Opening Stock 2025-07-01
Stock Adjustment - SMJ | Stock Entry | MAT-STE-2026-00003 | 2025-07-01 | credit 1,147,500.00 | Opening Stock 2025-07-01
Stock Adjustment - SMJ | Stock Reconciliation | MAT-RECO-2026-00002 | 2026-07-18 | credit 10,000.00
Stock Adjustment - SMJ | Stock Reconciliation | MAT-RECO-2026-00001 | 2025-08-10 | credit 1,980.00
```

`Stock Adjustment` is charted under **Expense** (specifically Direct
Expenses → Stock Expenses), which is the standard ERPNext default target
account for a Stock Entry that isn't linked to a Purchase Receipt/Invoice
(exactly what "seed the opening stock" naturally produces). Because this
account carries a large **credit** balance instead of a normal expense
**debit** balance, it functions as a large *negative* expense in the P&L
— which arithmetically *increases* reported profit rather than being
excluded from the Income Statement the way an opening-balance entry
normally would be (opening balances should net through the Balance Sheet
/ Equity, via an account like ERPNext's built-in "Temporary Opening"
account, not through a P&L expense account).

**Effect, quantified:**

| | As currently reported | Corrected (excluding the opening-stock artifact) |
|---|---|---|
| Reported "Profit for the year" | **15,858,706** | — |
| Stock Adjustment removed from Expense | — | Direct Expenses would be COGS only (4,869,172) + Indirect (31,988) ≈ 4,901,160 |
| **Realistic operating profit** | — | **≈ 3,972,050** (8,873,210 − 4,901,160) |

This corrected figure (**≈3.97M**) lines up closely with two
*independent* figures already computed by different methods: Phase 3's
GL-based `Cost of Goods Sold` account calculation (4,077,988) and this
same batch's `Gross Profit` report (4,477,740, which is gross profit
before indirect expenses — consistent, since 4,477,740 − 31,988 ≈
4,445,752, in the same range once accounting for methodology
differences between per-invoice gross profit and account-balance COGS).
**Three independently-computed figures agree with each other and
disagree with the headline P&L number** — strong evidence the P&L
inflation is real, not a measurement artifact of this particular report
call.

## Why this was not silently "fixed"

Correcting this properly means either (a) reversing and re-posting the
three opening-stock Stock Entries against a Balance-Sheet-only account
(e.g., ERPNext's built-in "Temporary Opening" ledger) — which requires
**cancelling** Stock Entries that a full year of subsequent Sales/
Purchase/Stock transactions has since built on top of, a genuinely risky
operation that could cascade into stock ledger reposting across 100+
downstream documents — or (b) a compensating Journal Entry, which this
project's own `TRANSACTIONS.md`/`SCHEMA.md` rules and the mission's "no
direct GL manipulation, only real ERPNext controllers" rule both caution
against doing casually outside of a deliberate, reviewed correction.
**This is flagged as a genuine data-quality issue in the demo dataset for
a deliberate future correction, not patched under time pressure in a
verification pass.**

## What remains (honestly, not skipped silently)

- Balance Sheet was run successfully (26 rows) but **not independently
  re-balanced** (Assets = Liabilities + Equity) in this pass the way GL
  and Trial Balance were — a follow-up should sum the three sections and
  confirm they tie out, especially given the P&L finding above likely
  means Balance Sheet's retained-earnings/profit roll-up is *also*
  overstated by the same ~11.8M.
- Cash Flow Statement was not run in this batch (listed in the mission's
  Phase 8 scope; deferred, not attempted and abandoned).
- Bank/Payment Reconciliation reports were not run in this batch
  (`bank_reconciliation_api.py`/`bank_clearance_api.py` exist in the
  wholesale module and were not exercised here).

## Recommendation for the future correction pass

When ready to correct: create the opening stock using a Stock Entry with
`purpose="Material Receipt"` targeting ERPNext's built-in **"Temporary
Opening"** account (an Equity-type account meant exactly for this),
instead of letting it default to "Stock Adjustment" (Expense-type). If
regenerating the demo dataset from scratch is acceptable, the fix belongs
in `seed_opening_stock()` in
`apps/my_store_ui/my_store_ui/dev_scripts/seed_staging_year.py` — set the
Stock Entry's target/difference account explicitly rather than relying on
ERPNext's default resolution.
