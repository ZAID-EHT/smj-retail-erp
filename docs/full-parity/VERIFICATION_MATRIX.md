# Full Feature Parity — Verification Matrix

Verification levels: **behavioural** (driven end-to-end with evidence),
**source_only** (code exists, read/reviewed), **route_only** (a route resolves),
**none**. Nothing reaches `verified_complete` without behavioural evidence.

## "Complete all pending tasks" continuation (2026-07-15, passes 13-21 — session end)

| Item | Level | Evidence |
|---|---|---|
| Pick List reservation gating | behavioural (server) | Confirmed site1 has `enable_stock_reservation=0`, so `create_stock_reservation_entries`/`reserve` correctly never appear even though the code path exists - verified the gate itself works, not just that the action is absent |
| 4 dead-credit bugs found and fixed | source_only, reproduced via required_missing diff | Each confirmed by checking the exact scanner-recorded `mapped_actions[0].action` string against the existing internal credit key, reading the real `.js` source to confirm the button calls the already-implemented server method, then verifying the specific `required_but_missing` entry disappeared after the fix (295→288-style before/after count matching for each individual batch) |
| Purchase Invoice make_lcv | behavioural (server) | Verified against a real submitted Purchase Invoice with `update_stock=1` (ACC-PINV-2026-00010/11/12) - action correctly appears |
| Supplier accounting_ledger/accounts_payable | behavioural (server) | Verified against a real Supplier (Zuckerman Security Ltd.) - both routes resolve with correctly percent-encoded party filter |
| Material Request/RFQ/Supplier Quotation/Lead/Opportunity/Quotation write actions | source_only | No submitted/draft records of these types exist on site1 - all source-verified only (signatures matched against real erpnext controller/JS source) |
| Registry tests / route+report verifiers / npm build | behavioural | 7/7 pass throughout all 9 batches; route verifier steady at 204 (no new routes past the Pick List batch); report verifier 183/0 failed; build passes on every commit |
| Final inventory regeneration (session end) | behavioural (server) | fingerprint unchanged at `af61813f...` from the last route-adding batch, confirming everything since was action-only credits, not route changes needing inventory regen |

## CONTINUE FROM 2e4c314 (2026-07-15, passes 9-12 — Priority 5 + Batch 11/12 warm-up)

| Item | Level | Evidence |
|---|---|---|
| Purchase Invoice block_invoice/unblock_invoice/change_release_date visibility | behavioural (server) | `_available_actions` against real submitted invoices with outstanding_amount=0 (actions correctly absent) and outstanding_amount=105000 (block_invoice correctly present) |
| Serial and Batch Bundle / Process Payment Reconciliation(+Log) routes | behavioural (server) | `route_coverage.verify_generated_routes` 201→204 served, 0 failed; `is_virtual`/`issingle`/`istable` confirmed false against installed schema before routing |
| Bank Clearance / Pegged Currencies superseded-by-BRT investigation | source_only, inconclusive by design | Read `bank_clearance.py` in full - confirmed it sets clearance_date on Payment/Journal Entries directly (no Bank Transaction dependency), a genuinely different input model from Bank Reconciliation Tool - deliberately left un-reclassified rather than force an unverified "superseded" label |
| Warehouse stock_balance / Batch view_ledger navigation routes | behavioural (server) | Resolved against a real Warehouse record (`Goods In Transit - Carpets toD`) with correct `%20` encoding |
| Purchase Receipt close/reopen dedup (debit_note/purchase_return/landed_cost_voucher) | source_only | purchase_receipt.js read in full; confirmed each button calls the exact already-credited server method |
| Purchase Order payment / dedups (purchase_receipt/purchase_invoice/re_open) | behavioural (server) + source | `payment` action verified to appear on a real submitted PO (PUR-ORD-2026-00014); dedups verified via purchase_order.js source (`unclose_purchase_order()` → `update_status("Submitted")`, the same call the existing `reopen` action makes) |
| Supplier Quotation `make-purchase-invoice` investigated, NOT credited | source_only, negative result | Read `supplier_quotation.js` in full - no button calling `make_purchase_invoice` was found; left honestly unavailable_with_reason rather than guess it's a duplicate (see DECISIONS.md D21) |
| Registry tests / route+report verifiers / npm build | behavioural | 7/7 pass throughout; 204/183 served, 0 failed; build passes on every commit this session |

