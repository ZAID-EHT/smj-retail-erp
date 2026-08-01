# SMJ Wholesale Transaction Register

Route `/retail-erp/sales/transactions`. Backend `my_store_ui/wholesale/register.py`,
page `frontend/src/pages/priority/WholesaleTransactionsPage.vue`.

One row per wholesale transaction, anchored on the Sales Order and assembled from
standard ERPNext links only (`Delivery Note Item.against_sales_order`,
`Sales Invoice Item.sales_order`, `Payment Entry Reference`, `Delivery Note.
return_against`). There is no shadow ledger.

## Transaction ID

`custom_wholesale_transaction_id` — `TRX-YYYY-######`, generated with Frappe's
atomic naming counter so parallel submits never collide. Stamped on the Sales Order
(`validate` hook) and propagated to the Delivery Note, Sales Invoice and Payment
Entry from their source links. Where the field is absent the Sales Order name is the
interim anchor, so the register works before fixtures are applied.

Proven end to end by acceptance scenario 1b.

## Row contents

Transaction ID, Sales Order, customer and customer name, customer type
(Credit / Non-Credit), transaction date, linked Delivery Notes, Sales Invoices,
Payment Entries and return Delivery Notes, plus:

| Status | Values |
|---|---|
| Delivery | Not / Partially / Fully Delivered |
| Invoice | Not / Partially / Fully Invoiced |
| Payment | Unpaid / Partially Paid / Paid |
| Return | No Return / Partially Returned / Fully Returned |
| Reservation | Not / Partially / Fully Reserved |

Financial columns (ordered total, paid, outstanding) are included **only** for users
with a finance role (`Accounts User`, `Accounts Manager`, `Sales Manager` or
`System Manager`). Everyone else receives the row without those keys — the figures
are withheld server-side, not hidden in the browser.

## Filters

`customer`, `status`, `company`, `warehouse`, `from_date`/`to_date`, `credit_type`,
`delivery_status`, `payment_status`, `invoice_status`, `return_status`,
`overdue_only`.

The filter set is an allowlist — any unsupported key is rejected. Sorting is
restricted to a fixed field list and direction. Page size is capped at 100.

Stored fields are filtered in SQL; the derived statuses are computed per row and
filtered after assembly.

## Permissions

Sales Orders are read with `frappe.get_list`, so User Permissions, company and
warehouse restrictions all apply.

The route itself declares `doctype: "Sales Order"`, so the route guard requires
exactly what the API requires. Before this was corrected, the guard admitted users
the API then refused with a 403 — note that **System Manager alone does not grant
Sales Order read** in ERPNext.

## Timeline

`get_transaction_timeline(sales_order)` returns the lifecycle: order created,
reservation, payments received, delivery, invoice, payment allocation, returns and
credit notes. All links open Retail ERP routes, not Desk.

## Verified

`test_transaction_register` (13) and `test_register_route_permission` (3); the page
is in the six-viewport browser matrix at 27/27 per viewport.
