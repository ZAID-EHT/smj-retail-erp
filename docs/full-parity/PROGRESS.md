# Full Feature Parity — Progress

_Last updated: 2026-07-15 (batch: FINISH ACCOUNTING FIRST — pass 7-8, Priority 4 complete)_

## Pass 7-8 — Priority 4: period closing and year-end accounting, complete

Two sub-batches, both using a technique that turned out to be very high
leverage for the rest of the mission: **check whether the underlying
doctype is a regular (non-virtual, non-table, non-single) doctype before
assuming a dedicated adapter is needed** — if it is, the generic universal
engine already serves list/detail/form/submit/cancel for free, and only the
*specific document actions* need real work.

**Sub-batch A — Chart of Accounts + ledger navigation** (commit `56a7146`):
real document actions on Account, Cost Center, Company, Journal Entry,
Period Closing Voucher, Warehouse via the existing universal engine's
action-execution path (`_available_actions`/`run_document_action`), not a
new adapter:
- Account: `chart_of_accounts`/`general_ledger` (navigation), `convert_to_group`/
  `convert_to_non_group` (wrap `convert_ledger_to_group`/`convert_group_to_ledger`),
  `merge_account` (wraps `erpnext...account.merge_account`),
  `update_account_name_number` (wraps `erpnext...account.update_account_number`).
- Cost Center: same convert-to-group pattern + `chart_of_cost_centers`/`budget`
  navigation + `update_cost_center_name_number` (wraps `erpnext.accounts.utils.update_cost_center`).
- Company: `chart_of_accounts`/`cost_centers` navigation, company-filtered.
- Journal Entry/Period Closing Voucher: `ledger` navigation. Deduped
  `reverse_journal_entry` (confirmed via source it's the same capability as
  the already-credited `make_reverse_journal_entry`).
- Warehouse: `general_ledger` navigation via the warehouse's linked account.

**Found and fixed a real bug while wiring the navigation actions:** neither
`PriorityReportPage.vue` nor `PriorityTreePage.vue` read the URL query
string at all — a "Ledger"/"Chart of Accounts" click landed on the right
page but showed an empty, unfiltered form instead of a genuine drill-down.
Fixed both to read `route.query` (`PriorityReportPage` also auto-runs when a
query-driven filter is present). Also fixed a `%20`-vs-`+` encoding mismatch:
Python's `urlencode()` default `quote_plus` produces `+` for spaces, but Vue
Router's `route.query` parsing uses `decodeURIComponent`, which does not
decode `+` as space — switched to `quote_via=quote` for these routes.

