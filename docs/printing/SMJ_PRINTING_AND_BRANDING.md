# SMJ Printing & Branding

Route: `/retail-erp/admin/printing` (System Manager gated). Backend:
`my_store_ui/printing_admin.py`. Tests: `test_printing_admin` (6, green).

## Approach: reuse ERPNext's print system

No separate PDF engine. Letter Head and Print Format **CRUD already exists** via the
generated universal engine (`/admin/letter-head`, `/admin/print-format`, both System
Manager gated). This page adds:

- a **landing overview** — letter heads (with default flag), and print formats per
  wholesale DocType with the configured default;
- **document preview** — renders a real document through Frappe's standard
  `frappe.get_print`.

## Covered document types

Quotation, Sales Order, Delivery Note, Sales Invoice, Payment Entry, Purchase Order,
Purchase Receipt, Purchase Invoice.

## Security

- Overview + preview candidates are System Manager gated.
- **Preview enforces document-level permission** (`has_permission(..., "print"/"read",
  doc=name)`), and `get_print` honours **field-level permissions** — a Sales user
  previewing a sales document does not see purchase-cost fields.
- Only the allowlisted printable DocTypes can be previewed; an arbitrary DocType
  (e.g. User) is rejected.
- Advanced HTML/Jinja Print Format authoring stays in the generated Print Format
  CRUD, which is System Manager gated; this page does not execute arbitrary templates.
