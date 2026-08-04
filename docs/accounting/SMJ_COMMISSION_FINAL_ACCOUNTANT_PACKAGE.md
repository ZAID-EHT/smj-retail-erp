# Commission Accounting — Final Accountant Decision Package

**Status: none of the ten decisions below has been made. Nothing has been posted.**
**Commission posting is disabled in this build and cannot be enabled by configuration.**

This package exists so that an accountant makes ten choices on evidence. The software
makes none of them, and is built so that it cannot start making them by accident: every
field below ships empty, an empty field keeps the policy `Incomplete`, and an incomplete
policy cannot pay.

Companion documents: `SMJ_COMMISSION_ACCOUNTING_OPTIONS.md` (the five payout document
candidates compared in full), `../sales/SMJ_COMMISSION_PAYOUT_BOUNDARY.md`.

---

## The worked example used throughout

One invoice, one team, so that each decision can be seen in figures rather than prose.

| | |
|---|---|
| Eligible commission base | LKR 100,000.00 |
| Commission rate | 2% |
| **Commission pool** | **LKR 2,000.00** |

| Member | Role | Share | Amount |
|---|---|---|---|
| Member A | Sales Manager | 50% | LKR 1,000.00 |
| Member B | Sales Representative | 25% | LKR 500.00 |
| Member C | Sales Representative | 25% | LKR 500.00 |
| | | **100%** | **LKR 2,000.00** |

This split is asserted by test rather than typed into a document, so it cannot drift
away from what the software would actually calculate.

**Note what the example does not say:** it does not say *when* those 2,000 became owed,
*what* the 100,000 was measured on, which accounts it touches, or who gets paid. Those
are exactly the ten decisions.

---

## The ten decisions

Each is a separate record in the Accountant Decision Centre at
`/retail-erp/admin/finance/decisions`, so that revising one does not silently reopen the
others.

### 1. Earning trigger — when is commission earned?

| | |
|---|---|
| Policy field | `earning_trigger` |
| Current value | *(empty)* |
| Options | Sales Invoice Submission · Customer Payment Collection · Full Payment Collection · Approved Custom Rule |
| Accounting impact | Fixes the period in which the expense and the matching liability are recognised. |
| Risk if guessed | Earning on invoicing accrues commission on money not yet collected — if the customer never pays, commission was accrued on a sale that did not happen. Earning on collection defers the cost away from the period that produced the revenue. |

**Decision:** ☐ Approved ☐ Approved with changes ☐ Rejected   Value: ......................

### 2. Calculation basis — what is commission calculated on?

| | |
|---|---|
| Policy field | `commission_basis` |
| Current value | *(empty)* |
| Options | Net Total · Net Total After Discount · Grand Total Excluding Tax · Gross Profit · Collected Amount · Approved Custom Basis |
| Accounting impact | Determines the base amount, and therefore every figure downstream. |
| Risk if guessed | Commission on a tax-inclusive total pays commission on tax the business merely collects. Gross Profit additionally exposes cost prices to anyone who can read a commission statement. |

**Decision:** ☐ Approved ☐ Approved with changes ☐ Rejected   Value: ......................

### 3. Commission expense account

| | |
|---|---|
| Policy field | `commission_expense_account` |
| Current value | *(empty)* |
| Options | An expense account chosen by the accountant |
| Accounting impact | Sets where commission cost appears in the Profit and Loss. |
| Risk if guessed | A guessed account misstates the P&L and can bury commission inside an unrelated cost line where no reviewer will recognise it. |

**Decision:** ☐ Approved ☐ Rejected   Account: ......................

### 4. Commission payable account

| | |
|---|---|
| Policy field | `commission_payable_account` |
| Current value | *(empty)* |
| Options | A liability account chosen by the accountant |
| Accounting impact | Sets where unpaid commission sits on the Balance Sheet until settled. |
| Risk if guessed | Without a distinct payable, commission owed is invisible on the balance sheet and cannot be aged against the payee. |

**Decision:** ☐ Approved ☐ Rejected   Account: ......................

### 5. Payee party type

| | |
|---|---|
| Policy field | `payee_party_type` |
| Current value | *(empty)* |
| Options | Employee · Supplier · Approved Other |
| Accounting impact | Determines which subledger the obligation lives in, and which tax and payroll rules apply. |
| Risk if guessed | Treating an employee as a supplier can bypass payroll withholding entirely. Treating a contractor as an employee pulls them into payroll reporting they do not belong in. |

**Decision:** ☐ Approved ☐ Rejected   Value: ......................

### 6. Payout document type