## FINISH ACCOUNTING FIRST (2026-07-15, passes 7-8 — Priority 4 period closing)

| Item | Level | Evidence |
|---|---|---|
| Account/Cost Center/Company/Journal Entry/Period Closing Voucher/Warehouse actions appear correctly | behavioural (server) | `_available_actions` called directly against real Account, Cost Center, Company records on site1 - exact expected action lists returned |
| Navigation routes resolve with correct percent-encoding | behavioural (server, bug found+fixed) | `run_document_action("account", ..., "general_ledger")` first returned `+`-encoded values (broken for `route.query`), reproduced then fixed to `%20` via `quote_via=quote` |
| PriorityReportPage.vue / PriorityTreePage.vue query-string bug | behavioural (source, bug found+fixed) | Neither component read `route.query` at all - confirmed by reading the full script blocks; fixed and rebuilt |
| 5 new Process-tool doctype routes | behavioural (server) | `route_coverage.verify_generated_routes` 196→201 served, 0 failed; each doctype's `is_virtual`/`issingle`/`istable` checked false against the installed schema before routing |
| Exchange Rate Revaluation/Dunning/Process Period Closing Voucher write actions | source_only | No submitted Exchange Rate Revaluation, Dunning, or Process Period Closing Voucher records exist on site1 - actions are source-verified (signatures matched, idempotency checks reproduced) but not behaviourally exercised |
| Registry tests / route verifier / npm build | behavioural | 7/7 pass; 201 served / 0 failed; build passes across both sub-batches |
| `generate_complete_inventory` re-run after route additions | behavioural (server) | fingerprint changed `69a2005d...`→`abc8d813...`, route-based `unmapped_user_facing` 1699→1694 (-5, matching the 5 new routes exactly) |

## FINISH ACCOUNTING FIRST (2026-07-15, pass 5 — financial report drill-down fixes)

| Item | Level | Evidence |
|---|---|---|
| AR/AP `report_date` fieldname bug | behavioural (source + server) | Confirmed real fieldname via `accounts_receivable.js`/`accounts_payable.js`; re-ran both reports live against site1 with `report_date` filter, returned results without error |
| Customer Ledger Summary `party` fieldname bug | behavioural (source + server) | Confirmed via `customer_ledger_summary.js`; re-ran live with `party` filter |
| MultiSelectList JSON-vs-list bug | behavioural (server, reproduced then fixed) | First attempt (`frappe.as_json([value])`) reproduced the exact `ValidationError: Cost Center: ["SMJ (Demo) - Carpets toD"] does not exist` against real site1 data; root-caused via `erpnext.accounts.report.financial_statements.get_cost_centers_with_children` source; fixed to a real list, re-verified clean run (75 rows) |
| General Ledger with cost_center + party filters | behavioural (server) | 75 rows (cost_center), 14 rows (party=`Palmer Productions Ltd.`), 116 rows (no filter) — all against real site1 data |
| Accounts Receivable / Trial Balance / P&L / Balance Sheet / Cash Flow / Supplier Ledger Summary | behavioural (server) | Each executed successfully against real site1 data with the new filter sets |
| `route_coverage.verify_generated_reports` / `verify_generated_routes` | behavioural (server) | served=183/failed=0, served=196/failed=0 — unchanged, confirms no report route regressed |
| Registry tests / `npm run build` | behavioural | 7/7 pass; build passes (backend-only change, frontend unaffected since `PriorityReportPage.vue` renders filters generically) |

## FINISH ACCOUNTING FIRST (2026-07-15, pass 4 — Bank Reconciliation Tool)

