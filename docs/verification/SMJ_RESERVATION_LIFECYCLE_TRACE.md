# Continuous Stock Reservation Lifecycle Trace

Verified on `staging.local`, 2026-07-26. One continuous scenario — same item,
warehouse and customer throughout — using only standard ERPNext controllers,
recording **Actual / Reserved / Available-to-Sell after every step**.

Harness: `my_store_ui/dev_scripts/reservation_lifecycle_trace.py`
(`execute()` returns the trace; `run()` prints it). Regression:
`test_reservation_lifecycle`.

Item `SMJ-LIFECYCLE-ITEM`, warehouse `SMJ Lifecycle Test WH - SMJ`.

## The trace

| Step | Action (standard controller) | Actual | Reserved | Available | Invariant |
|------|------------------------------|:------:|:--------:|:---------:|:---------:|
| 1 | Material Receipt of 20 | 20 | 0 | 20 | ✓ |
| 2 | Submit Sales Order qty 12 | 20 | 0 | 20 | ✓ |
| 3 | Reserve stock (12) | 20 | 12 | 8 | ✓ |
| 4 | Release the reservation | 20 | 0 | 20 | ✓ |
| 5 | Re-reserve (12) | 20 | 12 | 8 | ✓ |
| 6 | Partial Delivery Note, 5 | 15 | 7 | 8 | ✓ |
| 7 | Deliver remaining 7 | 8 | 0 | 8 | ✓ |
| 8 | Return Delivery Note, 2 | 10 | 0 | 10 | ✓ |

`Available-to-Sell = Actual − Reserved` at every single step, and Available never
went negative. `all_invariants_ok: true`, `no_negative_available: true`.

## What each transition proves

- **Reserving does not reduce physical stock** — step 3: Actual stays 20, only
  Available drops (20 → 8). Reservation is a soft hold, not a stock movement.
- **Release restores availability** — step 4: Reserved 12 → 0, Available 8 → 20.
- **Re-reservation works** — step 5 re-establishes the hold.
- **Delivery reduces physical stock and consumes the reservation together** —
  step 6: a 5-unit Delivery Note drops Actual 20 → 15 **and** Reserved 12 → 7;
  Available is unchanged at 8 because both moved by 5.
- **Full delivery consumes the reservation entirely** — step 7: Reserved → 0, and
  **no open reservation remains** (`open_reservations_after_full_delivery: []`).
- **Return increases physical stock and does not recreate a reservation** —
  step 8: Actual 8 → 10, Reserved stays 0, so no stale hold is resurrected.

## Honest note on post-submit quantity reduction

The mission listed "increase / reduce reserved quantity" as steps. Editing a
**submitted** Sales Order's line quantity and having the reservation follow it is
**not a cleanly supported ERPNext operation** — an earlier version of this trace
tried it and the reservation stayed at the original 12 despite the qty edit. The
supported way to change a reservation is **release then re-reserve** (steps 4–5),
which is what this trace uses and asserts. This is an ERPNext behaviour, documented
here rather than worked around with a non-standard post-submit edit.

## Reconciliation summary

| Check | Result |
|-------|--------|
| Available = Actual − Reserved at every step | ✓ |
| Available never negative | ✓ |
| Reserving leaves Actual unchanged | ✓ |
| Delivery reduces Actual and reservation | ✓ |
| Full delivery leaves no open reservation | ✓ |
| Return raises Actual, no stale reservation | ✓ |
| All fixtures torn down | ✓ |
