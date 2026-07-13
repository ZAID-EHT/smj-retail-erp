# Priority Retail ERP page coverage

Audited on 2026-07-13 against `site1.local` and starting commit
`98794f8300e3da9e2bf9648d538130522d4911a0`.

This is a route and adapter coverage ledger, not an ERPNext parity claim. A
`provisional` route is usable through the secure shared engine, but still needs
feature-specific browser, role and controller-edge-case graduation.

## Coverage model

- All paths below are relative to `/retail-erp`.
- `L/D/F` means list, detail and create/edit form.
- Every entity URL is resolved by the server-owned registry before Vue renders it.
- Every read/write/action is checked again by the relevant API.
- Handcrafted Customer, Item, Sales Order, Delivery Note, Sales Invoice and
  Payment Entry pages always win over the generated resolver.
- `/generated/*` remains a compatibility alias only and is absent from normal navigation.
- There is no arbitrary DocType, report name or Python method URL.

## Module and integration pages

| Route | Backend source | Implementation | Capability | Permission source | Test state | Limitation |
|---|---|---|---|---|---|---|
| `/home` | Permitted navigation and DocTypes | dashboard | Counts, recent records, quick actions | Per linked feature | Automated | Interactive visual matrix pending |
| `/sales` | Sales DocTypes/reports | dashboard | Real counts, recents, actions, links | Per linked feature | Automated | No expensive KPI analytics |
| `/purchases` | Buying/Stock/Accounts DocTypes | dashboard | Real counts, recents, actions, links | Per linked feature | Automated | — |
| `/inventory` | Stock DocTypes/reports | dashboard | Real counts, recents, actions, links | Per linked feature | Automated | — |
| `/finance` | Accounts DocTypes/reports | dashboard | Real counts, recents, actions, links | Per linked feature | Automated | — |
| `/crm` | CRM/Selling DocTypes | dashboard | Real counts, recents, actions, links | Per linked feature | Automated | — |
| `/operations` | Projects/Assets/Manufacturing/Support | dashboard | Real counts, recents, actions, links | Per linked feature | Automated | — |
| `/reports` | Installed Report records | report hub | Permitted report discovery | Report permission | Automated | Only priority report batch registered |
| `/admin` | Restricted setup features | dashboard | Permitted setup links and counts | System Manager plus target permission | Automated | No secrets or executable tools |
| `/smart-sales` | Item, Item Price, Customer, Sales Order | custom transaction | Live catalogue/cart and Draft Sales Order | Item/Customer/Sales Order | Build/source regression | Full POS remains POS Awesome |
| `/pos` | POS Profile and POS Awesome | safe integration | Assigned profile context and controlled launcher | POS Profile + POS Awesome assignment | Automated gating | No active assigned profile for Administrator on test site |

## Entity routes

Each base route below also registers `/new`, `/:encoded-name` and
`/:encoded-name/edit`. Tree bases render a hierarchy and use the same generated
form/detail engine for permitted maintenance.