| Item | Level | Evidence |
|---|---|---|
| Bank Reconciliation Tool controller reading | source_only | Read `erpnext/accounts/doctype/bank_reconciliation_tool/bank_reconciliation_tool.py` in full — confirmed virtual doctype (`Document` subclass body is `pass`), no built-in permission checks on any module-level whitelisted function |
| Journal Entry Type allowlist | source_only | Matched exactly against `erpnext/public/js/bank_reconciliation_tool/dialog_manager.js:319` field options |
| Route resolution (`/finance/bank-reconciliation` → `bank_reconciliation`) | behavioural (server) | `get_priority_route_definition` called directly against site1, returned correct component/doctype/permissions |
| `search_bank_account` / `search_account` / `search_mode_of_payment` / `search_party` | behavioural (server) | Exercised against real site1 data as Administrator — Account search returned `Cash - Carpets to`, Mode of Payment returned `Credit Card`/`Cash`/`Cheque`, party search returned 3 real customers |
| `get_summary` error path (nonexistent bank account) | behavioural (server) | Raised `ValidationError: Bank account does not belong to the selected company` — not a crash |
| Guest blocked on all 14 new whitelisted endpoints | behavioural (server) | Each called directly with `frappe.session.user = "Guest"`; all raised `AuthenticationError` |
| `get_summary`/`get_matches`/`reconcile_transaction`/`unreconcile_transaction`/`preview_*`/`confirm_*`/`auto_reconcile` write paths | source_only | site1 has zero `Bank Account`/`Bank Transaction` records — no data to reconcile against without creating test data; signatures matched against erpnext's real controller functions |
| Registry crediting (`BUILT_ADAPTER_ACTIONS_BY_PARENT` refactor) | behavioural (script) | `required_but_missing` 319→312 (exactly 1 doctype + 6 document actions, as designed); `test_parity_registry.py` 7/7 PASS after the refactor |
| `route_coverage.verify_generated_routes` / `verify_generated_reports` | behavioural (server) | served=196/failed=0, served=183/permission_denied=1(pre-existing)/failed=0 — unaffected by this batch (no ENTITY_ROUTES/REPORT_GROUPS change) |
| Vue production build | behavioural | `npm run build` PASS, 111 modules |
| `generate_complete_inventory` re-run (drift check) | behavioural (server) | fingerprint unchanged (`69a2005d...`), unmapped_user_facing unchanged at 1699 — confirms this batch changed component dispatch, not route presence |
| Browser render of BankReconciliationPage.vue | not run | No browser automation installed (same GATE 5 blocker as always) |

## URGENT MAPPING MISSION (2026-07-14, final mapping pass 1)

| Item | Level | Evidence |
|---|---|---|
| 25 new master DocType routes | behavioural (server) | `route_coverage.verify_generated_routes` served=196 (was 170), failed=0; all 25 confirmed `istable=0`/`issingle=0` via `frappe.client.get_list` before routing |
| 1 new report route (Addresses And Contacts) | behavioural (server) | `route_coverage.verify_generated_reports` served=183, failed=0 |
| `SYSTEM_INTERNAL_DOCTYPE_NAMES` correction (30 ledger/settings/tool doctypes → internal) | source_only + registry validation | `validate_parity_registry` PASS after each change; scoping bug (false-positive on GL-Entry-based reports) found and fixed same session |
| `WORKSPACE_OVERRIDES` (19 native workspaces → special_adapter/internal) | source_only | Cross-checked against existing `MODULES`/`ENTITY_ROUTES` nav structure in `priority_registry.py` |
| Smart Sales page bug (legacy stub vs real SPA route) | behavioural (source) | Confirmed real route in `frontend/src/router/routes.js:20-22` (`path: "/smart-sales"`) before correcting |
| Document-action crediting (18 actions: Lead, Opportunity, Quotation, Material Request, Purchase Order, Purchase Receipt, Supplier Quotation) | source_only | Read `my_store_ui/universal/api.py` `MAPPED_ACTIONS` + `_available_actions` directly; only credited actions with a real matching handler AND a routed parent doctype |
| Step 13 corrected audit computation | behavioural (script) | Spot-checked `required_but_missing_feature_keys` sample — all genuine gaps (unbuilt dashboard charts), zero false positives after the priority/status bug fix |
| Vue production build (7 times, once per batch) | behavioural | `npm run build` PASS every time, 109 modules, same hashed bundle names |
| Standalone registry tests | behavioural | `PYTHONPATH=. python3 my_store_ui/tests/test_parity_registry.py` → 7/7 PASS, run after every batch |
| Frappe `bench run-tests` / browser / staging | not run | Same environment blockers as before: `allow_tests` disabled on site1.local, no browser automation installed. Not attempted this pass — out of scope per the mission's "minimal checking only" instruction. |

