# SMJ Commission — Accounting Options

**No option has been selected.** This document exists so the choice is made on
evidence by someone qualified, not on convenience by whoever writes the code.

The policy carries an `accounting_document_type` field with these options. Until an
accountant sets it *and* the accounts, party type and approval reference,
`policy.may_post()` is False and every payout is blocked.

---

## The five candidates

### 1. Journal Entry

| | |
|---|---|
| Party handling | Full — party type and party per line |
| Payable recognition | Explicit: debit commission expense, credit commission payable |
| Payment handling | Separate; a later Payment Entry settles the payable |
| Tax / withholding | Supported as additional lines, but every rule is hand-built |
| Audit trail | Strong — a normal submitted, cancellable accounting document |
| Cancellation | Standard cancel + amend |
| Reconciliation | Payable ages properly against the party |
| Payroll implications | None |
| Non-employee reps | Works — party can be Supplier |

**Strongest for:** recognising the liability in the period it was earned, which is
what a commission accrual is.
**Weakest for:** withholding logic must be written by hand; nothing computes it.

### 2. Payment Entry

| | |
|---|---|
| Party handling | Full |
| Payable recognition | **None** — it pays, it does not accrue |
| Payment handling | Native |
| Tax / withholding | Deductions supported |
| Audit trail | Strong |
| Cancellation | Standard |
| Reconciliation | Native against the party |
| Payroll implications | None |
| Non-employee reps | Works |

**Strongest for:** the moment money actually leaves.
**Weakest for:** it skips the accrual entirely. Commission earned in March and paid
in April would land wholly in April, misstating both months. Realistically this is
the *second* document, after a Journal Entry.

### 3. Expense Claim

| | |
|---|---|
| Party handling | Employee only |
| Payable recognition | Yes, via the employee payable |
| Payment handling | Native, through the claim's own payment |
| Tax / withholding | Limited |
| Audit trail | Strong, with its own approval workflow |
| Cancellation | Standard |
| Reconciliation | Against the employee |
| Payroll implications | Appears in HR reporting as a reimbursement |
| Non-employee reps | **Fails** |

**Strongest for:** an existing approval workflow, if every representative is an
employee.
**Weakest for:** it means "I spent money, reimburse me". Commission is earnings, not
a reimbursement, and describing it as one distorts both HR and expense reporting.

### 4. Payroll component (Additional Salary)

| | |
|---|---|
| Party handling | Employee only |
| Payable recognition | Through the salary slip |
| Payment handling | Through the payroll run |
| Tax / withholding | **Native and correct** — the payroll engine handles statutory deductions |
| Audit trail | Strong within payroll |
| Cancellation | Salary slip cancellation |
| Reconciliation | Through payroll |
| Payroll implications | Full — this *is* payroll |
| Non-employee reps | **Fails** |

**Strongest for:** withholding and statutory treatment, which it does properly
instead of approximately.
**Weakest for:** requires HR/Payroll to be configured and every representative to be
an employee, and ties the commission cycle to the payroll cycle.

### 5. Supplier-style payable (Purchase Invoice against a Supplier)

| | |
|---|---|
| Party handling | Supplier |
| Payable recognition | Native |
| Payment handling | Standard supplier payment |
| Tax / withholding | Supported through purchase tax templates |
| Audit trail | Strong |
| Cancellation | Standard |
| Reconciliation | Native supplier ageing |
| Payroll implications | None |
| Non-employee reps | **Native fit** |

**Strongest for:** self-employed or agency representatives who invoice the business.
**Weakest for:** describing an employee as a supplier is wrong, and in many
jurisdictions a compliance problem.

---

## What the answer probably depends on

| If… | The likely fit |
|---|---|
| Every representative is an employee, and withholding is statutory | **Payroll component** |
| Every representative is an employee, and withholding is not statutory | **Journal Entry** to accrue, then Payment Entry |
| Representatives are self-employed and invoice | **Supplier payable** |
| A mixture | Two adapters, chosen per payee — which is why `payee_party_type` is on the policy |

The system does not choose. `SMJ_COMMISSION_PAYOUT_PREPARATION.md` records exactly
what has to be answered.

---

## The adapter, when a choice is made

`commission_payout.py` already produces the shape any of these need — party type,
party, debit account, credit account, amount, cost centre and a reference back to
the period — in `_preview_entries`. Implementing an adapter means turning that
preview into a real document, in five modes:

| Mode | Behaviour |
|---|---|
| `inspect` | What would be produced, and what is missing. **Built** (`get_commission_payout`). |
| `dry_run` | The full proposed entry, unposted. **Built** (`accounting_preview`). |
| `prepare_draft` | Create the document as a draft, unsubmitted. Not built. |
| `verify` | Reconcile the draft against the period. Not built. |
| `cancel_or_reverse` | Cancel or reverse a posted payout. Not built. |

`prepare_draft` and beyond stay unbuilt on purpose: each needs to know which
document it is creating, and that is the decision nobody has made.

## The gate that cannot be configured away

Even with every field set, submission additionally requires an authorised Accounts
role, a current backup, no duplicate payout for the period, an approved period, an
explicit confirmation, and the accountant's recorded approval reference.
`post_commission_payout` refuses today regardless, and the `Posted` and
`Partially Posted` statuses are refused by the payout controller itself, so the
status cannot be forced onto the record by any route.
