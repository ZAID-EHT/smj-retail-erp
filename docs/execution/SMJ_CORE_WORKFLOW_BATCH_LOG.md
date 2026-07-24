# SMJ Core Wholesale Workflow — Batch Log

Append-only log of logical batches. Newest at the bottom.

## Batch 0 — Preflight & audit (2026-07-24)
- Confirmed branch `full-feature-parity` @ `e15c37e`, clean tree.
- Confirmed both sites exist. `staging.local` = frappe+erpnext+my_store_ui only
  (clean isolated test site). `site1.local` carries the full app stack + business data.
- Created recovery tag `pre-smj-core-workflow-20260724-1140`.
- Took full `staging.local` backup (`--with-files`); DB 1.3 MiB (lean test site).
- Audited Smart Sales (`SmartSalesPage.vue`, `api.py`), reservation
  (`wholesale/reservation.py`), credit (`wholesale/credit.py`).
- Recorded four confirmed defects (see mission-state JSON `defects_found`).