## What was verifiable this mission (prior wholesale-core pass)

| Item | Level | Evidence |
|---|---|---|
| Vue production build | behavioural | `npm run build` / `npm run check` PASS, hashed bundle |
| Parity registry honesty contract | behavioural | `validate_parity_registry` PASS; 7/7 unit tests PASS standalone |
| Live inventory counts | behavioural | `generate_complete_inventory` re-run, fingerprint match |
| Blocker facts (reservation/credit/doc counts) | behavioural | read-only Frappe console queries |
| `wkhtmltopdf` present | behavioural (prior audit) | `wkhtmltopdf --version` 0.12.6.1 |
| 116 generated DocType routes (list config + list API) | behavioural (server) | `route_coverage.verify_generated_routes` → served=170, failed=0 |
| Universal list-engine text/hidden column fix | behavioural (server) | all 116 doctypes list without KeyError after fix |
| 156 generated report routes (definition + viewer) | behavioural (server) | `route_coverage.verify_generated_reports` → served=182, failed=0 |
| 351 workspace shortcuts credited to routed targets | behavioural (audit) | targets present in CANONICAL_ROUTE_BY_DOCTYPE / REPORT_GROUPS |
| 27 print formats credited to routed DocTypes | behavioural (audit) | doc_type present in CANONICAL_ROUTE_BY_DOCTYPE |
| Available-to-Sell in get_bootstrap (Actual/Reserved/Available/Projected) | behavioural (server) | real Bin data on site1 |
| Customer credit status + 7 delivery-gate rules | behavioural (server) | 7/7 PASS via bench execute; real balances |
| Wholesale transaction register + timeline | behavioural (server) | 5 real transactions, correct links/status/outstanding |
| /sales/transactions route resolves + page builds | behavioural (server) | component=register, HTTP 200, Vue build |
| Transaction-id propagation hooks safe on site1 | behavioural (server) | no-op confirmed with field absent |
| Reservation Bin-lock (FOR UPDATE) query validity | behavioural (server) | `_lock_bins` runs, rolled back |
| Reservation reserve/unreserve/expiry, concurrency 10/8/8 | NOT verified | needs staging (reservation on) |
| Applying custom fields (credit type + txn id) | NOT verified | needs migrate on staging |
| Browser (register render, Smart Sales, mobile) | NOT verified | needs Playwright (network) + login |

_Note: "behavioural (server)" means the exact resolve→feature→list API path was
driven as a real user server-side and returned. Browser rendering, role matrix
and interactive actions for these routes remain unverified (no browser)._

## What could NOT be verified (and why)

| Domain | Blocker | Registry status held at |
|---|---|---|
| Sales Order / DN / SI / Payment lifecycles | allow_tests off; no browser | implemented_unverified |
| Mapped-document actions (SO→DN, DN→SI, …) | allow_tests off; no browser | implemented_unverified / special_adapter |
| Stock reservation / Available-to-Sell | not implemented; GATE 1 | (unavailable) |
| Customer credit gate | not implemented; GATE 2 | (unavailable) |
| Transaction register | not implemented; GATE 3 | (unavailable) |
| Generic-engine doctypes/reports | route_only at best; no browser | generated_provisional |
| Collaboration writes / email | no outgoing Email Account; no browser | unavailable / provisional |

## Manual browser verification checklist (for when GATE 5 opens)

Run in Chrome and Edge on an approved staging site with single-role users:

1. Login, invalid/disabled/expired/OTP, logout, browser Back.
2. Each handcrafted route: list/new/detail/edit/save/submit/cancel/amend/map/
   return/print/PDF; validation and permission errors preserved.
3. Representative generated master + transaction routes; field permlevels; child tables.
4. Reservation concurrency: two sessions, 10 available, two 8-unit reservations → never 16.
5. Credit gate: over-limit and overdue customers blocked / manager-approved correctly.
6. Responsive 1920/1440/1366/1280/1024 and 768/390/375/320 at 80–150% zoom;
   vertical scroll, no horizontal overflow, dialog focus, keyboard/touch.
7. Collaboration: comments/files/assign/share/tags/version/email; inaccessible-record non-disclosure.
8. Capture screenshots, console/network logs, created document chain, ledger/stock reconciliation.

