# SMJ Commission Register

`/retail-erp/sales/commissions` — who earned what, on which invoice, and why.

Backed by `my_store_ui/commission.py`. Covered by
`my_store_ui/tests/test_commission.py` (19 tests).

## What a row is

**One team member, on one submitted Sales Invoice.** A three-person team on one
invoice produces three rows. A credit note produces its own rows, negative.

The Sales Invoice is the earning event because it is where the amount becomes
final. Sales Orders carry an estimate, shown on the order itself and on the
customer's history, but they do not appear in the register.

## Columns

| Column | Source |
|---|---|
| Date | `posting_date` |
| Transaction ID | `custom_wholesale_transaction_id`, when present |
| Sales Order | first order behind the invoice's items |
| Sales Invoice | `name` |
| Customer | `customer_name` |
| Team | frozen `custom_sales_team_name` |
| Team Source | `Customer Default` or `Overridden` (with the reason on hover) |
| Team Member | snapshot `sales_person_name` — the name **as it was** |
| Role | snapshot `team_role` |
| Allocation % | snapshot `allocation_percentage` |
| Commission Base | `amount_eligible_for_commission` |
| Commission Rate | frozen `custom_team_commission_rate` |
| Commission Pool | `total_commission` |
| Gross Commission | the member's amount on a normal invoice |
| Return Reversal | the member's amount on a credit note (negative) |
| Net Commission | gross + reversal |
| Payment Status | `Paid` / `Part Paid` / `Unpaid` / `Credit Note` |
| Commission Status | `Earned` / `Reversed` |

Every team figure is read from the frozen snapshot, never from the current master.
Editing a team today cannot change what this report said yesterday.

## Filters

Date range, company, team, team member, customer, Sales Order, Sales Invoice,
payment status and commission status. A cleared filter is sent as an empty string
and means "all" — it never becomes a missing argument.

## Permissions

| Who | What they see |
|---|---|
| System Manager, Sales Manager, Accounts Manager | Every line |
| Anyone else with Sales Invoice read | Only lines for the Sales Person linked to their own Employee record |
| A user with no linked Sales Person | An empty register — not other people's earnings |
| A user without Sales Invoice read | Refused outright |

**Sales User alone is refused.** In ERPNext v15 the Sales User role has no Sales
Invoice read, and the register reports invoice data, so it requires the same
permission the underlying data does. An ordinary counter user needs Accounts User
as well to see even their own line. This is deliberate: the alternative is reading
invoice figures out to someone who cannot open the invoice.

The user → Sales Person link is `User → Employee.user_id → Sales Person.employee`.

## Export

`export_commissions` returns the same rows as CSV, under the same filters and the
same scoping, and additionally requires Sales Invoice **export** permission. A user
restricted to their own lines exports only their own lines.

## Totals

Gross, reversal and net are summed across the visible rows and always reconcile
with them — asserted by `test_totals_reconcile_with_the_rows`. Because a full
return is an exact negative, an invoice that has been fully credited nets to zero.

## Limits

The register reads at most 500 invoices per request and says so when it truncates,
rather than silently showing a partial answer. Narrow the date range to see more.

## Related views

| View | Where |
|---|---|
| Frozen team on one document | Sales Order / Delivery Note / Sales Invoice detail |
| A customer's orders and their teams | Customer detail |
| A team's totals over a period | Sales Team form, Performance panel |