| | |
|---|---|
| Policy field | `accounting_document_type` |
| Current value | *(empty)* |
| Options | Journal Entry · Payment Entry · Expense Claim · Payroll Component · Approved Other |
| Accounting impact | Decides how the obligation is recognised and settled, and what cancellation and reconciliation look like. |
| Risk if guessed | Payment Entry alone skips the accrual — commission earned in March and paid in April lands wholly in April, misstating both months. Expense Claim describes earnings as a reimbursement and fails outright for non-employees. |

Summary of the comparison in `SMJ_COMMISSION_ACCOUNTING_OPTIONS.md`:

| Option | Accrual | Payment | Withholding | Non-employee payees |
|---|---|---|---|---|
| Journal Entry | Explicit | Separate entry | Hand-built | Works |
| Payment Entry | **None** | Native | Deductions | Works |
| Expense Claim | Via employee payable | Native | Limited | **Fails** |
| Payroll Component | Via salary slip | Payroll run | **Native** | **Fails** |

**Decision:** ☐ Approved ☐ Rejected   Value: ......................

### 7. Payout cycle

| | |
|---|---|
| Policy field | `payout_cycle` |
| Current value | *(empty)* |
| Options | Weekly · Fortnightly · Monthly · Quarterly · Manual Period |
| Accounting impact | Sets the period boundary every statement, carry-forward and clawback uses. |
| Risk if guessed | Changing the cycle after periods exist re-cuts boundaries and makes already-issued statements disagree with the system. |

**Decision:** ☐ Approved ☐ Rejected   Value: ......................

### 8. Withholding

| | |
|---|---|
| Policy field | `withholding_mode` |
| Current value | *(empty)* |
| Options | No Withholding · Fixed Percentage · Rule Based · External Payroll |
| Accounting impact | Determines what is deducted before the payee is paid. |
| Risk if guessed | A percentage nobody approved would be applied to real payments. Under-withholding creates a statutory liability for the business; over-withholding underpays the payee. |

**Decision:** ☐ Approved ☐ Rejected   Value: ......................   Rate: ..........%

### 9. Tax treatment

| | |
|---|---|
| Policy field | recorded on the decision record |
| Current value | *(empty)* |
| Accounting impact | Determines how commission is reported for tax purposes. |
| Risk if guessed | Depends on the payee party type and on local rules. The software has no basis on which to assume either, and a wrong assumption surfaces at filing. |

**Decision:** ☐ Approved ☐ Rejected   Treatment: ......................

### 10. Returns and clawback

| | |
|---|---|
| Policy field | `returns_rule` |
| Current value | *(empty)* |
| Options | Reverse Before Payout · Deduct From Next Period · Create Payable Adjustment · Manual Review |
| Accounting impact | Decides what happens to commission already earned when the sale is returned. |
| Risk if guessed | Each option produces a different balance for the same return. Deducting from the next period can drive a payee negative; reversing before payout can reopen a closed period. |

**Decision:** ☐ Approved ☐ Rejected   Value: ......................

---

## What the software does today

| Capability | State |
|---|---|
| Calculate commission from a policy and team | Built and tested |
| Prepare a period, review it, approve it | Built and tested |
| Produce statements per person | Built and tested |
| Prepare a payout and validate every line | Built and tested |
| Show the accounting that *would* be produced | Built — preview only |
| **Post commission accounting** | **Disabled. Cannot be enabled by configuration.** |
| **Pay a commission payout** | **Disabled.** |

`posting_blockers()` always returns a non-empty list — the final entry is added
unconditionally, so the list cannot become empty by filling fields in.
`post_commission_payout()` is reachable and always refuses, naming what is missing. The
endpoint is kept deliberately: an absent endpoint invites someone to write a quick one
against the ledger; an endpoint that refuses does not.

---

## Evidence requirements

The Decision Centre refuses to record an approval that has no evidence attachment or
reference, refuses a rejection with no reason, and refuses to let whoever prepared a
proposal record the decision on it. `System Manager` is excluded from the
decision-recording capability outright, so an administrator cannot manufacture finance
approval. Full matrix: `../security/SMJ_ACCOUNTANT_DECISION_PERMISSION_MATRIX.md`.

---

## Sign-off

All ten decisions above must be recorded before commission posting can be considered.
Recording them does **not** enable posting in this build; enabling posting is a separate
piece of development that must itself be reviewed once the answers are known.

Accountant name: ............................................................

Signature / reference: ......................................................

Date: ...................  Effective date: ...................

---

## Verification checklist — after the decisions are recorded

- [ ] All ten decisions show a recorded answer in the Decision Centre
- [ ] Each carries evidence and a named accountant
- [ ] No decision was recorded by the person who prepared it
- [ ] The policy fields match the recorded answers
- [ ] The policy reaches `Active` only after that
- [ ] `posting_blockers()` still lists the build-level block
- [ ] `post_commission_payout()` still refuses
- [ ] Decisions move to Implemented, then Verified