---

## Required-222 mission verification (2026-07-16)

16 new automated tests added this session, all passing against live site1
data via `bench execute` (standalone `unittest`, not `bench run-tests` —
`allow_tests` still disabled, GATE 4 unchanged):

- `my_store_ui/tests/test_module_dashboards.py` (10 tests) — all 6 module
  dashboards return every required card/chart key with real computed
  values; internal cross-checks against `frappe.db.count()`; guest denied;
  no raw SQL/`ignore_permissions`; frontend wiring present.
- `my_store_ui/tests/test_dashboard_connections.py` (6 tests) — real linked
  documents returned for Purchase Invoice/Supplier with working routes;
  only app-routed, permission-checked doctypes surfaced; guest denied;
  registry credits all 19 connection actions and the duplicate-key fix;
  frontend wiring present.

Not verified: browser/UI rendering (GATE 5, unchanged), `bench run-tests`
execution (GATE 4, unchanged). See `REQUIRED_222_COMPLETION_REPORT.md`.

---

## SMJ Master Mission — GATE 4 and GATE 5 both closed (2026-07-18)

Full detail: `docs/execution/SMJ_MASTER_BATCH_LOG.md`,
`docs/ui/SMJ_BROWSER_VERIFICATION.md`.

**GATE 4 (`bench run-tests` execution) — closed.** `allow_tests` enabled
on `staging.local`. First real run surfaced 36 errors, all traced to a
systemic 13-file test-infrastructure bug (hardcoded
`frappe.init(site="site1.local")` + `frappe.destroy()` in test
lifecycle hooks, corrupting shared process state and separately writing
test data against `site1.local` regardless of the target site — fixed
at the root in all 13 files) plus 3 smaller test-fixture defects. Final:
**201 tests, 198 passed, 3 skipped, 0 failures, 0 errors.**

**GATE 5 (browser/UI rendering) — closed.** Real Linux-native Playwright
Chromium (not Windows Chrome, not headless-screenshot-only) verified all
18 named workspaces at all 6 required viewports: 108/108 clean (0
overflow, 0 console errors, 0 failed requests). Deep interaction
testing (real clicks, not just presence) covered Home's full interactive
surface and one representative page per each of the app's 3 distinct
list/detail component engines. First-ever browser-level
permission-denied test in this project's history.

---
## 2026-07-27 (finance/deployment, v1.0.0-rc3)
- Opening-stock P&L: correction package built + QA-verified (savepoint); corrected
  profit 4,048,006; **not applied — accountant sign-off external**.
- Fresh-install script + Hetzner deployment package complete (live runs external:
  MariaDB root / Hetzner / DNS credentials).
- 338 backend tests green, 90/90 browser, secret scan clean, site1.local untouched.

## 2026-07-27 RC4 (v1.0.0-rc4)
Admin landing/navigation, secure PDF, scheduled reports, two-company separation,
truthful launch-readiness dashboard. 369 backend tests green, 96/96 browser, secret
scan clean, site1 untouched. External: accountant/SMTP/MariaDB-root/Hetzner/DNS/UAT.

## Wholesale operations (2026-08-01, v1.0.0-rc8)

