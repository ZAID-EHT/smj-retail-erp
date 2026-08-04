# SMJ Commission Payout Preparation

`Retail Commission Payout` — everything up to, and stopping short of, posting.

## Statuses

| Status | Reachable now | Meaning |
|---|---|---|
| `Draft` | yes | prepared, some lines still blocked |
| `Validated` | yes | every line valid, but the policy cannot post |
| `Ready for Posting` | **no** | requires `policy.may_post()`, which is False |
| `Posted` | **no** | refused by the controller outright |
| `Partially Posted` | **no** | refused by the controller outright |
| `Cancelled` | yes | |

`Posted` and `Partially Posted` are refused in `RetailCommissionPayout.validate`, so
the status cannot be forced onto the record by *any* route — API, Desk or script.
`test_a_posted_status_cannot_be_forced_onto_the_record` asserts it.

## Grouping

One line per member, per company, per currency, per period. Preparing twice reuses
the same record rather than creating a second.

Each line shows gross · reversals · withholding · adjustments · carry-forward in ·
net payable · carry-forward out · validation status · validation note.

## Validation

Per line: payee party type resolved · party resolved · expense account · payable
account · cost centre · non-negative net. Anything missing makes the line `Blocked`
and states why in plain words.

Payee resolution follows the policy's party type: `Employee` uses
`Sales Person.employee`; `Supplier` matches on supplier name; anything else is
reported as unapproved rather than guessed.

## Minimum payout and carry-forward

A net below the policy minimum becomes `0.00` payable with the balance in
`carry_forward_out` — carried into the next period's statement, never lost.

## The accounting preview

A dry run stored on the record as JSON and rendered in the Payout tab:

```json
{
  "proposed_document_type": null,
  "total": 6000.0,
  "entry_count": 3,
  "entries": [
    {"party_type": null, "party": null,
     "debit_account": null, "credit_account": null,
     "amount": 2000.0, "cost_center": null,
     "reference_doctype": "Retail Commission Period",
     "reference_name": "COM-PER-2026-000001",
     "remark": "Commission for …"}
  ],
  "would_post": false,
  "blocked_because": ["Policy configuration is incomplete: …", "Commission posting is disabled …"]
}
```

The nulls are the point: they are exactly the decisions nobody has made.

## Posting

`post_commission_payout(name, confirmation)` exists, is reachable, requires an
Accounts role — and **always refuses**, listing what is missing:

> Commission posting is not enabled. Policy configuration is incomplete: Commission
> Expense Account, Commission Payable Account, Payee Party Type, Cost Center,
> Accounting Document, Accountant Approval Reference. An accountant must first
> approve the expense account, the payable account or payment method, the payee
> party type, whether commission is earned on invoicing or on collection, the payout
> cycle, withholding, tax treatment, and the cancellation and clawback rules.

Kept reachable deliberately. A missing endpoint invites someone to write a quick one
against the ledger; an endpoint that refuses and explains does not.

## What must be true before submission is ever enabled

Policy approved and active · every required account configured · payee mapping
complete for every line · period approved · exact confirmation supplied · a current
backup · an authorised Accounts role · no duplicate payout for the period · the
accountant's approval reference recorded.

`test_no_gl_entry_is_ever_created` asserts the GL Entry count is unchanged across
preparation and validation.
