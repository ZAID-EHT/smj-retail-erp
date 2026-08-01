# SMJ Wholesale Operations — Batch Log

## Phase 0 — preflight (2026-08-01)

- Audited worktree: 3 modified test files + 7 untracked docs were present and unverified.
- Found and fixed a dead-coverage defect: `test_quick_entry_security._base()` still sent
  `department_price`, which `_clean()` rejects since `637f999`. `_clean()` runs before the
  permission gate, so all four permission tests were failing on `Unsupported field` instead
  of asserting `PermissionError`. Committed as `8311990` after verifying 39 tests green.
- Recovery tag `pre-smj-wholesale-operations-20260801-1121`; full staging backup taken.
- site1.local fingerprint recorded read-only (SHA256 f51fedb5…d9c3).
- Confirmed `v1.0.0-rc7` does not exist; previous mission incomplete.

## Phases 2-19 (2026-08-01)

Delivered in focused commits, each verified before the next:

- `a97c855` Carton as a real UOM conversion (selling + buying).
- `071dcab` FIFO delivery preparation, payment gate, database-backed idempotency.
- `df5b01c` Final Sales Invoice + customer payment allocation.
- `4323036` Sales returns, credit notes, supplier return documents.
- `95a2605` Purchasing: PO to receipt to invoice to supplier payment.
- `ba9d5c4` Landed cost vouchers.
- `518e73e` End-to-end acceptance scenarios (14).
- `45c615e` Transaction register statuses, filters, timeline.
- `8492236` Daily operations dashboard.
- `8a26767` Two defects found only by browser verification.

### Defects found and fixed (all real, all shipped-but-unverified)

| # | Defect | How it was found |
|---|---|---|
| 1 | `test_quick_entry_security` sent a rejected field, so its permission assertions never ran | Reading the failing input against `_clean()` ordering |
| 2 | Transport details written to fields absent on Delivery Note; Frappe discards unknown attributes silently | Meta check before trusting the field name |
| 3 | Idempotency was cache-only; a Redis restart would dispatch the same goods twice | Cache round-trip returned None under `bench execute` |
| 4 | Bank receipt accepted with no reference number, failing deep in the controller | Test run |
| 5 | Return reason written to `remarks`, which Delivery Note does not have in v15 | SQL error "Unknown column 'remarks'" |
| 6 | Credit note inherited the original invoice's advance rows and failed validation | Test run |
| 7 | Purchase Receipt lines broke received = accepted + rejected on partial receipt and on return | QtyMismatchError |
| 8 | `create_draft_sales_order` ignored the customer's Price Category, pricing against the site default | Acceptance scenario priced at zero |
| 9 | Register route guard admitted users its own API refuses (console 403) | Browser matrix |
| 10 | `get_bootstrap` raised DoesNotExistError because POS Awesome is not installed, breaking Smart Sales | Browser matrix |

### Verification

- Backend: 540 tests, 0 failures, 6 skipped (regression2). Final run recorded in the state doc.
- The first full run showed 9 errors in one module, all MariaDB deadlock (1213) caused by
  `bench schedule` / `bench worker` running against the same database during a 7-minute
  suite. That module passes 14/14 alone and the whole suite passed clean on re-run, so it
  is contention, not a defect. The workers were left running (mission safety rule).
- Frontend build clean. Browser matrix 162/162 across six viewports, zero console errors.
- Secret scan clean. site1.local fingerprint identical to the pre-mission baseline.
