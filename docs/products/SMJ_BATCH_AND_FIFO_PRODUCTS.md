# SMJ Batch & FIFO Products

New stock products created via the quick form are batch-managed (has_batch_no=1,
create_new_batch=1, series BAT-.YYYY.-.######). Batches are created/selected by
standard ERPNext stock transactions — no separate batch ledger.

## FIFO valuation (proven — test_batch_fifo)
Receive Batch A (10@1000) + Batch B (10@1200) via standard Stock Entries, issue 12,
read the standard Stock Ledger:
- Outgoing = 10×1000 + 2×1200 = **12,400**
- Remaining = 8 @ 1200 = **9,600**
No Stock Ledger Entry is written directly. Available-to-Sell = Actual − Reserved is
unchanged; batch tracking does not break reservation.

Enabling batch tracking on **existing stocked** products is a deliberate manual
migration (docs/data/SMJ_EXISTING_PRODUCT_CUSTOMER_MIGRATION.md).
