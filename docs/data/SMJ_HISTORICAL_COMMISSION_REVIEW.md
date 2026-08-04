# SMJ Historical Commission Review

`/retail-erp/sales/commissions/historical-review`

Documents raised before the sales team feature existed. They carry no team, so they
carry no commission — and none is invented for them.

## The count, measured not assumed

The previous mission reported ~333 rows. **Measured now: 331** in
`sites/staging.local/private/files/sales_team_manual_review.csv`. The figure is read
from the file on every run; it is never carried forward.

The review screen queries live: submitted Sales Orders and Sales Invoices with no
`custom_sales_team`.

## The rule that shapes the whole screen

> **A customer's current team is not evidence of the team a historical document was
> raised with.**

The customer's present team is shown for context, in its own column, labelled
"not evidence". It is never offered as a suggestion and can never be applied
automatically. `record_historical_commission_decision` **refuses** an `Assigned`
status unless the document itself carries sales-person rows.

## What counts as evidence

Only `Sales Team` child rows already on the document — the standard ERPNext
sales-person allocation, recorded at the time by whoever raised it. A team is
suggested only when one team's active membership matches those people **exactly**.

## Statuses

`Unreviewed` · `Evidence Found` · `Assigned` · `No Reliable Evidence` · `Excluded` ·
`Escalated`.

Every decision needs a reason. Assigning additionally needs the team and is refused
without evidence.

## Where decisions are stored

As Frappe `Comment` records against the source document, tagged
`[commission-review]` with a JSON payload. Frappe's Comment trail is the existing
audit record, so:

- the submitted document is **never edited** — no total, status or accounting value
  changes (`test_excluding_records_the_decision_without_editing_the_document`)
- the decision, its author and its timestamp are permanent
- no parallel audit model is invented

## Composition on staging

| Kind | Rows | Reason |
|---|---|---|
| Document | 303 | submitted before the feature; no historical team evidence |
| Customer | 27 | no sales team assigned |
| Team | 1 | commission rate is 0; amounts pending configuration |
| **Total** | **331** | |

## The recommendation

Accept that commission reporting begins from the feature's start date. The
alternative — assigning teams to 303 submitted documents from the customers'
*present* assignments — would fabricate commission history that looks authoritative
and is not.

Where a genuine record exists outside the system, a reviewer can work through the
list with that evidence in hand. The workflow supports it; the system will not do it
for them.
