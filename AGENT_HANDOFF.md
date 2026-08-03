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

## 0b. Update — URGENT MAPPING MISSION, final mapping pass 1 (2026-07-14, later same day)

A second follow-up mission ran on top of 0. and the wholesale-core batch above,
still on branch `full-feature-parity`, recovery tag
`pre-map-all-remaining-20260714-2056`. Re-ran the live audit first: confirmed
zero drift (2,482 user-facing, 1,746 unmapped, matching 0. exactly). Then
completed 8 real, independently committed, verified batches:

- **25 more safe master DocTypes** routed through the universal engine
  (Employee, Branch, Print Format, Incoterm, POS Coupon, ...), each confirmed
  `istable=0`/`issingle=0` before routing.
- **1 more required report** routed (Addresses And Contacts); 3 country-specific
  regional tax reports (IRS 1099, UAE VAT 201, VAT Audit Report) correctly
  reclassified `not_required` with real jurisdiction reasons.
- **Audit correction:** added `SYSTEM_INTERNAL_DOCTYPE_NAMES` — ~30 ledger
  tables (GL Entry, Stock Ledger Entry, Bin, Payment Ledger Entry, ...),
  repost/repair tools, and Settings singletons were wrongly falling into
  `unavailable_with_reason` purely because their module defaults to
  P1/P2_required; corrected to `internal` (never exposed as pages, per the
  "no unsafe ledger/stock records" rule). Found and fixed a scoping bug where
  this rule also wrongly caught GL-Entry-*based reports* (UAE VAT 201, VAT
  Audit Report are real Query Reports, not ledger tables).
- **Real bug found and fixed:** the handcrafted **Smart Sales** page — a
  protected primary route — was showing `unavailable_with_reason` because of
  a stale pre-SPA Frappe "Page" doctype stub (`my_store_ui/page/smart_sales/`)
  that the inventory generator was matching instead of the real Vue SPA route.
  Corrected via evidence pointing at `frontend/src/router/routes.js`.
- **19 native ERPNext module workspaces** (Selling, Buying, Stock, Accounts
  sub-workspaces, CRM, POS Awesome, ...) reclassified `special_adapter`
  (genuinely superseded by Retail ERP's own nav module landing pages) or
  `internal` (pure Desk admin workspaces like Home/Tools/Integrations).
- **Document-action crediting extended beyond the 6 handcrafted DocTypes:**
  the universal engine's action handler already serves generic lifecycle
  actions (submit/cancel/amend/duplicate/rename) and 9 real `MAPPED_ACTIONS`
  document-conversion handlers (Quotation→SO/SI, Material Request→RFQ/PO,
  PO→Receipt/Invoice, Opportunity→Quotation, Lead→Customer, ...) for ANY
  routed doctype — the audit only credited the 6 handcrafted ones. 18 real
  actions now correctly credited across Lead, Opportunity, Quotation,
  Material Request, Purchase Order, Purchase Receipt, Supplier Quotation.
- **Step 13 corrected production-parity audit** built
  (`parity_registry.corrected_production_parity_audit`), written to
  `docs/full-parity/corrected_production_parity_audit.json`.

**Net result:** `unmapped_user_facing` (route-based) 1746 → **1699**.
Registry: `unavailable_with_reason` 620 → **491**, `internal` 858 → **900**,
`generated_provisional` 728 → **776**, `implemented_unverified` 101 → **137**,
`special_adapter` (strategy) 95 → **130**.

The Step 13 corrected metrics give the truthful picture the raw route count
can't: **`corrected_unmapped_user_facing = 0`** (every one of the 2,482
features now has a real, documented registry status — nothing left
unclassified) but **`required_but_missing = 367`** (the honest count of
P0/P1/P2 capabilities with no real implementation yet — mostly unbuilt
dashboards/charts, and the Stock/Accounts document actions + special
finance/stock adapters + purchasing/imports + platform admin + POS Awesome
batches that this pass did not reach — see `docs/full-parity/BLOCKERS.md`
→ "URGENT MAPPING MISSION" for the exact list and why).

**Feature inventory mapping is substantially advanced, but the system is
NOT yet production-ready** — `required_but_missing = 367` and none of it has
browser or `bench run-tests` behavioural verification (same `allow_tests`
disabled / no browser installed blockers as before). No schema, site-config,
or other-app change was made. Recovery tag:
`pre-map-all-remaining-20260714-2056`.

## 0c. Update — URGENT MAPPING MISSION, pass 2 continuation (2026-07-14, later same day)

Continued directly on the same branch from 0b (commit `b3f0c5a`). 5 more real
batches, all independently committed and verified (`test_parity_registry.py`
7/7, route/report verifiers 0 failures, `npm run build` PASS every time):

- **Batches 7-8 (commit c2f95fa):** added 5 new allowlisted `MAPPED_ACTIONS`
  to `universal/api.py` — Purchase Receipt→Purchase Return/Landed Cost
  Voucher, Material Request→Stock Entry, Purchase Invoice→Debit Note,
  Journal Entry→Reverse Journal Entry. Each verified by directly importing
  the real erpnext controller function inside a `frappe.init()` context
  (`bench execute` has an unrelated pre-existing quirk with this app's
  whitelisted GET methods) before wiring it in.
- **Batch 13 (commit 0dcc9a0):** classified 45 platform/technical DocTypes
  (Integrations/OAuth/webhooks, Email infrastructure, Workflow *design*
  tooling, Automation config, system logs, one-time setup wizards) →
  `internal`; credited 9 report-attached financial-statement print formats
  (Trial Balance Standard, General Ledger Standard, etc.) via their
  already-routed report.
- **Batch 14 (commits 393c45a, 6a3d661):** classified all 23 POS
  Awesome-module registry entries per Step 12's taxonomy — 2 → `not_required`
  (Kenya M-Pesa integration, wrong jurisdiction), 18 → `external_app_adapter`
  (genuinely handled inside the POS Awesome app's own UI, reachable via the
  existing `/pos` launcher — including 5 ERPNext-core POS doctypes that POS
  Awesome creates and manages internally).

**Net result:** `required_but_missing` dropped from 367 → **327**.
`implemented_unverified` 137→160, `internal` 900→976, `unavailable_with_reason`
491→380, `external_app_adapter` (a strategy this pass used for the first
time) 0→18.

