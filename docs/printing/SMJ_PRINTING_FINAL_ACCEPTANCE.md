# SMJ Printing Final Acceptance

Routes: `/retail-erp/admin/printing` (+ Letter Head / Print Format CRUD via the
generated engine). Backend `printing_admin.py`. Tests `test_printing_admin` (10, 1
env-skip).

| Capability | Status |
|-----------|--------|
| Letter Head list/create/edit/duplicate/default | ✅ generated CRUD + overview |
| Print Format list, filter by DocType, create/edit/duplicate | ✅ generated CRUD + overview |
| Format default per DocType | ✅ shown in overview |
| Preview with an authorised document | ✅ (get_print) |
| Download PDF | ✅ `download_pdf` (standard pipeline) |
| Documents covered | Quotation, Sales Order, Delivery Note, Sales Invoice, Payment Entry, Purchase Order, Purchase Receipt, Purchase Invoice (Credit/Debit notes are is_return variants of the invoices) |
| Permission-safe (company / field-level) | ✅ document-level + field-level permission |
| No separate PDF engine / no arbitrary templates | ✅ |

**Environment note:** `wkhtmltopdf` needs network access to fetch any remote assets
in the print HTML; in the offline sandbox it raises HostNotFoundError. The endpoint
and permission path are correct and asserted; the binary render is exercised on a
networked host.
