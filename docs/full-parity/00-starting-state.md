# Full Feature Parity — Starting State (Stage 0)

## When and where

| Item | Value |
|---|---|
| Date/time | 2026-07-14 ~11:23 Asia/Colombo |
| Bench | `/home/zaidh/frappe-bench` |
| Site | `site1.local` |
| App | `apps/my_store_ui` |
| Recovery tag created | `pre-full-feature-parity-20260714-1123` → `3ce5958` |
| Work branch created | `full-feature-parity` (from `develop` @ `3ce5958`) |
| Prior branch | `develop` |
| Prior HEAD commit | `3ce5958392a66c9d75243fbec43fe780c168673c` — "feat: add priority ERPNext module page coverage" |
| Remote | none (local-only repository) |

## Installed applications (verified `bench --site site1.local list-apps`)

| App | Version | Branch |
|---|---|---|
| frappe | 15.108.0 | version-15 |
| erpnext | 15.108.3 | version-15 |
| smj_theme | 0.0.1 | develop |
| erpnext_chatgpt | 0.0.1 | main |
| erpnext_gemini_integration | 0.1.0 | main |
| posawesome | 15.30.0 | develop |
| my_store_ui | 0.0.1 | develop |

## Worktree state at start (before any work in this mission)

Pre-existing, **authored by the previous audit agent — preserved, not overwritten**:

- `AGENT_HANDOFF.md` (untracked) — the prior production-readiness audit.
- `docs/erpnext-v15-complete-inventory.json` (modified) — a single-line change bumping the recorded
  `my_store_ui` `git_commit` from `98794f8…` to `3ce5958…`. Re-running the canonical generator in this
  mission reproduced exactly this one-line difference and nothing else (content is otherwise identical),
  confirming the generator is deterministic against the current site.

These were carried onto the `full-feature-parity` branch unchanged.

## Existing recovery tags

- `pre-priority-page-expansion`
- `pre-universal-frontend-engine` → `9349636…`
- `pre-standalone-retail-erp` → `110d1fb…`
- `stage-0-baseline`
- `pre-full-feature-parity-20260714-1123` (new, this mission)

## Current tests

- 12 test files / **100** statically-discovered `test_*` methods under `my_store_ui/tests/`.
- **Execution BLOCKED**: `bench --site site1.local run-tests --app my_store_ui` refuses because
  `allow_tests` is disabled on `site1.local`. Enabling it is a site-config change requiring approval,
  so it was NOT changed. Test execution therefore has no fresh evidence this mission.

## Current Vue build status

- `npm run build` → PASS (Vite 6.4.3, 107 modules; `retail-erp-DWQjyjjl.js` 280.46 kB / 87.11 kB gzip,
  `my-store-ui-frontend-B3CqffZr.css` 70.18 kB / 12.06 kB gzip).
- `npm run check` → PASS (same build, `--emptyOutDir=false`; there is no separate type checker).
- Verified live this session.

## Current audit status (source of truth, re-run this mission)

Command:

```bash
bench --site site1.local execute my_store_ui.audit.feature_inventory.generate_complete_inventory
```

Result — fingerprint `c8cab9468d2eb48aa5f29f2a7a570c096f78366e60502a59c22c3fc5dcb17d14`:

| Metric | Value |
|---|---:|
| Total atomic features | 2841 |
| User-facing features | 2482 |
| System-internal exclusions | 359 |
| Currently mapped (has custom route) | 86 |
| Unmapped user-facing | 2396 |
| Strict route coverage | 3.46% |
| Strict audit status | **FAIL** |

Strict failure counts: `unclassified_user_facing=0`, `unmapped_user_facing=2396`,
`undocumented_actions=0`, `complete_without_tests=0`, `unhandled_active_workflows=0`.

## Known blockers carried in from the prior audit (verified still true this session)

Verified read-only against the live site on 2026-07-14:

- `Stock Settings.enable_stock_reservation = 0`; `allow_negative_stock = 0`.
- Stock Reservation Entry rows: **0**.
- Customer Credit Limit rows: **0**; no Credit/Non-Credit custom field on Customer.
- Submitted Delivery Notes: **0**; Purchase Receipts: **0**; Landed Cost Vouchers: **0**.
- Submitted Sales Orders / Sales Invoices / Payment Entries: 5 / 5 / 5. Purchase Orders: 10. Purchase Invoices: 6.
- `my_store_ui/api.py::get_bootstrap` sums `Bin.actual_qty` and returns it as `item.actual_qty` with
  no reserved-qty subtraction (Available-to-Sell model absent).
- `services/form_schemas.py` Customer schema has **zero** credit fields.

## Approval gates identified up front (mission will STOP on these, per the master prompt)

1. Enabling `enable_stock_reservation` (site-config change) + reservation business rules (expiry, backorder).
2. Any Custom Field creation — required for Credit/Non-Credit classification and the shared Transaction ID.
3. Any new DocType — e.g. a custom Import Shipment aggregate, if standard ERPNext proves insufficient.
4. Enabling `allow_tests` on `site1.local`, or provisioning a separate approved test site.
5. Any `bench migrate`, system-package install, or destructive operation.

All independent, non-gated work proceeds; gated items are documented in `docs/full-parity/BLOCKERS.md`
with approval proposals and are NOT executed without explicit approval.
