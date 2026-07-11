# Retail ERP frontend feature matrix

Last audited: 2026-07-11<br>
Target: ERPNext/Frappe v15 on `site1.local`<br>
Frontend app: `my_store_ui`

## Status and completion policy

This matrix is a development contract, not a completion claim. A feature may be marked **Complete** only after:

1. its custom route works without sending an ordinary user to a standard Workspace, List, or Form;
2. server-side read/write/create/submit/cancel/amend/print/report permissions are verified as applicable;
3. ERPNext validation, workflow, stock, accounting, and mapping logic remains authoritative;
4. desktop and mobile behavior is tested;
5. automated tests and a manual test record exist; and
6. its remaining Standard Desk dependency is `None` for ordinary users.

Current status values:

- **Foundation**: the shared Vue shell and placeholder route exist; business functionality does not.
- **Not started**: no custom working page exists.
- **Partial legacy**: functionality exists outside the SPA and is not the target implementation.

Engine classifications:

- **G** — generic metadata/schema-driven entity engine.
- **T** — transactional document engine with approved schema and child rows.
- **S** — specialized page/workflow.
- **R** — standard ERPNext report adapter.
- **L** — permission-aware launcher/dashboard.
- **A** — restricted administration page.

`L/D/F` means custom List, Detail, and Form support respectively.

## Current implementation audit

- `/app/retail-erp/*` is one Vue 3 SPA with a shared shell.
- Ten module routes exist; three approved pilot list routes now use the shared `EntityListPage.vue` engine.
- Header search, notifications, user menu, toast host, and confirm host are placeholders.
- Server-owned, permission-aware read-only list and detail registries exist for Customer, Item, and Sales Order. Detail pages include approved sections, summary cards, child rows, related summaries and activity metadata; forms, functional print, reports and document actions do not exist yet.
- `/app/smart-sales` is a separate legacy Desk Page. It can browse products and create a Draft Sales Order, but it is not inside the SPA and does not implement the complete sales workflow.
- No login landing or ordinary-user Desk route guard exists.
- All standard document work still depends on ERPNext Desk.

## Role-based feature inventory

Visibility is an initial navigation expectation only. The backend must evaluate current DocPerm, User Permission, sharing, workflow, company, and document-level rules on every request.

| Role/persona | Primary custom area | Expected features | Standard Desk target |
|---|---|---|---|
| Administrator | `/admin` and all modules | All permitted records, setup, developer and recovery tools | Allowed |
| System Manager | `/home` and `/admin` | Administration, configuration, audit, all role-permitted modules | Allowed |
| Sales Manager | `/smart-sales` | CRM, customers, quotations, orders, delivery, invoices, sales reports | Not required for daily work |
| Sales User | `/smart-sales` | Customers, quotations, orders, delivery/invoice actions granted by DocPerm | Not required for daily work |
| POS Manager / POS User | `/smart-sales` | Smart Sales and POS Awesome integration where permitted | Not required for daily work |
| Stock Manager | `/inventory` | Items, warehouses, stock documents, reconciliation, stock reports | Not required for daily work |
| Stock User | `/inventory` | Stock operations and read-only linked purchasing/selling records per DocPerm | Not required for daily work |
| Purchase Manager | `/purchases` | Suppliers, requests, quotations, orders, receipts, invoices/reports as permitted | Not required for daily work |
| Purchase User | `/purchases` | Purchase transaction workflow granted by DocPerm | Not required for daily work |
| Accounts Manager | `/finance` | Journal/payment entries, invoices, accounting reports and controls | Not required for daily work |
| Accounts User | `/finance` | Accounting documents/reports granted by DocPerm | Not required for daily work |
| Projects Manager / Projects User | `/operations` | Projects, tasks, related time/activity views | Not required for daily work |
| Manufacturing roles | `/operations` | BOM, Production Plan, Work Order, Job Card, quality links | Not required for daily work |
| Support Team | `/operations` | Issues, assignments, communication and support activity | Not required for daily work |
| Other Desk users | `/home` | Only modules and actions proven by server permissions | Not required for daily work |

### Permission enforcement contract

- Lists use permission-aware `frappe.get_list`, never unrestricted `frappe.get_all` for user-visible records.
- Detail reads require `frappe.has_permission(doctype, "read", doc=name)` or document `check_permission`.
- Create/write/submit/cancel/amend/print/export/report actions are returned by the server for the specific document and checked again when invoked.
- User Permissions, shared documents, match conditions, workflows, field permission levels, company access, and disabled records remain effective.
- The browser never promotes an action merely because a role name appears in this matrix.

## Route conventions

