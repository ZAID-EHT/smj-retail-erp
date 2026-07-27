# SMJ Staging Opening-Stock Correction Runbook

**Submission is externally blocked pending accountant sign-off.** Every prerequisite
below is complete; only step 7 requires the accountant.

## 1. Precheck
```
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.inspect
```
Confirm: correctable=true, opening_amount=11,820,700, source vouchers present,
already_submitted=null, Trial Balance balanced.

## 2. Backup
```
bench --site staging.local backup --with-files
```
(Latest on record: `20260727_094121-staging_local-*`.)

## 3. Accountant sign-off (EXTERNAL)
Record approval in `SMJ_ACCOUNTANT_CORRECTION_PACKAGE.md` (account, amount, date,
approver). **Do not proceed without this.**

## 4. Dry run
```
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.dry_run
```
Confirm profit_reduced_by = 11,820,700, balanced_before/after = true, persisted=false.

## 5. Draft creation (optional review)
```
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.prepare_draft
```
Creates a DRAFT JE titled "Opening Stock Account Reclassification — Accountant Approval Required".

## 6. Draft review
Open the draft JE in the Retail ERP; confirm Dr Stock Adjustment 11,820,700 /
Cr Opening Balance Equity 11,820,700, date 2025-07-01.

## 7. Submission (requires sign-off token)
```
bench --site staging.local execute my_store_ui.finance.opening_stock_correction.apply \
  --kwargs '{"confirm":"11820700:APPROVED"}'
```

## 8. Report rerun
Rerun Profit and Loss, Balance Sheet, Trial Balance, Stock Balance. Confirm profit
≈ 4,048,006, expenses positive, sheet balances.

## 9. Stock reconciliation
Confirm stock quantities and valuation unchanged (the correction touches no stock doc).

## 10. Acceptance criteria
- Profit ≈ 4,048,006; expense positive; TB balanced; BS balanced; stock unchanged;
  exactly one submitted correction JE; no duplicate.

## 11. Failure handling
If apply refuses (guardrail), read the message; do not force. Re-verify inspect().

## 12. Reversal
```
# Cancel the submitted JE (from the apply output) in the Retail ERP or:
bench --site staging.local execute frappe.client.cancel --kwargs '{"doctype":"Journal Entry","name":"<JE>"}'
```

## 13. Evidence capture
Save inspect/dry_run/apply/verify_after JSON output and the rerun reports to the
finance evidence folder.
