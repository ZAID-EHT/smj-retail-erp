# SMJ Commission Calculation

## The rule in one line

> **Commission pool = eligible sale × team rate. The member's allocation percentage
> divides the pool, never the sale.**

## The five quantities

| # | Quantity | Formula | Where it lives |
|---|---|---|---|
| 1 | Commission base | Σ item `base_net_amount` where `grant_commission` | `amount_eligible_for_commission` (ERPNext) |
| 2 | Team commission rate | set on the team, frozen onto the document | `Retail Sales Team.commission_rate` → `commission_rate` |
| 3 | Commission pool | base × rate ÷ 100 | `total_commission` (ERPNext) |
| 4 | Member allocation % | set on the team, frozen onto the document | snapshot row `allocation_percentage` |
| 5 | Member commission amount | pool × allocation ÷ 100 | snapshot row `commission_amount` |

A sixth figure exists and is **not** commission:

| Sales contribution | base × allocation ÷ 100 | `Sales Team.allocated_amount` (ERPNext) |
|---|---|---|

It is the share of the *sale* credited to a person for sales reporting. It is a much
larger number than their commission and must never be confused with it.

## The worked example

Verified end to end by
`my_store_ui/dev_scripts/verify_commission_chain.py` and asserted by
`TestCommissionModel.test_the_worked_example_from_the_requirements`.

```
Net eligible sale                       LKR 100,000
Team commission rate                             2%
Commission pool                         LKR   2,000

Sales Manager          50% of pool      LKR   1,000
Representative 1       25% of pool      LKR     500
Representative 2       25% of pool      LKR     500
                      ----                 --------
                      100%              LKR   2,000
```

The manager is **not** paid 50% of LKR 100,000. Their sales *contribution* is
LKR 50,000; their *commission* is LKR 1,000.

## The commission base, precisely

`amount_eligible_for_commission` is ERPNext's own figure:

```python
self.amount_eligible_for_commission = sum(
    item.base_net_amount for item in self.items if item.grant_commission
)
```

- `base_net_amount` is **net of discount and before tax**, in company currency.
- `grant_commission` comes from the Item master and defaults to `1`, so in practice
  every line counts. Clearing it on an Item excludes that Item from commission
  without affecting anything else.

This was chosen because it is the standard ERPNext definition already present in the
system, not invented for this feature. Nothing here changes it.

## Where the team rate comes from

The `Retail Sales Team.commission_rate` field already existed before this mission
and is validated to 0–100. **No default rate is assumed.** A team created with the
rate left at 0 produces a zero pool and zero member amounts — the split is still
recorded, so the allocation is preserved and only the money is pending
configuration. Nothing is silently invented.

## When each figure is worked out

| Stage | What the figure means | Status shown |
|---|---|---|
| Sales Order, draft | Estimate. Follows the order value as lines change. | `Draft` |
| Sales Order, submitted | Estimate, frozen with the order. | `Estimated` |
| Delivery Note | Carries the order's frozen team; no new money event. | — |
| Sales Invoice, submitted | **Earned.** The basis is the invoiced amount. | `Earned` |
| Credit Note | Reverses in proportion; the figures are negative. | `Reversed` |
| Cancelled document | Excluded from the register entirely. | `Cancelled` |

The team and the percentages are frozen the moment the document is first raised.
The *money* follows the document while it is still a draft, because a draft's value
can still change and the estimate has to remain honest. Once submitted, nothing
moves.

## Partial invoicing and multiple deliveries

Because the base is read from each invoice's own eligible amount, a part-invoiced
order produces commission on what was actually invoiced. Two invoices against one
order produce two register lines per member, each on its own base, and they add up
to the whole. No apportioning logic is needed and none is written.

## Returns and credit notes

A credit note is a Sales Invoice with `is_return` set. ERPNext gives it negative
item amounts, so:

- `amount_eligible_for_commission` is negative
- `total_commission` is negative
- each member's `commission_amount` is negative, in the same proportion

A full return therefore nets a member's commission back to exactly zero, and a
partial return reduces it in proportion — with no special-case arithmetic anywhere.
The reversal keeps the **original** team, inherited from the invoice it reverses, so
reassigning the customer afterwards cannot misdirect the reversal.

A reversal can never exceed the original, because ERPNext already refuses to return
more than was invoiced.

## Rounding

Percentages are balanced to total exactly 100 before anything is written (see
`docs/sales/SMJ_SALES_TEAM_DATA_MAPPING.md` §2), and member amounts are rounded to
the document's own currency precision. Member amounts therefore reconcile to the
pool exactly; `TestCommissionModel.test_member_amounts_reconcile_to_the_pool`
asserts it.

## What this model does *not* do

- It does not post commission to any account, ledger or payroll run. See
  `SMJ_COMMISSION_PAYOUT_BOUNDARY.md`.
- It does not create a separate commission ledger. Every figure is derived from
  standard ERPNext fields plus the snapshot rows.
- It does not recalculate from the Sales Team master. Ever.
