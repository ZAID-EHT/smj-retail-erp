# SMJ Complete Wholesale Sales Flow

Customer → Products → Sales Order → Reserve → Pay / Approve Credit → Delivery Note
→ Final Sales Invoice → Allocate Payment → Collect Balance → Complete.

ERPNext remains the stock and accounting source of truth. No GL Entry, Stock Ledger
Entry, Payment Ledger Entry or Bin row is ever written directly.

## 1. Customer first

Smart Sales requires the customer before any product can be added. Selecting the
customer loads their **Price Category** (`Customer.default_price_list`) and credit
position (`wholesale/credit.py::get_customer_credit_status`).

## 2. Pricing

`api.py::get_cart_pricing` prices every line through ERPNext's own
`get_item_details`, against the customer's Price Category. `create_draft_sales_order`
resolves the same price list, so the order is raised at the rate the cart quoted.

## 3. Units and Cartons

A line is entered in the stock unit or in **Cartons**. Carton is a real
`UOM Conversion Detail` row on the Item, maintained from the Product form's Carton
Qty (`wholesale/uom.py`). The factor is always resolved from the Item — an
undeclared UOM is refused, never silently treated as 1.

## 4. Availability

Available-to-Sell = Actual − Reserved, read from `Bin`. Quantities are converted to
stock units before any availability decision, and the cap is returned in the UOM the
user is entering. The server rechecks on order creation; browser figures are never
trusted.

## 5. Reservation

`wholesale/reservation.py` reserves against the submitted order. Reservation does
**not** reduce physical stock — it reduces Available-to-Sell only.

## 6. Payment and credit gate

`wholesale/credit.py::evaluate_sales_order_delivery_gate` decides dispatch:

| Customer | Condition | Outcome |
|---|---|---|
| Type unset | — | Blocked; a manager must classify |
| Non-Credit | Paid ≥ order total | Allowed |
| Non-Credit | Shortfall | Blocked; manager override with reason |
| Credit | Within limit, not overdue | Allowed |
| Credit | Overdue | Blocked; manager override with reason |
| Credit | Would exceed limit | Blocked; manager override with reason |

`sales_order_paid_amount()` counts submitted Payment Entry allocations to the order
and to invoices raised from it.

ERPNext independently refuses to **submit** a Sales Order beyond the credit limit,
and refuses to lower a credit limit below current outstanding. The gate above is the
second layer, covering what happens between submission and dispatch.

Overrides require a manager role and a reason, and are audited as a Comment on the
Delivery Note.

## 7. Delivery and FIFO

`wholesale/delivery.py::prepare_delivery` reports remaining quantity, availability,
the gate and a FIFO batch recommendation. Batch selection uses ERPNext's
`get_auto_batch_nos` (batch creation order = FIFO, already excluding stock reserved
elsewhere). A single covering batch is set on the line; a multi-batch line defers to
the standard Serial and Batch Bundle.

`create_delivery_note` builds the note from the standard `make_delivery_note`
mapping. Submission reduces physical stock through the standard Stock Ledger.

Refused: over-delivery, delivering a completed order, delivering a draft order,
insufficient batch stock, and dispatch while the gate blocks without an override.

## 8. Final Sales Invoice

`wholesale/invoicing.py::create_sales_invoice` maps from the Delivery Note
(delivery-first) or the Sales Order. Advances are attached via ERPNext's
`set_advances()` and capped at the invoice total. Re-invoicing a fully billed
delivery is refused.

## 9. Payment allocation

`wholesale/payments.py` records standard Payment Entries with explicit or
oldest-first automatic allocation, validated against real outstanding amounts.
Allocation is limited to Sales Order and Sales Invoice, and the document must belong
to the paying customer.

## 10. Idempotency

Every create endpoint accepts a `request_id`, stored on the document in
`custom_request_id` and resolved from the **database**. A retried request returns the
original document. The cache is only a fast path — it is never the source of truth,
because a lost cache key would otherwise dispatch the same goods twice.

## Related

- `docs/workflows/SMJ_PAYMENT_AND_CREDIT_FLOW.md`
- `docs/workflows/SMJ_DELIVERY_AND_FIFO_FLOW.md`
- `docs/workflows/SMJ_RETURNS_AND_CREDIT_NOTES.md`
- `docs/workflows/SMJ_COMPLETE_PURCHASE_FLOW.md`
- `docs/verification/SMJ_WHOLESALE_END_TO_END_ACCEPTANCE.md`