| Capability | Evidence | Verified |
|---|---|---|
| Carton UOM is a real conversion | test_carton_uom (11), test_carton_sales_flow (6) | yes |
| Customer Price Category drives the order rate | test_wholesale_acceptance scenarios 1-3 | yes |
| Availability judged in stock units | 5 cartons refused against 24 units | yes |
| Forged UOM refused | test_carton_sales_flow | yes |
| Idempotency survives cache loss | test_delivery_fifo, test_invoice_payment_flow, test_purchase_flow | yes |
| Non-Credit payment gate | test_delivery_fifo, acceptance 1-2 | yes |
| Credit gate + audited manager override | test_delivery_fifo, acceptance 4a/4b | yes |
| FIFO multi-batch allocation | test_delivery_fifo, acceptance 6 (10+2 of 12) | yes |
| Delivery reduces stock exactly once | acceptance 1 (50 -> 40) | yes |
| Partial then final delivery | test_delivery_fifo, acceptance 5 | yes |
| Over-delivery refused | test_delivery_fifo | yes |
| Final invoice + advance allocation | test_invoice_payment_flow (17) | yes |
| Payment allocation validated | test_invoice_payment_flow, acceptance 11 | yes |
| Sales return restores stock | test_sales_returns (16), acceptance 7 | yes |
| Credit note reduces receivable | test_sales_returns, acceptance 7 | yes |
| Purchasing to supplier payment | test_purchase_flow (18), acceptance 8 | yes |
| Purchase return + debit note | test_purchase_flow, acceptance 9 | yes |
| Landed cost raises valuation | test_landed_cost (8) — 2,000 charge -> +2,000 stock value | yes |
| Transaction ID propagation | acceptance 1b (SO -> DN -> SI) | yes |
| Register statuses and filters | test_transaction_register (13) | yes |
| Register route guard matches its API | test_register_route_permission (3) | yes |
| Dashboard withholds money from non-finance users | test_operations_dashboard (7) | yes |
| Navigation survives an absent optional app | test_navigation_missing_page (5) | yes |
| Six-viewport browser matrix | 162/162, zero console errors | yes |
| site1.local untouched | SHA256 fingerprint identical | yes |

## Sales Teams, snapshot and commission (2026-08-04)

| Requirement | Evidence | Verified |
|---|---|---|
| Team assigned to a Customer | test_sales_team (assignment, 8) | yes |
| Only active teams offered | test_search_only_offers_active_teams | yes |
| Inactive team refused on new work | test_an_inactive_team_cannot_be_used_on_a_new_document | yes |
| Smart Sales loads the customer's team | browser: card shows team, manager, reps, 50/25/25, 100% | yes |
| Stale response never wins | request-identity guard, asserted in the picker suite | yes |
| Permission-controlled override | test_a_manager_may_override_with_a_reason | yes |
| Override refused for a Sales User posting directly | test_an_ordinary_sales_user_cannot_override_even_by_posting_directly | yes |
| Override never changes the customer master | asserted in both override tests | yes |
| Sales Order freezes an immutable snapshot | test_order_stores_a_snapshot, browser | yes |
| Team-master edit cannot rewrite an old order | test_editing_the_team_master_does_not_change_the_old_order, browser | yes |
| Customer reassignment cannot rewrite an old order | test_reassigning_the_customer_does_not_change_the_old_order | yes |
| Submitted snapshot cannot be edited | test_a_submitted_snapshot_cannot_be_edited_in_place | yes |
| Concurrent master edit yields one consistent snapshot | test_a_team_edited_while_an_order_is_being_raised... | yes |
| Delivery Note preserves the snapshot | test_delivery_note_inherits_the_orders_snapshot | yes |
| Sales Invoice preserves it and earns on it | test_the_invoice_inherits_the_orders_frozen_team_and_earns_on_it | yes |
| Credit Note reverses proportionally | test_a_credit_note_reverses_the_commission_in_proportion (-4,000 = -2,000/-1,000/-1,000) | yes |
| Commission base / rate / pool / allocation / amount distinct | test_the_worked_example_from_the_requirements | yes |
| Manager is not paid a share of the whole sale | test_the_manager_is_not_paid_a_share_of_the_whole_sale | yes |
| Member amounts reconcile to the pool | test_member_amounts_reconcile_to_the_pool | yes |
| Percentages total exactly 100 for ERPNext | test_uneven_thirds_still_total_exactly_one_hundred | yes |
| Commission register with filters and export | test_commission (19), browser | yes |
| Register scoped to own lines for non-managers | test_a_sales_user_sees_only_their_own_lines | yes |
| Cross-company assignment denied | test_a_team_pinned_to_another_company_is_refused | yes |
| Backfill refuses the protected site | test_a_protected_site_is_refused_for_being_protected | yes |
| Backfill never guesses or rewrites history | test_a_customer_with_no_team_is_never_guessed_at, test_a_submitted_document_is_never_rewritten | yes |
| Backfill is idempotent | test_applying_twice_changes_nothing_the_second_time | yes |
| Six-viewport browser matrix | 228/228, zero console errors | yes |
| site1.local untouched | SHA256 fingerprint identical | yes |
| Commission payout | deferred — accountant approval required | documented, not implemented |
