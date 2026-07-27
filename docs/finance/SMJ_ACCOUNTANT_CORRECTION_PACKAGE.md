# SMJ Opening-Stock Correction — Accountant Package

Tool: `my_store_ui/finance/opening_stock_correction.py`. Tests:
`test_opening_stock_correction`.

## Root cause
Three Material Receipt Stock Entries (MAT-STE-2026-00001/2/3, 2025-07-01) credited the
opening inventory value to the **Expense** account `Stock Adjustment - SMJ`, inflating
profit. See `SMJ_OPENING_STOCK_CONFIRMED_ROOT_CAUSE.md`.

## The correction
Single reclassification Journal Entry, dated 2025-07-01:

| Line | Account | Debit | Credit |
|------|---------|------:|-------:|
| 1 | Stock Adjustment - SMJ (Expense) | **11,820,700** | — |
| 2 | Opening Balance Equity - SMJ (Equity) | — | **11,820,700** |

- **Exact amount:** LKR 11,820,700 (verified from GL; tool refuses any other amount)
- **Posting date:** 2025-07-01 (opening period)
- **Is Opening:** the JE records an opening reclassification; the remark labels it
- **User remark / title:** "Opening Stock Account Reclassification — Accountant Approval Required"

## Before → expected after (from dry run)

| Measure | Before | After |
|---------|-------:|------:|
| Profit for the period | 15,868,706 | **4,048,006** |
| Expense (net) | −6,995,496 | +4,825,204 |
| Trial Balance | balanced | balanced |
| Stock quantity / valuation | unchanged | unchanged |

## Risks & mitigations
- **Risk:** none to stock — no stock document is cancelled; no SLE reposting.
- **Risk:** wrong target account → mitigated: tool hard-checks Expense→Equity root types.
- **Risk:** double application → mitigated: refuses if a submitted correction exists.
- **Risk:** wrong amount/vouchers → mitigated: refuses unless the three source vouchers
  and the exact amount match.
- **Risk:** wrong site → mitigated: allowlist; site1.local always refused.

## Rollback
Cancel the submitted Journal Entry (standard). No ledger surgery.

## Accountant decision fields (record here on sign-off)
- [ ] Approved target account: `Opening Balance Equity - SMJ` (or specify alternative)
- [ ] Approved amount: `11,820,700`
- [ ] Approved posting date: `2025-07-01`
- [ ] Approver name / date: ____________________

## Commands
```
# Review (read-only):
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.inspect
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.dry_run

# Create a DRAFT JE for review (not submitted):
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.prepare_draft

# Apply (ONLY after accountant sign-off):
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.apply \
  --kwargs '{"confirm":"11820700:APPROVED"}'

# Verify after apply:
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.verify_after
```

**Apply is externally blocked pending accountant sign-off** — it is not run in this
mission.
