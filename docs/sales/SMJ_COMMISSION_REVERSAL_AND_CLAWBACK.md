# SMJ Commission — Reversals and Clawbacks

## Behaviour by event

| Event | Effect on commission | How |
|---|---|---|
| Invoice submitted | becomes eligible | frozen snapshot + policy basis |
| Partial payment | eligible in proportion, **if** the policy earns on collection | `_paid_fraction()` |
| Full payment | fully eligible under any collection trigger | |
| Payment cancelled | eligibility falls back with the outstanding amount | recomputed on next preparation |
| Invoice cancelled | excluded entirely | the register and period filter `docstatus: 1` |
| Partial credit note | reduces in proportion | ERPNext's negative item amounts flow through |
| Full credit note | nets to exactly zero | same |
| Return **before** a period is prepared | reduces the net directly | the credit note is picked up as a negative row |
| Return **after** preparation, before approval | re-preparing picks it up | period is still unlocked |
| Return **after approval** | **clawback** — never a silent rewrite | see below |
| Return after payout | clawback against the next period | see below |
| Bad debt / write-off | flagged for manual review | no automatic reversal; the decision is commercial |

Measured: a cancelled invoice produced **3 register lines before cancellation and 0
after**, while the snapshot itself survived — the evidence is kept, the money is
excluded.

## Approved periods are never rewritten

Once a period is `Approved` its rows are evidence. A late credit note is handled one
of two ways, both deliberate and both auditable:

1. **Reopen the period** — needs an Accounts Manager and a reason, is refused once
   any of it has been paid, and the decision log keeps the previous approval.
2. **Raise a clawback adjustment** — a `Return Clawback` adjustment against the
   *next* period, which is what `Deduct From Next Period` means.

Which of the two applies is the policy's `returns_rule`:

| `returns_rule` | Behaviour |
|---|---|
| `Reverse Before Payout` | reopen and re-prepare while unpaid |
| `Deduct From Next Period` | clawback adjustment on the following period |
| `Create Payable Adjustment` | adjustment against the current period |
| `Manual Review` | raise an exception and let a human decide |

There is no fifth, silent option.

## A reversal can never exceed the original

ERPNext already refuses to return more than was invoiced, so a credit note cannot
produce a reversal larger than the commission that was earned. Nothing extra is
needed, and nothing extra is written.

## Negative net payable

A member whose clawbacks exceed their earnings shows a negative net. The payout line
is **Blocked** with "The net payable is negative; it needs a clawback decision" —
because whether to withhold from future commission, invoice it back, or write it off
is a commercial decision, not an arithmetic one. The policy's
`maximum_negative_carry_forward` bounds how far it can be carried without higher
authority.