**Batches 10, 11, 12 remain genuinely open** — investigated Pick List's
`create_delivery_note`/`create_stock_entry` as a candidate for Batch 11 and
deliberately did NOT wire them into `MAPPED_ACTIONS`: reading the real
ERPNext source showed `create_delivery_note` can create multiple Delivery
Notes per call and may save documents internally, and `create_stock_entry`
takes a JSON-serialized Pick List rather than a docname — both break the
simple "get_mapped_doc → insert()" pattern every other `MAPPED_ACTIONS` entry
uses. Forcing them in without a dedicated adapter risked duplicate documents
or broken behaviour. Left honestly `unavailable_with_reason`; see
`docs/full-parity/BLOCKERS.md` for the full remaining list (special finance
adapters, special stock adapters, purchasing/imports, and ~255 remaining
document actions across Asset/Company/Bank Reconciliation flows).

**Still NOT production-ready** — `required_but_missing = 327`, still no
browser or `bench run-tests` verification. No schema, site-config, or
other-app change was made this pass either.

## 0d. Update — Payment Reconciliation adapter, pass 3 (2026-07-14, later same day)

Given the choice between more classification sweeps or building one real
adapter properly, built **Payment Reconciliation** end-to-end (commit
`54f3859`): backend module `my_store_ui/wholesale/payment_reconciliation_api.py`
(3 fixed-purpose whitelisted functions reproducing ERPNext's standard 3-step
reconciliation flow via the real `PaymentReconciliation` virtual-doctype
controller — never the generic browser-suppliable `run_doc_method`), a new
Vue page (`PaymentReconciliationPage.vue`) wired into the existing route
dispatch, and 2 search helpers for the filter form.

Verified behaviourally (read-only, rolled back) against real site1 data:
`get_unreconciled_entries` correctly found 2 outstanding invoices for Grant
Plastics Ltd. and resolved the right receivable account. Guest access is
blocked on every endpoint including `reconcile`. The write path
(`allocate`/`reconcile`) is source-verified against ERPNext's own Desk
client signatures but not behaviourally exercised — there is no unallocated
Payment Entry on site1 to reconcile against without creating test data.

`required_but_missing`: 323 → **319**. Batches 11 (special stock adapters)
and 12 (purchasing/imports) remain fully open; Batch 10 has one adapter done
(Payment Reconciliation) with several still open (Bank Reconciliation Tool,
GL/Trial Balance/P&L/Balance Sheet drill-down, Budgets, period-closing
tools) — same template applies to each if continued.

The audit below (Sections 1–25) remains valid as the production-readiness picture.

## 0e. Update — FINISH ACCOUNTING FIRST, pass 4: Bank Reconciliation Tool adapter (2026-07-15)

Resumed on branch `full-feature-parity`. Starting HEAD was `85e1e3c` (one
commit ahead of the `25740f1` cited in the mission brief — an unrelated
login-page CSS fix; worktree was clean either way). Re-ran the live corrected
audit first: `required_but_missing = 319`, exactly matching the mission
brief with zero drift. Froze the full 319-entry list to
`docs/full-parity/required_missing_before_accounting_completion.json` and
tagged `pre-finish-accounting-and-319-20260715-1316` before any change.

