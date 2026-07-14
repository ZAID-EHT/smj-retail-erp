# Retail ERP — Agent Handoff and Production-Readiness Audit

## 0. Update — Full Feature Parity mission (2026-07-14)

A follow-up "full feature parity" mission ran on branch `full-feature-parity`
(off `develop@3ce5958`, recovery tag `pre-full-feature-parity-20260714-1123`).
It completed the safe, non-gated foundation and stopped at the approval gates the
mission itself defines. See `docs/full-parity/`.

- **Authoritative parity registry** (`my_store_ui/audit/parity_registry.py`)
  classifies all 2482 user-facing features with truthful status/priority/strategy;
  honesty contract test-enforced (`test_parity_registry.py`, 7/7 pass standalone).
- **Real, server-verified implementation batches** (no schema/site-config changes):
  +116 in-scope standard DocTypes served by the universal engine, +156 reports via
  the permission-aware viewer, +351 workspace shortcuts credited by their routed
  destinations, +27 print formats via the routed print dialog, plus a genuine
  universal list-engine bug fix (KeyError on text/hidden default columns).
  Net: **`unmapped_user_facing` 2396 → 1746**, routed **86 → 736** (3.46% → 29.65%).
- **Registry-based completeness (the truthful measure):** of 2482 — 829 implemented
  in some form (0 `verified_complete`, honest given blocked tests/no browser), 858
  internal, 175 not_required, 620 genuinely pending. ~75% resolved, ~25% pending.
- **Wholesale core implemented (approved batch, 2026-07-14):** Available-to-Sell
  (Actual − Reserved) in Smart Sales + snapshot API; customer credit-status service
  with 7 verified delivery-gate rules; reservation service delegating to standard
  Stock Reservation Entry with Bin row-locking (concurrency-safe) + 3-day
  configurable expiry scheduler; atomic TRX-YYYY-###### stamping/propagation
  (SO→DN→SI→PE, safe no-op until fields applied); Wholesale Transaction Register at
  `/retail-erp/sales/transactions`. Custom fields added via fixtures (credit type +
  txn id — standard credit_limits reused, no duplicates). Code in
  `my_store_ui/wholesale/`. Everything schema-independent verified on site1
  read-only; no site config/schema/reservation change was made to site1.
