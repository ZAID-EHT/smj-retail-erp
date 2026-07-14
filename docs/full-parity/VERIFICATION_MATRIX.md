# Full Feature Parity — Verification Matrix

Verification levels: **behavioural** (driven end-to-end with evidence),
**source_only** (code exists, read/reviewed), **route_only** (a route resolves),
**none**. Nothing reaches `verified_complete` without behavioural evidence.

## What was verifiable this mission

| Item | Level | Evidence |
|---|---|---|
| Vue production build | behavioural | `npm run build` / `npm run check` PASS, hashed bundle |
| Parity registry honesty contract | behavioural | `validate_parity_registry` PASS; 7/7 unit tests PASS standalone |
| Live inventory counts | behavioural | `generate_complete_inventory` re-run, fingerprint match |
| Blocker facts (reservation/credit/doc counts) | behavioural | read-only Frappe console queries |
| `wkhtmltopdf` present | behavioural (prior audit) | `wkhtmltopdf --version` 0.12.6.1 |
| 116 generated DocType routes (list config + list API) | behavioural (server) | `route_coverage.verify_generated_routes` → served=170, failed=0 |
| Universal list-engine text/hidden column fix | behavioural (server) | all 116 doctypes list without KeyError after fix |
| 156 generated report routes (definition + viewer) | behavioural (server) | `route_coverage.verify_generated_reports` → served=182, failed=0 |
| 351 workspace shortcuts credited to routed targets | behavioural (audit) | targets present in CANONICAL_ROUTE_BY_DOCTYPE / REPORT_GROUPS |
| 27 print formats credited to routed DocTypes | behavioural (audit) | doc_type present in CANONICAL_ROUTE_BY_DOCTYPE |
| Available-to-Sell in get_bootstrap (Actual/Reserved/Available/Projected) | behavioural (server) | real Bin data on site1 |
| Customer credit status + 7 delivery-gate rules | behavioural (server) | 7/7 PASS via bench execute; real balances |
| Wholesale transaction register + timeline | behavioural (server) | 5 real transactions, correct links/status/outstanding |
| /sales/transactions route resolves + page builds | behavioural (server) | component=register, HTTP 200, Vue build |
| Transaction-id propagation hooks safe on site1 | behavioural (server) | no-op confirmed with field absent |
| Reservation Bin-lock (FOR UPDATE) query validity | behavioural (server) | `_lock_bins` runs, rolled back |
| Reservation reserve/unreserve/expiry, concurrency 10/8/8 | NOT verified | needs staging (reservation on) |
| Applying custom fields (credit type + txn id) | NOT verified | needs migrate on staging |
| Browser (register render, Smart Sales, mobile) | NOT verified | needs Playwright (network) + login |

_Note: "behavioural (server)" means the exact resolve→feature→list API path was
driven as a real user server-side and returned. Browser rendering, role matrix
and interactive actions for these routes remain unverified (no browser)._

## What could NOT be verified (and why)

| Domain | Blocker | Registry status held at |
|---|---|---|
| Sales Order / DN / SI / Payment lifecycles | allow_tests off; no browser | implemented_unverified |
| Mapped-document actions (SO→DN, DN→SI, …) | allow_tests off; no browser | implemented_unverified / special_adapter |
| Stock reservation / Available-to-Sell | not implemented; GATE 1 | (unavailable) |
| Customer credit gate | not implemented; GATE 2 | (unavailable) |
| Transaction register | not implemented; GATE 3 | (unavailable) |
| Generic-engine doctypes/reports | route_only at best; no browser | generated_provisional |
| Collaboration writes / email | no outgoing Email Account; no browser | unavailable / provisional |

## Manual browser verification checklist (for when GATE 5 opens)

Run in Chrome and Edge on an approved staging site with single-role users:

1. Login, invalid/disabled/expired/OTP, logout, browser Back.
2. Each handcrafted route: list/new/detail/edit/save/submit/cancel/amend/map/
   return/print/PDF; validation and permission errors preserved.
3. Representative generated master + transaction routes; field permlevels; child tables.
4. Reservation concurrency: two sessions, 10 available, two 8-unit reservations → never 16.
5. Credit gate: over-limit and overdue customers blocked / manager-approved correctly.
6. Responsive 1920/1440/1366/1280/1024 and 768/390/375/320 at 80–150% zoom;
   vertical scroll, no horizontal overflow, dialog focus, keyboard/touch.
7. Collaboration: comments/files/assign/share/tags/version/email; inaccessible-record non-disclosure.
8. Capture screenshots, console/network logs, created document chain, ledger/stock reconciliation.