| Page type | Route pattern |
|---|---|
| Module dashboard | `/app/retail-erp/{module}` |
| Entity list | `/app/retail-erp/{module}/{entity}` |
| New entity | `/app/retail-erp/{module}/{entity}/new` |
| Entity detail | `/app/retail-erp/{module}/{entity}/{encoded-name}` |
| Draft edit | `/app/retail-erp/{module}/{entity}/{encoded-name}/edit` |
| Report launcher | `/app/retail-erp/reports/{group}` |
| Report viewer | `/app/retail-erp/reports/view/{encoded-report-name}` |

Document names must be URL-encoded. Route definitions must carry an approved frontend schema key, not accept an arbitrary DocType from the URL.

## Complete feature and route inventory

| Module | Feature | ERPNext backend | Custom route | Engine | L/D/F | Required actions | Permission source | Print/PDF | Mobile | Tests | Status | Standard Desk dependency |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Shared | Read-only entity list engine | Approved DocTypes only | Approved entity routes | G | Y/N/N | Search, allowlisted filters/sort, pagination, refresh, row navigation | Server schema + `frappe.has_permission` + `frappe.get_list` | No | Verified table/cards | 6 automated + browser/API | Complete (list scope only) | None for implemented lists |
| Shared | Read-only entity detail engine | Approved DocTypes only | Approved detail routes | G | N/Y/N | Approved summary/sections, refresh, activity metadata, safe admin fallback | Doctype + document permission and permission-aware existence check | Placeholder only | Verified responsive layout | Automated/API/browser | Complete (read-only scope) | None for implemented detail reads |
| Shared | Read-only child-table display | Approved child DocTypes | Detail sections | G | N/Y/N | Approved columns, formatting, row count, desktop/mobile rendering | Parent document read plus server schema | No | Verified table/cards | Sales Order items/taxes tests | Complete (display only) | None for approved child rows |
| Shared | Related-document summaries | Approved related DocTypes | Detail sections | G | N/Y/N | Permission-filtered count up to cap and five recent records | Related DocType `read` + `frappe.get_list` | No | Verified cards | API/browser permission tests | Complete (summary only) | Custom detail routes unavailable for most related types |
| Shared | Home dashboard | Aggregated permitted DocTypes/reports | `/home` | L | N/A | Metrics, alerts, quick actions, recent records | Per metric/DocType | No | Planned | None | Foundation | Yes: placeholder only |
| Shared | Global search | Global Search plus approved DocTypes | Header overlay | S | N/A | Grouped search, keyboard open | Per result DocType/read | No | Planned | None | Not started | Yes |
| Shared | Comments/activity | Communication, Comment, Version | Detail panel | G | N/A | Read/add comments, timeline | Parent document permissions | No | Planned | None | Not started | Yes |
| Shared | Attachments | File | Detail/form panel | G | N/A | List/upload/remove/download | Parent and File permissions | No | Planned | None | Not started | Yes |
| Shared | Assignments | ToDo/assignment APIs | Detail panel | G | N/A | Assign/unassign/read | Parent and assignment permission | No | Planned | None | Not started | Yes |
| Sales | Smart Sales | Customer, Item, Item Price, Bin, Sales Order, Sales Invoice | `/smart-sales` | S | Custom | Cart, SO/SI state workflow, payment links | Each source/action | Invoice only | Planned | None | Partial legacy | Yes: legacy page and standard forms |
| Sales | Customers | Customer, Contact, Address | `/sales/customers` | G | Y/Y/Y | CRUD, contacts, addresses, transactions, balances | Customer + financial report permission | Optional | List/detail verified | API/browser detail tests | List and read-only detail complete; form not started | Yes: create/edit, full contacts/addresses, balances/activity |
| Sales | Quotations | Quotation | `/sales/quotations` | T | Y/Y/Y | Draft edit, submit/cancel/amend, map to SO, print | Quotation action permissions | Yes | Planned | None | Not started | Yes |
| Sales | Sales Orders | Sales Order | `/sales/orders` | T | Y/Y/Y | Draft edit, submit/cancel/amend, map DN/SI, status | Sales Order action permissions | Yes | List/detail verified | API/browser detail + child rows | List and read-only detail complete; form/actions not started | Yes: editing, print and all document actions |
| Sales | Delivery Notes | Delivery Note | `/sales/delivery-notes` | T | Y/Y/Y | Map from SO, stock validation, submit/cancel/amend, map SI | Delivery Note + stock permissions | Yes | Planned | None | Not started | Yes |
| Sales | Sales Invoices | Sales Invoice | `/sales/invoices` | T | Y/Y/Y | Map from SO/DN, submit/cancel/amend, payment, print | Sales Invoice + Accounts permissions | Yes | Planned | None | Not started | Yes |
| Sales | Payment Entries | Payment Entry | `/sales/payments` | T | Y/Y/Y | Allocate references, save, submit/cancel/amend | Payment Entry permissions | Yes | Planned | None | Not started | Yes |
| Sales reports | Sales Register | Report: Sales Register | `/reports/view/Sales%20Register` | R | N/A | Filters, run, totals, export, print | Report + Sales Invoice | Yes | Planned | None | Not started | Yes |
| Sales reports | Sales Order Analysis | Report: Sales Order Analysis | `/reports/view/Sales%20Order%20Analysis` | R | N/A | Filters, run, export | Report + Sales Order | Yes | Planned | None | Not started | Yes |
| Sales reports | Customer balances | Report: Customer Ledger Summary | `/reports/view/Customer%20Ledger%20Summary` | R | N/A | Filters, run, totals, export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Sales reports | Item-wise sales | Report: Item-wise Sales Register | `/reports/view/Item-wise%20Sales%20Register` | R | N/A | Filters, run, totals, export | Report + Sales Invoice | Yes | Planned | None | Not started | Yes |
| Sales reports | Sales analytics | Report: Sales Analytics | `/reports/view/Sales%20Analytics` | R | N/A | Tree/chart filters, run, export | Report + Sales Order | Yes | Planned | None | Not started | Yes |
| Purchases | Suppliers | Supplier, Contact, Address | `/purchases/suppliers` | G | Y/Y/Y | CRUD, contacts, addresses, transactions, balances | Supplier + financial report permission | Optional | Planned | None | Not started | Yes |
| Purchases | Material Requests | Material Request | `/purchases/material-requests` | T | Y/Y/Y | Draft edit, submit/cancel/amend, map RFQ/PO | Material Request permissions | Yes | Planned | None | Not started | Yes |
| Purchases | Requests for Quotation | Request for Quotation | `/purchases/requests-for-quotation` | T | Y/Y/Y | Suppliers, submit/cancel/amend, supplier response links | RFQ permissions | Yes | Planned | None | Not started | Yes |
| Purchases | Supplier Quotations | Supplier Quotation | `/purchases/supplier-quotations` | T | Y/Y/Y | Draft edit, submit/cancel/amend, map PO | Supplier Quotation permissions | Yes | Planned | None | Not started | Yes |
| Purchases | Purchase Orders | Purchase Order | `/purchases/orders` | T | Y/Y/Y | Draft edit, submit/cancel/amend, map PR/PI | Purchase Order permissions | Yes | Planned | None | Not started | Yes |
| Purchases | Purchase Receipts | Purchase Receipt | `/purchases/receipts` | T | Y/Y/Y | Map PO, stock validation, submit/cancel/amend, map PI | Purchase Receipt + stock permissions | Yes | Planned | None | Not started | Yes |
| Purchases | Purchase Invoices | Purchase Invoice | `/purchases/invoices` | T | Y/Y/Y | Map PO/PR, submit/cancel/amend, payment | Purchase Invoice + Accounts permissions | Yes | Planned | None | Not started | Yes |
| Purchase reports | Purchase Register | Report: Purchase Register | `/reports/view/Purchase%20Register` | R | N/A | Filters, totals, export, print | Report + Purchase Invoice | Yes | Planned | None | Not started | Yes |
| Purchase reports | Purchase Order Analysis | Report: Purchase Order Analysis | `/reports/view/Purchase%20Order%20Analysis` | R | N/A | Filters, run, export | Report + Purchase Order | Yes | Planned | None | Not started | Yes |
| Purchase reports | Supplier balances | Report: Supplier Ledger Summary | `/reports/view/Supplier%20Ledger%20Summary` | R | N/A | Filters, totals, export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Purchase reports | Item-wise purchasing | Report: Item-wise Purchase Register | `/reports/view/Item-wise%20Purchase%20Register` | R | N/A | Filters, totals, export | Report + Purchase Invoice | Yes | Planned | None | Not started | Yes |
| Inventory | Products | Item | `/inventory/products` | G | Y/Y/Y | Search, CRUD, disable, stock/prices/transactions | Item permissions plus related sources | Optional | List/detail verified | API/browser detail tests | List and read-only detail complete; form not started | Yes: create/edit and complete stock/price transaction views |
| Inventory | New Product | Item, Item Price, Barcode, stock documents | `/inventory/products/new` | S | N/N/Y | Pricing, SKU, image, Item Prices, opening stock | Item/Item Price/stock create permissions | No | Planned | None | Not started | Yes |
| Inventory | Item Groups | Item Group tree | `/inventory/item-groups` | G | Y/Y/Y | Tree read/create/edit | Item Group permissions | No | Planned | None | Not started | Yes |
| Inventory | Brands | Brand | `/inventory/brands` | G | Y/Y/Y | CRUD | Brand permissions | No | Planned | None | Not started | Yes |
| Inventory | Warehouses | Warehouse tree | `/inventory/warehouses` | G | Y/Y/Y | Tree read/create/edit/disable | Warehouse permissions/company scope | Optional | Planned | None | Not started | Yes |
| Inventory | Item Prices | Item Price | `/inventory/item-prices` | G | Y/Y/Y | Search, validity/UOM pricing CRUD | Item Price permissions | No | Planned | None | Not started | Yes |
| Inventory | Stock Entries | Stock Entry | `/inventory/stock-entries` | T | Y/Y/Y | Draft edit, purpose-specific rows, submit/cancel/amend | Stock Entry permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Material Transfer | Stock Entry purpose | `/inventory/transfers/new` | S/T | N/Y/Y | Source/target warehouses, items, submit | Stock Entry permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Material Receipt | Stock Entry purpose | `/inventory/receipts/new` | S/T | N/Y/Y | Target warehouse, valuation, submit | Stock Entry permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Material Issue | Stock Entry purpose | `/inventory/issues/new` | S/T | N/Y/Y | Source warehouse, items, submit | Stock Entry permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Stock Reconciliation | Stock Reconciliation | `/inventory/reconciliations` | S/T | Y/Y/Y | Items, quantities, valuation, submit/cancel | Stock Reconciliation permissions | Optional | Planned | None | Not started | Yes |
| Inventory | Stock Balance | Report: Stock Balance | `/reports/view/Stock%20Balance` | R | N/A | Filters, totals, export | Report + stock permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Stock Ledger | Report: Stock Ledger | `/reports/view/Stock%20Ledger` | R | N/A | Filters, running balance, export | Report + stock permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Stock Analytics | Report: Stock Analytics | `/reports/view/Stock%20Analytics` | R | N/A | Filters, tree/chart, export | Report + stock permissions | Yes | Planned | None | Not started | Yes |
| Inventory | Serial Numbers | Serial No | `/inventory/serial-numbers` | G | Y/Y/Restricted | Search, detail, linked transactions | Serial No permissions | Optional | Planned | None | Not started | Yes |
| Inventory | Batches | Batch | `/inventory/batches` | G | Y/Y/Restricted | Search, detail, stock/expiry links | Batch permissions | Optional | Planned | None | Not started | Yes |
| Inventory | Reorder alerts | Item Reorder/Bin/Material Request | `/inventory/reorder-alerts` | S | N/A | Alerts, suggested MR action | Item/Bin/MR permissions | No | Planned | None | Not started | Yes |
| Inventory | Price Lists | Price List | `/inventory/price-lists` | G/A | Y/Y/Y | Read/edit permitted lists | Price List permissions | No | Planned | None | Not started | Yes |
| Finance | Finance dashboard | Permitted accounting reports | `/finance` | L | N/A | KPIs, receivables/payables summaries | Per report and company | No | Planned | None | Foundation | Yes: placeholder only |
| Finance | Chart of Accounts | Account tree | `/finance/chart-of-accounts` | S | N/A | Tree browse and permitted maintenance | Account permissions/company | Optional | Planned | None | Not started | Yes |
| Finance | Journal Entries | Journal Entry | `/finance/journal-entries` | T | Y/Y/Y | Accounts rows, save, submit/cancel/amend | Journal Entry permissions | Yes | Planned | None | Not started | Yes |
| Finance | Payment Entries | Payment Entry | `/finance/payment-entries` | T | Y/Y/Y | References, allocations, submit/cancel/amend | Payment Entry permissions | Yes | Planned | None | Not started | Yes |
| Finance | Bank Reconciliation | Bank Transaction/Bank Reconciliation Tool | `/finance/bank-reconciliation` | S | N/A | Fetch, match, reconcile | Bank/account permissions | Optional | Planned | None | Not started | Yes |
| Finance | Accounts Receivable | Report: Accounts Receivable | `/reports/view/Accounts%20Receivable` | R | N/A | Filters, aging, totals, export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | Accounts Payable | Report: Accounts Payable | `/reports/view/Accounts%20Payable` | R | N/A | Filters, aging, totals, export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | General Ledger | Report: General Ledger | `/reports/view/General%20Ledger` | R | N/A | Filters, totals, linked vouchers | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | Trial Balance | Report: Trial Balance | `/reports/view/Trial%20Balance` | R | N/A | Filters, totals, tree/export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | Profit and Loss | Report: Profit and Loss Statement | `/reports/view/Profit%20and%20Loss%20Statement` | R | N/A | Period filters, totals, chart/export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | Balance Sheet | Report: Balance Sheet | `/reports/view/Balance%20Sheet` | R | N/A | Period filters, totals, chart/export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | Cash Flow | Report: Cash Flow | `/reports/view/Cash%20Flow` | R | N/A | Period filters, totals, export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| Finance | Bank statement | Report: Bank Reconciliation Statement | `/reports/view/Bank%20Reconciliation%20Statement` | R | N/A | Filters, totals, export | Report + financial permissions | Yes | Planned | None | Not started | Yes |
| CRM | Leads | Lead | `/crm/leads` | G | Y/Y/Y | CRUD, status, activities, conversion actions | Lead permissions | Optional | Planned | None | Not started | Yes |
| CRM | Opportunities | Opportunity | `/crm/opportunities` | G/S | Y/Y/Y | CRUD, status, activities, map quotation/customer | Opportunity + target permissions | Optional | Planned | None | Not started | Yes |
| CRM | Customers | Customer | `/crm/customers` | G | Y/Y/Y | Shared customer engine | Customer permissions | Optional | Planned | None | Not started | Yes |
| CRM | Contacts | Contact | `/crm/contacts` | G | Y/Y/Y | CRUD, dynamic links, communication | Contact permissions | Optional | Planned | None | Not started | Yes |
| CRM | Addresses | Address | `/crm/addresses` | G | Y/Y/Y | CRUD, dynamic links | Address permissions | Optional | Planned | None | Not started | Yes |
| CRM | Campaigns | Campaign | `/crm/campaigns` | G | Y/Y/Y | CRUD, linked leads/opportunities | Campaign permissions | Optional | Planned | None | Not started | Yes |
| CRM | Appointments | Appointment | `/crm/appointments` | G | Y/Y/Y | CRUD, date/status | Appointment permissions | Optional | Planned | None | Not started | Yes |
| CRM | CRM reports | Permitted CRM reports | `/reports/crm` | R/L | N/A | Discover/run permitted reports | Report and ref DocType | Yes | Planned | None | Not started | Yes |
| Operations | Assets | Asset | `/operations/assets` | T/G | Y/Y/Y | CRUD, submit/cancel/amend, related movements | Asset permissions | Yes | Planned | None | Not started | Yes |
| Operations | Asset Movements | Asset Movement | `/operations/asset-movements` | T | Y/Y/Y | Draft, submit/cancel, asset rows | Asset Movement permissions | Yes | Planned | None | Not started | Yes |
| Operations | Manufacturing dashboard | Manufacturing DocTypes/reports | `/operations/manufacturing` | L | N/A | Alerts and launchers | Per source | No | Planned | None | Not started | Yes |
| Operations | Bills of Materials | BOM | `/operations/manufacturing/boms` | S/T | Y/Y/Y | Items/operations, submit/cancel/amend | BOM permissions | Yes | Planned | None | Not started | Yes |
| Operations | Production Plans | Production Plan | `/operations/manufacturing/production-plans` | S/T | Y/Y/Y | Plan rows, submit, create work/material actions | Production Plan permissions | Yes | Planned | None | Not started | Yes |
| Operations | Work Orders | Work Order | `/operations/manufacturing/work-orders` | S/T | Y/Y/Y | Submit/status/material/job-card actions | Work Order permissions | Yes | Planned | None | Not started | Yes |
| Operations | Job Cards | Job Card | `/operations/manufacturing/job-cards` | S/T | Y/Y/Y | Time logs, quantities, submit/status | Job Card permissions | Yes | Planned | None | Not started | Yes |
| Operations | Subcontracting | Subcontracting Order/Receipt | `/operations/subcontracting` | S/T | Y/Y/Y | Standard subcontracting document workflow | Respective DocPerm | Yes | Planned | None | Not started | Yes |
| Operations | Quality Inspections | Quality Inspection | `/operations/quality-inspections` | T | Y/Y/Y | Reference document, readings, submit/cancel | Quality Inspection permissions | Yes | Planned | None | Not started | Yes |
| Operations | Projects | Project | `/operations/projects` | G | Y/Y/Y | CRUD, status, tasks, transactions | Project permissions | Optional | Planned | None | Not started | Yes |
| Operations | Tasks | Task tree | `/operations/tasks` | G/S | Y/Y/Y | CRUD, dependencies, status, assignments | Task permissions | Optional | Planned | None | Not started | Yes |
| Operations | Support Issues | Issue | `/operations/support/issues` | G/S | Y/Y/Y | CRUD, status, communication, assignment | Issue permissions | Optional | Planned | None | Not started | Yes |
| Reports | Reports hub | All approved standard reports | `/reports` | L/R | N/A | Discover only permitted report groups | Report permissions | N/A | Planned | None | Foundation | Yes: placeholder only |
| Reports | Sales launcher | Standard sales reports | `/reports/sales` | L/R | N/A | Discover only permitted reports | Report permissions | N/A | Planned | None | Not started | Yes |
| Reports | Purchase launcher | Standard purchase reports | `/reports/purchases` | L/R | N/A | Discover only permitted reports | Report permissions | N/A | Planned | None | Not started | Yes |
| Reports | Inventory launcher | Standard stock reports | `/reports/inventory` | L/R | N/A | Discover only permitted reports | Report permissions | N/A | Planned | None | Not started | Yes |
| Reports | Finance launcher | Standard accounting reports | `/reports/finance` | L/R | N/A | Discover only permitted reports | Report permissions | N/A | Planned | None | Not started | Yes |
| Reports | CRM launcher | Standard CRM reports | `/reports/crm` | L/R | N/A | Discover only permitted reports | Report permissions | N/A | Planned | None | Not started | Yes |
| Reports | Operations launcher | Standard operational reports | `/reports/operations` | L/R | N/A | Discover only permitted reports | Report permissions | N/A | Planned | None | Not started | Yes |
| Admin | Users | User | `/admin/users` | A/G | Y/Y/Y | CRUD/enable/disable/roles as permitted | User permissions | Optional | Planned | None | Not started | Yes |
| Admin | Roles | Role | `/admin/roles` | A/G | Y/Y/Y | CRUD as permitted | Role permissions | Optional | Planned | None | Not started | Yes |
| Admin | Role Permissions | DocPerm/Custom DocPerm APIs | `/admin/permissions` | A/S | N/A | Permission management | System Manager/admin checks | No | Planned | None | Not started | Yes |
| Admin | Companies | Company tree | `/admin/companies` | A/G | Y/Y/Y | CRUD/configuration | Company permissions | Optional | Planned | None | Not started | Yes |
| Admin | Warehouses | Warehouse tree | `/admin/warehouses` | A/G | Y/Y/Y | Administration view | Warehouse permissions | Optional | Planned | None | Not started | Yes |
| Admin | Price Lists | Price List | `/admin/price-lists` | A/G | Y/Y/Y | Configuration | Price List permissions | No | Planned | None | Not started | Yes |
| Admin | Retail settings | Retail ERP Frontend Settings | `/admin/settings` | A/S | N/Y/Y | Frontend configuration/landing rules | System Manager only | No | Planned | None | Not started | Settings DocType not created |
| Admin | Integrations | Integration DocTypes | `/admin/integrations` | A/L | N/A | Permission-aware launchers | Respective setup permissions | No | Planned | None | Not started | Yes |
| Admin | Website | Website settings/content | `/admin/website` | A/L | N/A | Permission-aware launchers | Website Manager/System Manager | Optional | Planned | None | Not started | Yes |
| Admin | System health | System Health/monitoring APIs | `/admin/system-health` | A/S | N/A | Read health and diagnostics | System Manager/admin | No | Planned | None | Not started | Yes |
| Admin | Background jobs | RQ/Background Jobs views | `/admin/background-jobs` | A/S | N/A | Read/retry only where supported | System Manager/admin | No | Planned | None | Not started | Yes |
| Admin | Standard Desk fallback | Frappe Desk | `/app` external fallback | A | N/A | Open fallback | Administrator/System Manager only | N/A | Desktop | None | Existing | Target: admin-only |