| Base route | ERPNext feature | Type | L/D/F | Actions | Print/PDF | Test/classification | Remaining limitation |
|---|---|---|---|---|---|---|---|
| `/sales/customers` | Customer | handcrafted | Y/Y/Y | Existing custom CRUD | Existing support | Existing regression | Advanced contact/address management |
| `/inventory/products` | Item | handcrafted | Y/Y/Y | Existing custom CRUD/pricing | Existing support | Existing regression | Advanced stock/price operations |
| `/sales/orders` | Sales Order | handcrafted transaction | Y/Y/Y | Lifecycle and official mappings | Existing support | Existing lifecycle suite | Remaining advanced mappings |
| `/sales/delivery-notes` | Delivery Note | handcrafted transaction | Y/Y/Y | Lifecycle and mappings | Existing support | Existing lifecycle suite | Serial/batch interactive edge cases |
| `/sales/invoices` | Sales Invoice | handcrafted transaction | Y/Y/Y | Lifecycle and payment mapping | Existing support | Existing lifecycle suite | Outbound email/browser matrix |
| `/finance/payments` | Payment Entry | handcrafted transaction | Y/Y/Y | Lifecycle and allocation | Existing support | Existing lifecycle suite | Bank reconciliation separate |
| `/sales/quotations` | Quotation | generated transaction | Y/Y/Y | Submit/cancel/amend, SO/SI mappings | Shared Print Preview; PDF dependency | Provisional/API | ERPNext client-only pricing UX not adapted |
| `/purchases/suppliers` | Supplier | generated master | Y/Y/Y | CRUD/duplicate/rename/hold | Shared | Provisional/API | Per-feature browser graduation |
| `/purchases/supplier-groups` | Supplier Group | generated tree | Y/Y/Y | CRUD/duplicate/rename | Shared | Provisional/API | Tree drag/reparent not implemented |
| `/purchases/material-requests` | Material Request | generated transaction | Y/Y/Y | Submit/cancel/amend/stop/reopen, RFQ/PO mappings | Shared | Provisional/API | Purpose-specific client affordances |
| `/purchases/requests-for-quotation` | Request for Quotation | generated transaction | Y/Y/Y | Submit/cancel/amend, Supplier Quotation mapping | Shared | Provisional/API | Email-to-suppliers adapter pending |
| `/purchases/supplier-quotations` | Supplier Quotation | generated transaction | Y/Y/Y | Submit/cancel/amend, PO mapping | Shared | Provisional/API | Comparison view pending |
| `/purchases/orders` | Purchase Order | generated transaction | Y/Y/Y | Submit/cancel/amend/hold/close/reopen, PR/PI mappings | Shared | Provisional/API | Controller edge-case browser suite |
| `/purchases/receipts` | Purchase Receipt | generated transaction | Y/Y/Y | Submit/cancel/amend, PI mapping | Shared | Provisional/API | Serial/batch and return UX specialised |
| `/purchases/invoices` | Purchase Invoice | generated transaction | Y/Y/Y | Submit/cancel/amend, Payment Entry mapping | Shared | Provisional/API | Advances/returns specialised |
| `/inventory/item-groups` | Item Group | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | Tree reparent pending |
| `/inventory/brands` | Brand | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/inventory/warehouses` | Warehouse | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | Company tree browser matrix |
| `/inventory/item-prices` | Item Price | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | Pricing-rule tools separate |
| `/inventory/price-lists` | Price List | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/inventory/uoms` | UOM | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/inventory/stock-entries` | Stock Entry | generated transaction | Y/Y/Y | Submit/cancel/amend | Shared | Provisional/API | Purpose/serial-batch specialised UX needed |
| `/inventory/reconciliations` | Stock Reconciliation | generated specialised | Y/Y/Y | Standard save/submit/cancel | Shared | Specialised provisional | Scan/upload and valuation review adapter |
| `/inventory/serial-numbers` | Serial No | generated record | Y/Y/Y | Permission-approved standard actions | Shared | Provisional/API | Bundle interaction separate |
| `/inventory/batches` | Batch | generated record | Y/Y/Y | Permission-approved standard actions | Shared | Provisional/API | Bundle interaction separate |
| `/finance/chart-of-accounts` | Account | tree adapter | Y/Y/Y | Permission-approved maintenance | Shared | Provisional/API | Accounting tree-specific actions pending |
| `/finance/journal-entries` | Journal Entry | generated transaction | Y/Y/Y | Submit/cancel/amend | Shared | Provisional/API | Dedicated debit/credit balancing UX needed |
| `/finance/payment-requests` | Payment Request | generated transaction | Y/Y/Y | Standard lifecycle | Shared | Provisional/API | Gateway-specific actions pending |
| `/finance/cost-centers` | Cost Center | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | Tree reparent pending |
| `/finance/modes-of-payment` | Mode of Payment | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/crm/leads` | Lead | generated CRM | Y/Y/Y | CRUD, Opportunity/Customer conversions | Shared | Provisional/API | Conversion dialogs use generic parameters |
| `/crm/opportunities` | Opportunity | generated CRM | Y/Y/Y | CRUD, close/reopen, Quotation/Customer mappings | Shared | Provisional/API | Lost-reason specialised dialog pending |
| `/crm/contacts` | Contact | generated master | Y/Y/Y | CRUD/collaboration | Shared | Provisional/API | — |
| `/crm/addresses` | Address | generated master | Y/Y/Y | CRUD/dynamic links | Shared | Provisional/API | Map display specialised |
| `/crm/campaigns` | Campaign | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | Campaign analytics separate |
| `/crm/appointments` | Appointment | generated record | Y/Y/Y | CRUD | Shared | Provisional/API | Calendar adapter pending |
| `/crm/territories` | Territory | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | Tree reparent pending |
| `/crm/customer-groups` | Customer Group | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | Tree reparent pending |
| `/crm/sales-people` | Sales Person | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | Allocation visualisation pending |
| `/operations/projects` | Project | generated record | Y/Y/Y | CRUD/collaboration | Shared | Provisional/API | Gantt/Kanban specialised views pending |
| `/operations/tasks` | Task | generated specialised | Y/Y/Y | CRUD/collaboration | Shared | Specialised provisional | Dependency/tree visual adapter pending |
| `/operations/assets` | Asset | generated record | Y/Y/Y | Standard lifecycle actions returned by server | Shared | Provisional/API | Asset-specific transactions pending |
| `/operations/asset-movements` | Asset Movement | generated transaction | Y/Y/Y | Submit/cancel/amend | Shared | Provisional/API | Dedicated movement flow pending |
| `/operations/quality-inspections` | Quality Inspection | generated transaction | Y/Y/Y | Submit/cancel/amend | Shared | Provisional/API | Reading-entry specialised UI pending |
| `/operations/support/issues` | Issue | generated collaboration | Y/Y/Y | CRUD/comments/assignments/files | Shared | Provisional/API | SLA dashboard pending |
| `/operations/departments` | Department | generated tree | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/operations/designations` | Designation | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/operations/manufacturing/boms` | BOM | generated specialised | Y/Y/Y | Safe standard lifecycle only | Shared | Specialised provisional | BOM explosion/cost/update tools pending |
| `/operations/manufacturing/production-plans` | Production Plan | generated specialised | Y/Y/Y | Safe standard lifecycle only | Shared | Specialised provisional | Planning/mapping adapter pending |
| `/operations/manufacturing/work-orders` | Work Order | generated specialised | Y/Y/Y | Safe standard lifecycle only | Shared | Specialised provisional | Production/transfer action adapter pending |
| `/operations/manufacturing/job-cards` | Job Card | generated specialised | Y/Y/Y | Safe standard lifecycle only | Shared | Specialised provisional | Time-log/completion adapter pending |
| `/operations/manufacturing/operations` | Operation | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/operations/manufacturing/workstations` | Workstation | generated master | Y/Y/Y | CRUD | Shared | Provisional/API | — |
| `/operations/subcontracting/orders` | Subcontracting Order | generated specialised | Y/Y/Y | Safe standard lifecycle only | Shared | Specialised provisional | Supply/receipt mappings pending |
| `/operations/subcontracting/receipts` | Subcontracting Receipt | generated specialised | Y/Y/Y | Safe standard lifecycle only | Shared | Specialised provisional | Serial/batch and return flow pending |
| `/admin/users` | User | restricted generated admin | Y/Y/Y | Standard permission-checked save | Shared | Provisional/API | Dedicated account safety UX pending |
| `/admin/roles` | Role | restricted generated admin | Y/Y/Y | Standard permission-checked save | Shared | Provisional/API | — |
| `/admin/companies` | Company | restricted generated admin | Y/Y/Y | Standard permission-checked save | Shared | Provisional/API | Company setup wizard not reproduced |
| `/admin/warehouses` | Warehouse | restricted tree alias | Y/Y/Y | Standard permission-checked save | Shared | Provisional/API | — |
| `/admin/price-lists` | Price List | restricted generated admin | Y/Y/Y | Standard permission-checked save | Shared | Provisional/API | — |

## Purpose, report and specialised routes

| Route | Adapter | Working scope | Classification/limitation |
|---|---|---|---|
| `/inventory/transfers/new` | Stock Entry form | Server-owned Material Transfer default | Transaction provisional |
| `/inventory/receipts/new` | Stock Entry form | Server-owned Material Receipt default | Transaction provisional |
| `/inventory/issues/new` | Stock Entry form | Server-owned Material Issue default | Transaction provisional |
| `/inventory/reorder-alerts` | Stock Projected Qty | Permission-checked report alias | Report provisional |
| `/finance/payment-reconciliation` | Payment Reconciliation | Permission-filtered safe context | Specialised interaction pending |
| `/finance/bank-reconciliation` | Bank Reconciliation Tool | Permission-filtered safe context | Specialised interaction pending |
| `/crm/customers` | Customer | Internal alias to handcrafted Customer page | Working alias |
| `/operations/manufacturing` | Manufacturing DocTypes | Permitted recent records and links | Specialised launch dashboard provisional |
| `/operations/subcontracting` | Subcontracting DocTypes | Permitted recent records and links | Specialised launch dashboard provisional |
| `/admin/permissions` | DocPerm metadata | Bounded read-only priority-role matrix | Mutation remains controlled by User/Role forms |
| `/admin/settings` | System Settings | Safe read-only context | Dedicated safe settings editor pending |
| `/admin/integrations` | OAuth Client/Connected App | Safe permitted recent records | Secrets never returned; configuration UX pending |
| `/admin/website` | Website Settings/Web Page | Safe permitted context | Full website builder pending |
| `/admin/system-health` | RQ Job/Error Log/apps | Safe aggregate facts | No payloads, traceback contents or config secrets |
| `/admin/background-jobs` | RQ Job/Error Log | Safe aggregate facts | Job control intentionally not exposed |

Report group routes are `/reports/{sales|purchases|inventory|finance|crm|operations}`.
The viewer route is `/reports/view/:encoded-report-name`. Twenty-six of the 27
allowlisted priority reports are installed and permission-discoverable;
`CRM Analytics` is absent from this site. The viewer calls the installed
Frappe Query/Script Report engine, supports allowlisted filters, formatted rows,
charts, totals, permission-filtered voucher links, CSV export and browser Print
Preview. `Stock Balance` reports prepared-report capability. `wkhtmltopdf` is
not installed, so protected PDF output cannot be verified and is never claimed.

## Navigation and search

The server-filtered header contains Home, Smart Sales, Sales, Purchases,
Inventory, Finance, CRM, Operations, Reports, POS and Admin only when the
current session is allowed to see them. Desktop menus use a compact two-column
dropdown for long modules; the mobile drawer uses the same server response.
There are no raw `/generated/*` links in normal navigation.

Global search now covers allowlisted customer, supplier, item, sales,
purchasing, payment, journal, stock, CRM, project, asset, support, manufacturing
and restricted User records. It uses debounced permission-aware `get_list`
queries and routes results only to clean Retail ERP URLs.

## Security and testing notes

- Guest API access is rejected.
- Route visibility never grants document or action permission.
- Lists use permission-aware `frappe.get_list`; document APIs use document-level checks.
- Dynamic Links validate both the controlling DocType and target document.
- Mapping requests accept symbolic registered actions only. Fixed adapters call
  installed ERPNext mapping helpers and insert the returned Draft through the
  normal controller.
- No core app was changed and no schema, migration, restart or site configuration change occurred.
- Automated coverage is representative and deep at the shared adapter layer;
  it is not a claim that every provisional feature completed its full browser workflow.

