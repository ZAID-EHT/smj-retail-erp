# SMJ Delivery and FIFO Flow

Module: `my_store_ui/wholesale/delivery.py`.

## Preparation

`prepare_delivery(sales_order)` returns, for a submitted order:

- per line: ordered, delivered, remaining (and remaining in stock units), Actual /
  Reserved / Available-to-Sell, the FIFO batch recommendation and any shortfall
- the payment/credit gate decision
- transport method and detail defaults from the customer, shipping address and
  contact
- `fully_delivered` when nothing is outstanding

A draft Sales Order cannot be prepared for delivery.

## FIFO batch allocation

`fifo_batches(item_code, warehouse, qty, company)` delegates to ERPNext's
`get_auto_batch_nos` with `based_on="FIFO"`. That allocator:

- orders available batches by **batch creation** (FIFO)
- already excludes stock reserved elsewhere (Stock Reservation Entries, POS
  reservations, picked batches)
- splits the requirement across batches when one does not cover it

`get_fifo_allocation(item_code, warehouse, qty, uom)` exposes the recommendation to
the UI, converting the entered quantity through the Item's UOM first, and reports
`allocated_qty`, `shortfall` and `fully_allocated`.

An item that is not batch-managed returns no batches; the line simply carries no
batch.

## Creating the delivery

`create_delivery_note(sales_order, lines, transport_method, transport_detail,
override_reason, submit, request_id)`

1. Permission check on Delivery Note create and Sales Order read.
2. Idempotency: an existing document for this `request_id` is returned unchanged.
3. The order must be submitted and not already fully delivered.
4. The payment/credit gate must pass, or a manager must override with a reason
   (audited as a Comment).
5. The note is built by the standard `make_delivery_note` mapping and trimmed to the
   requested quantities (`lines` = `[{idx, qty}]` in the order line's UOM; omit for
   everything outstanding).
6. Batch-managed lines get their FIFO batch. A single covering batch is set as
   `batch_no`; a multi-batch line is left to the standard Serial and Batch Bundle
   rather than being forced onto one batch.
7. Transport fields are validated against the Delivery Note meta before being set —
   Frappe silently discards unknown attributes, so an unapplied fixture is reported
   instead of losing the data.

On submit, ERPNext reduces physical stock through the Stock Ledger, releases or
converts the reservation, and updates the order's delivery status.

## Refusals

| Attempt | Result |
|---|---|
| Deliver more than outstanding | Refused with the line number and the remainder |
| Deliver a fully delivered order | Refused |
| Deliver a draft order | Refused |
| Batch stock insufficient | Refused with allocated vs required |
| Gate blocked, no override reason | Refused |
| Override reason without a manager role | PermissionError |
| Retried `request_id` | Original document returned, nothing duplicated |

## Proven

`test_delivery_fifo` (22): FIFO spanning two batches oldest-first (10 then 2),
partial then completing delivery, stock reduced exactly once, over-delivery refused,
transport recorded, and idempotency holding after the cache key is deleted.
Acceptance scenarios 5, 6 and 12 exercise the same paths end to end.