## Official ERPNext mappings that must remain authoritative

The custom frontend should wrap these standard controller methods with explicit source/target permission and document-state checks rather than copying rows in JavaScript.

| Source | Target | Standard mapping/controller entry point |
|---|---|---|
| Quotation | Sales Order | `erpnext.selling.doctype.quotation.quotation.make_sales_order` |
| Quotation | Sales Invoice | `erpnext.selling.doctype.quotation.quotation.make_sales_invoice` where valid |
| Sales Order | Delivery Note | `erpnext.selling.doctype.sales_order.sales_order.make_delivery_note` |
| Sales Order | Sales Invoice | `erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice` |
| Delivery Note | Sales Invoice | `erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice` |
| Sales/Purchase Invoice | Payment Entry | `erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry` |
| Material Request | Request for Quotation | standard Material Request mapping method verified at implementation time |
| Material Request | Purchase Order | `erpnext.stock.doctype.material_request.material_request.make_purchase_order` |
| Request for Quotation | Supplier Quotation | `request_for_quotation.make_supplier_quotation_from_rfq` |
| Supplier Quotation | Purchase Order | `supplier_quotation.make_purchase_order` |
| Purchase Order | Purchase Receipt | `purchase_order.make_purchase_receipt` |
| Purchase Order | Purchase Invoice | `purchase_order.make_purchase_invoice` |
| Purchase Receipt | Purchase Invoice | `purchase_receipt.make_purchase_invoice` |

