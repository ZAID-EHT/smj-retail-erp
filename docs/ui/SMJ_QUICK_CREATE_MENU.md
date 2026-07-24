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
| Inventory | Item, Stock Entry, Stock Reconciliation, Warehouse |
| Administration | User, Role |
| More | Journal Entry, Contact, Address |

`Role Profile` is intentionally omitted — it has no create route in the registry,
so offering it would be a dead action.

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
- `test_frontend_layout.test_header_mounts_permission_aware_quick_create_menu`:
  header wiring + keyboard/dismissal markers.
- `npm run build`: clean (201 modules).
