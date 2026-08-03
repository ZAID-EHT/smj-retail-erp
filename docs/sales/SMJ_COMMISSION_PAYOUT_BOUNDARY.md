# SMJ Commission Payout Boundary

## Status: **deferred, pending accountant approval**

Commission is calculated, frozen, reported and exportable. It is **not** paid out
by this system, and no accounting entry of any kind is created for it.

## Why it stops here

Paying commission means creating a real financial posting against a real person.
Doing that requires decisions this system has no authority to make:

| Decision | Why it cannot be assumed |
|---|---|
| Which expense account commission is charged to | Picking one silently misstates the P&L. |
| Whether the payee is an Employee or a Supplier party | Changes the tax treatment and the ledger entirely. |
| Whether commission is earned on invoicing or on collection | Changes *when* the liability exists, and by how much when a customer never pays. |
| The payout cycle and cut-off | Determines which invoices fall into which run. |
| Withholding and statutory deductions | Legally binding, and jurisdiction-specific. |

None of these exist in writing. Guessing any one of them would produce accounting
entries that look authoritative and are wrong — which is worse than producing none.

The mission's own safety rules forbid it directly: no direct GL Entry writes, no
separate commission ledger, and no automatic Payment Entry to an employee without
confirmed accounting rules.

## What *is* implemented

| Capability | State |
|---|---|
| Commission base, rate, pool | Implemented, from standard ERPNext fields |
| Per-member allocation and amount | Implemented, from the immutable snapshot |
| Return and credit-note reversal | Implemented, proportional |
| Commission register with filters | Implemented, `/retail-erp/sales/commissions` |
| Permission scoping (own lines vs all) | Implemented |
| CSV export | Implemented, permission-gated on Sales Invoice export |
| Payout posting | **Not implemented. Deferred.** |

## The statuses the register uses

Deliberately limited to what the system can honestly assert:

| Status | Meaning |
|---|---|
| `Draft` | On an unsubmitted document. An estimate that can still move. |
| `Estimated` | On a submitted Sales Order. Not yet earned. |
| `Earned` | On a submitted Sales Invoice. The basis is final. |
| `Reversed` | On a credit note. Negative, proportional. |
| `Cancelled` | The document was cancelled; excluded from the register. |

**There is deliberately no `Paid` status.** Marking a line `Paid` would assert that
money left the business, which nothing in this system can verify. A `Paid` status
will only be added alongside a real, approved payout process.

## The intended path when payout is approved

Recorded so the design is not re-derived later. Not built.

```
Calculated  ->  Reviewed  ->  Approved  ->  Paid
 (automatic)  (Sales Mgr)  (Accounts Mgr)  (Accounts User,
                                            against a real posting)
```

| Step | Role | What it would need |
|---|---|---|
| Reviewed | Sales Manager | A per-line review flag, plus a period lock |
| Approved | Accounts Manager | The approved expense account and party type |
| Paid | Accounts User | A reference to a genuine Payment Entry or payroll run |

Until an accountant has signed off the account, party type and earning trigger, the
export is the handover: finance takes the CSV into whatever payroll or payables
process already exists.

## External requirement to close this out

> **Accountant approval is required** for: the commission expense account, the
> payee party type, whether commission is earned on invoicing or on collection, the
> payout cycle, and withholding treatment.

Recorded in `docs/execution/SMJ_SALES_TEAM_INTEGRATION_BLOCKERS.md` as external
requirement #1.