Method signatures and whitelisting must be rechecked against the installed ERPNext version immediately before integration.

## Reusable architecture plan

### 1. Approved frontend schema registry

Do not accept arbitrary DocTypes from browser route parameters. Define a server-owned registry for each exposed entity:

- route key and DocType;
- permitted list columns, filters, search fields, and sort fields;
- form field allowlist, layout, conditional rules, and child-table schemas;
- detail sections, totals, links, and timeline capabilities;
- allowed workflow/mapping actions and required document states;
- supported reports and print behavior;
- mobile column/card representation.

Frappe metadata supplies labels, types, precision, defaults, `reqd`, `read_only`, `hidden`, permission level, `depends_on`, `mandatory_depends_on`, Link options, and child DocType definitions. The approved registry further restricts what is exposed.

### 2. Entity list engine

Frontend responsibilities:

- reusable search/filter/sort/date/status controls;
- URL-persisted query state;
- responsive table/mobile cards;
- selection and permission-approved bulk actions;
- pagination, loading, empty, and permission states.

Server responsibilities:

- validate schema key, filters, fields, operators, sort, and page size;
- use `frappe.get_list` with current-user permissions;
- return field definitions, permitted row actions, totals where approved, and export capability;
- reject restricted fields and expensive/unindexed searches.

