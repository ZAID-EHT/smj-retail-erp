# ACCOUNT CREATION.docx — Completion Record

Follow-up to `SMJ_ACCOUNT_CREATION_DOC_RESULTS.md`, closing the three items that
report left open plus the form audit.

## Previously open items — all built

| Item | Route | Backend | Tests |
|---|---|---|---|
| Henderson Analysis | `/retail-erp/reports/henderson-analysis` | `henderson.py` + 2 DocTypes | 12 |
| Accounts workspace | `/retail-erp/finance/accounts` | `accounts_workspace.py` | 6 |
| Print Format administration | `/retail-erp/admin/print-formats` | `print_format_admin.py` + 2 DocTypes | 13 |
| Payment Reconciliation | `/retail-erp/finance/payment-reconciliation` | existing adapter + totals | 8 |
| Bank Reconciliation | `/retail-erp/finance/bank-reconciliation` | existing adapter + date guard | 4 |

### Henderson Analysis

`Henderson Assessment` + `Henderson Assessment Domain` DocTypes store real editable
data — no invented figures. Six domains with current/target scores, derived
alignment gaps, ranked priority areas, management notes and standard audit fields
for "last updated / by whom".

Editing: System Manager and Accounts Manager. Read-only: Sales, Purchase and Stock
Managers. A Sales User is refused entirely. Scores are range-checked 0–5 and
duplicate domains rejected in the DocType's own `validate`, so the API is not the
only guard.

Separation is asserted by test: saving an assessment changes neither `Item Price`
nor `Sales Order` counts.

### Accounts workspace

Replaces the bare Chart-of-Accounts tree. Sections for ledgers, receivables,
payables, cash and bank, reconciliation tools and reports — each present only if the
user may read the underlying doctype.

**Monetary totals are withheld server-side** from users without an accounting role:
the response contains no currency cards at all, rather than sending figures for the
browser to hide. A test iterates every card returned to a Sales User and fails if
any has `kind == "currency"`.

Figures are read through `frappe.get_list`, so User Permissions apply, and one test
recomputes the receivables total directly from Sales Invoices to prove the number is
real.

### Print Format administration

All nine required document types (Stock Entry presented as **Stock Transfer**).
Choose the Retail ERP default format and language, create or duplicate a custom
format, disable a custom format, preview through ERPNext's own engine.

ERPNext Standard formats are protected by construction:

- duplicating a standard format always writes `standard = "No"`, and a test asserts
  the source is still `"Yes"` afterwards
- disabling a standard format is refused
- disabling a format that is the current default clears the default rather than
  leaving a dangling pointer

Defaults live in the `Retail ERP Print Setting` single DocType, so the selection is
reproducible through `bench migrate`.

The preview modal was rebuilt: aligned header/body/footer, scrollable body, working
Close/Cancel/Print, Escape-to-close, focus moved to Close on open and restored on
close, explicit loading and error states, and a stacked mobile layout.

## Form audit — measured, not asserted

Six forms already used dedicated curated pages (Customer, Item, Sales Order,
Delivery Note, Sales Invoice, Payment Entry). Seven were still rendering the **raw**
ERPNext form. Curated add-form sets now exist for all of them:

| Form | Add form | Full form | Reduction |
|---|---|---|---|
| Supplier | 9 | 38 | −76% |
| Lead | 11 | 47 | −77% |
| Quotation | 13 | 84 | −85% |
| Purchase Order | 13 | 107 | −88% |
| Purchase Receipt | 10 | 101 | −90% |
| Purchase Invoice | 14 | 135 | −90% |
| Stock Entry (Stock Transfer) | 7 | 58 | −88% |
| Warehouse | 11 | 22 | −50% |

Only the ADD form is trimmed. Omitted fields still exist on the DocType, ERPNext's
defaults still apply, and the detail view stays complete — no backend field was
removed and no validation weakened.

## Bug found in the browser

`/reports/henderson-analysis` was swallowed by the `/reports/:report` catch-all and
rendered "Unable to load report" with a console 404. It now has an explicit Vue
route ahead of the catch-all.

## Evidence

| Check | Result |
|---|---|
| Backend suite | **615 tests, 0 failures, 6 environmental skips** |
| New tests this task | 54 |
| Frontend build | clean |
| Browser matrix | **192/192** (32 routes × 6 viewports), zero console errors |
| Button audit | **9/9** |
| `bench migrate` | clean and idempotent (re-run twice) |
| Secret scan | clean |
| `site1.local` | fingerprint unchanged (`f51fedb5…d9c3`) |

The 6 skips are environmental: staging has a single Company, so cross-company
warehouse cases skip there.
