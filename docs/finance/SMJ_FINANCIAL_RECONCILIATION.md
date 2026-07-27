# Financial Reconciliation — Opening-Stock Correction

Basis: live GL on `staging.local`, 2026-07-27, before correction; and the
savepoint dry-run "after" figures from `correct_opening_stock_pnl.run`.

## Trial Balance

| | Before | After (dry run) |
|---|-------:|----------------:|
| Total debit | 68,293,914.30 | 80,114,614.30 |
| Total credit | 68,293,914.30 | 80,114,614.30 |
| Balanced | ✓ | ✓ |

The correction adds 11,820,700 to both debit (Stock Adjustment) and credit (Opening
Balance Equity), so totals rise equally and the Trial Balance stays balanced.

## Profit & Loss

| Line | Before | After |
|------|-------:|------:|
| Income | 8,873,210 | 8,873,210 |
| Expense (net) | −6,995,496 | 4,825,204 |
| Profit for the period | 15,868,706 | 4,048,006 |

The opening inventory (11,820,700) is removed from the Income Statement. The
remaining profit (4,048,006) reflects actual trading, and the expense total is now
positive and credible (COGS + operating expenses), no longer a nonsensical negative.

## Balance Sheet integrity

- **Stock in Hand (asset)** — unchanged; the correction does not touch any stock
  document or the Stock Ledger.
- **Retained earnings** — fall by 11,820,700 as the fake profit is removed.
- **Opening Balance Equity** — rise by 11,820,700.
- **Net equity** — unchanged (retained earnings down = opening equity up).
- Therefore **Assets = Liabilities + Equity still holds**, and the Trial Balance
  remains balanced (proven above).

## Stock integrity

- No Stock Ledger Entry is written or reposted.
- No submitted stock/business document is cancelled or deleted.
- No negative stock is created (nothing stock-side changes).

## Management-analysis reliability note

Any management/analysis figure that read the pre-correction P&L profit of
**15,868,706** was reading an opening-stock-inflated number. The corrected,
reconciled profit for the period is **4,048,006**. Downstream analyses should cite
the corrected figure once the reclassification JE is applied with accountant
sign-off.

## Post-application steps (after `apply()` with sign-off)

1. Rerun Profit and Loss Statement, Balance Sheet, Trial Balance, Stock Balance.
2. Confirm Profit for the period ≈ 4,048,006 and expenses positive.
3. Confirm Balance Sheet balances and Stock Balance value equals the stock asset
   ledger.
4. Confirm no negative stock and no cancelled business documents.
