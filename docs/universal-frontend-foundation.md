# Metadata-driven universal frontend foundation

Date: 2026-07-13

Source inventory: `erpnext-v15-complete-inventory.json`

Registry snapshot: `universal-feature-registry.json`

## Routing and registry contract

Resolution order is fixed:

1. handcrafted custom route;
2. allowlisted generated route;
3. registered specialised adapter;
4. Feature Unavailable.

Customer, Item, Sales Order, Delivery Note, Sales Invoice, Payment Entry,
Payment Entry Allocation and Smart Sales are custom overrides. A generated
URL for one of these keys is rejected. The first generated allowlist contains
20 safer master-data DocTypes: Supplier, Warehouse, Lead, Opportunity,
Project, Asset, Address, Contact, Territory, Customer Group, Supplier Group,
Item Group, Brand, UOM, Sales Person, Price List, Mode of Payment, Cost Center,
Department and Designation.

All 20 are classified `generated_provisional`. This means their metadata and
permission-aware lists were tested, but the feature is not considered complete
until its applicable create/edit/actions/print/collaboration paths have passed
role, desktop and mobile tests.

## Security model

- The browser sends a registry feature key, never a DocType or Python method.
- Server metadata removes fields outside the user's read permission levels.
- Writes accept only current metadata fields inside the user's write permission
  levels; unknown/read-only fields and unknown child fields are rejected.
- Lists use `frappe.get_list`, bounded pagination, allowlisted fields, filters,
  operators and sorting. Match conditions and User Permissions remain active.
- Detail reads query permission-visible names before loading a document, which
  avoids a missing-versus-denied existence oracle.
- Inserts, saves, deletes, submit, cancel, amend, duplicate and workflows use
  standard Frappe document APIs. No `ignore_permissions`, arbitrary method
  execution, direct SQL write, manual `docstatus`, stock or ledger write exists.
- Link searches are derived from a field on the approved parent/child metadata
  and recheck target read permission.
- Registry responses are paginated and permission filtered. The 2,843-record
  inventory is not loaded into the initial JavaScript bundle.

## Frontend engines

Implemented foundations:

- universal responsive list with search, metadata filters, server pagination,
  sorting, loading/empty/error/permission states and mobile record cards;
- universal form with create/edit, defaults, required/read-only fields,
  validation, dirty navigation protection and double-submit prevention;
- universal field rendering for Data, Link, Select, Date/Datetime/Time,
  numeric, Check, text, Attach URL, Color and other safe scalar types;
- universal editable child tables with add, remove, duplicate and reorder;
- universal detail with summary, readable fields, child tables, related records,
  timeline, print discovery and server-returned actions;
- lazy routes for generated documents plus provisional report/view adapters.

Generated route patterns remain available under both existing mounting modes:

- `/retail-erp/generated/:feature`
- `/retail-erp/generated/:feature/new`
- `/retail-erp/generated/:feature/:name`
- `/retail-erp/generated/:feature/:name/edit`
- `/retail-erp/reports/:report`
- `/retail-erp/views/:feature/:view`

The existing `/app/retail-erp/*` compatibility mount is retained.

Role smoke testing used the existing non-Administrator
`zaidhnajeeb98@gmail.com` account (System Manager plus Purchase, Sales and
Accounts User roles) without changing it. Supplier, Warehouse, Lead and
Designation were permission-filtered as expected; Project was denied and the
registry exposed 17 of the 20 provisional features. Dedicated isolated
single-role browser users do not exist and were not created.

## Unsupported metadata and specialised adapters

Vue does not execute ERPNext Client Scripts, `eval:` dependencies or Button
field handlers. These are marked `unsupported_client_behavior`; a reviewed
adapter or custom override is required. Dynamic Link, Signature, Geolocation,
rich HTML sanitisation, file upload, Table MultiSelect semantics, tree naming,
complex transaction pricing, specialised maps, close/hold/resume methods,
report rendering and collaboration writes still require controlled adapters.

The universal action foundation currently executes only standard submit,
cancel, amend, delete and duplicate actions plus active workflow transitions.
Rename, close, reopen, hold, resume and mappings remain server-registry work.
Reports, Workspaces, dashboards, Kanban, calendar, tree, Gantt, map and POS are
registered as special; their current route is a Retail ERP provisional screen,
not a completion claim.

## Coverage snapshot

Registry records: 2,843 (2,841 inventory records plus two app-owned synthetic
features). Classification: 8 custom, 20 generated provisional, 352 special,
2,104 unavailable and 359 internal.

- Direct custom or generated-provisional UI entry coverage: 28 / 2,484
  registry user-facing records = **1.13%** of the atomic inventory.
- Special-adapter classification coverage: 352 / 2,484 = **14.17%**, but these
  are not functionally complete.
- Functional tested coverage is not increased for the 20 provisional features.
- The project's previously estimated strict completion remains approximately
  **19%**; the machine strict audit remains the authoritative red gate at
  `unmapped_user_facing=2477`.

Projected dates assume sustained staged implementation and timely approvals:

- 55% tested functional completion: 2026-10-30
- 75%: 2027-02-26
- 90%: 2027-07-30
- near-full tested parity: 2027-12-17

These are planning estimates, not delivery guarantees; specialised accounting,
stock, manufacturing, regional and installed-app behavior can move them.
