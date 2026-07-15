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

## D8. Crediting workspace shortcuts by their destination

A `workspace_target` is a shortcut inside an ERPNext workspace. Retail ERP does
not render ERPNext workspaces, but the *destination* a shortcut points to (a
DocType or Report) may have a real Retail ERP route. The audit now credits a
workspace_target with its target's **real** route (never an empty one) when the
target DocType/Report is routed; targets to unrouted DocTypes, Number Cards,
Pages, Charts or Dashboards stay unmapped. This is truthful navigation
reachability, not metric-padding: 351 of 597 shortcuts point to genuinely-served
destinations. In the registry these are `generated_provisional` (the destination
works; interactive workspace-card verification is still pending).

## D9. Batches so far reduced unmapped only through real engine coverage

- Batch "generated DocType masters": +116 doctypes served by the universal engine
  (server-verified). Included a real engine bug fix (list KeyError on text/hidden
  default columns).
- Batch "generated reports": +156 reports served by the permission-aware viewer
  (server-verified definitions).
- Batch "workspace shortcuts": +351 shortcuts credited via their routed targets.

No empty routes were invented; ledger/system tables, singles and POS were
excluded from generic CRUD. `unmapped_user_facing` 2396 → 1773.

## D7. Repository safety

Work is on branch `full-feature-parity` off `develop@3ce5958`, with recovery tag
`pre-full-feature-parity-20260714-1123`. The prior agent's `AGENT_HANDOFF.md` and
the deterministic inventory commit-bump were preserved, not overwritten. No other
app (frappe/erpnext/posawesome/smj_theme) was touched. No site config, schema,
Custom Field, DocType, or migration was changed.

## D10. Two separate "unmapped" numbers exist on purpose (URGENT MAPPING MISSION)

The route-based `unmapped_user_facing` (feature_inventory.py, currently 1699) and
the registry-based `corrected_unmapped_user_facing` (parity_registry.py, currently
0) measure different things and must not be conflated:

- Route-based: counts any feature without a `current_custom_route`. Will never
  reach zero honestly, because most internal/not-required/deferred features
  correctly have no route (a GL Entry table should never get a page).
- Registry-based (Step 13 corrected audit): counts features with NO truthful
  classification at all. This is zero because every one of the 2,482
  user-facing features has exactly one of the 8 honest statuses with a real
  documented reason (enforced by `validate_parity_registry`).

Neither number means "production ready." The number that matters for that
question is `required_but_missing` (367) — the honest count of P0/P1/P2
capabilities with no real implementation yet. See PROGRESS.md and
BLOCKERS.md for exactly what remains.

## D11. Registry status corrections apply per-feature, not per-module

Several audit-correction rules added this pass (`SYSTEM_INTERNAL_DOCTYPE_NAMES`,
`WORKSPACE_OVERRIDES`, `PAGE_OVERRIDES`, `NOT_REQUIRED_REPORT_NAMES`,
`DOCTYPE_SPECIFIC_ACTIONS`) override a feature's status by exact name, layered
on top of (not replacing) the existing module-based `business_priority`
default. This was a deliberate choice over editing `MODULE_PRIORITY`: a whole
module (e.g. "Accounts") is genuinely P1-required, but specific DocTypes
within it (GL Entry, Accounts Settings) are not independent user
destinations. Correcting the metric computation (Step 13's
`corrected_production_parity_audit`) to key off *status* rather than raw
module priority was necessary as a result — see the bug found and fixed in
commit 921448e (first version wrongly counted 846 "gaps" that included
doctypes already correctly marked `internal`).

## D17. Route additions require re-running generate_complete_inventory before generate_corrected_audit

`build_parity_registry()` reads the canonical `docs/erpnext-v15-complete-
inventory.json` snapshot, not a live site query. Adding a new `ENTITY_ROUTES`/
`REPORT_GROUPS` entry changes what the Python code *would* report for
`current_custom_route`, but the corrected audit undercounts the drop until
`generate_complete_inventory()` re-runs and refreshes that snapshot -
observed directly in pass 8 (295→293 instead of the expected 295→288 until
the inventory was regenerated). Registry-only changes (`DOCTYPE_SPECIFIC_
ACTIONS`, `BUILT_ADAPTER_*`) don't need this since they only affect
classification of already-present inventory rows, not `current_custom_route`
itself. Rule: always regenerate the canonical inventory first whenever a
batch touched `ENTITY_ROUTES`/`REPORT_GROUPS`.

## D18. A regular, non-virtual, non-table, non-single doctype never needs a bespoke adapter

Passes 7-8 routed 5 more "Process *"/"Unreconcile Payment" tool doctypes by
checking their `is_virtual`/`issingle`/`istable` flags against the installed
schema first (all falsy) and simply adding them to `ENTITY_ROUTES` -
identical to how the ~141 other generic doctypes were routed in earlier
batches. This is the same rule Bank Reconciliation Tool's own build (pass 4)
established in the opposite direction: `Bank Reconciliation Tool`'s
`Document` subclass body is literally `pass` (genuinely virtual), which is
*why* it needed a dedicated adapter instead of a route. Checking this flag
first is now the standing rule before spending adapter-building effort on
any remaining "doctype" required_but_missing entry.

## D19. Pure navigation actions (no document created or changed) are real, creditable work - if actually wired

