# SMJ Returns and Credit Notes

Module: `my_store_ui/wholesale/returns.py`.

Sales: Delivery Note → Return Delivery Note → Credit Note → refund or account credit.
Purchases: Purchase Receipt → Return Purchase Receipt → Debit Note.

Every return document is produced by ERPNext's own return mapping
(`make_sales_return`, `make_purchase_return`, `make_return_doc`), which creates the
negative-quantity document against the original. Stock returns through the standard
Stock Ledger and the receivable/payable is adjusted by the standard accounting
controller. **No ledger entry is reversed by hand.**

## Return position

`get_return_position(delivery_note)` reports per line: delivered quantity, quantity
already returned (summed from submitted returns via `return_against`), and the
remaining returnable quantity. `fully_returned` closes the delivery to further
returns.

A draft delivery, and a return document itself, cannot be returned.

## Sales return

`create_sales_return(delivery_note, lines, reason, condition, warehouse, submit,
request_id)`

- `lines` = `[{idx, qty}]` for a partial return; omit to return everything
  returnable. Quantities are positive on input and written as negative on the
  document.
- **Reason is mandatory** and must be one of: Damaged, Wrong Item, Excess Delivery,
  Quality Issue, Customer Cancelled, Expired, Other. `condition` is free text
  describing the state of the goods.
- Reason and condition are written to the document's narrative field. That field is
  resolved from the doctype meta — Delivery Note has `instructions` and **no**
  `remarks` in ERPNext v15, while Purchase Receipt has both.
- An optional receiving `warehouse` must belong to the delivery's company.
- Returning more than was delivered, more than the un-returned remainder, or against
  a fully returned delivery is refused.

## Credit note

`create_credit_note(sales_invoice, submit, request_id)` raises the return Sales
Invoice against the original, reducing the receivable.

The mapping copies the original invoice's advance allocations, which are invalid on
a return; they are cleared so ERPNext resolves them afresh.

Crediting a credit note, or crediting a draft invoice, is refused.

## Supplier returns

`create_purchase_return(purchase_receipt, lines, reason, submit, request_id)` with
the same quantity protection. A Purchase Receipt line must satisfy
received = accepted + rejected, and a return may not carry a rejected quantity, so
the return sets `rejected_qty = 0` and `received_qty = qty`.

`create_debit_note(purchase_invoice, submit, request_id)` raises the return invoice,
reducing the payable.

## Refunds

A refund is a standard Payment Entry against the credit note, recorded through
`wholesale/payments.py`. Where the customer keeps the value on account, the credit
note simply reduces their outstanding.

## Proven

`test_sales_returns` (16) and `test_purchase_flow` (18) — stock restored on a full
return, a partial return leaving exactly the remainder returnable, quantity
protection, and negative-total credit and debit notes. Acceptance scenarios 7 and 9.
