# SMJ Reservation Concurrency Result

## The guarantee (unchanged, standard engine)
`reserve_sales_order` takes a `SELECT … FOR UPDATE` row lock on each affected Bin
(`_lock_bins`) before calling ERPNext's `create_stock_reservation_entries()`. Two
parallel reservations of the same item/warehouse serialise on that lock and the
standard engine validates available qty, so the classic case — 10 available, two
8-unit reservations — can **never** reserve 16. The prior mission (Phase 4/10)
demonstrated this live via `dev_scripts/wholesale_concurrency_test.py`
(two real OS processes) with zero over-reservation and zero corruption.

## The UX fix added this mission
Previously the losing side of a lock race surfaced a raw `QueryDeadlockError` (a
500-class traceback). `reserve_sales_order` now wraps the lock + reservation in a
bounded retry:

- On a lock conflict (MariaDB error **1213** deadlock or **1205** lock-wait
  timeout, classified by `_is_lock_conflict`) it rolls back, reloads the Sales
  Order, backs off briefly, and retries — up to `RESERVE_MAX_ATTEMPTS` (3).
- A transient conflict that clears on retry succeeds normally (the response
  reports `attempts`).
- A persistent conflict returns a friendly `ValidationError`:
  *"This stock is being reserved by another order right now. Please try again in a
  moment."* — never a raw database traceback.
- Every failed attempt rolls back first, so no partial reservation or corruption
  can occur.

## Verification
`test_reservation_retry` (3, staging), deterministic (simulated error 1213):
- `_is_lock_conflict` correctly classifies a deadlock vs an unrelated error.
- A persistent conflict is retried exactly `RESERVE_MAX_ATTEMPTS` times, then a
  friendly `ValidationError` is raised (bounded — no infinite loop).
- A transient conflict (one deadlock, then clear) is retried and succeeds with
  `attempts == 2`.

## Remaining (truthful)
- A fresh live two-process 10/8/8 run against the new wrapper (the prior mission ran
  it against the pre-retry path; the over-reservation guarantee is unchanged, and
  the friendly-retry path is now unit-verified). Listed as remaining in the final
  report.
