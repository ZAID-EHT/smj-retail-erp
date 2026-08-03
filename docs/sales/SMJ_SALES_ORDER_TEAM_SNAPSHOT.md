# SMJ — The Sales Order Team Snapshot

## The promise

> A document raised today keeps the team, the split and the rate it was raised
> with, for ever. Nothing that happens to the master afterwards can change it.

## How it is frozen

Two hooks, in this order, on Sales Order, Delivery Note and Sales Invoice:

| Hook | What it does |
|---|---|
| `before_validate` → `freeze_team` | Settles the team, the members, the roles and the percentages. Runs **once**. |
| `validate` → `price_commission` | Splits the pool ERPNext has just worked out between the frozen members. |

### Why `before_validate` and not `validate`

Frappe runs a document's own method **before** the hooks:

```python
def compose(fn, *hooks):
    def runner(self, method, *args, **kwargs):
        add_to_return_value(self, fn(self, *args, **kwargs))   # the document's own validate
        for f in hooks:                                        # then ours
            add_to_return_value(self, f(self, method, *args, **kwargs))
```

A `validate` hook therefore lands **after** ERPNext's `calculate_commission` and
`calculate_contribution` have already run. Setting the rate and the percentages
there would leave the pool stale for a whole save. Setting them in
`before_validate` lets ERPNext derive the eligible amount, the pool and each
person's contribution itself.

Pricing then runs in `validate`, once the pool exists.

## What is written

| Field | Frozen |
|---|---|
| `custom_sales_team` | the team used |
| `custom_sales_team_name` | its name **at the time** |
| `custom_sales_manager` | the manager at the time |
| `custom_team_commission_rate` | the rate at the time |
| `custom_customer_sales_team` | the customer's default at the time |
| `custom_sales_team_source` | `Customer Default` or `Overridden` |
| `custom_sales_team_override_reason` | why they differ |
| `custom_sales_team_captured_on` / `_by` | when, and by whom |
| `custom_sales_team_members` | one row per member: person, name, role, allocation %, commission amount |
| `custom_sales_team_snapshot` | the complete audit copy as JSON, hidden and print-hidden |
| `sales_team` (standard) | the same people and percentages, for standard ERPNext reporting |
| `commission_rate` (standard) | the team rate, so ERPNext computes the pool |

`custom_sales_team_captured_on` is the sentinel: once set, the team never moves
again.

## What is frozen and what still moves

| | Frozen at creation | Follows a draft |
|---|---|---|
| Team, name, code | yes | — |
| Members, roles | yes | — |
| Allocation percentages | yes | — |
| Commission rate | yes | — |
| Source, reason, who and when | yes | — |
| Commission **base** | — | yes |
| Commission **pool** | — | yes |
| Member commission **amounts** | — | yes |

The money follows a draft because a draft's value can still change and the estimate
has to stay honest. Once submitted, nothing moves at all.

## Immutability after submit

`before_update_after_submit` → `guard_snapshot_after_submit` compares the frozen
fields against the stored document and refuses any change with:

> The sales team on a submitted document cannot be changed. Cancel and amend it
> instead.

Frappe's own read-only, non-`allow_on_submit` fields are the first line; this is the
explicit second.

## Inheritance down the chain

```
Sales Order
   ├── Delivery Note   ← items' against_sales_order / sales_order
   └── Sales Invoice   ← items' sales_order, or the delivery note
            └── Credit Note ← return_against
```

`_snapshot_from_source` walks those references and copies the snapshot whole. It
**never** re-reads the customer or the master, so one frozen team runs the entire
chain — including the reversal, which therefore credits the people who were
credited originally.

A document raised standalone, with no source, falls back to the customer's team at
that moment and records that it did.

## Why a dedicated child table

ERPNext's standard `Sales Team` row cannot carry four things this needs:

1. the member's **role** — there is no field for it
2. a reference back to the **team master**
3. the **override source and reason**
4. **frozen identity** — its `commission_rate` is `fetch_from
   sales_person.commission_rate`, so the row re-reads the master and is not frozen
   at all

The standard table is still populated, so nothing standard stops working. The
snapshot table is additive: no replacement sales document, no separate ledger.

## Proven by

`test_order_stores_a_snapshot`,
`test_reassigning_the_customer_does_not_change_the_old_order`,
`test_editing_the_team_master_does_not_change_the_old_order`,
`test_a_submitted_snapshot_cannot_be_edited_in_place`,
`test_delivery_note_inherits_the_orders_snapshot`,
`test_the_invoice_inherits_the_orders_frozen_team_and_earns_on_it`,
`test_a_credit_note_reverses_the_commission_in_proportion`,
`test_a_team_edited_while_an_order_is_being_raised_still_saves_one_consistent_snapshot`,
and in a real browser: *editing the team master leaves the raised order untouched*.
