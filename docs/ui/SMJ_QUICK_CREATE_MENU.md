# SMJ Quick Create ( + Create ) Header Menu

A permission-aware `+ Create` menu in the app header, separate from module
navigation. It only ever offers **real, create-permitted** routes — never a guessed
URL or a dead action.

## Backend
`my_store_ui.services.frontend_routes.get_quick_create_actions` (whitelisted GET):
- Reads the universal registry (`get_registry_records()`), indexing doctypes that
  have a genuine `create_route`.
- Iterates a curated group order (Sales / Purchasing / Inventory / Administration /
  More) and includes a doctype only when **both** `feature_is_permitted(record,
  "create")` and `frappe.has_permission(doctype, "create")` pass.
- Guests are rejected (`AuthenticationError`).
- Returns `{groups: [{group, items: [{label, doctype, path, feature, group}]}]}`.

Backend still enforces create permission on the actual form/insert path — the menu
is a convenience surface, not a security boundary.

### Actions offered (when permitted)
| Group | Doctypes |
|-------|----------|
| Sales | Customer, Quotation, Sales Order, Delivery Note, Sales Invoice, Payment Entry |
| Purchasing | Supplier, Material Request, Request for Quotation, Supplier Quotation, Purchase Order, Purchase Receipt, Purchase Invoice |
| Inventory | Product (Item), Stock Entry, Stock Reconciliation, Warehouse |
| Administration | User, Role, Role Profile |
| More | Journal Entry, Contact, Address, Internal Transfer |

**26 actions** across 5 groups (was 22).

### Update 2026-07-25 — the two Phase 6 gaps are closed

**Role Profile is no longer omitted.** It previously had
`implementation_type: "unavailable"` and `create_route: None`, so it genuinely had
no route. It is now registered at `/admin/role-profiles` in `ENTITY_ROUTES`
(`generated_provisional`), which gives it real list/new/detail/edit routes.

Two things were required to make it actually *work*, not just route:
- It is gated to `System Manager` via `ADMIN_FEATURE_ROLES` — a Role Profile
  bundles roles, so it is at least as sensitive as `Role` itself.
- Its `roles` table is `read_only=1, hidden=1` in metadata because Desk replaces
  it with a JavaScript `roles_html` RoleEditor widget. Vue never runs Desk client
  scripts, so `SPECIAL_WRITABLE_FIELDS["Role Profile"] = {"roles"}` re-exposes
  exactly that one table to privileged user managers. Without it a Role Profile
  could be created but never given any roles.

**Payment Entry is now three distinct actions.** One DocType does three unrelated
jobs, so `FORM_VARIANTS` presets `payment_type` — the same mechanism the three
Stock Entry variants already used:

| Menu label | Route | Preset |
|------------|-------|--------|
| Receive Payment (Sales) | `/finance/payments/receive/new` | `payment_type: Receive` |
| Pay Supplier (Purchasing) | `/finance/payments/pay/new` | `payment_type: Pay` |
| Internal Transfer (More) | `/finance/payments/internal-transfer/new` | `payment_type: Internal Transfer` |

Presets are server-owned; the browser never chooses them.
`test_variant_presets_are_valid_doctype_options` asserts each preset is a real
`Select` option, so a typo cannot ship a form that fails on save.

**Menu entries can now override the label and pin a path.** A `QUICK_CREATE_GROUPS`
entry is either a plain DocType string or a dict
(`{"doctype", "label", "path"}`) — that is how "Product", "Receive Payment",
"Pay Supplier" and "Internal Transfer" get their names. `get_quick_create_actions`
additionally resolves **every** item's path through `resolve_frontend_route` +
`route_is_permitted` before offering it, so a dead entry cannot reach the menu even
if the registry disagrees.

**Frontend key fix.** The menu keyed items on `item.doctype`. With Payment Entry now
appearing three times that produced duplicate Vue keys and made keyboard navigation
highlight all three Payment Entry rows at once. It keys on `item.path`, which is
unique across the whole menu.

## Frontend
`components/shell/QuickCreateMenu.vue`, mounted in `AppHeader.vue`:
- Teleported-to-body dropdown (never clipped), right-edge aware positioning.
- In-menu search, grouped sections.
- Keyboard: ArrowUp/Down move the active item, Enter opens it, Escape closes and
  returns focus to the trigger.
- Click-outside closes. Reposition on scroll/resize. Mobile: label collapses,
  groups stack to one column.
- Truthful empty state: "You do not have permission to create records."

## Verification
- `test_quick_create` (4, staging): Administrator sees all groups with resolvable
  create routes; **no action is a dead route** (every path resolves with
  `permission=create`); a Sales-only user does not see the Administration group;
  Guest is rejected.
- `test_create_routes` (11, staging): all 23 required create DocTypes have a real,
  resolvable, permitted create route that never points at `/app/`; Role Profile is
  registered, admin-gated, has a writable `roles` table and can actually be created
  with roles (savepoint + rollback); the three Payment Entry presets are valid
  Select options; the menu offers exactly the required labels per group; no dead
  action; paths are unique and the Vue menu keys on `path`.
- `test_priority_page_coverage.test_purpose_variants_are_server_owned` +
  `test_variant_presets_are_valid_doctype_options` (17 total): every `FORM_VARIANTS`
  entry takes doctype/defaults/base_path from the server and presets a real option.
- `test_frontend_layout.test_header_mounts_permission_aware_quick_create_menu`:
  header wiring + keyboard/dismissal markers.
- `npm run build`: clean (201 modules).