### 3. Entity detail engine

Frontend responsibilities:

- schema-defined summary, status, totals, child rows, links, attachments, comments, assignments, and activity;
- render only server-returned actions;
- confirmation for submit/cancel/amend and unsaved navigation.

Server responsibilities:

- load the document with read permission;
- serialize only approved fields;
- compute actions from DocPerm, docstatus, workflow, ownership/sharing, and controller state;
- invoke standard print, mapping, submit, cancel, amend, attachment, comment, and assignment APIs.

### 4. Entity form engine

Frontend responsibilities:

- render approved Data, Link, Dynamic Link, Select, Date, Datetime, Currency, Check, Attach/Image, Text, Section/Column, and Table controls;
- apply presentation-level dependencies while treating server validation as final;
- preserve dirty-state warnings and structured server errors.

Server responsibilities:

- return defaults using standard Frappe/ERPNext helpers;
- accept only approved writable fields;
- reload the current document and reject stale/invalid state transitions;
- call `doc.insert()`, `doc.save()`, `doc.submit()`, `doc.cancel()`, or standard amendment/mapping APIs under the current user;
- never accept browser-calculated totals as authoritative.

### 5. Child-table editor

The shared grid supports approved child schemas, add/remove/reorder, Link queries, keyboard navigation, row validation, and mobile cards. Transaction controllers still recalculate item defaults, UOM conversions, warehouses, taxes, discounts, stock, accounts, and totals on the server.

