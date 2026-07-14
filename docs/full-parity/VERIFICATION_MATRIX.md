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