- **Two ENVIRONMENT blockers remain** (see `docs/full-parity/BLOCKERS.md` → STAGING):
  the MariaDB **root password** (to create the staging DB) and **network access**
  (npm registry unreachable → Playwright/Chromium can't download). `setup_staging.sh`
  is turn-key once the root password is available; it applies fixtures, enables
  reservation + allow_tests on staging only, and runs the wholesale test suite.
- Earlier gated items (reservation policy, credit fields, transaction id) are now
  DONE in code; only staging execution + browser verification remain.
- Key trackers: `docs/full-parity/PROGRESS.md`, `BLOCKERS.md`, `DECISIONS.md`,
  `VERIFICATION_MATRIX.md`, and `docs/full-parity/inventory/`.

The audit below (Sections 1–25) remains valid as the production-readiness picture.

## 1. Executive Summary

**Final status: NOT YET PRODUCTION-READY.**

Retail ERP is a substantial custom Vue 3/Frappe foundation, but it is not yet a production system for the stated large wholesale importing and selling business. The current application has a standalone authenticated shell, permission-aware routing, six handcrafted ERPNext document interfaces, a metadata-driven provisional engine, priority module routes, selected report adapters, and working server PDF generation. Those are valuable foundations; they do not yet implement or prove the fixed wholesale operating model.

The decisive blockers are:

1. **The required reservation model is absent from the Retail ERP workflow.** `Stock Settings.enable_stock_reservation` is `0`; the site contains zero `Stock Reservation Entry` records; Stock Reservation Entry and its Sales Order/Pick List actions are unmapped in `docs/erpnext-v15-complete-inventory.json`. `my_store_ui.api.get_bootstrap` returns only summed `Bin.actual_qty`, while `SmartSalesPage.vue` labels that value “available”. It does not calculate `Actual - Reserved`.
2. **The required customer-credit model is absent.** There are no Customer credit custom fields, no `Customer Credit Limit` rows, no Credit/Non-Credit classification, no credit period/available credit/overdue/override-reason enforcement, and no server-side delivery gate. Evidence: read-only site inspection on 2026-07-14 and `my_store_ui/services/form_schemas.py::FORM_SCHEMAS["customers"]`.
3. **The shared wholesale transaction ID/register is absent.** No transaction custom field exists on Sales Order, Delivery Note, Sales Invoice, or Payment Entry; `/retail-erp/sales/transactions` is not registered; there is no `TRX-YYYY-000001` service or register.
4. **Purchasing, importing, landed cost, reconciliation, serial/batch, pick/pack, and logistics remain generated or specialised provisional rather than verified workflows.** No submitted Purchase Receipt, submitted Delivery Note, Stock Reservation Entry, or Landed Cost Voucher exists on the site to provide behavioural evidence.
5. **Current regression verification is incomplete.** `bench --site site1.local run-tests --app my_store_ui` was attempted on 2026-07-14 but Frappe refused because `allow_tests` is disabled. The repository contains 100 discovered test methods, but none was re-run in this audit. Browser automation and browser executables are not installed.

The current machine inventory has **2,482 user-facing features**, of which **86 have a registered Retail ERP route/adaptor**. Strict route coverage is therefore **3.46%**. Of those 86, six are handcrafted DocType workflows, 52 are generated provisional DocTypes, 26 are provisional reports, one is the SPA shell, and one is Smart Sales. The strict audit correctly fails with `unmapped_user_facing=2396`.

A practical implementation-maturity estimate of roughly **15–20%** is reasonable only as a planning judgement about foundations already built. It is not tested functional parity and must not be presented as a verified completion percentage. The auditable strict coverage figure is **3.46%**.

## 2. Audit Date and Environment

| Item | Verified value | Evidence |
|---|---|---|
| Audit date | 2026-07-14, Asia/Colombo | This audit run |
| Bench | `/home/zaidh/frappe-bench` | `pwd` |
| Site | `site1.local` | Prompt and inventory `site` field |
| Custom app | `/home/zaidh/frappe-bench/apps/my_store_ui` | Git and filesystem inspection |
| Vue frontend | `apps/my_store_ui/frontend` | `frontend/package.json`, `frontend/src/main.js` |
| Main route | `http://127.0.0.1:8000/retail-erp/home` | Live HTTP 200 on 2026-07-14 |
| Runtime | Python 3.14 virtual environment, Node `v24.15.0`, npm `11.12.1`, Yarn `1.22.22` | `env/bin/python`, `node --version`, `npm --version`, `yarn --version` |
| PDF renderer | `/home/zaidh/.local/bin/wkhtmltopdf`, `0.12.6.1 (with patched qt)` | `command -v wkhtmltopdf`; `wkhtmltopdf --version` |
| Active system users | 2 total; 1 non-Administrator | Read-only Frappe console count, 2026-07-14 |
| Companies / enabled warehouses | 2 / 10 | Read-only Frappe console count, 2026-07-14 |
| Active workflows | 0 | Inventory and direct database count |
| Outgoing email accounts | 0 | Read-only Frappe console count |
| Stock reservation setting | Disabled (`0`) | `Stock Settings.enable_stock_reservation` |
| Negative stock | Disabled (`0`) | `Stock Settings.allow_negative_stock` |

No site configuration, schema, role, permission, business document, or other application was changed during this audit.

## 3. Current Git State

Starting state recorded before audit generation:

| Item | Value |
|---|---|
| Branch | `develop` |
| Starting commit | `3ce5958392a66c9d75243fbec43fe780c168673c` |
| Commit subject | `feat: add priority ERPNext module page coverage` |
| Starting worktree | Clean |

The requested history was recorded with `git -C apps/my_store_ui log --oneline --decorate -n 30`. The relevant implementation chain is:

- `3ce5958` priority ERPNext module page coverage
- `98794f8` universal generated UX
- `e180ffe` metadata-driven universal foundation
- `9349636` permission-aware navigation/global search
- `24193e6` standalone role-based frontend
- `eff7348` global scrolling correction
- `4096aa6` Payment Entry allocation
- `680ab20` Payment Entry lifecycle
- `e97dffa` Delivery Note/Sales Invoice lifecycles
- `f6af320` Sales Order lifecycle
- `bfad3ca` secure form engine
- `853bab6` complete feature inventory
- `968c6aa`, `2dd1514` detail/list engines

Current audit worktree changes before any review/commit:

- `AGENT_HANDOFF.md` — this new handoff.
- `docs/erpnext-v15-complete-inventory.json` — inventory generator updated the recorded `my_store_ui` commit from `98794f8...` to `3ce5958...`; no feature count changed as a side effect.

No commit was created because the prompt expressly requires review before committing.

## 4. Installed Apps and Versions

Verified on 2026-07-14 with `bench --site site1.local list-apps`:

| App | Version | Branch |
|---|---:|---|
| frappe | 15.108.0 | version-15 |
| erpnext | 15.108.3 | version-15 |
| smj_theme | 0.0.1 | develop |
| erpnext_chatgpt | 0.0.1 | main |
| erpnext_gemini_integration | 0.1.0 | main |
| posawesome | 15.30.0 | develop |
| my_store_ui | 0.0.1 | develop |

All seven installed applications were inspected by the inventory generator. POS Awesome, ChatGPT, Gemini, and theme sources were not modified.

## 5. Architecture Overview

### Backend package

`apps/my_store_ui/my_store_ui` contains:

- `hooks.py`: app metadata, Item Custom Field fixtures, standalone home page, `/retail-erp/*` website route rules, and `before_request` Desk guard.
- `standalone.py`: Guest-safe session bootstrap, server-resolved landing route, navigation, CSRF token delivery, and route authorization.
- `route_guard.py`: browser-HTML-only `/app` redirects; APIs, assets, files, print/PDF and integration requests are not intentionally intercepted.
- `services/frontend_routes.py` and `services/priority_registry.py`: server-owned route/navigation/feature declarations.
- `entity_api.py`, `form_api.py`, `document_actions.py`, `sales_order_actions.py`, `payment_api.py`: handcrafted Customer, Item, Sales Order, Delivery Note, Sales Invoice, and Payment Entry APIs.
- `universal/registry.py`, `universal/api.py`, `universal/collaboration.py`: metadata-driven provisional list/form/detail/action/report/collaboration APIs.
- `priority_pages.py`: module dashboards, report hub/viewer, trees, specialised read/launcher pages, POS context, and read-only administration facts.
- `audit/feature_inventory.py`: installed-code/site inventory and strict parity audit.
- `tests/`: 12 files with 100 statically discovered `test_*` methods.

### Frontend

`frontend/src` contains:

- `StandaloneRoot.vue`, `LoginPage.vue`, `services/session.js`: custom login, standard Frappe session cookies/CSRF, OTP response handling, password reset request, route authorization, logout and session clearing.
- `App.vue` and `components/shell/*`: Retail ERP shell, server-filtered header/navigation, user menu, and global search.
- `router/index.js` and `router/routes.js`: standalone `/retail-erp/` history base, handcrafted route priority, clean priority routes, generated compatibility routes, and 404.
- `pages/entities/*`: handcrafted list/form/detail pages.
- `pages/generated/*` and `components/generated/*`: universal generated list/form/detail/child table/print/collaboration components.
- `pages/priority/*`: module dashboard, report, tree, POS/special launchers and clean-route resolver.
- `design/*`: shared responsive design and the global scrolling correction.

### Route model

- 37 static server route definitions in `services/frontend_routes.py::ROUTE_REGISTRY`.
- 54 clean entity bases in `services/priority_registry.py::ENTITY_ROUTES`; each resolver supports list/new/detail/edit shapes where applicable.
- 3 Stock Entry purpose variants, 13 special routes, 6 report groups, and 27 allowlisted priority report names.
- 106 declared navigation links are filtered again by server permissions.
- Canonical inventory evidence: 86 mapped user-facing features, not “all generated URL permutations”.

Routing priority is custom handcrafted page, then clean generated/provisional route, then specialised route, then unavailable/not-found. `universal/registry.py::CUSTOM_OVERRIDES` protects Customer, Item, Sales Order, Delivery Note, Sales Invoice, and Payment Entry from generic replacement. Payment Entry Allocation and Smart Sales are synthetic custom registry entries.

### Permission and business-logic boundary

The intended boundary is sound: Frappe/ERPNext remains responsible for authentication, permission checks, naming, validation, pricing, taxes, workflows, stock/accounting ledgers, submission/cancellation, and mapped documents. Evidence includes `universal/api.py::_get_permitted_doc`, `_clean_payload`, `run_document_action`, `run_workflow_action`, and fixed `MAPPED_ACTIONS`; `sales_order_actions.py::MAPPED_TARGETS`; and `document_actions.py::ENTITY_REGISTRY`.

No `ignore_permissions=True` or direct SQL write path was found in application runtime code. `frappe.get_all` occurs only in the audit utility and tests. Two amendment/duplicate implementations set copied documents to `docstatus = 0` before insert (`document_actions.py` and `universal/api.py`); although this mirrors common amendment-copy preparation, it must be reviewed against the explicit project rule and standard Frappe amendment helpers before production approval.

## 6. Business Workflow Requirements

The fixed business flow is:

```text
Select Customer
→ show customer credit status
→ search wholesale items
→ show Actual / Reserved / Available-to-Sell
→ build cart
→ reserve order
→ create and submit Sales Order
→ reserve stock without reducing physical stock
→ receive payment or approve credit
→ prepare/pick/pack
→ submit Delivery Note and reduce physical stock
→ reduce/release reservation
→ create one final Sales Invoice
→ allocate payments and collect balance
→ complete order
```

There must be no “Sales Transfer” step. Stock Transfer means only an optional inter-warehouse Stock Entry. Partial reservation, payment, delivery, invoicing/returns, backorders, and multiple warehouses must preserve normal ERPNext controller behaviour.

Required stock presentation:

```text
Available to Sell = Actual Warehouse Stock - Reserved Stock
```

Current mismatch: `my_store_ui/api.py::get_bootstrap` sums `Bin.actual_qty` and returns it as `item.actual_qty`. `SmartSalesPage.vue` renders `item.actual_qty ... available`. No reserved quantity is fetched or subtracted. This is **not** the required available-to-sell model.

Required customer-credit presentation and enforcement:

```text
Credit/Non-Credit, individual limit, period, outstanding,
available credit, overdue amount/status, delivery-before-payment flag,
authorised override with reason and audit trail.
```

Current mismatch: the Customer form exposes general identity/contact/price-list/payment-terms fields only. The detail page can display standard `credit_limits`, but the site has zero rows and the form does not manage them. No Credit/Non-Credit or delivery gate exists.

## 7. Verified Completed Work

The word “verified” below means verified in this audit or directly supported by a current source/test artifact. It does not imply full feature parity.

| Status | Capability | Evidence and verified boundary |
|---|---|---|
| [VERIFIED COMPLETE] | Standalone shell delivery | `/`, `/retail-erp/home`, Sales Order new, Payment list, Supplier generated and Warehouse generated routes returned HTTP 200 with `retail-erp-root` and no sampled Desk markers on 2026-07-14. `www/retail_erp.py/html`, `hooks.py`. |
| [VERIFIED COMPLETE] | Guest bootstrap minimisation | GET `my_store_ui.standalone.get_session_bootstrap` returned only `{"authenticated": false}`. |
| [VERIFIED COMPLETE] | Browser Desk redirects for sampled routes | `/app`, Customer, Item, Sales Order, Delivery Note, Sales Invoice, Payment Entry and Accounting returned non-cacheable 302 targets inside Retail ERP. `route_guard.py`. |
| [VERIFIED COMPLETE] | Hashed production assets and build | `npm run build` and `npm run check` passed; 107 modules; JS 280.46 kB (87.11 kB gzip), CSS 70.18 kB (12.06 kB gzip); live HTML references `retail-erp-DWQjyjjl.js` and `my-store-ui-frontend-B3CqffZr.css`. |
| [VERIFIED COMPLETE] | Feature discovery integrity | Generator completed with fingerprint `c8cab946...17d14`; 2,841 total features, 2,482 user-facing, 359 internal, zero unclassified. `docs/erpnext-v15-complete-inventory.json`. |
| [VERIFIED COMPLETE] | Strict parity guard remains enabled | It exited non-zero with 2,396 unmapped and zero unclassified/undocumented/complete-without-tests/unhandled-workflows. `audit_feature_parity`. |
| [VERIFIED COMPLETE] | Server PDF environment | `wkhtmltopdf 0.12.6.1` is installed. Standard Frappe `download_pdf` generated a valid one-page, 65,865-byte Sales Invoice PDF for `ACC-SINV-2026-00010`; temporary output was deleted. |
| [VERIFIED COMPLETE] | Worker presence | `bench doctor`: `Workers online: 1`. This is a development-health fact, not production topology approval. |
| [VERIFIED COMPLETE] | Handcrafted route ownership | Inventory classifies Customer, Item, Sales Order, Delivery Note, Sales Invoice, and Payment Entry as handcrafted within documented scope; routes and server schemas exist. |
| [VERIFIED COMPLETE] | Payment allocation implementation exists | `PaymentAllocationDialog.vue`, `payment_api.py::get_outstanding_references`, Payment Entry references/deductions schemas, standard Payment Entry controller save/submit/cancel paths. Current interactive/regression execution was not possible, so behavioural status is covered under Section 10. |
| [VERIFIED COMPLETE] | Item custom pricing schema exists | Eleven Item fields are fixtures in `my_store_ui/fixtures/custom_field.json`; server recalculation is in `form_api.py::_apply_item_pricing`. This does not establish ERPNext Item Price/Pricing Rule parity. |

## 8. Partially Completed Work

| Status | Area | What exists | What remains |
|---|---|---|---|
| [PARTIAL] | Smart Sales | Live paginated items, customer search, warehouse/price-list selectors, cart, idempotent Draft Sales Order creation. `api.py`, `SmartSalesPage.vue`. | No credit status/gate, no reserved/available stock, no reservation, no submit/payment/pick/pack orchestration, browser-entered price intentionally ignored, no shared TRX ID. |
| [IMPLEMENTED, NOT VERIFIED] | Sales Order lifecycle | Handcrafted form/detail plus server allowlisted submit/cancel/amend/hold/resume/close/reopen and official DN/SI mappings. | Current tests did not run; stock reservation actions absent; credit approvals absent; full partial-delivery/payment/concurrency behaviour unproved. |
| [IMPLEMENTED, NOT VERIFIED] | Delivery Note lifecycle | Draft form, item table, standard submit/cancel/amend, return and Sales Invoice mapping adapters. | Site has zero submitted Delivery Notes; stock reduction/reversal, serial/batch, partial delivery and linked-order recalculation were not behaviourally proven today. |
| [IMPLEMENTED, NOT VERIFIED] | Sales Invoice lifecycle | Draft form, submit/cancel/amend/credit-note/Payment Entry mapping, detail, print. Five submitted invoices exist and PDF generation works. | One-final-invoice policy, return accounting, partial delivery billing, outbound email and role/browser matrix are unproved. |
| [IMPLEMENTED, NOT VERIFIED] | Payment Entry lifecycle | Receive/Pay/Internal Transfer forms, reference allocation, standard submit/cancel/amend, print. Five submitted entries exist. | Current GL/Payment Ledger/outstanding reduction and reversal were not reconciled by this audit; bank/payment reconciliation is absent. |
| [PARTIAL] | Generated engine | 52 DocTypes have list/detail/form/action provisional routes; server filters metadata/fields and calls normal document APIs. | Every one remains `generated_provisional`; per-feature create/edit/delete/action, client-script equivalence, role, browser and collaboration tests are incomplete. |
| [PARTIAL] | Reports | 26 installed priority reports are allowlisted; filters, server execution, totals/charts, CSV and voucher links exist. | 198 reports exist; 171 user-facing reports have no Retail ERP adapter. Priority reports remain provisional; interactive filter/chart/PDF tests are incomplete. `CRM Analytics` is one registered priority name not installed. |
| [PARTIAL] | Collaboration | Generated pages have attachments, comments, assignments, sharing, tags, versions and email adapters. | Not proven interactively; attachment upload uses standard generic endpoint; handcrafted pages do not have equivalent complete collaboration UI; no outgoing Email Account exists. |
| [PARTIAL] | Trees/special pages | Account/Warehouse/Cost Center/etc. tree reads and safe specialised contexts exist. | Reparenting and domain actions are incomplete; reconciliation, BOM, Job Card, Work Order, admin settings and POS remain specialised provisional. |
| [PARTIAL] | Administration | Restricted users/roles/company/master routes and read-only permission/system-health contexts exist. | Dedicated safe role-permission editing, settings, backup, job control, integrations and operational admin verification remain. |

## 9. Missing or Unavailable Work

Critical missing Retail ERP capabilities include:

- [MISSING] Stock reservation UI/API orchestration, expiry, unreserve, cancellation, partial reservation, backorder handling, concurrency locking tests, and Reserved Stock report integration.
- [MISSING] Credit/Non-Credit classification and all required delivery/credit controls.
- [MISSING] `/retail-erp/sales/transactions`, shared transaction ID, register/export/timeline, and cross-document reconciliation.
- [MISSING] Pick List and Packing Slip routes/workflows; inventory marks their records and actions unmapped.
- [MISSING] Import Shipment business record and container/BoL/shipping/customs/clearing timeline.
- [MISSING] Landed Cost Voucher Retail ERP route and import cost report adapter; site has zero LCVs.
- [MISSING] Dedicated Purchase Receipt/Purchase Invoice return and debit-note interfaces and behavioural posting tests.
- [MISSING] Dedicated Stock Reconciliation and Serial and Batch Bundle interactions.
- [MISSING] Bank Reconciliation and Payment Reconciliation interactions.
- [MISSING] Dedicated Journal Entry debit/credit/dimensions UX and accounting verification.
- [MISSING] Delivery Trip/Pick/Pack/proof-of-delivery/signature/failure workflow.
- [MISSING] Outgoing email configuration and end-to-end email verification.
- [MISSING] Staging, production infrastructure, HTTPS/domain, off-server backups, restore proof, monitoring, alerting, load/concurrency tests, data-migration rehearsal, UAT, training and go-live/rollback exercises.

Many other ERPNext features are [STANDARD DESK ONLY] at the backend level, but the current `route_guard.py` redirects normal HTML `/app` access into Retail ERP. Therefore “Desk only” does **not** mean ordinary users currently have a usable fallback. It means ERPNext implements the backend/Desk feature while Retail ERP does not yet expose it.

## 10. Unverified Work

- [BLOCKED] The current Python suite: Frappe returned `Testing is disabled for the site! ... bench --site site1.local set-config allow_tests true`. This audit did not change site configuration.
- [BLOCKED] Chrome/Edge/Firefox/Chromium browser automation: no browser executable, Playwright, Cypress, Selenium, or related node package was found.
- [IMPLEMENTED, NOT VERIFIED] Valid login, OTP, disabled user, logout/Back, forced session expiry, multi-role landing and role-specific UI. Two-factor authentication is disabled; only one enabled non-Administrator system user exists and it has several business roles.
- [IMPLEMENTED, NOT VERIFIED] Desktop/mobile visual layout, touch/keyboard scrolling, modal focus, zoom matrix and page-level overflow after the latest priority expansion.
- [IMPLEMENTED, NOT VERIFIED] Collaboration writes, file upload/removal/download, comments, assignments, sharing, tags, versions and document email.
- [IMPLEMENTED, NOT VERIFIED] Lifecycle posting/reversal and mapped-document behaviour under the current commit because no current test run was permitted.
- [IMPLEMENTED, NOT VERIFIED] User Permission, ownership, sharing, company and warehouse restrictions across representative single-role users.
- [IMPLEMENTED, NOT VERIFIED] Duplicate-click/idempotency under real concurrent sessions.

## 11. Current Feature Inventory and Coverage

Verified 2026-07-14 using:

```bash
bench --site site1.local execute my_store_ui.audit.feature_inventory.generate_complete_inventory
bench --site site1.local execute my_store_ui.audit.feature_inventory.audit_feature_parity
```

Canonical output: `docs/erpnext-v15-complete-inventory.json`; summary: `docs/feature-audit-summary.md`.

| Metric | Current value |
|---|---:|
| Installed applications | 7 |
| Modules | 40 |
| Parent / child DocTypes | 467 / 335 |
| Custom DocTypes | 1 |
| Reports / Pages / Workspaces | 198 / 22 / 25 |
| Dashboard aggregate | 176 |
| Active workflows | 0 |
| Print Formats | 44 |
| Client / Server Scripts | 1 / 0 |
| Custom Fields / Property Setters | 212 / 101 |
| Document mappings/actions | 634 |
| User-facing / internal | 2,482 / 359 |
| Total atomic features | 2,841 |
| Generic engine candidates | 249 |
| Specialised interfaces | 1,481 |
| Mapped Retail ERP features | 86 |
| Unmapped user-facing | 2,396 |
| Strict route coverage | 3.46% |

Mapped-feature composition:

| Classification | Count | Completion interpretation |
|---|---:|---|
| Handcrafted DocTypes | 6 | Implemented within documented scope; full wholesale parity not implied |
| Generated provisional DocTypes | 52 | Route/adapter foundation only |
| Provisional report viewers | 26 | Priority subset only |
| SPA shell/app | 1 | Shell implemented, feature parity incomplete |
| Smart Sales page | 1 | Partial Draft-order experience |

Strict audit result: **FAIL**.

```text
unclassified_user_facing=0
unmapped_user_facing=2396
undocumented_actions=0
complete_without_tests=0
unhandled_active_workflows=0
```

## 12. Domain-by-Domain Status

### 12.1 Wholesale Sales

| Feature | Status | Evidence / limitation |
|---|---|---|
| Lead | [PARTIAL] | `/retail-erp/crm/leads`; generated provisional; conversion adapter exists but not browser/role verified. |
| Opportunity | [PARTIAL] | `/retail-erp/crm/opportunities`; generated provisional; Quotation/Customer mappings registered. |
| Quotation | [PARTIAL] | `/retail-erp/sales/quotations`; generated transaction with SO/SI mappings; client pricing/tax/action edge cases unverified. |
| Sales Order | [IMPLEMENTED, NOT VERIFIED] | Handcrafted list/form/detail/lifecycle; current test suite blocked; reservation/credit policy missing. |
| Smart Sales catalogue/cart | [PARTIAL] | Creates Draft Sales Order via standard insert; no reservation/credit/true available-to-sell. |
| Warehouse selection | [VERIFIED COMPLETE] | Smart Sales validates permitted non-group warehouse in company; `api.py::_validate_link`. |
| Actual stock | [PARTIAL] | Summed permitted `Bin.actual_qty`; no per-reservation subtraction; role/warehouse leakage requires dedicated verification. |
| Reserved / Available-to-Sell | [MISSING] | Reservation disabled; zero entries; no calculation. |
| Advance/partial payments | [IMPLEMENTED, NOT VERIFIED] | Payment Entry allocation exists; current accounting reconciliation absent. |
| Pick List / Packing Slip | [MISSING] | Inventory features/actions unmapped. |
| Delivery Note / partial delivery | [IMPLEMENTED, NOT VERIFIED] | Standard controller path exists; zero submitted DNs means no current behavioural proof. |
| Sales Invoice | [IMPLEMENTED, NOT VERIFIED] | Handcrafted lifecycle and five submitted invoices; one-final-invoice policy not enforced/proven. |
| Returns / Credit Notes | [IMPLEMENTED, NOT VERIFIED] | Official return mappings registered in `document_actions.py`; no current lifecycle test. |
| Customer statement / ageing | [PARTIAL] | Accounts Receivable and Customer Ledger Summary report adapters are provisional. |
| Transaction ID/Register/timeline | [MISSING] | No fields, route, service or register. |

### 12.2 Customers, Pricing and Credit

| Feature | Status | Evidence / limitation |
|---|---|---|
| Customer | [IMPLEMENTED, NOT VERIFIED] | Handcrafted CRUD route; current tests blocked. |
| Contact / Address | [PARTIAL] | Generated provisional routes; Customer does not automatically manage them. |
| Customer Group / Territory / Sales Person | [PARTIAL] | Generated tree routes; reparenting and browser tests incomplete. |
| Price List / Item Price | [PARTIAL] | Generated provisional pages; Smart Sales reads standard selling Item Price. |
| Pricing Rule, quantity/customer pricing | [STANDARD DESK ONLY] | ERPNext feature exists; no Retail ERP route/action parity. |
| Minimum price / discount approval | [MISSING] | No explicit Retail ERP policy, approval workflow or test. |
| Credit/Non-Credit selector | [MISSING] | No metadata/custom field/form field. |
| Individual credit limit | [PARTIAL] | Standard Customer child table can be displayed to hardcoded roles, but zero rows and no authorised edit flow. |
| Credit period | [MISSING] | Payment Terms Template is selectable; required individual credit-period model/gate is absent. |
| Outstanding/overdue/available credit | [MISSING] | No customer credit service or delivery gate; official receivables must come from ERPNext reports, not Vue arithmetic. |
| Credit approval/override history | [MISSING] | No workflow, reason, role control or audit record. |

### 12.3 Purchasing and Suppliers

| Feature | Status | Evidence / limitation |
|---|---|---|
| Supplier | [PARTIAL] | Generated provisional CRUD/hold route. |
| Material Request → RFQ/PO | [PARTIAL] | Fixed official mapping adapters in `universal/api.py::_run_mapped_action`; transaction/browser tests blocked. |
| RFQ → Supplier Quotation | [PARTIAL] | Official helper and supplier allowlist validation; supplier email flow missing. |
| Supplier Quotation/comparison | [PARTIAL] | PO mapping exists; comparison interface missing. |
| Purchase Order → Receipt/Invoice | [PARTIAL] | Official mappings registered; 10 POs exist, but controller edge cases and browser roles unverified. |
| Purchase Receipt | [PARTIAL] | Generated lifecycle; zero submitted Purchase Receipts, so stock posting/reversal unproved. |
| Purchase Invoice | [PARTIAL] | Generated lifecycle and Payment Entry mapping; six records exist; GL/AP posting/reversal not reconciled. |
| Supplier advance / Payment Entry | [PARTIAL] | Payment Entry supports Pay/advance architecture; Purchase-specific end-to-end test absent. |
| Purchase Return / Debit Note | [MISSING] | Standard ERPNext behaviour exists; no dedicated Retail ERP return adapter. |
| Blanket Order / drop shipping | [STANDARD DESK ONLY] | Installed ERPNext capabilities are not registered as completed Retail ERP workflows. |
| Supplier price lists/statements/performance | [PARTIAL] | Item Price and some reports exist; full supplier views/analytics are absent. |

### 12.4 Import Shipment Management

| Feature | Status | Evidence / limitation |
|---|---|---|
| Import Shipment business record | [MISSING] | No installed `Import Shipment` DocType found in current inventory. Requires approved custom design/schema. |
| Container, BoL, shipping line, vessel, forwarder, ports, ETD/ETA/arrival, customs, clearing agent | [MISSING] | No consolidated record/route/timeline. Standard `Shipment` exists but is not this import-management model. |
| Shipment attachments/timeline and multiple POs | [MISSING] | Universal collaboration foundation does not create the required import aggregate. |
| Landed Cost Voucher | [STANDARD DESK ONLY] | Standard ERPNext DocType/action/report found; no Retail ERP route; zero site records. |
| Import cost report | [STANDARD DESK ONLY] | `Landed Cost Report` is installed/unmapped. |
| Multi-currency / exchange gain-loss | [PARTIAL] | Standard Purchase Invoice/Payment Entry controllers support it; no complete import-chain verification. |

Standard ERPNext should continue to own Purchase Receipt, Purchase Invoice, Landed Cost Voucher, currency and accounting. A custom Import Shipment coordination record and Transaction ID integration require a separately approved schema checkpoint.

### 12.5 Inventory and Warehouses

| Feature | Status | Evidence / limitation |
|---|---|---|
| Item | [IMPLEMENTED, NOT VERIFIED] | Handcrafted Item CRUD/pricing fields; standard Item Price/Pricing Rule parity incomplete. |
| Item Group/Brand/UOM/Warehouse | [PARTIAL] | Generated provisional list/tree/forms. |
| Actual/Reserved/Available | [MISSING] | Only actual is displayed; reserved/available model absent. |
| Incoming/projected | [PARTIAL] | Stock Projected Qty priority report exists; not integrated into Smart Sales decisions. |
| Stock Entry and Transfer/Receipt/Issue | [PARTIAL] | Generated provisional forms with server-owned purpose defaults; no posting/browser proof. |
| Stock Reconciliation | [PARTIAL] | Specialised provisional context; scan/upload/valuation grid missing. |
| Serial and Batch Bundle | [MISSING] | DocType/actions/reports unmapped; DN schema has fields but no complete bundle selector. |
| Barcode | [PARTIAL] | Item detail/search support exists; Item form flattens first barcode and advanced scan/bundle flows are unverified. |
| Reorder/Auto Material Request | [PARTIAL] | Reorder report alias exists; full reorder configuration/auto-MR flow unverified. |
| Stock Ledger/Balance | [PARTIAL] | Priority report adapters exist; filters/performance/role/browser tests incomplete. |
| Stock Ageing/slow/dead stock | [STANDARD DESK ONLY] | Installed reports are not in priority adapter batch. |
| Batch expiry/damaged/rejected stock | [STANDARD DESK ONLY] | ERPNext backend capabilities exist; Retail ERP specialised workflows missing. |

### 12.6 Accounting and Finance

| Feature | Status | Evidence / limitation |
|---|---|---|
| Chart of Accounts | [PARTIAL] | Read/tree adapter, no complete account-specific actions. |
| General Ledger | [PARTIAL] | Priority report viewer; no accountant sign-off/performance proof. |
| Journal Entry | [PARTIAL] | Generated lifecycle; dedicated balanced debit/credit/dimensions UX missing. |
| Sales Invoice | [IMPLEMENTED, NOT VERIFIED] | Handcrafted; current GL/AR reconciliation not performed. |
| Purchase Invoice | [PARTIAL] | Generated provisional; current AP/GL reversal tests absent. |
| Payment Entry | [IMPLEMENTED, NOT VERIFIED] | Handcrafted lifecycle/allocation; current GL/Payment Ledger/outstanding reconciliation absent. |
| Payment Reconciliation | [MISSING] | Specialised context only; allocation workflow missing. |
| Bank Reconciliation / transactions | [MISSING] | Specialised context only; upload/matching/reconciliation actions unmapped. |
| AR/AP and ageing | [PARTIAL] | Priority reports registered; interactive/accuracy/accountant validation incomplete. |
| Credit/Debit Notes | [PARTIAL] | Sales return mapping exists; purchasing debit-note flow missing. |
| Taxes / dimensions / cost centers | [PARTIAL] | Controllers retained; Cost Center tree exists; full dimensions/UI coverage unverified. |
| Budgets / exchange revaluation / opening balances | [STANDARD DESK ONLY] | Inventory lists them as unmapped. |
| Trial Balance/P&L/Balance Sheet/Cash Flow | [PARTIAL] | Priority report adapters; no accountant sign-off or production dataset validation. |

### 12.7 Delivery and Logistics

| Feature | Status | Evidence / limitation |
|---|---|---|
| Pick List and picking | [MISSING] | Record/actions unmapped. |
| Packing Slip/packages | [MISSING] | Record/actions unmapped. |
| Dispatch | [PARTIAL] | Delivery Note has transporter/driver/vehicle fields; no dispatch board. |
| Vehicle/Driver | [PARTIAL] | Link fields available; no complete fleet/logistics workflow. |
| Delivery Trip/Route | [STANDARD DESK ONLY] | Installed backend not exposed as priority Retail ERP workflow. |
| Proof of delivery/signature | [MISSING] | No capture/attachment/signature acceptance flow. |
| Failed/partial delivery | [PARTIAL] | ERPNext partial DN can support quantities, but no dedicated failure/retry workflow or test. |

### 12.8 Returns and Corrections

| Feature | Status | Evidence / limitation |
|---|---|---|
| Return Delivery Note | [IMPLEMENTED, NOT VERIFIED] | Official mapped return adapter; stock reversal unproved today. |
| Sales Credit Note | [IMPLEMENTED, NOT VERIFIED] | Official Sales Invoice return adapter; accounting reversal unproved today. |
| Purchase Return/Debit Note | [MISSING] | No Retail ERP adapter. |
| Partial returns | [IMPLEMENTED, NOT VERIFIED] | Mapping supports mapped rows, but quantity edge cases not currently tested. |
| Return reason/approval/refund/replacement | [MISSING] | No dedicated policy/workflow/UI. |
| Cancel/amend | [PARTIAL] | Allowlisted standard controller calls on custom/generated documents; current suite blocked and copied-doc `docstatus=0` preparation needs review. |

### 12.9 Reports and Dashboards

- [PARTIAL] 198 reports discovered; 26 installed priority reports have provisional Retail ERP viewers; 171 user-facing reports remain without an adapter.
- [PARTIAL] Nine module/dashboard routes show permission-aware counts/recent records, but not full Workspace/Dashboard parity.
- [STANDARD DESK ONLY] Most of the 25 Workspaces, 49 dashboard charts, 50 number cards, 68 dashboard connections and their interactive actions.
- [PARTIAL] CSV export and browser print exist in priority reports; prepared-report, tree/chart, totals and linked voucher behaviour require report-specific tests.
- [VERIFIED COMPLETE] Server PDF dependency is now available, rejecting the old “wkhtmltopdf missing” blocker.

Critical wholesale report backlog:

1. Reserved Stock and Available-to-Sell by item/warehouse/customer/order.
2. Reservation expiry/backorder/fulfilment and order-to-delivery status.
3. Customer credit exposure, overdue and approval override history.
4. Stock Ageing, slow/dead stock, expiry and damaged/rejected stock.
5. Import shipment/container status and landed cost/margin.
6. Purchase receipt/invoice matching and supplier performance.
7. Wholesale gross margin by transaction/customer/item and salesperson.
8. Payment allocation exceptions, bank reconciliation and cash collection.

### 12.10 Platform and Administration

| Feature | Status | Evidence / limitation |
|---|---|---|
| Users/Roles | [PARTIAL] | Restricted generated routes; dedicated safe lifecycle and role assignment verification incomplete. |
| Role Permission Manager | [PARTIAL] | Read-only matrix context; mutation workflow not reproduced. |
| User/field/company/warehouse permissions | [IMPLEMENTED, NOT VERIFIED] | Universal APIs filter permissions; representative single-role test users are absent. |
| Workflows/actions | [PARTIAL] | Generic workflow action adapter exists; zero active workflows on site. |
| Notifications | [STANDARD DESK ONLY] | Four discovered, two user-facing; Retail ERP notification centre parity absent. |
| Comments/assignments/sharing/tags/version | [PARTIAL] | Generated collaboration adapter only; interactive write tests unavailable. |
| Import/export/bulk actions | [MISSING] | No comprehensive Retail ERP Data Import/Export/bulk action adapter. |
| Deleted-document restore | [STANDARD DESK ONLY] | Restore action inventory entry unmapped. |
| Print Formats/Letter Heads | [PARTIAL] | Discovery and print/PDF selectors exist; 40 print-format inventory features still marked unimplemented. |
| Email Accounts | [BLOCKED] | Zero enabled outgoing accounts. |
| System health/background jobs | [PARTIAL] | Safe read-only facts; no production monitoring or job-control plan. |
| Scheduler/workers | [PARTIAL] | One worker online; production process topology and alerts unproven. |
| Error logs/audit history | [PARTIAL] | Backend logs/Version records exist; no complete operational UI/runbook. |

### 12.11 Other ERPNext Modules

| Module | Business relevance | Current classification |
|---|---|---|
| CRM | Required for lead-to-order if client uses it | [PARTIAL] generated Lead/Opportunity/Contact/Address/Campaign pages |
| Projects | Optional unless implementation/service projects are in scope | [PARTIAL] Project/Task provisional; Gantt/dependencies missing |
| Assets | Important administration, not core wholesale day-one sales | [PARTIAL] generated Asset/Movement; accounting lifecycle unverified |
| Quality | Potentially required for imported-goods inspection | [PARTIAL] Quality Inspection provisional; readings workflow missing |
| Support | Optional/important after go-live | [PARTIAL] Issue collaboration provisional; SLA dashboard missing |
| Manufacturing | Not required unless the business manufactures/re-packs/assembles | [PARTIAL] specialised provisional; do not treat as usable production planning |
| Subcontracting | Optional unless used operationally | [PARTIAL] specialised provisional |
| HR/Payroll | Not required for the stated initial wholesale ERP scope unless client confirms | [STANDARD DESK ONLY] / outside current priority routes |
| Maintenance | Optional unless fleet/equipment maintenance is in scope | [STANDARD DESK ONLY] |

## 13. Security and Permission Review

Positive controls verified in source:

- Server-owned entity/form/feature/action/report allowlists; the browser does not submit an arbitrary Python method.
- `frappe.get_list`, document-level `frappe.has_permission`, metadata field filtering, User Permission-aware document lookup, stale `modified` checks, and normal `doc.insert/save/submit/cancel` calls.
- Universal mass-assignment defence: `universal/api.py::_clean_payload` accepts only writable metadata fields and validates child/Dynamic Links.
- Guest rejection on protected APIs; Guest bootstrap contains no roles or records.
- Standard Frappe session cookie and CSRF token flow in `frontend/src/services/session.js`; credentials/session secrets are not stored in localStorage.
- Fixed mapped actions import known ERPNext helpers; no arbitrary import path is accepted from Vue.
- Runtime source scan found no direct SQL writes and no `ignore_permissions=True`.

Security work still required:

1. **[P0] Direct Guest authorization response disclosed an `exc` traceback envelope.** GET `standalone.authorize_frontend_route` returned HTTP 403 and `exc_type=PermissionError`, with `exc` present. The Vue frontend hides it, but the API response must be made production-safe and retested with production error settings.
2. **[P0] Handcrafted field-permission parity is not proven.** `form_api.py` uses fixed schemas and document permissions but does not visibly derive readable/writable field permlevels as comprehensively as `universal/api.py::_readable_fields/_writable_fields`. Audit each handcrafted field, especially accounts, valuation, credit and company data.
3. **[P0] Single-role/User Permission/company/warehouse/ownership/share tests are missing.** The one non-Administrator user has multiple Sales/Purchase/Accounts roles; there are no Stock User/Manager assignments.
4. **[P1] Generic upload endpoint and collaboration mutations require adversarial permission tests**, including attachment reassignment/removal, recipient/user enumeration, private-file download and CSRF failure.
5. **[P1] Amendment/duplicate copied-doc `docstatus=0` preparation requires controller review** against approved standard amendment helpers and the “never manually change docstatus” project rule.
6. **[P1] Desk blocking is not feature parity.** Unmapped users are redirected to Feature Unavailable, so permission-safe business continuity requires implementing every required route before go-live.
7. **[P1] No security/load/concurrency test report, dependency scan, secret-management review, HTTPS deployment or penetration test exists.**

## 14. Testing Status

| Command/check | Result on 2026-07-14 | Exact issue / impact |
|---|---|---|
| `bench --site site1.local list-apps` | PASS | Seven apps/versions recorded. |
| `bench --site site1.local run-tests --app my_store_ui` | BLOCKED | `Testing is disabled for the site!` Enabling `allow_tests` would change site configuration. Current regressions are not re-verified. |
| Static discovery of `tests/test_*.py` | PASS | 12 files, 100 `test_*` methods; existence is not execution. |
| `npm run build` | PASS | Vite 6.4.3, 107 modules, hashed bundle generated. |
| `npm run check` | PASS | Same Vite build with `--emptyOutDir=false`; no separate type checker. |
| Lint/type check | SKIPPED/UNAVAILABLE | No package scripts; `pre-commit`, `ruff`, `eslint`, `prettier` executables unavailable in current shell. Do not install during audit. |
| Feature inventory | PASS (generation), audit status FAIL | Current counts generated; fail is expected due 2,396 unmapped. |
| Strict parity audit | FAIL as designed | Exact ValidationError counts in Section 11. |
| Guest/live HTTP shell checks | PASS with one security finding | Shell/redirect/assets pass; Guest protected API includes traceback envelope. |
| Frappe Sales Invoice PDF | PASS | Valid one-page PDF; temporary output deleted. |
| `bench doctor` | PASS for minimal dev check | One worker online; no production topology proof. |
| Browser automation | UNAVAILABLE | No Chrome/Edge/Chromium/Firefox/Playwright/Cypress/Selenium. |

Manual browser plan before any production claim:

1. Provision a separate staging site and approved single-role test users (Sales, Stock, Purchase, Accounts, managers, restricted company/warehouse, shared/owner-only).
2. Test login, invalid/disabled/expired/OTP, logout and browser Back in Chrome and Edge.
3. Exercise every handcrafted route: list/new/detail/edit/save/submit/cancel/amend/map/return/print/PDF and validation preservation.
4. Exercise representative generated master and transaction routes; verify field permlevels and child tables.
5. Test desktop 1920/1440/1366/1280/1024 and mobile 768/390/375/320 at 80/100/125/150% zoom; check vertical scrolling, page-level horizontal overflow, dialogs, focus, keyboard and touch.
6. Test comments/files/assign/share/tags/version/email and inaccessible-record non-disclosure.
7. Use two simultaneous sessions to attempt duplicate submit, over-allocation, duplicate mapping and stock over-reservation.
8. Capture screenshots, console/network logs, created document chain and ledger/stock reconciliation evidence.

## 15. Performance and Multi-User Testing Status

[MISSING] No load test, concurrency test, report benchmark, queue saturation test, upload benchmark, or database query profile was found. The intended peak users, order lines, items, warehouses, daily transactions, attachment volume and report periods are not documented.

Existing positive design choices include server pagination, limited Link search, abortable frontend requests, list page-size caps, bounded related records, idempotency cache keys and no per-row Smart Sales stock/price calls. They are not substitutes for real workload tests.

Before go-live:

- Define expected/peak concurrent users and daily order/receipt/invoice volumes.
- Load-test catalogue search, available-to-sell/reservation, order submit, payment allocation, DN submit, invoice submit, priority reports and file upload.
- Race-test reservation and idempotency against multiple workers.
- Profile MariaDB indexes/query plans and Redis/queue latency.
- Verify scheduler/worker recovery and long/prepared reports.
- Set service objectives and alert thresholds.

## 16. Printing, PDF and Email Status

- [VERIFIED COMPLETE] `wkhtmltopdf` is **not missing**. Version 0.12.6.1 with patched Qt is at `/home/zaidh/.local/bin/wkhtmltopdf`.
- [VERIFIED COMPLETE] Standard Frappe Sales Invoice PDF generation succeeded on 2026-07-14. This rejects the old blocker recorded in `docs/universal-generated-ux.md` and `docs/priority-page-coverage.md`; those passages are historical/stale.
- [PARTIAL] Print Preview/PDF selectors exist for handcrafted and generated documents (`EntityActions.vue`, `SalesOrderActions.vue`, `UniversalPrintDialog.vue`, `universal/api.py::get_print_formats`). Every Print Format/letterhead/language and role is not verified.
- [BLOCKED] Outbound email cannot be considered operational because the site has zero outgoing Email Accounts. `universal/collaboration.py::email_document` exists but was not invoked to avoid external effects.
- [PARTIAL] PDF attachment uses standard `frappe.attach_print`, but email queue/delivery, bounce handling, sender domain/DKIM/SPF and attachment permissions require staging verification.

## 17. Data Migration and Accounting Verification Status

[MISSING] No migration mapping/rehearsal, trial import, reconciliation sign-off, opening-balance rehearsal or cutover plan was found.

Current document counts are not sufficient proof of correctness:

- Submitted Sales Orders: 5
- Submitted Delivery Notes: 0
- Submitted Sales Invoices: 5
- Submitted Payment Entries: 5
- Purchase Orders: 10
- Purchase Receipts: 0
- Purchase Invoices: 6
- Landed Cost Vouchers: 0
- Stock Reservation Entries: 0

Required accountant/stock-controller verification must reconcile source documents to Stock Ledger, GL Entry, Payment Ledger, receivables/payables, taxes, currency gains/losses, LCV valuation, returns and cancellations. Do not edit those ledgers directly.

## 18. Infrastructure and Deployment Status

Current evidence:

- Development server responds on `127.0.0.1:8000`.
- `bench doctor` sees one worker.
- Complete local backups from 2026-07-13 exist under `sites/site1.local/private/backups`, including database, public files, private files and site-config backup. Latest verified set prefix: `20260713_140620-site1_local-*`.
- Recovery tags/documentation exist for standalone and universal stages.

Missing production evidence:

- [MISSING] Separate staging and production environments in a client-owned cloud account.
- [MISSING] Domain, TLS/HTTPS, reverse proxy, firewall and production process manager validation.
- [MISSING] Encrypted off-server/immutable backup and retention policy.
- [MISSING] Successful restore drill. Local backup existence is not restore proof.
- [MISSING] Monitoring for HTTP, workers, scheduler, Redis, MariaDB, disk, files, queues, backups, errors and business posting exceptions.
- [MISSING] Alert routing/on-call/incident response.
- [MISSING] Deployment pipeline, dependency/security update policy, release approvals and tested rollback.
- [MISSING] Email delivery configuration.
- [MISSING] Capacity/load results and data retention plan.

## 19. Production Blockers

### P0 — Blocks production

1. Reservation and available-to-sell model absent/disabled; Smart Sales currently mislabels actual stock as available.
2. No server-enforced Credit/Non-Credit model or delivery-before-payment rules.
3. No shared transaction ID/register and no complete wholesale orchestration.
4. Current regression suite blocked; no staging role/browser/concurrency evidence.
5. Purchasing/import/LCV/returns and stock/accounting posting chain not end-to-end verified.
6. Guest API traceback disclosure and handcrafted field-permission parity require security correction/verification.
7. No restore proof, production infrastructure, monitoring or accounting sign-off.

### P1 — Required before client go-live

- Pick/pack/dispatch, partial delivery/payment, returns and one-final-invoice enforcement.
- Dedicated Purchase Receipt/Purchase Invoice return flows, Import Shipment and LCV.
- Journal Entry, Bank/Payment Reconciliation, serial/batch and Stock Reconciliation.
- Required wholesale reports, email, print-format acceptance and data migration rehearsal.
- UAT, training, user/admin/backup guides and support/go-live plan.

### P2 — Important after go-live

- Broader report/workspace/dashboard parity, optional integrations, advanced analytics, CRM automation, Projects/Assets/Quality/Support enhancements, and optional Manufacturing/Subcontracting/HR/Payroll/Maintenance based on confirmed scope.

## 20. Prioritised Remaining Roadmap

### P0 — Blocks production

#### 1. Stock reservation and Available-to-Sell

- **Current status:** Missing; ERPNext setting disabled; zero SREs; Smart Sales uses only `Bin.actual_qty`.
- **Why it matters:** Prevents overselling and enforces the fixed wholesale process without reducing physical stock early.
- **Files/modules:** `api.py`, Smart Sales, Sales Order actions, new allowlisted reservation service/UI, Stock Reservation Entry/Pick List ERPNext controllers.
- **Dependencies:** Approved business reservation policy, warehouse rules, expiry and backorder rules; staging data.
- **Acceptance criteria:** Actual/Reserved/Available by warehouse; atomic reserve/unreserve; expiry/cancel/partial/delivery release; no physical stock change until DN; multiple warehouse/backorder support.
- **Tests:** Concurrent double-reservation, partial delivery/cancel/return, expiry, warehouse permissions, negative/serial/batch cases, Stock Ledger unchanged until DN.
- **Risk:** Critical stock integrity.
- **Order:** First.

#### 2. Customer credit and delivery gate

- **Current status:** Missing; zero credit-limit rows and no custom classification.
- **Why it matters:** Controls receivables and determines whether goods may leave before payment.
- **Files/modules:** Customer schema/form/detail, standard credit-limit/payment terms, server credit-status service, Sales Order/DN action gate, workflow/audit trail.
- **Dependencies:** Approved fields/schema checkpoint, role matrix, overdue/override policy and accountant validation.
- **Acceptance criteria:** Credit/Non-Credit selection; official outstanding/overdue; available credit; authorised changes; reasoned manager override; delivery blocked/allowed correctly.
- **Tests:** Boundary/overdue/multi-company/partial payment/concurrent exposure/permission/audit tests.
- **Risk:** Critical financial exposure.
- **Order:** Second, designed alongside reservation.

#### 3. Wholesale Transaction ID/Register/orchestration

- **Current status:** Missing.
- **Why it matters:** Gives operations one reliable order-level view while retaining ERPNext document numbers.
- **Files/modules:** Approved shared-reference fields/service, `/sales/transactions`, reports/timeline/links/export, mapping propagation hooks without ledger edits.
- **Dependencies:** Schema approval and lifecycle policy.
- **Acceptance criteria:** Atomic `TRX-YYYY-######`; one row/order; SO/SRE/PE/Pick/Packing/DN/SI/returns links; secure financial columns; filters/exports/timeline.
- **Tests:** Propagation, partial documents, returns, permissions, concurrency, rollback and encoded routes.
- **Risk:** High operational traceability.
- **Order:** Third after reference design is approved.

#### 4. End-to-end stock/accounting security regression

- **Current status:** Blocked on current site; test execution disabled.
- **Why it matters:** Existing UI code cannot be trusted for production without repeatable evidence.
- **Files/modules:** All 100 tests plus new integration/security/concurrency suites on staging.
- **Dependencies:** Separate test site, approved role users, deterministic stock/accounts.
- **Acceptance criteria:** Clean repeatable suite; no leaked records; ledger/stock assertions; duplicate/stale actions blocked; no test residue.
- **Tests:** Full chain, permissions, race/load and rollback.
- **Risk:** Critical unknown regression/data integrity.
- **Order:** Establish test environment before feature implementation continues.

#### 5. Production platform and recovery

- **Current status:** Local dev only; local backups exist but restore unproved.
- **Why it matters:** Business continuity and security.
- **Files/modules:** Deployment repository/runbooks rather than ERP business code.
- **Dependencies:** Client cloud/domain/security ownership.
- **Acceptance criteria:** Staging/prod, HTTPS, off-server backups, successful restore, monitoring/alerts, deploy/rollback, incident runbook.
- **Tests:** Restore drill, failover/worker restart, backup alert, deployment rollback, security scan.
- **Risk:** Critical outage/data-loss.
- **Order:** In parallel with functional work.

### P1 — Required before client go-live

#### 6. Purchasing/import/landed-cost chain

- **Current status:** Generated provisional; Import Shipment missing; zero PR/LCV evidence.
- **Why it matters:** Core business is wholesale importing.
- **Files/modules:** Priority purchase routes, specialised returns/serial-batch, custom Import Shipment (approved schema), LCV/report adapters.
- **Dependencies:** Import process design, currency/tax/customs/accounting policy.
- **Acceptance criteria:** Supplier→MR/RFQ/SQ/PO→PR→LCV→PI→Payment, returns, attachments, multi-PO shipment and cost allocation.
- **Tests:** Official mappings, stock/GL/valuation, currency, partials/returns, permissions and concurrency.
- **Risk:** High inventory valuation/payables.
- **Order:** Immediately after P0 foundations.

#### 7. Pick/pack/delivery/returns

- **Current status:** DN partial; pick/pack/POD missing.
- **Why it matters:** Warehouse execution and customer proof.
- **Files/modules:** Pick List, Packing Slip, Delivery Trip, DN return/credit note, signature/attachments.
- **Dependencies:** Reservation workflow and warehouse devices/process.
- **Acceptance criteria:** Partial pick/delivery, failed delivery, POD, reservation release, correct return reversal.
- **Tests:** Stock Ledger and order percentage reconciliation, serial/batch, mobile scanning and permissions.
- **Risk:** High stock/customer disputes.
- **Order:** After reservation, before UAT.

#### 8. Finance operations and reports

- **Current status:** Payment custom; Journal/Reconciliation provisional/missing; reports provisional.
- **Why it matters:** Cash, AR/AP and closing controls.
- **Files/modules:** Journal Entry, Payment/Bank Reconciliation, report viewer/performance, statements and credit reports.
- **Dependencies:** Accountant-approved chart/tax/currency/dimensions.
- **Acceptance criteria:** Operational finance workflows and signed ledger/report reconciliation.
- **Tests:** GL/Payment Ledger/outstanding/reversal, multi-currency, bank matching and role restrictions.
- **Risk:** High financial reporting.
- **Order:** Parallel with purchasing completion.

#### 9. Email, migration, UAT and training

- **Current status:** Missing/unconfigured.
- **Why it matters:** Customer/supplier communication and adoption.
- **Files/modules:** Email Account/Print Formats, import templates, runbooks/training documentation.
- **Dependencies:** Approved email domain and cleansed legacy data.
- **Acceptance criteria:** Email/PDF delivered; migration reconciled; UAT signed; staff trained; go-live support agreed.
- **Tests:** Staging delivery, migration rehearsal, role scenarios and go-live simulation.
- **Risk:** High operational readiness.
- **Order:** Begin early, finish after stable workflows.

### P2 — Important after go-live

#### 10. Broader parity and optional modules

- **Current status:** 2,396 user-facing atomic features unmapped; many are not day-one wholesale requirements.
- **Why it matters:** Reduces Desk dependence and expands capability safely.
- **Files/modules:** Universal/report/visual/special adapters and inventory classifications.
- **Dependencies:** Signed scope priorities and stable core.
- **Acceptance criteria:** Each feature graduated only after applicable actions/permissions/browser tests.
- **Tests:** Registry, role, functional and visual coverage per batch.
- **Risk:** Scope dilution if done before P0/P1.
- **Order:** After go-live-critical acceptance.

No precise delivery dates are defensible until the business rules, staging environment, approved schema changes, users/data volumes and acceptance team are known.

## 21. Definition of Production Ready

Retail ERP may be called production-ready only when all of the following have evidence and sign-off:

- Complete wholesale flow passes, with no “Sales Transfer” step.
- Actual, Reserved and Available stock are correct per warehouse.
- Concurrent users cannot over-reserve.
- Credit and Non-Credit rules are enforced server-side.
- Payment allocation and outstanding balances reconcile.
- Delivery Notes reduce stock and reservations correctly.
- Sales Invoices post once per agreed workflow and returns reverse correctly.
- Purchasing, import shipment and landed cost work.
- AR/AP, taxes, currency and financial statements are accountant-approved.
- Role, document, field, User Permission, company, warehouse, owner and share restrictions pass.
- Required reports, Print Formats, PDF and email pass.
- Data migration and opening balances are rehearsed/reconciled.
- Staging, browser/mobile, concurrent-user/load and security tests pass.
- Off-server backup and restore are proven.
- HTTPS, monitoring, alerts, scheduler/workers and incident procedures are configured.
- Client UAT, training, support, go-live and rollback are signed off.

Current outcome: **NOT YET PRODUCTION-READY**.

## 22. Exact Commands for the Next Agent

Preserve the current changes and begin with read-only checks:

```bash
cd /home/zaidh/frappe-bench
git -C apps/my_store_ui status --short
git -C apps/my_store_ui branch --show-current
git -C apps/my_store_ui rev-parse HEAD
bench --site site1.local list-apps
```

Review this handoff and inventory:

```bash
sed -n '1,260p' apps/my_store_ui/AGENT_HANDOFF.md
sed -n '1,180p' apps/my_store_ui/docs/feature-audit-summary.md
sed -n '1,260p' apps/my_store_ui/docs/priority-page-coverage.md
```

After explicit approval to use a separate test site or enable testing there:

```bash
bench --site <approved-test-site> run-tests --app my_store_ui
```

Do **not** run `set-config allow_tests true` on `site1.local` without approval.

Frontend verification:

```bash
cd /home/zaidh/frappe-bench/apps/my_store_ui/frontend
npm run build
npm run check
```

Inventory/parity (once after a coherent implementation batch):

```bash
cd /home/zaidh/frappe-bench
bench --site site1.local execute my_store_ui.audit.feature_inventory.generate_complete_inventory
bench --site site1.local execute my_store_ui.audit.feature_inventory.audit_feature_parity
```

The strict audit must exit non-zero until all failure counts are resolved.

Read-only health/PDF checks:

```bash
bench doctor
command -v wkhtmltopdf
wkhtmltopdf --version
```

Recommended next implementation sequence: create an approved staging/test site and role matrix; design/approve reservation and customer-credit schemas/policies; implement atomic reservation/available-to-sell; then Transaction ID/Register; then purchasing/import/LCV.

## 23. Recovery and Rollback Information

Known recovery tags:

- `pre-standalone-retail-erp` — documented commit `110d1fb97f41e573a8c5ec4c27b81a74754b0697`
- `pre-universal-frontend-engine` — documented commit `9349636c617939361d29c1bf8091e175660cfaa6`
- `pre-priority-page-expansion` — points to the pre-expansion state around `98794f8`
- `stage-0-baseline`

Latest complete local backup set:

```text
/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-site_config_backup.json
/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-database.sql.gz
/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-files.tar
/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-private-files.tar
```

These files were listed and sized during the audit, but no restore was attempted. Do not use `git reset`, restore a database, or replace files on a live site without preserving subsequent data, obtaining approval, and entering a maintenance window.

Safe application rollback approach:

1. Preserve/commit current work on a separate branch.
2. Use an approved revert or recovery branch from the appropriate tag; never reset a dirty worktree.
3. Rebuild `apps/my_store_ui/frontend` with `npm run build`.
4. Clear only required normal Frappe website/asset caches under an approved deployment process.
5. Verify `/`, `/retail-erp/home`, login, business routes, APIs, assets, print/PDF and old-route redirects.
6. Restore database/files only if the release included database/data changes and the restore is explicitly approved and rehearsed.

Detailed historical instructions: `docs/pre-standalone-recovery.md` and `docs/pre-universal-frontend-recovery.md`.

## 24. Files and Documentation Index

| Purpose | Path |
|---|---|
| This handoff | `apps/my_store_ui/AGENT_HANDOFF.md` |
| App hooks | `apps/my_store_ui/my_store_ui/hooks.py` |
| Standalone session/auth | `my_store_ui/standalone.py`, `frontend/src/services/session.js` |
| Desk guard | `my_store_ui/route_guard.py` |
| Route/navigation registry | `my_store_ui/services/frontend_routes.py`, `my_store_ui/services/priority_registry.py` |
| Handcrafted schemas | `my_store_ui/services/entity_schemas.py`, `my_store_ui/services/form_schemas.py` |
| Handcrafted APIs/actions | `entity_api.py`, `form_api.py`, `sales_order_actions.py`, `document_actions.py`, `payment_api.py` |
| Smart Sales | `api.py`, `frontend/src/pages/priority/SmartSalesPage.vue` |
| Universal engine | `my_store_ui/universal/registry.py`, `api.py`, `collaboration.py`; `frontend/src/pages/generated/*` |
| Priority reports/special pages | `my_store_ui/priority_pages.py`, `frontend/src/pages/priority/*` |
| Router | `frontend/src/router/index.js`, `frontend/src/router/routes.js` |
| Tests | `my_store_ui/tests/` |
| Canonical inventory | `docs/erpnext-v15-complete-inventory.json` |
| Human inventory | `docs/erpnext-v15-complete-inventory.md` |
| Audit summary/unmapped | `docs/feature-audit-summary.md`, `docs/unmapped-features.md` |
| Feature matrix | `docs/frontend-feature-matrix.md` |
| Priority coverage/backlog | `docs/priority-page-coverage.md`, `docs/specialised-page-backlog.md` |
| Standalone/browser notes | `docs/standalone-routing.md`, `docs/standalone-browser-verification.md` |
| Universal docs | `docs/universal-frontend-foundation.md`, `docs/universal-generated-ux.md`, `docs/universal-feature-registry.json` |
| Recovery | `docs/pre-standalone-recovery.md`, `docs/pre-universal-frontend-recovery.md` |

Historical documents dated 2026-07-13 that say wkhtmltopdf is missing are now stale; the live 2026-07-14 PDF test in Sections 7 and 16 supersedes that environment warning.

## 25. Final Honest Readiness Assessment

**NOT YET PRODUCTION-READY.**

The project has a strong reusable frontend/security foundation and meaningful handcrafted sales/payment code. The current build and standalone delivery work, server PDF is repaired, feature classification is complete, and the parity guard is doing its job. However, the intended wholesale operating model is not present: reservation is disabled, available-to-sell is wrong/incomplete, customer credit controls are missing, transaction tracking is missing, purchasing/import/landed cost and warehouse execution are provisional, and current regression/browser/concurrency/accounting/restore evidence is absent.

Auditable coverage is **86/2,482 = 3.46% registered user-facing feature coverage**, with only six handcrafted DocTypes and all 52 generated DocTypes still provisional. A planning estimate of 15–20% maturity reflects reusable foundations, not production completeness. Production approval must wait for all Section 21 conditions, especially reservation/credit correctness, complete stock/accounting reconciliation, staging role/concurrency tests, backup restore, UAT and accountant sign-off.
