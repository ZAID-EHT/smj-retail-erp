# SMJ Accountant Sign-off Checklist

## Opening-stock reclassification (required before go-live)

**Issue:** opening inventory (LKR 11,820,700) was booked as a credit to the Expense
account `Stock Adjustment`, inflating reported profit (15,868,706) and producing a
nonsensical negative expense total.

**Proposed correction (reviewed, reversible):** a Journal Entry dated 2025-07-01
moving 11,820,700 from `Stock Adjustment` (Expense) to `Opening Balance Equity`
(Equity). Dry-run reconciliation (rolled back, nothing persisted):

- Profit for the period: 15,868,706 → **4,048,006** (−11,820,700)
- Expense total: −6,995,496 → **+4,825,204**
- Trial Balance: balanced before and after
- Balance Sheet: still balances (equity composition shifts, total unchanged)

## Sign-off decisions
- [ ] Confirm `Opening Balance Equity` is the correct target account (vs. Capital, etc.).
- [ ] Confirm the corrected period profit (~4,048,006) is credible for the period.
- [ ] Authorise applying the correction on staging/production:
      `bench --site <site> execute my_store_ui.dev_scripts.correct_opening_stock_pnl.apply`
- [ ] After apply: re-review P&L, Balance Sheet, Trial Balance and Stock Balance.

## Notes
- The apply is a single standard Journal Entry; undo = cancel that JE.
- No stock document is cancelled; no ledger is edited directly.