Built **Bank Reconciliation Tool** (Priority 1 of the mission), the single
largest specifically-requested adapter: `my_store_ui/wholesale/
bank_reconciliation_api.py` (14 fixed-purpose whitelisted functions —
summary/matches read paths, update-reference/reconcile/unreconcile/create-
payment-entry/create-journal-entry/auto-reconcile write paths, all delegating
to erpnext's real `bank_reconciliation_tool` controller functions and `Bank
Transaction.remove_payment_entries`, never a generic method-path RPC) +
`frontend/src/pages/priority/BankReconciliationPage.vue` (summary banner,
transaction table, match panel, Payment/Journal Entry creation with a
read-only preview step before posting). Wired through
`priority_pages.py`/`PriorityRoutePage.vue` exactly like Payment
Reconciliation. Registry crediting required refactoring the old flat
`BUILT_ADAPTER_ACTIONS` set into a parent-doctype-keyed
`BUILT_ADAPTER_ACTIONS_BY_PARENT` map, because this adapter also serves two
of `Bank Transaction`'s own document actions (see `DECISIONS.md` D13).

Verified: all 14 new endpoints reject Guest with `AuthenticationError`; the
route resolves correctly; search helpers return real permission-filtered
site1 data; the missing-bank-account error path fails safely. Write paths
are source-verified against erpnext's own controller signatures but not
behaviourally exercised — site1 has zero `Bank Account`/`Bank Transaction`
records to reconcile against without creating test data (same category of
gap as Payment Reconciliation's write path in pass 3).

`required_but_missing`: 319 → **312**. Registry tests 7/7 pass,
`validate_parity_registry` passes, route/report verifiers 0 failures,
`npm run build` passes, `generate_complete_inventory` confirms zero drift
(fingerprint unchanged, route-based `unmapped_user_facing` still 1699 — this
batch changed which component serves an existing route, not route presence).

**Not done this pass** (left honestly `unavailable_with_reason`): Bank
Statement Import, Bank Clearance (a genuinely different, older doctype — see
`DECISIONS.md` D14), Bank.refresh_plaid_link, Bank Account's
make_bank_account/unlink_external_integrations actions, GL/Trial Balance/P&L/
Balance Sheet/Budget/Accounting Dimension dedicated adapters (Priorities 2–3
of the mission), period closing (Priority 4), and remaining payment tools
(Priority 5). See `PROGRESS.md` pass 4 and `BLOCKERS.md` for the exact list.
Full mission scope (Stock/Purchasing/remaining actions/dashboard widgets)
was not reached this pass — see `docs/full-parity/required_missing_latest.json`
for the current complete gap list.

## 0f. Update — Priority 2/3 verification + real bug fixes, passes 5-6 (2026-07-15)

Continued directly from 0e. **Priority 2 (financial report drill-downs)**:
checked the mission's report list against the registry first rather than
assuming new adapters were needed — all nine real reports (GL, Trial
Balance, P&L, Balance Sheet, Cash Flow, AR, AP, Customer/Supplier Ledger
Summary, Payment Ledger) were already routed `generated_provisional` from an
earlier batch. Reading their real ERPNext filter definitions instead of
trusting the existing config found **three real bugs**: AR/AP used the
wrong filter fieldname (`posting_date` vs the real `report_date`, so the
date filter was silently ignored), Customer Ledger Summary used `customer`
instead of the real `party`, and none of them exposed cost_center/
finance_book/project/currency filters at all despite the mission explicitly
asking for them. Fixing the filter set surfaced a fourth, deeper bug found
by reproducing it live: `cost_center`/`project`/`party`/`account` need a
real Python **list**, not a JSON string, on the reports that use
`erpnext...get_cost_centers_with_children` — confirmed by hitting the exact
`ValidationError` against site1 with the first fix attempt, then corrected.
All fixes verified behaviourally against real site1 data (General Ledger
75/116/14 rows across filter variants, AR/TB/PL/BS/CF/SLS all ran clean).
"Bank Book"/"Cash Book" from the mission's report list are not installed
ERPNext v15 reports (confirmed via `frappe.db.exists`) — correctly left as
"use General Ledger filtered by account", not faked into a route.

**Priority 3 (Budget/accounting setup)**: verification-only pass — Budget,
Monthly Distribution, Accounting Dimensions, Cost Center/Account tree,
Fiscal Year, Finance Book, Payment Terms(+Template), Mode of Payment, Bank
Account, Exchange Rate Revaluation were all already routed; no new code
needed. A handful of tree-mutation document actions (`convert_to_group` /
`merge_account` / etc.) remain genuinely open — `PriorityTreePage.vue` is
read-only (19 lines), so these need real adapter work in a future session,
not a quick credit.

`required_but_missing`: 312 (unchanged by passes 5-6 — both were
verification/correctness passes, not new-routing passes; the value was
proving already-"implemented" reports actually work, and confirming
Priority 3 needed no new routes).

**Session status at handoff:** Priorities 1-3 of the mission are complete
(1 genuinely built, 2-3 verified/fixed). Priorities 4-5 (period closing,
remaining payment tools) and the entire post-accounting scope (Stock,
Purchasing, remaining document actions, dashboard widgets) were not reached
this session — continuing the mission means picking up at Priority 4
(`Period Closing Voucher`/`Process Period Closing Voucher`/`Process
Deferred Accounting`) using the same read-real-source-first, verify-against-
live-site1 methodology established in passes 4-6. See `BLOCKERS.md` →
"FINISH ACCOUNTING FIRST mission status" for the exact per-priority
breakdown and `docs/full-parity/required_missing_latest.json` for the
current complete 312-item gap list.

## 0g. Update — CONTINUE FROM 2e4c314: Priority 5 complete, Batch 11/12 warm-up (2026-07-15, session end)

Continued directly from 0f (commit `2e4c314`). Four more real, independently
committed batches, same methodology (read real erpnext source, verify
against live site1, regenerate the canonical inventory before re-auditing
whenever routes changed):

- **Purchase Invoice** (`bd9ce0a`): block_invoice/unblock_invoice/
  change_release_date (real controller methods) + 2 dedups.
- **Serial and Batch Bundle + Process Payment Reconciliation(+Log)**
  (`a498b70`): 3 more regular doctypes routed. Bank Clearance/Pegged
  Currencies investigated and left open (Single doctypes; Bank Clearance
  confirmed functionally different from Bank Reconciliation Tool, not
  reclassified without stronger justification).
- **Stock module** (`f0129f8`): Purchase Receipt close/reopen + 3 dedups;
  Warehouse/Batch/Serial No ledger navigation actions; Stock Ledger's
  filter set extended with `batch_no`; Batch.recalculate_batch_qty.
- **Purchase Order** (`9567d72`): `payment` action (shared, renamed
  `dunning_payment`→`make_payment_entry_generic`) + 3 dedups. Investigated
  Supplier Quotation's `make-purchase-invoice` and found no matching
  button in source — left honestly uncredited rather than guess.

`required_but_missing`: 285 → **264**. Registry tests 7/7 pass throughout,
route verifier steady at 204 served/0 failed, `npm run build` passes on
every commit.

**Full session arc from the mission's stated starting point:** 319 → 264
(55 items resolved, ~17% of the frozen baseline) across 10 commits, all
individually verified (registry tests, route/report verifiers, live site1
behavioural checks where safe test data existed, source-only for write
paths without safe test data) and documented with the reasoning, not just
the count. Zero fake routes, zero unsafe generic method execution, zero
reclassifications-to-hide-a-gap — every credited item has either real new
code or a source-verified scanner-noise dedup explanation.

**Genuinely unbuilt, not reached this session** (~264 remaining): Pick List
actions (reserve/unreserve/reserved-stock — `create_delivery_note`/
`create_stock_entry` were already ruled out in an earlier session), Stock
Reconciliation and Stock Entry purpose-specific actions, Material Request's
13 actions, Request for Quotation/Supplier Quotation's remaining actions,
Landed Cost Voucher, Blanket Order, Drop Shipping, Supplier's ledger/
pricing-rule shortcuts, the entire CRM (33) and Selling (18) modules, and
all 59 dashboard-chart/number-card/dashboard entries (a different kind of
work — real Vue chart components reading live data, not document-action
wiring). See `docs/full-parity/required_missing_latest.json` for the exact
264-item list and `PROGRESS.md`/`BLOCKERS.md` for the module-by-module
breakdown of what's left.

## 0h. Update — "complete all pending tasks" continuation, session end at 222 (2026-07-15)

Continued directly from 0g (commit `9567d72`) after being asked to work
through every remaining pending task without pausing for approval. Nine
more real, independently committed batches:

- **Pick List** (`c6bf92c`): stock reservation controls (create/cancel_
  stock_reservation_entries, update_current_stock, reserved_stock nav) -
  real doc-bound whitelisted methods, never touching Bin/Stock Ledger Entry
  directly, reproducing erpnext's own `enable_stock_reservation` +
  `has_unreserved_stock()`/`has_reserved_stock()` gating exactly (verified
  live: site1 has reservation disabled, so the gate correctly suppresses
  the action).
- **Material Request** (`d7ae13f`): 3 real MAPPED_ACTIONS (make_supplier_
  quotation/create_pick_list/make_in_transit_stock_entry, type-gated to
  match erpnext's per-`material_request_type` Desk buttons exactly) + 9
  scanner-noise dedups.
- **Stock Entry** (`fe665e1`): make_stock_in_entry ("End Transit").
- **Request for Quotation** (`6104a36`) and **Supplier Quotation**
  (`40a3e35`): found and fixed 2 **dead credits** - internal MAPPED_ACTIONS
  keys chosen in earlier sessions that never matched the real scanner
  action key, so the (already-correct) code was silently uncounted. Added
  4 real new actions (supplier_quotation_comparison, send_emails_to_
  suppliers, Supplier Quotation→Quotation).
- **Supplier** (`3b49018`): accounting_ledger/accounts_payable navigation.
- **Purchase Invoice** (`b46432e`): make_lcv (Landed Cost Voucher).
- **Lead/Opportunity** (`7fbcbdc`): 2 more dead-credit fixes + 3 real new
  actions (Lead.make_quotation, Opportunity.make_supplier_quotation/
  make_request_for_quotation).
- **Quotation/Opportunity** (`0842d88`): set_as_lost (shared
  declare_enquiry_lost() doc method).

`required_but_missing`: 258 → **222**. Registry tests 7/7 pass throughout,
route verifier steady at 204 served/0 failed (action-only batches past
Pick List), report verifier 183 served/0 failed, `npm run build` passes on
every commit.

**Full session arc (both continuations combined, starting from the mission
brief's frozen baseline):** 319 → **222** (97 items resolved, ~30% of the
frozen baseline) across **21 commits**, every one individually verified
(registry tests, route/report verifiers, live site1 behavioural checks
where safe test data existed, source-only with explicit source citations
for write paths without safe test data). Zero fake routes, zero unsafe
generic method execution, zero unjustified reclassifications. Found and
fixed one real frontend bug (report/tree pages ignoring URL query strings),
one encoding bug (`+` vs `%20`), and four "dead credit" bugs from earlier
sessions (see DECISIONS.md D22) - all confirmed via source reading and
before/after count verification, never assumed.

**Not reached this session:** all 59 dashboard-chart/number-card/dashboard
entries (needs real Vue chart components, a different kind of work than
document-action wiring), the remainder of CRM/Selling (Prospect, Campaign,
Communication-based Lead creation), Blanket Order/Drop Shipping/Supplier
Scorecard, Bank Clearance/Pegged Currencies (Single doctypes needing the
special-page pattern), and a genuine systematic audit for more dead
credits like the 4 found this pass (flagged as real, cheap remaining work
in BLOCKERS.md). See `docs/full-parity/required_missing_latest.json` for
the exact 222-item list with module/type breakdown.

## 0i. Update — self-audit pass: 3 bugs found in my own work (2026-07-15, commit `821ac57`)

Asked to audit this session's work and fix mistakes. Re-drove the navigation
actions **end-to-end** (action → route → actually running the destination
report) instead of only asserting the returned route string, which is all the
original batches checked. Found and fixed **3 real bugs**:

1. **General Ledger `account` → JSONDecodeError.** Broke the Account and
   Warehouse "General Ledger" actions *and* any user picking an Account in the
   GL filter form. Cause: GL `parse_json`s account/party/cost_center/project;
   my drill-down batch fixed 3 of 4 and missed `account` — I half-fixed the bug
   and declared it fixed. Now returns 4 real rows.
2. **Pick List → Reserved Stock → ValidationError.** Omitted the mandatory
   `from_date`/`to_date` that `reserved_stock.py` requires and erpnext's own JS
   sends. Crashed on every click. Now runs clean.
3. **Gross Profit → TypeError on every run** (pre-existing, from the earlier
   generated-reports batch). `group_by` is reqd-with-default in erpnext and its
   `execute()` indexes by it; no default was supplied. Now returns 16 real rows.

Also replaced spot-checking with a systematic script cross-checking every
`REPORT_FILTERS` entry against real erpnext source. It found 2 gaps manual
review missed — **and one false positive** (Fixed Asset Register, which uses
plain `==`); blindly applying its output would have broken a working report.
See DECISIONS.md **D23** (verify the destination, not the route string) and
**D24** (per-report filter semantics aren't guessable from the fieldname).

`required_but_missing` unchanged at **222** — correctness fixes to features the
metric already counted as done. **The honest implication: the 222 figure counts
routes/adapters that exist, and at least 3 of them did not actually work until
this audit.** Only the actions I built this session were re-driven; the ~180
generated reports have never been run per-declared-filter and are the most
likely place for more of the same. Flagged in BLOCKERS.md as the highest-value
remaining verification work.

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

## 26. SMJ Global UI Theme Rebuild (2026-07-16)

A UI-only pass applied the SMJ Retail ERP design system (colours,
typography, spacing, a real custom icon pack) across the entire existing
frontend, without remapping any routes or changing the parity registry.
Recovery tag: `pre-global-ui-theme-rebuild-20260716-0832`.

**What changed:**
- `frontend/src/design/tokens.css` rewritten to the exact SMJ palette from
  `SMJ_Retail_ERP_UI_Design_Pack/03_design_specs/`. Every existing route's
  `meta.accent` value keeps working unchanged — the legacy accent keys
  (`blue`, `dark-blue`, `purple`, `pink`, `green`, `orange`, `turquoise`)
  now resolve to the matching SMJ module colour.
- 54 new custom SVG icon components in `frontend/src/components/icons/`
  (25 required by `ICON_PACK_SPEC.md` + utility icons), replacing every
  placeholder glyph (`☰ ⌕ ◆ ◇ ⌄ ×`) across the header, module nav, mobile
  nav, search, user menu, and several list/empty-state views.
- Header restyled to the exact `90deg #07369D → #071B72` gradient; buttons/
  inputs/icon-buttons bumped to the 44px touch-target/control-height spec.
- `frontend/src/composables/pageActions.js` +
  `frontend/src/components/shell/HeaderPageActions.vue` added as the shared
  mechanism for pages to push actions into the header — infrastructure only,
  no page wired to it yet (see `docs/ui/SMJ_HEADER_NAVIGATION.md`).
- All hardcoded hex colours in `frontend/src/design/*.css` (base, universal,
  generated-ux, priority-pages, standalone) that carried semantic meaning
  (danger/warning/module-accent gradients) were replaced with the new
  semantic/module tokens. A full-repo grep confirmed zero hardcoded hex
  colours inside any `.vue` page template, before or after — every page
  already delegated colour to these shared stylesheets, which is why this
  cascades to every handcrafted and universal page without per-page edits.
- `npm run build` passes after every batch (111 → 171 modules once icons
  were wired in).

**Explicitly not done / known gaps:** page-level action bars were not
relocated into the header (infrastructure exists, adoption doesn't yet); no
notification bell (no backend exists — see `SMJ_HEADER_NAVIGATION.md`); no
browser screenshots (Playwright not installed, not installed without
approval — see `SMJ_VISUAL_REGRESSION.md`); pixel-level layout matching
against the 9 reference preview images was not attempted, only the token
values were matched. Full detail in `docs/ui/*.md`.

**Parity status unchanged**: `required_but_missing = 222`,
`unclassified = 0`. This was a visual-layer pass only.

## 27. Browser Verification & UI Correction Pass (2026-07-16)

A follow-up to Section 26 that tried to prove the UI theme actually works,
not just that it builds. Recovery tag:
`pre-ui-browser-verification-20260716-0903`.

**Browser automation status: blocked, not skipped.** Playwright was
attempted with explicit user approval (`npm install -D @playwright/test`,
including `NODE_OPTIONS=--use-system-ca`) and fails at the network layer —
`UNABLE_TO_VERIFY_LEAF_SIGNATURE` against the standard CA bundle, and a
plain-HTTP request to the same host returns `403`. This points at a
sandbox egress proxy, not a fixable local config issue. `--insecure` was
deliberately not attempted. Full detail in `docs/ui/SMJ_VISUAL_REGRESSION.md`.

**What ran instead:** an authenticated HTTP verification harness
(committed at `frontend/e2e/http_verify.py`) against the live `bench serve`
instance, plus a focused code audit of the application shell. The
Administrator password was rotated for this session at the user's explicit
instruction; it is not recorded anywhere in this repo. This is a local dev
site with no other test accounts.

**Genuinely verified (not just "built"):** login, session bootstrap,
navigation payload (all 11 modules' icon keys match the frontend's icon
map), global search returning real records, all 9 module dashboards, the
universal engine's list config/document list/missing-record handling for a
real generated doctype, the tree page (Chart of Accounts, real nodes), a
report executed end-to-end with real filtered data (Sales Register, 2
rows), and logout genuinely terminating the server-side session. Full
results in `docs/ui/SMJ_BROWSER_VERIFICATION.md`.

**Defects found and fixed** (`docs/ui/SMJ_BROWSER_ISSUES_FIXED.md`):
1. `ModuleNavigation` and `UserMenu` dropdowns didn't close on Escape —
   fixed, now matches `GlobalSearch`/`MobileNavigation`'s existing behaviour.
2. No active-module indication on desktop (mobile had it, desktop's plain
   `<button>`-based module toggles didn't) — fixed with `aria-current` +
   `.is-active` styling.
3. `.ref-module-navigation` had no overflow-x handling for the 11 modules
   now in the live navigation payload at the 1181–1450px range — added the
   horizontal-scroll fallback the mission itself endorses.

**False alarm, corrected:** the skip-to-content link was briefly flagged as
missing (a `.vue`-only grep missed it) and briefly re-added, creating a
duplicate; found it already existed correctly in
`my_store_ui/www/retail_erp.html` and reverted the duplicate. Net change:
none. Documented so the mistake doesn't get repeated.

**Found, documented, not fixed** (scope/proportionality call): `ToastHost`
and `ConfirmDialogHost` are both empty, completely unwired shell elements —
no service anywhere pushes content into them, and destructive actions use
native `window.confirm()` instead. Pre-existing, not introduced by the UI
work. Building a real toast/confirm system and rewiring call sites across
the app is a feature addition, not a correction — flagged as follow-up work
rather than attempted under this mission's scope.

**Parity status unchanged**: `required_but_missing = 222` (confirmed by
re-reading `docs/full-parity/required_missing_latest.json` directly, not
assumed), `unclassified = 0`. No routes were remapped.

## 28. Strict Visual Parity, Charts, Real Buttons, Real Browser (2026-07-16)

Follow-up to Section 27. Recovery tag:
`pre-strict-visual-parity-rebuild-20260716-0957`.

**Real browser screenshots achieved.** Found Chrome/Edge on the Windows
host reachable from WSL (`/mnt/c/Program Files/Google/Chrome/Application/chrome.exe`).
Got authenticated headless screenshots working (session cookie written
into an ephemeral, user-approved Chrome profile under `C:\Windows\Temp\`,
deleted at session end). This is the first session in this project able to
show real rendered pages rather than only HTTP responses or code review.
Full detail: `docs/ui/SMJ_BROWSER_VERIFICATION.md`.

**Real defect found via screenshot, not guesswork:** module header pill
colours didn't match the SMJ reference — Purchases showed orange (should
be purple), Inventory showed green (should be orange), Finance showed
purple (should be gold), Sales showed blue (should be green). Root cause:
the previous session's "remap legacy 7-color accent keys onto SMJ hex
values" fix never checked whether each *route* was assigned the *correct*
accent key in the first place. Fixed in both `frontend/src/router/routes.js`
and the server-side navigation payload
(`my_store_ui/services/frontend_routes.py`) — every Sales/Inventory/Finance
handcrafted route's accent was corrected, not just the module dashboards.

**Home dashboard rebuilt** (`frontend/src/pages/priority/HomeDashboardPage.vue`,
wired into `/home`) — previously the generic metadata-driven
`ModuleDashboardPage` (permitted-record counts, no charts), now a real
KPI/chart dashboard matching `01_home_dashboard.png`'s structure: 6 live
KPI cards with trend%/sparkline, a Sales Trend line chart, Payment
Collection donut, Top Selling Categories bar chart, Recent Transactions
table, Stock Overview, Low Stock Alerts, Top Customers/Products. All data
is real (`my_store_ui/dashboard_analytics.py`, 8 new permission-checked,
zero-raw-SQL endpoints) — confirmed via direct API testing, not assumed.
One real Frappe gotcha found and fixed while building it: `get_list()` on
a child doctype (`Sales Invoice Item`) silently filters out rows that
`get_all()` correctly returns — see `docs/ui/SMJ_DASHBOARD_DATA_SOURCES.md`.

**New chart framework** (`frontend/src/components/charts/`) — hand-rolled
SVG (`SmjSparkline`, `SmjLineChart`, `SmjDonutChart`, `SmjBarChart`,
`SmjKpiCard`, `SmjChartCard`), zero new npm dependencies, because `npm
install` is still network-blocked in this environment (confirmed
unchanged from the previous session's diagnosis).

**ToastHost and ConfirmDialogHost are now real**, not empty shells (see
Section 27's finding). `composables/toast.js` and `composables/confirm.js`
back them with real reactive queues; migrated the three highest-traffic
shared action components (`SalesOrderActions.vue`, `EntityActions.vue`,
`UniversalDetailPage.vue`'s action handler) off `window.confirm` onto the
real dialog. Several lower-traffic `window.confirm` sites (Bank/Payment
Reconciliation, unsaved-changes guards) were left as-is under time
pressure — documented in `docs/ui/SMJ_BUTTON_ACTION_MATRIX.md`.

**Mobile responsive**: found and fixed a real horizontal-overflow bug in
the new Home dashboard via screenshot (KPI grid + CSS Grid's `min-width:
auto` default on `.rug-page`'s children — the general fix,
`.rug-page > * { min-width: 0; }`, applies to every page using this shared
pattern, not just Home). One residual mobile issue (two small text
elements slightly clipped in a chart card) was not conclusively resolved
despite several rounds of fixes that were confirmed correctly compiled but
showed no visible change across screenshots — flagged honestly as
"source-fix applied, not conclusively visually verified" rather than
claimed fixed. Full detail: `docs/ui/SMJ_RESPONSIVE_RESULTS.md`.

**Not attempted this pass**: the other 8 reference pages (Smart Sales,
Sales Orders, Products, Customer Credit, Purchases, Finance, Transaction
Register, Reports) were not rebuilt to the reference's KPI-sidebar+chart
depth — they inherited the accent-colour fix and have the new chart
framework available, but their layouts are unchanged. A full per-button
verification matrix across all 9 pages was not built (see
`docs/ui/SMJ_BUTTON_ACTION_MATRIX.md` for what was and wasn't covered).

**Parity status unchanged**: `required_but_missing = 222`,
`unclassified = 0`. No routes were remapped; only accent metadata and one
route's component (`/home`) changed.

## 29. Required-222 Mission: Dashboards + Dead-Credit (2026-07-16)

Full completion attempt at driving `required_but_missing` (the corrected
production-parity registry gap, not the raw route count) to zero. Recovery
tag: `pre-complete-required-222-20260716-2109`. Result:
**`required_but_missing` 222 → 144** (78 items, 35%), in 2 feature commits.
The mission was **not completed** — this is reported honestly, not spun.
Full detail: `docs/full-parity/REQUIRED_222_COMPLETION_REPORT.md`,
`docs/full-parity/REQUIRED_222_BATCH_LOG.md`,
`docs/full-parity/DEAD_CREDIT_FINAL_AUDIT.md`,
`docs/full-parity/REMAINING_APPROVAL_BLOCKERS.md`.

**Batch 1 (222 → 163)**: all 59 required Dashboard Charts/Number
Cards/Dashboards. New `my_store_ui/module_dashboards.py` — six real,
permission-checked, live-data endpoints (Accounts, Payments, Buying, CRM,
Selling, Stock), reusing the standard "Profit and Loss Statement"/"Budget
Variance Report" query reports for accounting math rather than
reimplementing it (same pattern as the existing Gross Profit reuse in
`dashboard_analytics.py`). Wired into `ModuleDashboardPage.vue` via a new
`moduleDashboards.js` service, rendered through the existing SMJ chart
framework. Verified against real site1 data via `bench execute`. New
`DASHBOARD_ANALYTICS_ADAPTERS` registry credit table, matched by exact
scanner `(feature_type, name)` key. 10 new tests
(`test_module_dashboards.py`), all passing.

**Batch 2 (163 → 144)**: dead-credit pass found 20 of the remaining items
were ERPNext's standard "Connections" sidebar tiles (Purchase Invoice → its
source PO, Supplier → its POs/PIs, etc.), not distinct buttons — verified
precisely by loading each doctype's real `get_dashboard_data()` and
checking the scanner's action key against its linked-doctype names, not
guessed from labels. New generic `get_dashboard_connections()` adapter
(`my_store_ui/universal/api.py`) reuses each doctype's own dashboard config
(the same source Desk's Connections panel reads), permission-rechecks every
linked doctype (stricter than the standard `frappe.desk.notifications.
get_open_count`, which doesn't), and only surfaces app-routed doctypes.
19/20 credited (the 20th, Blanket Order, stays pending until that doctype
itself gets a route). Wired into `UniversalDetailPage.vue` as a new "Linked
documents" section — confirmed via the router that this is the actual page
serving Purchase Order/Invoice/Receipt/RFQ/Supplier Quotation/Material
Request/Blanket Order/Payment Order/Quotation/Lead/Supplier, not the
separate `EntityDetailPage.vue` (which only serves 3 handcrafted entities).

**Real bug found and fixed while reading the registry code** (not a
scanner-classification issue — an actual Python bug): `DOCTYPE_SPECIFIC_
ACTIONS` had two `"Supplier"` dict-literal keys; the later one silently
overwrote the earlier one, so `Supplier.hold`/`Supplier.resume` — real,
working, already-implemented actions — were never actually being checked
by the registry despite the code's clear intent. Merged into one entry.
Full detail in `DEAD_CREDIT_FINAL_AUDIT.md`.

**What remains (144 items, honestly not blocked, just not yet reached)**:
140 individual document-actions across Accounts (50), Stock (35), Buying
(23), Setup (11), CRM (10), Selling (4), Contacts (4), Printing (4),
Maintenance (2), Manufacturing (1) — each requires its own real ERPNext
source verification before a fixed-purpose adapter can be written, so this
is inherently one-at-a-time work, unlike Batches 1–2's shared patterns. Plus
2 Single DocType pages (Bank Clearance, Pegged Currencies — investigated,
not implemented; the universal engine has no Single-DocType load path yet)
and 2 standalone analytics pages (Sales Funnel, Warehouse Capacity
Summary — same pattern as Batch 1, not yet reached). See
`REMAINING_APPROVAL_BLOCKERS.md` for confirmation that essentially none of
these 144 are actually approval- or environment-blocked — they are
ordinary backlog.

**Verification this session**: `npm run build` passed 4 times, `py_compile`
passed on every changed file, 16 new tests all passing against live site1
data via `bench execute`, `validate_parity_registry()` 0 errors both times,
`corrected_production_parity_audit()` re-run live (not cached) to confirm
every delta. No fake routes, no permission bypasses, no direct ledger/Bin
writes, no `ignore_permissions`. Browser/UI rendering remains unverified
(no Chrome/Playwright in this environment, unchanged from every prior
session's diagnosis) — every new capability is `implemented_unverified` or
`special_adapter`, never falsely `verified_complete`.

## 30. Required-222 Mission Completion (2026-07-16)

Section 29 is historical and is superseded by this section. The remaining 144
items were completed in six further source-verified batches:

- `8201749`: Bank Clearance and Pegged Currencies Single tools.
- `264a151`: Sales Funnel and Warehouse Capacity pages.
- `c3973ac`: Buying action adapters.
- `3bbbedf`: Accounts action adapters.
- `b64aecc`: Stock action adapters.
- `325527b`: CRM, Selling, Setup, Contacts, Printing and Maintenance adapters.

Final generated audit fingerprint:
`029f8e0d2a940f071d20a66010f820fbd8083401ae4eae6f906f0a909b0562d0`.
Final corrected values are `required_but_missing = 0` and `unclassified = 0`.
The broad inventory audit is still red (`unmapped_user_facing = 1683`), and
browser verification remains unavailable. Consequently the registry correctly
reports `verified_complete = 0`, `implemented_unverified = 469`, and
`generated_provisional = 805`; this is corrected required-scope completion,
not a claim of full ERPNext parity or production readiness.

The authoritative final evidence is:

- `docs/full-parity/REQUIRED_222_COMPLETION_REPORT.md`
- `docs/full-parity/REQUIRED_222_BATCH_LOG.md`
- `docs/full-parity/required_missing_latest.json`
- `docs/full-parity/corrected_production_parity_audit.json`
- `docs/full-parity/REMAINING_APPROVAL_BLOCKERS.md`

## 31. SMJ Retail ERP — Autonomous Pre-Production Completion Mission (2026-07-18)

A separate, later autonomous mission (fully logged in
`docs/execution/SMJ_MASTER_*`) picked up from here to close the
*verification* gap Section 30 explicitly named (`verified_complete = 0`
against 1,274 `implemented_unverified`/`generated_provisional` features).
Ten phases were run; full detail, real command output, and every
commit hash are in `docs/execution/SMJ_MASTER_BATCH_LOG.md`. Summary:

- **Demo data & environment**: built a full year of realistic demo data
  on `staging.local` (26 customers, 12 suppliers, 40 items, 102 Sales
  Orders, 100 Delivery Notes, 100 Sales Invoices, 124 Payment Entries,
  67 Purchase Orders, all 10 named sales scenarios and 7 purchase
  scenarios), found and fixed a missing-Fiscal-Year bug that would have
  silently blocked all future-dated transactions.
- **Wholesale workflow + concurrency** (`docs/workflows/SMJ_WHOLESALE_*`):
  built a real two-process race for the last units of stock — confirmed
  no over-reservation is ever possible. All 6 of the mission's
  acceptance scenarios verified against live data.
- **Security** (`docs/security/SMJ_*`): 594 real permission checks + 6
  genuine cross-role write-attempt tests across 10 roles. Zero
  unauthorized access found.
- **Browser/visual/responsive** (`docs/ui/SMJ_BROWSER_VERIFICATION.md`,
  `docs/ui/SMJ_RESPONSIVE_RESULTS.md`): the first real browser
  verification in this project's history using Linux-native Playwright
  Chromium — a 108-point sweep (18 workspaces × 6 viewports) with zero
  defects, plus deep click-through interaction testing and the
  first-ever browser-level permission-denied test. Resolved a
  2026-07-16-session mobile-CSS uncertainty as genuinely fixed. Also
  fixed a systemic 13-file test-infrastructure bug that was corrupting
  the backend test suite and separately writing test data against
  `site1.local` regardless of which site was targeted — backend suite
  now 201 tests, 0 failures, 0 errors (was 36 errors).
- **Accounting verification** (`docs/verification/SMJ_ACCOUNTING_VERIFICATION.md`):
  ran 14 standard reports through ERPNext's real Report API. Found and
  fully root-caused a real P&L overstatement (~11.8M LKR) caused by
  opening-stock postings hitting the wrong account type — documented
  with an exact fix, not patched live (a year of transactions now
  depends on those entries).
- **Import/purchasing** (`docs/workflows/SMJ_IMPORT_PURCHASING_REPORT.md`):
  verified both real procurement chains end-to-end with exact document
  links; Landed Cost Voucher math confirmed precise to the decimal.
- **Load/concurrency/backup-restore** (`docs/verification/SMJ_*`): a
  full backup-restore drill with exact data match; concurrent reads
  100% consistent; concurrent writes confirmed safe (zero corruption)
  under contention, with a documented UX hardening recommendation.

**Parity audit re-run (2026-07-18):** fingerprint
`029f8e0d2a940f071d20a66010f820fbd8083401ae4eae6f906f0a909b0562d0` —
**identical** to Section 30's, confirming zero structural drift across
this entire mission. `required_but_missing = 0` and `unclassified = 0`
remain true. `verified_complete` in the aggregate registry counter is
still mechanically `0`, because that counter requires an explicit
per-feature reclassification pass this mission did not build — but the
real, evidenced verification work above exists and is fully documented
per-feature in the `docs/execution/`, `docs/workflows/`,
`docs/security/`, `docs/verification/`, and `docs/ui/` reports, which
are the authoritative record of what was actually tested, how, and with
what result.

---

## Final-readiness mission (2026-07-27)

333 backend tests / 42 modules green; frontend build clean; browser matrix 90/90 over
six viewports. New admin surfaces: Setup wizard (`/setup`), Printing (`/admin/printing`),
Email (`/admin/email`), Data Management (`/admin/data`), System Operations
(`/admin/system`), plus the Access Control page from the prior mission.

Key docs: `docs/execution/SMJ_FINAL_PRODUCTION_READINESS_REPORT.md`,
`docs/verification/SMJ_FINAL_ACCEPTANCE_MATRIX.md`,
`docs/verification/SMJ_FINAL_BROWSER_MATRIX.md`,
`docs/finance/SMJ_OPENING_STOCK_*`, `docs/release/*`.

External requirements: SMTP credentials, MariaDB root (QA/fresh sites), accountant
sign-off (opening-stock JE), Hetzner/DNS. Enable the scheduler in production.

---

## Finance / deployment mission (2026-07-27) — tag v1.0.0-rc3

- Finance figures re-verified from the ledger: profit 15,868,706 → corrected
  **4,048,006** (the "4,048,825,204" figure never existed in the repo). Guarded
  correction package at `my_store_ui/finance/opening_stock_correction.py`
  (inspect/dry_run/prepare_draft/verify_after/apply). **Not applied — accountant
  sign-off external.** Runbook: `docs/finance/SMJ_STAGING_CORRECTION_RUNBOOK.md`.
- Fresh-install script `scripts/verify_fresh_install.sh` (static-validated; live run
  needs MariaDB root).
- Hetzner deployment package under `deployment/` (compose statically valid; 8 scripts;
  secrets git-ignored). Live deploy external.
- 338 backend tests, 90/90 browser, secret scan clean, site1 untouched.

Externals: accountant sign-off, MariaDB root (QA/fresh sites), SMTP, Hetzner/DNS/
registry/git-push, client UAT.

---
## RC4 (2026-07-27, v1.0.0-rc4)
New: /admin (Administration landing), /admin/readiness (truthful launch-readiness),
/reports/scheduled (scheduled reports), secure PDF download on /admin/printing,
two-company separation test. 369 backend tests, 96/96 browser, secret scan clean,
site1 untouched. External unchanged: accountant, SMTP, MariaDB root, Hetzner/DNS, UAT.
Owner actions: docs/release/SMJ_OWNER_ACTIONS_BEFORE_GO_LIVE.md.

---
## Product/Customer quick-entry (2026-07-27, v1.0.0-rc6)
Exact Product form (P100001 ID / 5001 SKU auto, 18 fields, batch-managed, 4 Item
Prices incl Department) and Customer form (14 fields, linked address/contact, credit).
Backends: my_store_ui/quick_entry/{product,customer,options,existing_data}.py. Batch/
FIFO proven (12,400/9,600). 405 backend tests, 108/108 browser. Existing-data migration
tool dry-run only (batch-on-stocked-items is manual). site1 untouched.

---
## Wholesale operations: sales, purchasing, payments, returns (2026-08-01, v1.0.0-rc8)
Complete wholesale chain on standard ERPNext controllers only -- no direct GL, Stock
Ledger, Payment Ledger or Bin writes anywhere.

Sales: Smart Sales -> Sales Order (customer Price Category, Unit/Carton, server-side
revalidation) -> reservation -> payment/credit gate -> FIFO Delivery Note -> final
Sales Invoice with advance allocation -> payment allocation -> completion. Returns:
Return Delivery Note + Credit Note. Purchasing: PO -> (partial) Purchase Receipt ->
Purchase Invoice -> supplier payment, plus Landed Cost Vouchers and supplier returns
with Debit Notes. Transaction register with delivery/invoice/payment/return/
reservation status and a lifecycle timeline; daily operations dashboard.

New modules: my_store_ui/wholesale/{uom,delivery,invoicing,payments,purchasing,
returns,landed_cost,idempotency,operations_dashboard}.py.

Carton is now a real UOM conversion on the Item (it was a display-only number), and
idempotency is stored on the document in custom_request_id rather than the cache --
a Redis restart could previously have dispatched the same goods twice.

Ten real defects found and fixed; two were visible only in a browser (a route guard
that admitted users its own API refuses, and a missing optional app breaking the whole
Smart Sales bootstrap). See docs/execution/SMJ_WHOLESALE_OPERATIONS_LOG.md.

+140 backend tests (540 total, 0 failures, 6 skipped), 162/162 browser across six
viewports, frontend build clean, secret scan clean, site1.local fingerprint unchanged.

External unchanged: accountant approval for the opening-stock correction, SMTP,
MariaDB root, Hetzner/DNS, bank credentials, client UAT.
Docs: docs/workflows/SMJ_COMPLETE_WHOLESALE_SALES_FLOW.md and siblings;
docs/verification/SMJ_WHOLESALE_END_TO_END_ACCEPTANCE.md.

## Sales Teams end to end: customer, Smart Sales, snapshot, commission (2026-08-04)
Create a Sales Team -> assign it to a Customer -> Smart Sales loads it -> the Sales
Order freezes it -> Delivery Note and Sales Invoice inherit it -> the Commission
Register reports it -> a Credit Note reverses it. Nothing recalculates from the team
master, ever.

The commission model reuses ERPNext's own chain rather than duplicating the maths.
`freeze_team` runs in `before_validate` and supplies two inputs -- the document
`commission_rate` and the allocated percentages -- and ERPNext's selling controller
derives the eligible amount, the pool and each person's contribution itself.
`price_commission` then runs in `validate`, once the pool exists, and splits it
between the frozen members. A `validate` hook would be too late: Frappe runs a
document's own method before the hooks.

Five quantities are kept strictly distinct (base, rate, pool, allocation %, member
amount). LKR 100,000 at a 2% team rate is a 2,000 pool split 1,000/500/500 -- the
manager's 50% divides the *pool*, never the sale. Their sales *contribution* is
50,000 and lives in ERPNext's own `allocated_amount`.

New: snapshot child rows carrying the team role (which the standard Sales Team row
has no field for), transaction provenance (customer default vs override, the reason,
who froze it and when), a permission-controlled per-order team override, the
Commission Register at /retail-erp/sales/commissions with export, team performance,
customer team history from Frappe's own Version trail, and a guarded five-mode
backfill.

New modules: my_store_ui/{commission,sales_team_migration}.py; doctype Retail Sales
Team Snapshot; patches/install_sales_team_fields.py re-run for the new fields.

Six real defects found and fixed, four of which no existing test could have caught:
`Sales Team.commission_rate` is `Data`, read-only and `fetch_from
sales_person.commission_rate`, so the previous code's write of the team rate was
silently discarded; ERPNext compares the standard rows against 100.0 exactly, so a
legal 33.333 x 3 split passed our own tolerance and then blocked the order; a field
named `company` is auto-filled by Frappe from the user default, which would have made
"works for every company" unreachable (hence `restrict_to_company`); a disabled Sales
Person in an active team would have failed every new order at the counter rather than
on the master where it can be fixed; `_snapshot_from_source` subscripted a child
Document; and the customer-history test could not observe the Version trail at all
because Frappe sets `ignore_version = frappe.flags.in_test` on every save.

+62 backend tests (735 total, 0 failures, 6 skipped), browser 73/73 sales team,
228/228 across six viewports, 15/15 customer picker, 10/10 button audit, frontend
build clean, secret scan clean, site1.local fingerprint unchanged.

Backfill result: nothing to do, correctly. All 303 existing documents are submitted
and predate the feature, so none carries evidence of the team it was raised with;
guessing would fabricate commission history. They are exported for manual review
(333 rows, site private files) instead.

External unchanged, plus one new: accountant approval is required before commission
can be paid out -- the expense account, payee party type, whether commission is
earned on invoicing or on collection, the payout cycle and withholding. Calculation,
reporting and export are complete; posting is deliberately not implemented and there
is deliberately no "Paid" status.
Docs: docs/sales/SMJ_SALES_TEAM_DATA_MAPPING.md, SMJ_COMMISSION_CALCULATION.md,
SMJ_COMMISSION_REGISTER.md, SMJ_COMMISSION_PAYOUT_BOUNDARY.md,
SMJ_SALES_ORDER_TEAM_SNAPSHOT.md, SMJ_CUSTOMER_SALES_TEAM_ASSIGNMENT.md,
SMJ_SMART_SALES_TEAM_INTEGRATION.md; docs/security/SMJ_SALES_TEAM_PERMISSION_MATRIX.md;
docs/data/SMJ_SALES_TEAM_MIGRATION_RESULT.md;
docs/verification/SMJ_SALES_TEAM_END_TO_END_ACCEPTANCE.md and
SMJ_SALES_TEAM_BROWSER_MATRIX.md.
