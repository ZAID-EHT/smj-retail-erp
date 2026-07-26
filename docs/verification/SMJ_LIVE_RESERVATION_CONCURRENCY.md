# Live Two-Process Stock Reservation Concurrency

Verified on `staging.local`, 2026-07-26. This is a **genuine two-process** race —
two independent `bench execute` processes with separate database connections, not
two threads and not one transaction.

Harness: `my_store_ui/dev_scripts/live_reservation_concurrency.py`
(`setup` → two `worker` processes → `report` → `teardown`). It refuses to run on
any site other than `staging.local` and removes every fixture afterwards.

## Scenario

| | |
|---|---|
| Item | `SMJ-CONC-TEST-ITEM` (stock item) |
| Warehouse | `SMJ Concurrency Test WH - SMJ` (fresh, no pre-existing stock) |
| Starting Actual | 10 |
| Starting Reserved | 0 |
| Starting Available | 10 |
| Process A | reserve Sales Order for 8 |
| Process B | reserve Sales Order for 8 |
| Timing | both released at a shared wall-clock barrier so they hit the bin lock together |

## Result

| | Process A (PID 16200) | Process B (PID 16201) |
|---|---|---|
| Outcome | reserved | reserved |
| Reserved qty | **2** (Partially Reserved) | **8** (Reserved) |
| Attempts | **2** (retried after a lock conflict) | 1 |
| Raw 500 / deadlock traceback | none | none |

| Ending state | Value |
|---|---|
| Actual | 10 |
| Reserved | **10** |
| Available-to-Sell | 0 |
| `over_reserved` | **false** |
| Sum of reservation entries | 10 (= stock, not 16) |

## What this proves

- **No over-reservation under real concurrency.** Two orders for 8 each against 10
  stock reserved **10 in total, never 16.** The `SELECT … FOR UPDATE` bin lock in
  `reserve_sales_order` serialised the two processes: B won the lock and reserved 8,
  A blocked, hit a lock conflict, **retried within its bounded budget** (attempts=2),
  then the standard ERPNext engine let it reserve only the remaining 2.
- **Bounded retry, no infinite loop** — A stopped at 2 attempts.
- **Rollback on conflict** — the losing attempt rolled back before retrying; no
  partial or duplicate Sales Order or reservation residue remained.
- **No raw deadlock reached the user** — no HTTP 500, no traceback; the retry path
  absorbed the `1213`/`1205` lock conflict.
- **Available-to-Sell never went negative.**

## Friendly-message path

When a lock conflict **persists** past the retry budget, the user gets a structured
friendly `ValidationError` ("This stock is being reserved by another order right
now. Please try again in a moment.") rather than a raw deadlock. That path is proven
deterministically — without depending on a flaky live race — by
`test_reservation_retry` (3 tests): persistent conflict → friendly message after
exactly `RESERVE_MAX_ATTEMPTS`; transient conflict → retried then succeeds.

A reserve against **zero** available creates a zero-quantity partial reservation
(standard ERPNext behaviour) rather than throwing; that is still not
over-reservation — the total stays capped at Actual.

## Automated regression

`test_reservation_concurrency` (2 tests) proves the same invariant deterministically
inside the suite (a subprocess race is too flaky to gate CI on): against 10 stock,
two Sales Orders for 8 each reserve **10 total, not 16**; the second is capped; and
Available-to-Sell = Actual − Reserved and never goes negative. It skips cleanly if
stock reservation is disabled on the site.

## Database integrity and cleanup

Ending Reserved (10) ≤ Actual (10); sum of Stock Reservation Entries = 10. All
fixtures (item, stock entry, both Sales Orders, reservation entries, warehouse,
customer) removed by `teardown`, verified.