### 6. Report adapter

- discover only reports the user can run;
- obtain report metadata and filters through supported Frappe report APIs;
- execute standard Script/Query Reports server-side;
- render returned columns, data, totals, charts, pagination, export, and print without recreating calculations.

## Generic reusable component candidates

Primarily generic (**G**) with approved schemas:

- Customer, Supplier, Item, Brand, Contact, Address, Campaign, Appointment;
- Lead, Project, Task, Issue;
- Item Price, Serial No, Batch;
- User, Role, Company for administrators;
- Warehouse, Item Group, Account require tree adapters but share detail/form primitives.

Transactional (**T**) pages can share one transaction framework but need explicit schemas:

- Quotation, Sales Order, Delivery Note, Sales Invoice, Payment Entry;
- Material Request, Request for Quotation, Supplier Quotation;
- Purchase Order, Purchase Receipt, Purchase Invoice;
- Stock Entry, Stock Reconciliation, Journal Entry;
- Asset Movement and Quality Inspection.

## Features requiring specialized pages

- Home and finance dashboards;
- global cross-DocType search;
- Smart Sales and its document-state workflow;
- New Product pricing, SKU, Item Price, image, and opening-stock flow;
- Chart of Accounts and other trees;
- Bank Reconciliation;
- stock transfer/receipt/issue assistants;
- Stock Reconciliation high-volume grid;
- reorder alerts and suggested Material Requests;
- report viewer and chart adapters;
- manufacturing BOM, Production Plan, Work Order, and Job Card interactions;
- Role Permission Manager;
- system health/background jobs;
- print preview/PDF selection;
- configurable role landing and ordinary-user Desk route guard.

