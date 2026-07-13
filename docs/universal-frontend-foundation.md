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

All 20 remain classified `generated_provisional`. Their metadata,
permission-aware list configuration and bounded list reads were tested for
Administrator and the existing non-Administrator user. A feature is not
promoted until every applicable write, action, collaboration, print/PDF and
interactive desktop/mobile path is proven.

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

- universal responsive list with module-coloured presentation, plural titles,
  search, no more than five primary filters, a More Filters drawer, active
  filter chips, a 12-column server allowlist, saved non-business display
  preferences, sticky table headers, internal table overflow and mobile cards;
- universal form with primary fields first, metadata sections, two-column
  cards, an Advanced disclosure, create/edit defaults, required/read-only
  fields, validation, dirty navigation protection and double-submit prevention;
- universal field rendering for Data, Link, Select, Date/Datetime/Time,
  numeric, Check, text, Attach URL, Color and other safe scalar types;
- universal editable child tables with add, remove, duplicate and reorder;
- universal detail with summary cards, grouped sections, child tables, related
  records, timeline, collaboration panels, print selection and server-returned
  actions;
- permission-aware collaboration adapters for private file upload through the
  standard Frappe upload endpoint, attachment list/download/removal, comments,
  assignments, sharing, tags, document email and field-name-only version
  summaries;
- print-format, letterhead and language discovery plus standard Frappe print
  preview and protected PDF URLs;
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
`zaidhnajeeb98@gmail.com` without changing it. Administrator could list all 20
allowlisted features. The existing user could list 17; Department, Project and
UOM were denied by the current server permissions. Guest API access remains
denied. Dedicated isolated single-role browser users do not exist and were not
created.

## Generated UX completion review (2026-07-13)

The shared list, form and detail experience is no longer presented as a raw
metadata/debug surface. Presentation configuration is server-owned and falls
back to installed metadata. The same engines serve all 20 allowlisted features;
no Supplier-only page was introduced.

No feature was promoted to `generated_complete` in this stage. This is
intentional: interactive browser coverage at every requested viewport was not
available, collaboration write paths were not exercised for every feature, and
the server cannot generate PDFs because `wkhtmltopdf` is absent. Automated and
read-only role smoke tests are evidence for the shared foundation, not full
feature parity.

Frappe's PDF path currently fails with:

```text
OSError: No wkhtmltopdf executable found: "b''"
```

The application reports this dependency in the print dialog and keeps Print
Preview/browser printing available. Installing a supported wkhtmltopdf build is
a machine change and requires separate approval.

## Unsupported metadata and specialised adapters

Vue does not execute ERPNext Client Scripts, `eval:` dependencies or Button
field handlers. These are marked `unsupported_client_behavior`; a reviewed
adapter or custom override is required. Dynamic Link, Signature, Geolocation,
rich HTML semantics, Table MultiSelect semantics, tree naming, complex
transaction pricing and specialised maps still require controlled adapters.

The universal action foundation supports standard submit, cancel, amend,
delete, duplicate and active workflow transitions, plus allowlisted Rename,
Opportunity Close/Reopen, Supplier Hold/Resume, Lead-to-Opportunity and
Opportunity-to-Customer adapters. The browser never supplies a Python method.
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
- Functional strict coverage is not increased for the 20 provisional features.
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