A JS button that only calls `frappe.set_route(...)` with prefilled
`frappe.route_options` (Account's "General Ledger", Journal Entry's
"Ledger", Company's "Chart of Accounts", etc.) creates or changes nothing -
it is real functionality (a working drill-down), and the existing
`run_document_action` response contract already supports it for free
(returning `{"route": "..."}` triggers `router.push` in
`UniversalDetailPage.vue`'s existing `act()` handler, no frontend action-menu
changes needed). The catch, found while implementing this: it is *not*
free if the destination page ignores its own query string (see D17's
sibling bug fixed the same pass in `PriorityReportPage.vue`/
`PriorityTreePage.vue`). Crediting a navigation action as `implemented_
unverified` without verifying the destination actually consumes the passed
filters would have been exactly the kind of "route exists but doesn't do
what's claimed" gap the mission explicitly forbids - always click through
the whole chain (action → route → destination reads the filter), not just
confirm the route resolves.

## D15. "generated_provisional" reports can still hide real functional bugs

Pass 5 found that `Accounts Receivable`/`Accounts Payable` (`posting_date`
vs the real `report_date` fieldname) and `Customer Ledger Summary`
(`customer` vs the real `party` fieldname) had wrong filter keys — the date/
party filter was silently dropped by ERPNext rather than erroring, so the
report still "ran" and looked implemented. This is why `required_but_missing`
staying flat at 312 after pass 5 doesn't mean nothing happened: the registry
metric tracks whether a route+strategy exists, not whether every filter on
an already-routed report actually works. Established a rule for finishing
the remaining report drill-down work: read the real `<report>.js` filter
array (or the shared `financial_statements.js` for P&L/Balance Sheet/Cash
Flow) before trusting an existing `REPORT_FILTERS` entry, even for reports
already marked implemented.

## D16. MultiSelectList report filters need a real Python list, not JSON text

Reports whose Desk filter widget is `MultiSelectList` (General Ledger's
account/project/cost_center/party, Trial Balance/P&L/Balance Sheet/Cash
Flow's cost_center/project, AR/AP's party/cost_center/project) are read
server-side as an actual Python `list`, not a JSON-encoded string — some
call `frappe.parse_json()` on it defensively (harmless no-op when already a
list), but `erpnext.accounts.report.financial_statements.
get_cost_centers_with_children` explicitly does `isinstance(x, list)` and,
if false, treats the whole value as one comma-separated string. Passing
`frappe.as_json([value])` (a JSON string) through this path produced a
garbled "Cost Center: [\n \"...\"\n] does not exist" error — reproduced
against real site1 data before the fix. `MULTISELECT_REPORT_FILTER_FIELDS`
in `priority_pages.py` now wraps a single chosen value into a real one-item
list (`[value]`), matching what the Desk client's own array value looks like
after Frappe's request-layer JSON decoding.

## D13. A built adapter can credit document actions whose parent isn't its own doctype

`Bank Reconciliation Tool` (pass 4) serves two of `Bank Transaction`'s document
actions (`create_bank_entries`, `unreconcile_transaction`) in addition to its
own five. The original `BUILT_ADAPTER_ACTIONS` was a single flat set shared
across all built adapters, keyed only by "is the action's parent doctype in
`BUILT_ADAPTER_DOCTYPE_NAMES`" — that check would have silently failed to
credit Bank Transaction's actions (Bank Transaction is a normal routed
doctype, not itself a virtual-tool entry in `BUILT_ADAPTER_DOCTYPE_NAMES`),
and a flat action-name set risked crediting an unrelated action with the same
name on a different, unbuilt doctype. Refactored to
`BUILT_ADAPTER_ACTIONS_BY_PARENT: dict[str, set[str]]`, keyed by the actual
document_action parent, with a matching `BUILT_ADAPTER_ACTION_ROUTE` map so
each parent resolves to the correct adapter route in the credited evidence.
No behaviour changed for Payment Reconciliation (same three actions, same
route) — this is a scope-widening refactor, not a reclassification.

## D14. "Bank Clearance" is a different doctype from "Bank Reconciliation Tool"

`Bank Clearance` (`erpnext.accounts.doctype.bank_clearance`) is a separate,
older ERPNext tool doctype with its own `get_payment_entries` /
`update_clearance_date` actions — it is NOT superseded or served by the new
`bank_reconciliation_api.py` adapter, despite the similar name and business
domain. Left honestly `unavailable_with_reason`; building it (if still
relevant alongside the newer Bank Reconciliation Tool) is separate future
work, not silently folded into this pass's credit.

## D12. Document-action crediting extended beyond the 6 handcrafted DocTypes

`my_store_ui/universal/api.py`'s action handler (`_available_actions`,
`MAPPED_ACTIONS`) already served generic lifecycle actions (submit, cancel,
amend, delete, duplicate, rename) and 9 real document-conversion handlers for
ANY routed doctype — not just the 6 handcrafted ones — but the audit only
credited the 6. Added `GENERIC_LIFECYCLE_ACTIONS` + `DOCTYPE_SPECIFIC_ACTIONS`
lookup tables to `parity_registry.py`, cross-referenced against a
`routed_doctypes` set built once from the canonical inventory, so a
document_action is only credited when both (a) its action key matches a real
handler and (b) its parent doctype genuinely has a route. This is server-code
truth, not a registry guess — verified against the actual Python source of
`universal/api.py` before writing the tables.
