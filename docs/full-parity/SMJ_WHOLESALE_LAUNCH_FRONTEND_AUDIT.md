# SMJ Wholesale-Launch Frontend Coverage Audit

Final audit, 2026-07-27. Classification per feature:

- **V** Fully implemented and verified (tests/browser)
- **U** Implemented through the universal generated engine
- **D** Dedicated custom page
- **X** Backend exists, frontend intentionally minimal / linked
- **N** Not required for first wholesale launch
- **E** External infrastructure requirement

| Feature | Class | Notes |
|---------|:----:|-------|
| Company | V/D | Setup wizard create + generated `/admin/companies` |
| Fiscal Year | U | `/finance/fiscal-year` |
| Chart of Accounts | U | `/finance/chart-of-accounts` (tree) |
| Warehouses | U | generated CRUD; default warehouse now on Product form |
| Price Lists | V | wholesale/retail/buying ensured by setup + Item Price sync |
| Taxes | U | templates/category/rule via generated CRUD |
| Customer | V/D | curated entity form, customer-first Smart Sales |
| Supplier | V/D | curated add form |
| Product | V/D | curated form incl. the 7 completed fields + Item Price sync |
| Sales (SO/DN/SI) | V/D | Smart Sales + curated forms; stock gating; reservation |
| Purchasing (MR→RFQ→SQ→PO→PR→PI→PE) | V | `test_purchase_workflow` |
| Inventory / Stock | V | Actual/Reserved/Available; FIFO; reservation lifecycle |
| Accounts | U/D | generated + report drill-downs |
| Payments | V/D | Payment Entry + reconciliation |
| Reconciliation | V/D | Payment + Bank reconciliation adapters |
| Returns / Credit Notes | V | covered in reservation lifecycle + stock parity |
| Printing | D | `/admin/printing` landing + preview; Letter Head/Print Format CRUD generated |
| Email | D | `/admin/email` status/templates/notifications; SMTP is **E** |
| Workflows | U | generated engine + document actions |
| Users / Roles / Role Profiles | V/D | `/admin/*` generated CRUD + Access Control |
| User Permissions | V/D | Access Control → restrictions |
| Effective Access | V/D | Access Control → effective access |
| Import / Export | V/D | `/admin/data` allowlisted |
| Audit / Error logs | V/D | System Operations error summary |
| Backups | V/D | System Operations backup status; restore is **E**/server-only |
| Reports | V | drill-downs done (prior mission) |
| Scheduled reports | N | not required for first launch |
| Customer portal / Website | N | no storefront for wholesale launch |
| Integrations / Webhooks | N | not required for first launch |
| Form customisation / Naming series | U | via generated engine where needed |
| First-time setup | V/D | setup wizard (fresh-site run **E**) |
| System health / readiness | V/D | System Operations |

## Launch-critical gaps remaining

**None** in the frontend. Remaining items are:
- **External (E):** SMTP credentials; fresh-site/QA creation (MariaDB root); accountant
  sign-off on the opening-stock reclassification; Hetzner/DNS deployment.
- **Ordinary remaining development (not launch-critical):** a two-company end-to-end
  separation test on a fresh site; scheduled reports; storefront/integrations (not
  needed for a wholesale launch).

Optional broad ERPNext features were deliberately **not** built solely to raise a
percentage.
