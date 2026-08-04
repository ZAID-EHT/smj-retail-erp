# SMJ Commission Policy

`Retail Commission Policy` — the decisions that turn a calculated figure into money
owed. Screen: **Admin → Commission Policy** (`/retail-erp/admin/sales/commission-policy`).

## The principle

**Nothing here has a business default.** Every unanswered question keeps the policy
`Incomplete`, and an incomplete policy cannot open a period or prepare a payout.
Defaulting any of them would produce authoritative-looking figures that nobody
approved.

## The two levels of completeness

| Level | Requires | Grants |
|---|---|---|
| **Calculation** | earning trigger, basis, rate source, payout cycle, withholding mode, returns rule | open periods, prepare, review, approve, statements, payout preparation |
| **Posting** | the above **plus** expense account, payable account, payee party type, cost centre, accounting document type, accountant approval reference | nothing yet — posting is disabled in this build |

A policy reaches `Active` on calculation completeness alone. `may_post()` stays
False without the second level, and is the single place that answers "can real money
move?".

## Statuses

| Status | Meaning |
|---|---|
| `Draft` | nothing chosen yet |
| `Incomplete` | some but not all calculation decisions made |
| `Ready for Review` | complete for calculation, not yet approved |
| `Approved` | approved but not enabled |
| `Active` | approved **and** enabled **and** within its effective dates |
| `Suspended` | deliberately taken out of force, with a reason |
| `Retired` | past its effective-to date |

Status is derived, never accepted from a payload. `status`, `approved_by` and
`approved_on` are deliberately absent from the writable field list.

## The decisions

### Earning trigger
`Sales Invoice Submission` · `Customer Payment Collection` · `Full Payment
Collection` · `Approved Custom Rule` (needs the approved wording recorded).

Collection-based triggers only include invoices actually paid within the period.
Payment Entry has no sales team field, so collection is derived by joining Payment
Entry Reference → Sales Invoice rather than by stamping the payment.

### Commission basis
`Net Total` · `Net Total After Discount` · `Grand Total Excluding Tax` ·
`Gross Profit` · `Collected Amount` · `Approved Custom Basis`.

Gross Profit reads item cost server-side; cost never reaches the client, and only
the resulting commission figure is shown to a member.

### Rate source
`Sales Team Rate` · `Customer Rate` · `Product Category Rate` · `Fixed Policy Rate` ·
`Approved Priority Order`.

**Customer Rate and Product Category Rate have no data source in this system.**
Selecting one raises a *blocking exception* on every row rather than falling back to
the team rate. Paying a number nobody configured, under a policy that says something
else, would be worse than an unpayable period.

### Withholding
`No Withholding` · `Fixed Percentage` · `Rule Based` · `External Payroll`.

A fixed percentage of zero is refused: leave the mode unset until the rate is
approved. `Rule Based` blocks, because no rules exist.

### Returns and clawbacks
`Reverse Before Payout` · `Deduct From Next Period` · `Create Payable Adjustment` ·
`Manual Review`. See `SMJ_COMMISSION_REVERSAL_AND_CLAWBACK.md`.

### Thresholds
Minimum payout amount, carry-forward of small balances, maximum negative
carry-forward, and a manual approval threshold above which an adjustment needs
higher authority.

## Approval withdrawal

Editing any term of an approved policy **withdraws the approval automatically**.
Otherwise a rate could be changed under a signature given for something else.
Asserted by `test_changing_the_terms_withdraws_the_approval`.

## Endpoints

`list_commission_policies` · `get_commission_policy` · `save_commission_policy` ·
`approve_commission_policy` · `suspend_commission_policy` ·
`validate_commission_policy` · `inspect_commission_policy` ·
`get_commission_policy_status` · `simulate_commission_policy`

Every one declares a default for each argument, so a cleared field arriving as an
empty string is a value meaning "all" — never a missing argument and an HTTP 500.
