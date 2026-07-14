# Full Feature Parity — Decisions

## D1. Source of truth is the re-run live audit, not historical numbers

The mission's historical figures (2482/86/2396/3.46%) were re-verified live on
2026-07-14 (fingerprint `c8cab946…17d14`) and are still current. All work uses
this re-run inventory, captured under `docs/full-parity/inventory/`.

## D2. `unmapped_user_facing` will NOT be driven to zero by adding routes

The canonical strict audit counts a feature "mapped" iff it has a
`current_custom_route` (`feature_inventory._audit_result`). Assigning routes to
all 2,396 features would satisfy the number while faking parity — explicitly
forbidden. Instead we built a separate **authoritative registry** whose notion of
"mapped" is a truthful *status*, not the presence of a route. The route-based
audit stays FAIL until features are genuinely implemented.

## D3. Registry is generated deterministically, not hand-authored

2,482 hand-written entries are unmaintainable and would drift. `parity_registry.py`
derives entries from the canonical inventory via explicit rule tables + a small
override set (the 6 handcrafted doctypes, P0 doctypes, module→priority map). This
is reproducible and its honesty contract is test-enforced.

## D4. What counts as `internal` (1212 features)

Feature types that are *components of a parent*, not independent user
destinations, are `internal`:
- `custom_field` (212), `property_setter` (101) — attributes of a form, not routes.
- `workspace_target` (597) — a shortcut/link inside a workspace; its target
  DocType/report is separately inventoried and classified on its own.
- `dashboard_connection` (68), `client_script`, `installed_app`, `notification`,
  `source_only_report`.
Plus platform/technical modules (Core, Desk, Custom, Utilities, Geo) that Frappe
Desk owns. This is why `internal` is large; none of it is hidden or dropped —
every item still has an entry and a reason.

## D5. Business priority reflects a wholesale IMPORTING & SELLING business

- P1_required: Accounts, Stock, Selling, Buying, Contacts.
- P0_go_live: the specific fixed-flow doctypes (Customer, Item, Sales Order,
  Delivery Note, Sales Invoice, Payment Entry, Stock Reservation Entry, Bin,
  Pick List, Packing Slip, Customer Credit Limit).
- not_required: Manufacturing, Subcontracting, Website, Portal, Social,
  Telephony, EDI, Maintenance, and the AI integration modules — outside the
  stated scope. They remain available in Desk; they are not deleted or hidden.
- Setup/CRM/Printing/POSAwesome: P2. Assets/Projects/Support/Quality/Automation: P3.

Priority is a planning signal only; it never inflates a feature's *status*.

## D6. `verified_complete` is currently zero — and that is honest

With `allow_tests` disabled and no browser automation, nothing has behavioural
evidence this mission. The strongest truthful status for the handcrafted
sales/payment stack is `implemented_unverified`. Zero `verified_complete` is the
correct, non-inflated state until GATE 4/5 (BLOCKERS.md) are opened.

## D7. Repository safety

Work is on branch `full-feature-parity` off `develop@3ce5958`, with recovery tag
`pre-full-feature-parity-20260714-1123`. The prior agent's `AGENT_HANDOFF.md` and
the deterministic inventory commit-bump were preserved, not overwritten. No other
app (frappe/erpnext/posawesome/smj_theme) was touched. No site config, schema,
Custom Field, DocType, or migration was changed.
