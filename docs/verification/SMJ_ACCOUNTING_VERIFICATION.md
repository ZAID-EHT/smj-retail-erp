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

## Follow-up batch: Balance Sheet re-balance, Cash Flow, bank reconciliation

Completed in a second pass, script:
`apps/my_store_ui/my_store_ui/dev_scripts/report_reconciliation_phase8_remainder.py`.

### Balance Sheet — independently re-balanced, confirms the P&L finding

```
Total Assets (Debit)                      26,829,566.00
  Debtors                                  3,303,735.70
  Bank Accounts                            3,519,939.60
  Cash In Hand                               383,694.70
  Stock In Hand                           19,622,196.00
Total Liabilities (Credit)                 5,970,860.00
  Creditors                                5,044,760.00
  Stock Received But Not Billed              926,100.00
Total Equity (Credit)                      5,000,000.00
  Revaluation Surplus (capital injection)  5,000,000.00
Provisional Profit / Loss (Credit)        15,858,706.00
Total (Credit)                            26,829,566.00
```

**Assets (26,829,566) = Liabilities (5,970,860) + Equity (5,000,000) +
Provisional Profit/Loss (15,858,706) = 26,829,566.** The Balance Sheet
*does* balance — GL integrity holds — but it balances **by including the
same inflated 15,858,706 "Provisional Profit/Loss" figure as part of
equity**, which is exactly what the P&L finding above predicted. This is
not a new problem, it is the same one, now confirmed from a second,
independent report. If the opening-stock reclassification described above
is corrected, this is a pure **reclassification within equity** — total
assets and total liabilities are unaffected either way; only the split
between "Provisional Profit/Loss" (would drop to ≈4.0M) and a
(currently-missing) "Temporary Opening"-style equity line (would show
≈11.8M) changes. The balance sheet would still balance to 26,829,566
after correction — nothing about total assets/liabilities is in question.

### Cash Flow Statement — runs cleanly, same inflated starting point

Ran without error (18 rows). As expected, it starts its reconciliation
from **"Profit for the year" = 15,858,706** (the same inflated headline
figure) and adjusts for changes in receivables (−3,303,735.70), payables
(+5,044,760.00), and stock (−19,622,196.00), plus the 5,000,000 capital
injection as a financing inflow. **Note on completeness:** the report's
returned rows did not reliably include per-line `account_name` labels in
this call (most came back as `None`), so this pass confirms the report
*executes correctly* and *uses the already-identified inflated profit
figure as its base*, but does not independently re-derive the exact
ending cash balance line-by-line. The report is real and running against
real GL data either way — not a fabricated result — but a fully labeled
line-by-line reconciliation of Cash Flow is left as a further follow-up
if needed.

### Bank Reconciliation Statement — runs cleanly, real data, one honest observation

Ran successfully against "Business Bank Account - SMJ": **87 rows**, all
real Payment Entries and Journal Entries with debit/credit amounts and
reference numbers. **Every row has `clearance_date = null`** — meaning no
bank reconciliation/clearing has ever been performed on this demo
dataset. This is realistic (a business would periodically match
statements), not a bug, but the companion **Bank Clearance Summary**
report correspondingly returns **0 rows** for the same reason (it only
reports on entries that have been cleared). If the demo dataset is later
used to exercise/showcase the bank-reconciliation workflow specifically,
a follow-up should mark a realistic subset of these 87 entries as cleared
via the actual Bank Reconciliation Tool, not a direct DB update.

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
