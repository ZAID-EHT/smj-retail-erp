# SMJ Commission Payout — Blockers and External Requirements

## The one blocker: eight accountant decisions

Commission is calculated, closed, reviewed, approved, stated and prepared for
payout. It is **not posted**, and cannot be, until an accountant settles all eight:

| # | Decision | Why it cannot be guessed | Where it goes |
|---|---|---|---|
| 1 | **Commission expense account** | Picking one silently misstates the P&L. | `commission_expense_account` |
| 2 | **Commission payable account or payment method** | Determines whether the liability is recognised at all, and where it ages. | `commission_payable_account`, `mode_of_payment` |
| 3 | **Payee party type** | Employee vs Supplier changes the tax treatment, the ledger and, in many jurisdictions, the legal position. | `payee_party_type` |
| 4 | **Earned on invoicing or on collection** | Changes *when* the liability exists, and by how much when a customer never pays. | `earning_trigger` |
| 5 | **Payout cycle** | Determines which invoices fall into which run. | `payout_cycle` |
| 6 | **Withholding treatment** | Statutory and jurisdiction-specific. A wrong rate is a compliance failure, not a rounding error. | `withholding_mode`, `withholding_percentage` |
| 7 | **Tax treatment** | Whether commission carries tax, and at what rate. | part of the accounting document choice |
| 8 | **Cancellation and clawback rules** | What happens to money already paid when the sale comes back. | `returns_rule` |

Every one has a field waiting for it. None has a default. The policy stays
`Incomplete` until 4, 5, 6 and 8 are answered, and `may_post()` stays False until
1, 2, 3 and 7 are as well.

## Which accounting document

Not chosen, deliberately. Five candidates are compared on party handling, payable
recognition, payment handling, withholding support, audit trail, cancellation,
reconciliation, payroll implications and non-employee representatives in
`docs/accounting/SMJ_COMMISSION_ACCOUNTING_OPTIONS.md`.

The likely answer depends on whether representatives are employees, and whether
withholding is statutory — which are decisions 3 and 6.

## What was built instead of guessing

| Capability | State |
|---|---|
| Policy configuration with no defaults | complete |
| Policy validation and simulation over real data | complete |
| Period closing, overlap prevention, idempotent preparation | complete |
| Exceptions that block approval | complete |
| Adjustments with segregation of duties | complete |
| Member statements with permission filtering | complete |
| Review and approval with an audit trail | complete |
| Payout grouping, payee resolution, line validation | complete |
| Dry-run accounting preview | complete |
| Historical review with no fabrication | complete |
| Dashboards and reports | complete |
| **Accounting posting** | **deferred — the eight decisions above** |

## Other external requirements, unchanged

| # | Requirement | Status |
|---|---|---|
| 1 | Pushing the branch and tags | no git remote credentials in this environment |
| 2 | Multi-company proof at production scale | `staging.local` has one Company; the guard is implemented and unit-tested against a throwaway company |
| 3 | Outgoing email for statement delivery | no Email Account is configured, so emailing is deliberately not wired rather than silently doing nothing |

## Explicitly *not* blockers

| Item | Why it is ordinary work |
|---|---|
| The 303 submitted historical documents | A commercial judgement with evidence outside the system. The review workflow exists; it will not invent an answer. |
| The 27 customers with no team | Assign one on the customer form; new orders pick it up. |
| Customer-specific and per-category rates | The policy offers them; they raise a blocking exception because no data source exists. Building one is ordinary development, once someone says which. |