## Proposed source files for the reusable-engine stage

No files in this section exist yet; creation requires approval.

```text
frontend/src/
├── router/entityRoutes.js
├── schemas/
│   ├── registry.js
│   ├── sales.js
│   ├── purchases.js
│   ├── inventory.js
│   ├── finance.js
│   ├── crm.js
│   └── operations.js
├── services/
│   ├── api.js
│   ├── metadata.js
│   ├── permissions.js
│   ├── documents.js
│   └── reports.js
├── stores/
│   ├── session.js
│   ├── entityList.js
│   └── document.js
├── components/entity/
│   ├── EntityListPage.vue
│   ├── EntityDetailPage.vue
│   ├── EntityFormPage.vue
│   ├── EntityTable.vue
│   ├── EntityMobileCards.vue
│   ├── FilterBar.vue
│   ├── Pagination.vue
│   └── DocumentActions.vue
├── components/forms/
│   ├── SchemaForm.vue
│   ├── SchemaField.vue
│   ├── LinkField.vue
│   ├── AttachField.vue
│   └── ChildTableEditor.vue
└── components/activity/
    ├── ActivityTimeline.vue
    ├── AttachmentPanel.vue
    ├── CommentPanel.vue
    └── AssignmentPanel.vue

my_store_ui/
├── api/
│   ├── entities.py
│   ├── metadata.py
│   ├── documents.py
│   ├── reports.py
│   ├── print.py
│   └── activity.py
├── services/
│   ├── schema_registry.py
│   ├── permissions.py
│   ├── serializers.py
│   └── document_actions.py
└── tests/
    ├── test_entity_api.py
    ├── test_metadata_api.py
    ├── test_document_actions.py
    └── test_permission_filtering.py
```

