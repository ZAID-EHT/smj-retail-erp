# Opening-Stock Correction Plan

## The correction

A single **reclassification Journal Entry** dated `2025-07-01`, moving the opening
inventory offset out of the Expense account into equity:

```
Dr  Stock Adjustment - SMJ        11,820,700   (removes the P&L artifact)
Cr  Opening Balance Equity - SMJ  11,820,700   (parks it as opening equity)
```

Script: `dev_scripts/correct_opening_stock_pnl.py` (`run` = dry run, `apply` =
persist).

## Why a Journal Entry and not cancel/amend

The three opening Stock Entries have 100+ downstream documents (deliveries,
invoices, FIFO consumption) built on top of them. Cancelling them would trigger a
Stock Ledger reposting cascade across all of those. A reclassification JE **touches
no stock document and no Stock Ledger Entry** — it only moves the accounting offset
between two GL accounts. Nothing submitted is cancelled or deleted.

## Why `Opening Balance Equity` (not `Temporary Opening`)

`Temporary Opening - SMJ` exists but is an **Asset** account. Crediting it would
reduce total assets while the stock asset remains, leaving the Balance Sheet
unbalanced once the inflated profit is removed. The offset must land in **Equity** so
that the drop in retained earnings (from removing the fake profit) is matched by a
rise in opening equity, keeping Assets = Liabilities + Equity. `Opening Balance
Equity` is the standard account for exactly this.

## Safety properties of the script

- **Refuses to run off `staging.local`.**
- **Refuses to run twice** — looks for its own marker Journal Entry first.
- **Verifies the three expected source Stock Entries** and the exact amount before
  acting; aborts if they are not all present.
- **Verifies both accounts exist** and have the expected root types (Expense →
  Equity); aborts otherwise.
- **`run()` is a dry run** — it builds and submits the JE inside a savepoint, records
  before/after, then rolls back, persisting nothing.
- **`apply()` is reversible** — it creates a standard submitted Journal Entry that
  can be cancelled to undo the correction; a full staging backup was taken first.
- No raw SQL ledger writes; a standard `Journal Entry` controller does all posting.

## Reconciliation targets (all met in the dry run)

- Trial Balance debit = credit, before and after.
- Profit reduced by exactly 11,820,700.
- Expense total flips from an impossible −6,995,496 to a credible +4,825,204.
- Balance Sheet still balances (equity composition shifts; total unchanged).
- No negative stock, no cancelled business document.

See `SMJ_OPENING_STOCK_QA_RESULT.md` and `SMJ_FINANCIAL_RECONCILIATION.md`.
