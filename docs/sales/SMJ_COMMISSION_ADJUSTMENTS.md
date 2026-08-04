# SMJ Commission Adjustments

`Retail Commission Adjustment` — a controlled change to what a member is owed.

## The rule

**No adjustment ever touches an invoice.** It is a separate, auditable record that
the period totals read. `test_an_adjustment_never_touches_the_invoice` asserts the
invoice's `total_commission` and `grand_total` are byte-identical afterwards.

## Types

`Bonus` · `Deduction` · `Correction` · `Carry Forward` · `Return Clawback` ·
`Rounding` · `Approved Special Adjustment`.

A positive amount adds to the member's payable; a negative one deducts.

## Fields

Period · team member · type · amount · reason · supporting reference · requested by ·
requested on · approved by · approved on · status · decision note.

## Segregation of duties

| Action | Who |
|---|---|
| Request | System Manager, Sales Manager, Accounts Manager |
| Approve or reject | System Manager, Accounts Manager |
| Approve **your own** request | nobody except System Manager |

`test_a_requester_cannot_approve_their_own_adjustment` asserts the refusal.

## Guardrails from the policy

| Guardrail | Effect |
|---|---|
| `manual_approval_threshold` | an amount above it needs System Manager |
| `maximum_negative_carry_forward` | a deduction beyond it needs System Manager |

## Validation

- A non-zero amount and a reason are both required.
- The member must already have commission rows in that period — you cannot adjust
  someone the period does not pay.
- Rejecting requires a note.
- A period cannot be approved while any adjustment is still `Requested`.

## Effect on the period

Approving an adjustment re-prepares an **unlocked** period, so the totals follow
immediately. A **locked** (approved or later) period is left alone: history is not
rewritten. Changing an approved period means reopening it deliberately, or raising a
further adjustment against the next one.