**Sub-batch B — remaining Priority 4 items** (commit `8c46d8e`): routed 5
regular tool doctypes through the generic engine (confirmed
`is_virtual`/`issingle`/`istable` all falsy against the installed schema
before routing, per the mission's own verification requirement): `Process
Period Closing Voucher`, `Process Deferred Accounting`, `Process Statement
Of Accounts`, `Process Subscription`, `Unreconcile Payment`. Added real
actions: Exchange Rate Revaluation's `make_jv_entries` (gated by its own
`check_journal_entry_condition()` idempotency check, matching erpnext's own
Desk button visibility exactly; deduped `journal_entries`), Dunning's
`resolve`/`payment` (the latter reusing the same doctype-agnostic
`get_payment_entry()` call already used by Purchase Invoice's
`make_payment_entry`), Process Period Closing Voucher's
`start`/`pause`/`resume_pcv_processing` (real background-job controls;
deduped `cancel_pcv_processing` — read the source and confirmed it is
erpnext's own `on_cancel()` hook, already triggered by the standard
`cancel` lifecycle action now that the doctype is routed).

**Important process note found this pass:** adding new `ENTITY_ROUTES`
entries only changes what the code *would* report; `build_parity_registry()`
reads from the canonical `docs/erpnext-v15-complete-inventory.json` snapshot,
which is stale until `generate_complete_inventory()` re-runs. Running
`generate_corrected_audit()` right after an `ENTITY_ROUTES` change (without
first regenerating the canonical inventory) undercounts the drop —
confirmed by watching 295→293 (only the non-route DOCTYPE_SPECIFIC_ACTIONS
credits) instead of the expected 295→288 until the inventory was
regenerated. **Rule for future batches: always run
`generate_complete_inventory` before `generate_corrected_audit` whenever
`ENTITY_ROUTES`/`REPORT_GROUPS` changed; registry-only changes (
`DOCTYPE_SPECIFIC_ACTIONS`/`BUILT_ADAPTER_*`) don't need it.**

**Left honestly open** (unavailable_with_reason, not forced): Invoice
Discounting's loan-disbursement actions (niche trade-finance feature, lower
priority than Stock/Purchasing for this business), Process Statement Of
Accounts' `download`/`send_emails` (a file-download response and an email
send respectively — don't fit the generic action-executor's JSON contract,
and site1 has zero configured outgoing Email Accounts to test against),
Unreconcile Payment's `create_unreconcile_doc_for_selection` (a bulk
list-view action from the Payment Ledger report — the underlying capability
IS already reachable via Unreconcile Payment's own generic create form, but
the exact bulk-select UX is genuinely different, same "don't force-fit a
different UX pattern" reasoning as Pick List's create_delivery_note in an
earlier pass).

`required_but_missing`: 312 → **285** across both sub-batches (293→285 net
of the -2/-5 inventory-regen split noted above). Registry tests 7/7 pass
throughout, route verifier climbed 196→201 served (the 5 new doctypes),
`npm run build` passes.

## Pass 6 — Priority 3: Budget and accounting setup — verification, no new code needed

Checked the mission's Priority 3 list (Budget, Monthly Distribution,
Accounting Dimensions, Cost Center tree, Account tree, Fiscal Year, Finance
Book, Payment Terms, Payment Terms Template, Mode of Payment, Bank Account,
Currency Exchange, Exchange Rate Revaluation) against
`required_missing_latest.json`: **none of these doctypes themselves appear
in `required_but_missing`** — all were already routed as `generated_provisional`
in an earlier batch, and Account/Cost Center already have dedicated tree
views (`TREE_CONFIG` in `priority_pages.py`). No new adapter work was needed
or done here; this was a verification pass, not a build pass.

What genuinely remains open under this priority (still `unavailable_with_reason`,
real gaps, not fake-credited): a handful of **document actions** on these
doctypes — `Account`/`Cost Center` tree mutations (`convert_to_group`,
`convert_to_non_group`, `update_account_name_number`, `merge_account`,
chart-of-accounts/chart-of-cost-centers shortcuts, cost-center `budget`
shortcut), `Exchange Rate Revaluation`'s journal-entry-creation actions, and
`Bank Account`'s `make_bank_account` action. Checked
`PriorityTreePage.vue` (19 lines) — it is a read-only tree renderer with no
mutation UI yet, so these are genuinely unbuilt, not a quick win; they need
the same dedicated-adapter treatment as Bank Reconciliation Tool, not a
five-minute credit. Left honestly `unavailable_with_reason`.

`required_but_missing` unchanged at **312** (as expected — a verification
pass with no new routes credits nothing new; the small action list above
was already correctly counted as missing before this pass and remains so).

## Pass 5 — Priority 2: financial report drill-down verification + real bug fixes

Checked the mission's Priority 2 list (GL, Trial Balance, P&L, Balance
Sheet, Cash Flow, Accounts Receivable, Accounts Payable, Customer Ledger,
Supplier Ledger, Payment Ledger, Bank Book, Cash Book) against the existing
registry rather than assuming it needed new adapters — all nine real reports
were **already routed and `generated_provisional`** from an earlier "+156
generated reports" batch (`_GENERATED_REPORT_GROUPS` in
`priority_registry.py`), so none of them appear in `required_but_missing`.
"Bank Book" and "Cash Book" are not installed ERPNext reports at all (v15
does not ship them as standalone reports — verified via `frappe.db.exists`);
they are legitimately achieved through General Ledger filtered by a
bank/cash account, not a fake route.

Reading the real filter definitions (`erpnext/accounts/report/<name>/<name>.js`
and the shared `erpnext/public/js/financial_statements.js` used by P&L/
Balance Sheet/Cash Flow) instead of trusting the existing `REPORT_FILTERS`
entries found **two real, pre-existing bugs** and one real gap:

1. **Bug:** `Accounts Receivable`/`Accounts Payable` used filter key
   `"posting_date"`, but the report's actual Python filter reads
   `report_date` — the date filter was silently ignored by
   `frappe.desk.query_report.run` (default date used instead).
2. **Bug:** `Customer Ledger Summary` used filter key `"customer"`, but the
   report reads `party` — same silent-ignore bug.
3. **Gap:** none of GL/TB/P&L/Balance Sheet/Cash Flow/AR/AP had `cost_center`,
   `finance_book`, `project`, or `presentation_currency` filters at all,
   despite the mission explicitly asking for Cost Center/Accounting
   Dimension/Finance Book/Currency filtering.

Fixed both bugs and closed the gap: extended `REPORT_FILTERS` for all nine
reports with their real filter fieldnames, extended `_filter_definition`/
`REPORT_LINK_DOCTYPES` in `priority_pages.py` with the new Link fields
(Cost Center, Project, Finance Book, Currency, Customer/Supplier Group,
Territory, Sales Partner/Person, Payment Terms Template) and the
`filter_based_on` Select (exact `["Fiscal Year", "Date Range"]` options
matched against `financial_statements.js`).

**Found and fixed a third, deeper bug while verifying behaviourally against
site1:** General Ledger, Trial Balance, the financial-statements reports and
AR/AP all read `cost_center`/`project`/`party`/`account` as a **native Python
list** (the Desk client's MultiSelectList value survives outer JSON decoding
as a list; `erpnext.accounts.report.financial_statements.
get_cost_centers_with_children` explicitly checks `isinstance(x, list)` and
falls back to splitting on commas otherwise). The first fix attempt
JSON-encoded a single value as a string (`frappe.as_json([value])`), which
`get_cost_centers_with_children`'s comma-split fallback mangled into one
garbled "cost center" containing the literal JSON brackets — confirmed by
reproducing the exact `ValidationError` against real site1 data, then
corrected to pass a real one-item Python list instead.

Verified behaviourally against real site1 data: General Ledger (75/116/14
rows across cost_center/no-filter/party filter variants), Accounts
Receivable, Trial Balance, Profit and Loss Statement, Balance Sheet, Cash
Flow and Supplier Ledger Summary all ran successfully with the new filters,
including a real Cost Center (`SMJ (Demo) - Carpets toD`) and a real
Customer (`Palmer Productions Ltd.`) filter value. `route_coverage.
verify_generated_reports` and `verify_generated_routes` both still 0
failures, registry tests 7/7 pass, `npm run build` passes.
`required_but_missing` unchanged at **312** — this was a correctness fix to
already-"implemented" reports, not new routing (their status was already
`generated_provisional`, which is why the report drill-down filters not
actually working was a real, hidden gap the raw metric couldn't see).

## Pass 4 — real new feature: Bank Reconciliation Tool adapter (Batch 10 continued)

Re-verified the starting state first: HEAD was `85e1e3c` (one commit ahead of the
`25740f1` mentioned in the mission brief — an unrelated login-page CSS fix),
worktree clean. Re-ran the live corrected audit: `required_but_missing = 319`,
exactly matching the mission brief with zero drift. Froze the full 319-entry
list (the corrected-audit JSON caps its list at 200) to
`docs/full-parity/required_missing_before_accounting_completion.json`, tagged
`pre-finish-accounting-and-319-20260715-1316` at that commit.

Built **Bank Reconciliation Tool** end-to-end, following the exact template
`BLOCKERS.md`/`PROGRESS.md` pass 3 called out: read the real ERPNext
controller first (`erpnext.accounts.doctype.bank_reconciliation_tool.
bank_reconciliation_tool` — confirmed it is a virtual doctype, `Document`
subclass body is literally `pass`; all real behaviour lives in module-level
`@frappe.whitelist()` functions with **no built-in permission checks** —
ERPNext's own Desk-only page gates access purely via "Bank Reconciliation
Tool" DocPerm read), then wrapped it with fixed-purpose whitelisted functions
that add explicit company/bank-account/doctype permission checks the
original module lacks:

- **Backend** (`my_store_ui/wholesale/bank_reconciliation_api.py`): 14
  whitelisted functions — `get_summary` / `get_matches` (read-only),
  `update_transaction_reference` / `reconcile_transaction` /
  `unreconcile_transaction` / `preview_payment_entry` /
  `confirm_payment_entry` / `preview_journal_entry` / `confirm_journal_entry`
  / `auto_reconcile` (writes, each delegating to the real erpnext
  `create_payment_entry_bts` / `create_journal_entry_bts` /
  `reconcile_vouchers` / `auto_reconcile_vouchers` / `Bank Transaction.
  remove_payment_entries` — never a generic method-path RPC), plus
  `search_bank_account` / `search_account` / `search_party` /
  `search_mode_of_payment` filter-form helpers. Journal Entry type is
  restricted to the exact allowlist ERPNext's own dialog offers (matched
  against `bank_reconciliation_tool/dialog_manager.js`).
- **Frontend** (`BankReconciliationPage.vue`): summary banner (ledger balance
  / statement balance / difference), unreconciled-transaction table with
  per-row Match / + Payment / + Journal / Unreconcile actions, a candidate-
  match panel, and Payment/Journal Entry creation forms with a genuine
  read-only preview step (calls the real controller with `allow_edit=1`,
  which for Payment Entry also runs full `.validate()` before returning —
  matches ERPNext's own tool behaviour, including its one real gap: Journal
  Entry preview does *not* validate before returning, so debit/credit
  balance errors only surface at confirm, exactly as in Desk).
- **Verified:** all 14 new endpoints confirmed to reject Guest with
  `AuthenticationError`. Route resolves (`/finance/bank-reconciliation` →
  `component: bank_reconciliation`). Search helpers behaviourally exercised
  against real site1 data (Account/Mode of Payment/Customer search all
  returned real permission-filtered results). `get_summary` against a
  non-existent bank account correctly raised `ValidationError` rather than
  crashing. Write paths are source-verified against erpnext's own
  controller signatures (matching the same rigor as Payment Reconciliation)
  but not behaviourally exercised — site1 has zero `Bank Account` / `Bank
  Transaction` records, so there is nothing to reconcile against without
  creating test data.
- **Registry:** `BUILT_ADAPTER_DOCTYPE_NAMES` extended with `Bank
  Reconciliation Tool`; the old flat `BUILT_ADAPTER_ACTIONS` set was
  refactored into `BUILT_ADAPTER_ACTIONS_BY_PARENT` (a doctype → allowed
  action keys map) because this adapter serves two of Bank Transaction's
  document actions (`create_bank_entries`, `unreconcile_transaction`) in
  addition to Bank Reconciliation Tool's own five — a document_action's
  parent doctype is not always the adapter's primary doctype.

`required_but_missing`: 319 → **312** (1 doctype + 6 document actions
credited). `implemented_unverified` 168→175, `special_adapter` (strategy)
139→146. Registry tests 7/7 pass, `validate_parity_registry` passes,
`verify_generated_routes`/`verify_generated_reports` both 0 failures,
`npm run build` passes. Route-based `unmapped_user_facing` is unchanged at
1699 — `/finance/bank-reconciliation` already had a route (it existed as
`specialised_provisional`); this batch changed which component serves it,
not whether it has a route, exactly like the Payment Reconciliation batch.

**Not done in this pass** (left honestly `unavailable_with_reason`,
different tools requiring separate adapters — see `BLOCKERS.md`):
`Bank Statement Import` (upload_bank_statement action + its own actions),
`Bank Clearance` (a separate, older parallel clearance doctype — not the
same as Bank Reconciliation Tool), `Bank.refresh_plaid_link`,
`Bank Account.make_bank_account`/`unlink_external_integrations`. The
remaining ~106 Accounts-module `required_but_missing` entries (now ~99)
are GL/Trial Balance/P&L/Balance Sheet drill-down, Budget/Accounting
Dimension adapters, Period Closing/Process Statement Of Accounts/Process
Subscription tools, dashboard charts/number cards, and a batch of
document-action scanner-noise duplicates (e.g. Journal Entry's JS-observed
`reverse_journal_entry` button name vs the already-credited Python
`make_reverse_journal_entry` method it calls — confirmed via
`journal_entry.js` source, candidate for a future dedup pass) — genuinely
open, see `BLOCKERS.md` and `required_missing_latest.json`.

## Pass 3 — real new feature: Payment Reconciliation adapter (Batch 10)

User chose "pick one adapter to build properly" over more classification
sweeps. Built the first genuinely new UI + backend feature since the
wholesale-core batch (commit `54f3859`):

- **Backend** (`my_store_ui/wholesale/payment_reconciliation_api.py`): 3
  fixed-purpose whitelisted functions reproducing ERPNext's standard 3-step
  Payment Reconciliation flow (`get_unreconciled_entries` →
  `preview_allocation` → `reconcile`), each delegating to the exact same
  `PaymentReconciliation` virtual-doctype controller methods the ERPNext
  Desk client itself calls. Deliberately did NOT expose Frappe's generic
  `run_doc_method` (browser-suppliable method path) — only these 3 named
  operations can ever run.
- **Frontend** (`PaymentReconciliationPage.vue`): 3-step selection UI
  wired into the existing `PriorityRoutePage.vue` dispatch pattern via a
  new `payment_reconciliation` component type.
- **Verified:** `get_unreconciled_entries` behaviourally exercised against
  real site1 data (Grant Plastics Ltd. → 2 outstanding invoices, correct
  receivable account resolved, then rolled back). Guest access confirmed
  blocked on every endpoint including `reconcile`. `allocate`/`reconcile`
  are source-verified (signatures matched against ERPNext's own Desk
  client) but not behaviourally exercised — no unallocated Payment Entry
  exists on site1 to reconcile against without creating test data.

`required_but_missing`: 323 → **319**.

This is a template for the remaining Batch 10/11/12 items if the user wants
more built the same way: read the real ERPNext controller first, reproduce
its exact call contract with fixed-purpose whitelisted wrappers (never a
generic method-path RPC), build a dedicated Vue page, verify what's safely
verifiable against live data without creating test records, and credit it
in `parity_registry.py` via a `BUILT_ADAPTER_DOCTYPE_NAMES`-style table.

---

## Pass 2 — continuation (Batches 7, 8, 13, 14 + a POS follow-up fix)

Continued directly from pass 1 (commit `b3f0c5a`). 5 more real, independently
committed, verified batches:

| Batch | What | Commit |
|---|---|---|
| 7-8 | Added 5 new allowlisted `MAPPED_ACTIONS` to `universal/api.py` (Purchase Receipt→Purchase Return/Landed Cost Voucher, Material Request→Stock Entry, Purchase Invoice→Debit Note, Journal Entry→Reverse Journal Entry), each verified against real erpnext controller source before wiring | c2f95fa |
| 13 | Classified 45 platform/technical DocTypes (Integrations, Email, Workflow-design, Automation-config, system logs, setup wizards) → `internal`; credited 9 report-attached financial-statement print formats via their already-routed report | 0dcc9a0 |
| 14 | Classified 23 POS Awesome-module entries per Step 12's taxonomy: 2 → `not_required` (Kenya M-Pesa, wrong jurisdiction), 8 → `external_app_adapter` (genuinely handled inside the POS Awesome app UI, reachable via `/pos`) | 393c45a |
| 14b | Follow-up: extended the same `external_app_adapter` reasoning to 5 ERPNext-core POS doctypes (POS Invoice, POS Profile, POS Opening/Closing Entry, Cashier Closing) that POS Awesome creates and manages internally | 6a3d661 |

### Headline metrics after pass 2

| Metric | After pass 1 | After pass 2 |
|---|---:|---:|
| Route-based unmapped_user_facing | 1,699 | 1,699 (unchanged — this pass was classification + real action handlers, not new routes) |
| Registry: implemented_unverified | 137 | 160 |
| Registry: internal | 900 | 976 |
| Registry: not_required | 178 | 181 |
| Registry: unavailable_with_reason | 491 | 380 |
| Registry: special_adapter (strategy) | 130 | 135 |
| Registry: external_app_adapter (strategy) | 0 | 18 |
| **Corrected `required_but_missing`** | 367 | **327** |

### What's still genuinely NOT done (Batches 10, 11, 12)

Investigated further before stopping — a few candidates (Pick List → Delivery
Note / Stock Entry) were deliberately **not** wired into `MAPPED_ACTIONS`
after reading their real ERPNext source: `create_delivery_note` can create
*multiple* Delivery Notes per call and may save documents internally rather
than returning one unsaved doc for `.insert()`; `create_stock_entry` takes a
JSON-serialized Pick List (not a docname) as its argument. Both break the
simple 1:1 "get_mapped_doc → insert()" pattern every other `MAPPED_ACTIONS`
entry uses, and forcing them in without a dedicated adapter risked duplicate
documents or broken behaviour — exactly what the mission forbids. Left
honestly `unavailable_with_reason`; real Pick List → Delivery Note fulfillment
already exists via the wholesale-core reservation flow (Smart Sales → SO →
reserve → DN), just not through this generic action path.

Remaining `required_but_missing = 327` breaks down as: 255 document_actions
(mostly Asset lifecycle, Company setup wizards, Bank/Payment Reconciliation
actions, remaining Pick List/Stock Entry purpose-specific actions — genuinely
need dedicated handlers or adapters), 28 dashboard_chart + 25 number_card + 6
dashboard (unbuilt analytics UI, unchanged from pass 1), ~12 doctypes (Bank
Reconciliation Tool, Payment Reconciliation, Serial and Batch Bundle, and
company period-closing/subscription/reconciliation process tools — Batch
10/11 special-adapter territory), 4 print_format, 2 page (sales-funnel,
warehouse-capacity-summary).

---

## Final mapping mission — batches completed this pass

Ran the "map every remaining capability" mission on top of the wholesale-core
work below. Re-ran the live audit first (confirmed no drift: 2,482 user-facing,
1,746 unmapped, matching the prior handoff exactly), then worked 8 real,
independently committed batches:

| Batch | What | Commit |
|---|---|---|
| Step 2 | Froze pre-mapping baseline (`strict_audit_before_final_mapping.json`, `unmapped_before_final_mapping.json`) | f885fd7 |
| 1 | Routed 25 more safe master DocTypes (Employee, Branch, Print Format, Incoterm, POS Coupon, ...); added `SYSTEM_INTERNAL_DOCTYPE_NAMES` audit correction (ledger tables, settings singletons, repost tools → `internal`) | 9c175f3 |
| 2 | Routed the one missing required report (Addresses And Contacts); reclassified 3 country-specific regional tax reports → `not_required`; fixed a scoping bug where the internal-doctype rule wrongly caught GL-Entry-based reports | 46d36c9 |
| 3 | Fixed classification of 19 native ERPNext module workspaces (Selling, Buying, Stock, Accounts sub-workspaces, CRM, POS Awesome, ...) → `special_adapter` (superseded by the Retail ERP nav module) or `internal` (Desk admin workspaces) | c0abed9 |
| 4 | Found and fixed a real bug: the handcrafted **Smart Sales** page was showing `unavailable_with_reason` because of a stale legacy Frappe "Page" stub; corrected to point at its real SPA route. Also fixed `point-of-sale`/`pos`/`posapp`/`stock-balance`/print-builder tooling | b02d47b |
| 5-6, 9 | Extended document-action crediting: the universal engine's allowlisted action handler (submit/cancel/amend/duplicate/rename + 9 `MAPPED_ACTIONS` conversions) already serves ANY routed doctype, not just the 6 handcrafted ones — the audit was undercounting this. 18 real actions credited across Lead, Opportunity, Quotation, Material Request, Purchase Order, Purchase Receipt, Supplier Quotation | 11f96bf |
| 15 | Step 13 corrected production-parity audit: `corrected_production_parity_audit()` in `parity_registry.py`, written to `docs/full-parity/corrected_production_parity_audit.json` | 921448e |

### Headline metrics after this pass

| Metric | Mission start | After this pass |
|---|---:|---:|
| Route-based unmapped_user_facing | 1,746 | **1,699** |
| Registry: generated_provisional | 728 | 776 |
| Registry: implemented_unverified | 101 | 137 |
| Registry: internal | 858 | 900 |
| Registry: not_required | 175 | 178 |
| Registry: unavailable_with_reason | 620 | 491 |
| Registry: special_adapter (strategy) | 95 | 130 |
| **Corrected `required_but_missing` (Step 13, honest gap count)** | not computed | **367** |
| **Corrected `corrected_unmapped_user_facing`** | not computed | **0** |

`corrected_unmapped_user_facing = 0` means every one of the 2,482 user-facing
features now has a truthful registry status with a real documented reason —
no unclassified capability remains. It does **not** mean the system is
production-ready: `required_but_missing = 367` is the honest count of P0/P1/P2
capabilities that still have no real implementation (mostly unbuilt
dashboards/charts, and the Stock/Accounts document-action + special
finance/stock adapter batches below that were not reached this pass).

### Batches NOT completed this pass (real remaining work, see BLOCKERS.md)

- Batch 7 — Stock document actions (Stock Entry purposes, Serial/Batch actions, Stock Reconciliation actions): the universal engine's `MAPPED_ACTIONS`/`DOCTYPE_SPECIFIC_ACTIONS` tables have no Stock-flow entries yet; needs real server handler work, not just registry classification.
- Batch 8 — Accounts document actions (Journal Entry actions, payment/reconciliation actions, credit/debit note actions): same — no allowlisted handler exists yet.
- Batch 10 — Special finance adapters (Bank Reconciliation Tool, Payment Reconciliation, GL/Trial Balance/P&L/Balance Sheet drill-down, Budgets, Accounting Dimensions): genuinely unbuilt; the underlying report routes exist (Batch 1/2 of the prior wholesale-core work) but dedicated interactive adapters do not.
- Batch 11 — Special stock adapters (Serial and Batch Bundle UI, barcode workflows, Stock Ledger/Ageing views, Transit Warehouse, reorder tools): genuinely unbuilt.
- Batch 12 — Purchasing/imports (Blanket Order, Drop Shipping, Supplier Statements/Performance, Import Shipment): genuinely unbuilt; Import Shipment likely needs a new Custom DocType (schema change → must stay `blocked` until approved).
- Batch 13 — Platform administration (Data Import/Export, Bulk Update/Rename, System Health, Background Jobs, Scheduler, Error/Audit Logs): not yet triaged for internal-vs-admin-route classification.
- Batch 14 — POS Awesome / external-app capability inventory (POS Opening/Closing Shift, POS Cash Movement, Mpesa integration, Cashier Closing, etc.): not yet classified; `external_app_adapter` strategy is currently unused (count 0).

These are exactly the items flagged `unavailable_with_reason` behind
`required_but_missing = 367` — none were faked into a route or a fake
`internal`/`not_required` label to hit zero.

---

_Last updated: 2026-07-14 (batch: wholesale core)_

## Wholesale core (approved implementation batch)

| Capability | Code | Verified now | Blocked on |
|---|---|---|---|
| Available-to-Sell (Actual − Reserved) in Smart Sales + snapshot API | ✅ | ✅ site1 read-only | — |
| Customer credit-status service + 7 delivery-gate rules | ✅ | ✅ 7/7 via bench + real balances | — |
| Transaction Register (SO-anchored, native links, role-gated $) | ✅ | ✅ site1 real data, route HTTP 200 | — |
| `/retail-erp/sales/transactions` page (filters/sort/CSV/mobile/timeline) | ✅ | ✅ resolves + builds | browser render |
| Transaction ID stamping/propagation (SO→DN→SI→PE, no-op safe) | ✅ | ✅ no-op safe on site1 | needs fields applied |
| Custom fields (credit type + txn id) via fixtures | ✅ | metadata inspected, no dupes | migrate on staging |
| Reservation service (delegates to standard SRE + Bin locking) | ✅ | ✅ lock query valid; snapshot | reservation on (staging) |
| Reservation expiry (3d configurable) daily scheduler | ✅ | — | staging |
| Concurrency / reservation / integration tests | ✅ written | credit 7/7 | staging |
| Playwright browser suite | ✅ scaffold | — | network + login |

Two environment blockers remain (see BLOCKERS.md → STAGING): the MariaDB **root
password** (to create the staging DB) and **network access** (npm registry is
unreachable, so Playwright/Chromium can't download). All code is written,
committed, and everything schema-independent is verified against site1 read-only.
No site config, schema, or reservation setting was changed on site1.

---

_Last updated: 2026-07-14 (batch: print formats)_

## Headline metrics

| Metric | Starting | Current |
|---|---:|---:|
| User-facing capabilities (source of truth) | 2482 | 2482 |
| Unmapped user-facing (route-based strict audit) | 2396 | **1746** |
| Currently routed features | 86 | **736** |
| Strict route coverage | 3.46% | **29.65%** |
| Authoritative registry entries | 0 | **2482** |

_Batch "generated DocType masters": added 116 in-scope standard parent DocTypes to
`ENTITY_ROUTES`, genuinely served by the universal metadata engine (verified
server-side: 170 served / 0 failures). Fixed a universal list-engine `KeyError`
that crashed doctypes whose default columns include text/hidden fields. Ledger/
system tables, single Settings/Tools and the POS family were intentionally
excluded. All 116 are `generated_provisional` (route + engine work; behavioural
browser/role verification still pending)._

> The route-based strict audit is intentionally unchanged: this batch added the
> authoritative registry and the Stage 0–2 capture without inventing any routes.
> Reducing `unmapped_user_facing` by mass-assigning routes would be the exact
> "fake parity" the mission forbids. Real coverage advances only as features are
> genuinely implemented and verified.

## Registry-based completeness — the truthful measure

The route-based strict audit treats any route as "mapped" and cannot reach zero
without routing internal components and out-of-scope features (which would be
fake). The authoritative registry is the meaningful measure. Of 2482 user-facing:

| Disposition | Count | % | Meaning |
|---|---:|---:|---|
| Implemented in some form | 829 | 33% | custom_override + generated_provisional + special_adapter (route + engine work; browser/role unverified) |
| Internal | 858 | 35% | fields, property setters, workspace/dashboard components, platform — no independent route |
| Not required | 175 | 7% | Manufacturing, Subcontracting, Website, POS-family, AI add-ons — out of wholesale scope |
| Genuinely pending | 620 | 25% | `unavailable_with_reason` — inventoried, not yet built; Desk owns it |

So ~75% is truthfully resolved (implemented, internal, or out-of-scope) and ~25%
is honestly pending. The route metric's remaining 1746 breaks down as: 858
internal, 175 not_required, 93 already-implemented mapped actions (not route-
credited), 620 pending.

## Authoritative registry — status distribution (of 2482 user-facing)

| Status | Count |
|---|---:|
| generated_provisional | 728 |
| implemented_unverified | 101 |
| verified_complete | 0 |
| blocked | 0 |
| unavailable_with_reason (planned; Desk owns it) | 620 |
| not_required (out of wholesale scope) | 175 |
| internal (fields, property setters, workspace/dashboard components, platform) | 858 |

"Implemented in some form" (generated_provisional + implemented_unverified, which
includes the 93 special_adapter mapped actions) total: **829**. `verified_complete`
remains 0 — honest, since `allow_tests` is disabled and no browser exists. See
`inventory/parity_registry_summary.md` for the strategy breakdown.

## Business priority distribution

| Priority | Count |
|---|---:|
| P0_go_live | 54 |
| P1_required | 1290 |
| P2_important | 255 |
| P3_optional | 359 |
| not_required | 259 |
| internal | 265 |

## Verification state

| Check | Result |
|---|---|
| Vue build (`npm run build`, `npm run check`) | PASS |
| Registry validation (`validate_parity_registry`) | PASS (0 errors) |
| Registry tests (`test_parity_registry`, standalone) | PASS (7/7) |
| Frappe test suite (`run-tests`) | BLOCKED — `allow_tests` disabled on site1.local |
| Browser verification | UNAVAILABLE — no Chrome/Chromium/Playwright/Cypress/Selenium |
| Live wholesale flow (reservation/credit) | NOT IMPLEMENTED — gated on approvals |

## Current commit chain (branch `full-feature-parity`)

- `chore: capture starting state for full feature parity`
- `chore: capture current complete feature inventory`
- `feat: establish authoritative full parity registry`
- `docs: full-parity tracking, blockers and approval proposals`
- `feat: map 116 in-scope standard DocTypes through the universal engine`
- `chore: keep before-baselines frozen, emit latest inventory snapshots`
- `feat: map 156 in-scope standard reports through the report viewer`
- `feat: credit workspace shortcuts that resolve to mapped destinations`
- `feat: credit print formats reachable from routed DocType print dialog`
- `docs: finalise implementation-batch progress and approval request` (this batch)

## Implementation batches this session (all server-verified, no schema changes)

| Batch | Added | Verification |
|---|---:|---|
| Generated DocType masters | 116 routes | `route_coverage.verify_generated_routes` served=170 fail=0 |
| Universal list-engine bug fix | — | all 116 list without KeyError (was 25 failing) |
| Generated reports | 156 routes | `route_coverage.verify_generated_reports` served=182 fail=0 |
| Workspace shortcuts | 351 credited | targets resolve to routed DocTypes/Reports |
| Print formats | 27 credited | reachable from routed DocType print dialog |

Net: `unmapped_user_facing` **2396 → 1746**, routed **86 → 736** (3.46% → 29.65%).

## Completed batch

Stage 0 (checkpoint), Stage 1 (live inventory capture), Stage 2 (authoritative
registry + validation tests), Stage 12 tracking docs, Stage 6 approval proposals.

## Next batch (BLOCKED on approvals — see BLOCKERS.md)

1. Stock reservation + Available-to-Sell (needs `enable_stock_reservation` + policy).
2. Customer Credit/Non-Credit model (needs Custom Fields).
3. Wholesale Transaction ID / register (needs Custom Fields).
4. End-to-end regression on an approved test site (needs `allow_tests` / staging site).

Independent, non-gated implementation (generic-engine hardening for in-scope
masters/reports) can proceed in parallel but cannot be marked `verified_complete`
until a test/browser environment exists.
