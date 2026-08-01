# SMJ Complete Purchase Flow

Supplier → Purchase Order → Purchase Receipt → Purchase Invoice → Supplier Payment
→ Complete. Supplier returns run Purchase Receipt → Return Purchase Receipt →
Debit Note.

Module: `my_store_ui/wholesale/purchasing.py`, returns in `wholesale/returns.py`,
overheads in `wholesale/landed_cost.py`.

## Purchase Order

`create_purchase_order(supplier, items, company, warehouse, schedule_date, submit)`

- Items are `{item_code, qty, rate, uom}`. Quantities convert through the Item's own
  UOM table exactly as on the selling side, so buying 5 Cartons of 12 books 60 stock
  units. An undeclared UOM is refused.
- Validates supplier, company, warehouse (company-scoped) and that each item is a
  purchase item; duplicates and non-positive quantities are refused.
- Draft, submit, cancel, amend, close and reopen are standard ERPNext actions.

## Purchase Receipt

`create_purchase_receipt(purchase_order, lines, submit)` maps through the standard
`make_purchase_receipt`, so batches are created and valuation is standard.

- `lines` is `[{idx, qty}]` for a partial receipt; omit for everything outstanding.
- A Purchase Receipt line must satisfy **received = accepted + rejected**, so `qty`
  and `received_qty` are always moved together.
- Refused: over-receipt, receiving a completed order, receiving a draft order.

`get_purchase_position(purchase_order)` reports ordered / received / pending and
billed per line.

## Purchase Invoice

`create_purchase_invoice(purchase_receipt | purchase_order, submit)` maps from the
receipt (preferred) or the order. A supplier bill number is generated when the
caller does not supply one. Double-billing a receipt is refused.

## Supplier Payment

`create_supplier_payment(...)` records a standard Payment Entry of type Pay.
Allocations are limited to Purchase Order and Purchase Invoice, must belong to the
supplier being paid, and cannot exceed the payment. A bank payment requires a
reference number.

## Landed Cost

`create_landed_cost_voucher(purchase_receipts, charges, distribute_on)` applies
freight, customs, clearing, insurance and handling through the standard **Landed
Cost Voucher**, which distributes the charges across the receipt lines and re-posts
valuation itself. Valuation rates are never edited directly. Distribution supports
the standard Qty / Amount / Distribute Manually methods.

`get_landed_costs(purchase_receipt)` lists what has already been applied.

## Supplier returns

`create_purchase_return(purchase_receipt, lines, reason)` produces the return
receipt through `make_purchase_return`; stock leaves through the standard ledger.
A return may not carry a rejected quantity, and cannot exceed what was received and
not yet returned.

`create_debit_note(purchase_invoice)` raises the return invoice, reducing the
payable.

## Verified

`test_purchase_flow` (18), `test_landed_cost` (8), and acceptance scenarios 8, 9 and
12 in `test_wholesale_acceptance`.
