# SMJ Payment and Credit Flow

Module: `my_store_ui/wholesale/credit.py`, `my_store_ui/wholesale/payments.py`.

## Customer classification

`Customer.custom_credit_type` is either **Credit Customer** or **Non-Credit
Customer**. Non-Credit customers have credit limit and credit days forced to zero.
Credit limit lives in the standard `credit_limits` child table (per company);
credit days in `custom_credit_days`.

## Credit snapshot

`get_customer_credit_status(customer, company)` returns credit limit, current
outstanding, available credit, overdue amount and the overdue flag. Official
balances come from ERPNext (`get_credit_limit`, `get_customer_outstanding`) — Vue
never computes a receivable.

## Delivery gate

`decide_delivery_gate(...)` is a pure decision (no DB access) and
`evaluate_sales_order_delivery_gate(sales_order)` applies it with the order's real
payment position.

| Customer | Condition | allowed | requires_manager_approval |
|---|---|---|---|
| Type unset | — | no | yes |
| Non-Credit | paid ≥ total | **yes** | no |
| Non-Credit | shortfall | no | yes |
| Credit | overdue | no | yes |
| Credit | projected > limit | no | yes |
| Credit | within limit, not overdue | **yes** | no |

A rounding tolerance of 0.01 treats a near-exact payment as settled.

### Payment recognised against an order

`sales_order_paid_amount(sales_order)` sums submitted Payment Entry Reference
allocations to the Sales Order itself **plus** allocations to Sales Invoices raised
from it, so both an advance and a post-invoice receipt count.

### Manager override

Requires one of `Sales Manager`, `Accounts Manager`, `Credit Manager` (or
`System Manager`) **and** a non-empty reason. The override is written to the
standard comment trail on the Delivery Note with the user, the gate reason, the
order and the unpaid amount.

## Two layers of credit defence

ERPNext refuses to **submit** a Sales Order that exceeds the credit limit, and
refuses to lower a credit limit below current outstanding. The delivery gate is the
second layer, covering the window between submission and dispatch (for example a
customer who falls into arrears after the order was accepted).

## Receipts and allocation

`create_customer_payment(customer, amount, ...)` records a standard Payment Entry.

- Explicit `allocations` are validated against the real outstanding amount, must
  belong to the paying customer, and are limited to Sales Order and Sales Invoice.
- With no allocations, the receipt is applied oldest-first to outstanding invoices,
  then held as an advance against unbilled orders.
- A bank payment requires a reference number (caught up front, not deep in the
  controller).
- Supported modes: Cash, Bank Transfer, Card, Cheque and any configured Mode of
  Payment; the receiving account follows the Mode of Payment default.

`get_outstanding_documents(customer, company)` lists unpaid invoices (oldest due
first) and unbilled orders with a pending amount.

Outstanding values are never written or patched directly.

## Verified

`test_wholesale_credit` (7), `test_delivery_fifo` gate cases,
`test_invoice_payment_flow` (17), acceptance scenarios 1–4.
