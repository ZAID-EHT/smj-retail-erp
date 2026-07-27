# SMJ Secure PDF Download

Endpoint: `my_store_ui.printing_admin.download_pdf(doctype, name, print_format?, letterhead?)`.

## Security
- Authentication required; Guest rejected.
- Only allowlisted printable DocTypes (`PRINTABLE_DOCTYPES`); others → ValidationError.
- **Document-level permission** (`has_permission(dt, "print"/"read", doc=name)`) — this
  applies **company and User Permission scoping**, so a user cannot download another
  company's document.
- **Field-level permission** via `frappe.get_print` — purchase-cost fields a Sales
  user cannot see are omitted from the output.
- Format validated to belong to the DocType; letter head validated to exist.
- Standard ERPNext pipeline (`frappe.get_print` → `frappe.utils.pdf.get_pdf`); no
  bespoke PDF engine; no arbitrary template execution.

## Output
Sets `frappe.local.response` as a `pdf` download (`<name>.pdf`). The test asserts the
`%PDF-` signature and non-emptiness when the binary renders.