## Dependency order

1. Server-owned schema registry and permission service.
2. Shared API client, session store, error normalization, and request cancellation.
3. Entity list API and Vue list engine.
4. Detail serializer/API and Vue detail engine.
5. Form metadata/API and Vue form engine.
6. Child-table editor and standard item-detail recalculation contract.
7. Activity, comments, attachments, and assignments.
8. Print formats, preview, PDF, export, and report adapters.
9. Functional global search.
10. Products and specialized New Product workflow.
11. Customers and Suppliers.
12. Smart Sales migration into the SPA.
13. Sales transaction schemas and official mappings.
14. Purchase transaction schemas and official mappings.
15. Stock documents and reports.
16. CRM schemas and conversion actions.
17. Finance documents and reports.
18. Manufacturing, projects, quality, assets, and support.
19. Restricted administration pages.
20. Role landing settings and route/access guard after replacement coverage is sufficient.
21. Full persona, permission, workflow, mobile, accessibility, and regression testing.
22. Remove ordinary-user Standard Desk dependency only after the matrix proves coverage.

## Remaining Standard Desk dependencies

At this audit, ordinary users still depend on Standard Desk for all of the following:

- every entity list, detail, create, and edit page;
- all submit, cancel, amend, workflow, and related-document actions;
- all transaction child-table editing;
- all reports and accounting statements;
- print preview, Print Format selection, and PDF download;
- attachments, comments, assignments, and activity history;
- all product creation, pricing, SKU, Item Price, and opening stock actions;
- all sales flow after the legacy page creates a Draft Sales Order;
- all purchase, inventory, finance, CRM, operations, and administration work;
- global search result navigation;
- user landing and `/app` route behavior.

Standard Desk must therefore remain available during development. The final ordinary-user route guard must not be enabled until required daily workflows are functional in Retail ERP, or users would be trapped behind placeholder pages.

## Next approved implementation stage

Build only the schema registry, permission/metadata services, and shared entity-list engine first. Pilot it with read-only lists for Customer, Item, and Sales Order before enabling create/edit or changing login routing. Required evidence:

- field/filter allowlist tests;
- permission-filtering tests for at least Sales, Stock, Accounts, and System Manager personas;
- pagination/search/sort tests;
- desktop/mobile screenshots;
- browser-console check;
- exact APIs and remaining Desk dependencies documented.
