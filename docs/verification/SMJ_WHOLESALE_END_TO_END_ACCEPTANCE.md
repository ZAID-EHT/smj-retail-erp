# SMJ Wholesale End-to-End Acceptance

Suite: `my_store_ui/tests/test_wholesale_acceptance.py` — **14 scenarios, all green**
on `staging.local`. Each runs the real business sequence through the real endpoints
inside a savepoint, and rolls back, so nothing is left behind.

| # | Scenario | What it proves |
|---|---|---|
| 1 | Non-Credit full sale | Order → pay in full → deliver → invoice; order 100% delivered and billed, invoice outstanding 0, stock down exactly 10 of 50 |
| 1b | Transaction ID propagation | `TRX-YYYY-######` stamped on the Sales Order appears unchanged on the Delivery Note and Sales Invoice |
| 2 | Non-Credit partial payment | Gate blocks, delivery refused, **stock untouched** (50 still on hand) |
| 3 | Credit sale within limit | Delivers without prepayment, invoice leaves a receivable, later payment clears it |
| 4a | Over-limit order | ERPNext refuses to submit the order at all (first line of defence) |
| 4b | Overdue customer | Gate blocks delivery, manager override with a reason succeeds and is audited as a Comment |
| 5 | Partial then final delivery | 4 then 6 of 10; order stays open at 46 in stock, completes at 40 |
| 6 | Multi-batch FIFO | 10@1000 + 10@1200, issue 12 → 10 from the older batch, 2 from the newer; delivery leaves 8 |
| 7 | Sales return + credit note | 3 of 10 returned → stock back to 43; credit note carries a negative total |
| 8 | Purchase to supplier payment | PO 20 → receipt 8 (stock 8) → receipt 12 (stock 20) → invoice → payment clears the payable |
| 9 | Purchase return + debit note | 5 returned → stock 15; debit note negative |
| 10 | Insufficient shared stock | A second order for more than Available-to-Sell is refused |
| 11 | Cross-party documents | Paying customer B against customer A's order is refused |
| 12 | Carton workflow | Buy 5 cartons → 60 stock units; sell 2 cartons → 24 units out, 36 remain |

## Notes on scenarios 4a/4b

ERPNext defends credit in two layers, and the scenarios were corrected to match
reality rather than forcing the code to fit an assumption:

1. It refuses to **submit** a Sales Order beyond the customer's credit limit, and
   refuses to lower a credit limit below current outstanding.
2. The application's delivery gate covers the window between submission and
   dispatch — the overdue branch is what exercises the manager override.

## Scenario 10 scope

The guard proven here is the server-side Available-to-Sell recheck in
`create_draft_sales_order`, which refuses an order beyond available stock. True
parallel-process reservation contention is covered separately by
`test_reservation_concurrency` and `dev_scripts/wholesale_concurrency_test.py`.

## Supporting suites

| Suite | Tests |
|---|---|
| `test_carton_uom` | 11 |
| `test_carton_sales_flow` | 6 |
| `test_delivery_fifo` | 22 |
| `test_invoice_payment_flow` | 17 |
| `test_sales_returns` | 16 |
| `test_purchase_flow` | 18 |
| `test_landed_cost` | 8 |
| `test_transaction_register` | 13 |
| `test_operations_dashboard` | 7 |
| `test_wholesale_acceptance` | 14 |
| **New in this mission** | **132** |
