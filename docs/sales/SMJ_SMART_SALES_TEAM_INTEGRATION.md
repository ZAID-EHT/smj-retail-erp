# SMJ — Sales Team in Smart Sales

## What happens when a customer is chosen

Selecting a customer loads, in parallel, their details, price category, payment
type, credit position and **assigned sales team**, then reprices the cart and
refreshes stock.

The team panel sits directly below Sale Setup and above the catalogue, so it never
overlaps either.

```
Sales Team: Colombo Wholesale Team          Code STM-00012
Customer default

Sales Manager
  Mohamed                              50%

Representatives
  Amal                                 25%
  Nimal                                25%

Team Commission Rate 2%      Total Allocation 100%
```

The manager is separated from the representatives, and the team code is shown
alongside the name.

## Stale-request protection

Every load records the customer it was started for and discards its own result if
the selection has moved on:

```js
const forCustomer = customer.value;
const result = await getCustomerSalesAssignment(forCustomer);
if (customer.value !== forCustomer) return;   // a newer selection already won
```

So customer A's team can never be shown against customer B, however slowly the
network answers. The same guard is used on the commission register and both detail
panels.

Changing the customer replaces the team. Clearing the customer clears it. Editing
the picker text without choosing anything leaves the previous customer's team
untouched until a new one is actually selected.

## States

| State | Shown |
|---|---|
| No customer yet | "Select a customer to load the assigned sales team." |
| Loading | "Loading sales team…" with `role="status"` |
| Customer has no team | The empty message, plus a warning that the order will carry no commission split |
| Assigned team went inactive | A warning to choose another team before raising a new order |
| Error | The server's message, never a traceback |

## Overriding the team for one order

Available to a Sales Manager (`can_override` on the assignment response). The
button is hidden for everyone else — and hiding it is *not* the control; the
document hook re-authorises the override on save, so posting straight at the REST
API is refused identically.

1. "Use another team" opens a small dialog.
2. It lists only active teams valid for the order's company.
3. A **reason is required**. Applying without one is refused in the browser and
   again on the server.
4. The card then shows "Overridden for this order" with the reason.
5. Cancelling restores the customer's own team without another round trip.

**The customer master is never changed by an override.** Changing a customer's own
team is a separate, deliberate action on the customer form, which needs Customer
write permission.

The order records all of it: the team used, the customer's default at the time, the
source, the reason, and who froze it when.

## Editing percentages in Smart Sales

Not supported, deliberately. The requirement gates it behind "a separate approved
permission", and no such permission exists. See Scenario 4 in
`docs/verification/SMJ_SALES_TEAM_END_TO_END_ACCEPTANCE.md`.

To sell with a different split, use a team that has that split — which is what the
override is for.

## Mobile

The panel and the override dialog are part of the six-viewport matrix, down to
360 × 800. The member list reflows to a single column and nothing overflows
horizontally.

## What the cart sends

```json
{
  "request_id": "…",
  "customer": "CUST-0001",
  "warehouse": "…",
  "items": [{ "item_code": "…", "qty": 10 }],
  "sales_team": "STM-00013",
  "sales_team_override_reason": "Covering the northern route this week"
}
```

`sales_team` is sent only when a team other than the customer's own was chosen.
The server re-authorises it either way, so the two fields are an expression of
intent, never a grant of permission.
