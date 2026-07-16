# SMJ Retail ERP — Browser Verification Results (2026-07-16)

## Method

**No real browser automation ran.** Playwright is not installed; installing
it was attempted (with explicit user approval) and failed at the network
layer — `npm install -D @playwright/test` fails with
`UNABLE_TO_VERIFY_LEAF_SIGNATURE` even against the system CA bundle and even
with Node's `--use-system-ca` flag (the exact fix npm's own error message
suggests). A plain HTTP request to the same registry returned `403`, which
together points at a sandbox egress proxy that cannot be bypassed safely —
disabling TLS verification was not attempted. No Chromium/Firefox binary and
no `pip playwright` package exist either. This is an environment limitation,
not a permissions one.

**What ran instead:** an authenticated HTTP verification harness
(`curl`/Python `urllib` against the live `bench serve` instance on
`127.0.0.1:8000`), plus rigorous source-code review of every shell component
and every stylesheet. Every result below is labeled accordingly. Nothing is
reported as "browser-verified" — that column is honestly "not tested" for
every row.

**Test user:** `Administrator`. The password was set for this session at
the user's explicit instruction (`bench --site site1.local
set-admin-password <redacted>`) — this is a local dev site, not shared or
production infrastructure, and the password is not recorded here or
anywhere else in this repo. No other test accounts exist on this site
(only `Administrator` and the developer's own personal login).

## What the HTTP harness actually proved (not just "it built")

| Check | Result |
|---|---|
| Login (`/api/method/login`) | 200, session cookie issued |
| Session bootstrap (`get_session_bootstrap`) | 200, real user/company/roles/navigation, `csrf_token` present |
| Navigation payload icon/accent fields | All 11 permitted modules (`home, smart-sales, sales, purchases, inventory, finance, operations, crm, reports, pos, admin`) carry `icon` values that are all covered by `frontend/src/components/icons/moduleIconMap.js` — confirmed against the live server payload, not just the static route file |
| Global search (`my_store_ui.search.global_search`) | Real query for `"item"` returns an actual `Item` (`SKU005`, "Sneakers") with a correctly-shaped route (`/inventory/products/SKU005`); irrelevant queries correctly return 0, not an error |
| Home dashboard (`get_module_dashboard?module=home`) | Real, non-hardcoded counts (3 customers, 3 suppliers, 11 products, 165 accounts, 5 sales invoices, etc.) — confirms Section 12.A's "no hardcoded preview values" requirement |
| All 9 other module dashboards | All return 200 with the identical, consistent response shape |
| Report hub (`get_report_hub`) | 200, real group/report structure |
| Universal engine — list configuration | Correct 403 for `feature=customer` ("not available through the generated engine" — Customer is a handcrafted page, confirmed intentional, not a bug) and correct 200 + real column/filter metadata for a genuine generated doctype (`asset`) |
| Universal engine — document list | 200, legitimate empty result for `asset` (0 records exist in this demo dataset — a true empty state, not an error) |
| Tree page (`get_tree_nodes`, Chart of Accounts) | 200, real account hierarchy nodes returned |
| Report execution (`run_priority_report`, Sales Register) | 200, **2 real data rows**, columns, chart payload, summary — the report engine genuinely executes against real data with real filters |
| Universal engine — missing record | `get_document_detail` for a non-existent name returns a clean `404 DoesNotExistError` with a safe user-facing message, no leaked internals in the message shown to the client |
| Route authorization (`authorize_frontend_route`) | Correctly distinguishes handcrafted pages ("This route uses a dedicated Retail ERP page") from generated ones, and correctly resolves clean URLs (`/finance/bank-reconciliation`, `/admin/users`, etc.) to permission-checked outcomes |
| Logout | Sending the CSRF token the real frontend code sends (`session.js`), logout returns 200 and a subsequent `get_session_bootstrap` call correctly returns `authenticated: false` — the session is genuinely terminated server-side |
| Guest (unauthenticated) bootstrap | 200, `authenticated: false`, no error — confirms the guest path doesn't crash |
| SPA shell routing | Every `/retail-erp/*` path tested (including a deliberately invalid one) returns `200` with the SPA shell — server-side deep-linking/refresh never 404s, Vue Router handles the rest client-side |
| Asset delivery | The exact CSS/JS files referenced by the served HTML resolve with `200` and match byte-for-byte the sizes from the last `npm run build`; grepped for known SMJ markers (`07369d`, `smj-icon`) to confirm the live site is serving the actual themed build, not a stale cache |

## What was NOT verified (honest gaps)

- Real console output (`console.error`, unhandled rejections, Vue warnings) — impossible without a browser.
- Actual rendered layout/overflow at any viewport — impossible without a browser. The responsive claims in `SMJ_MOBILE_VERIFICATION.md` remain CSS-math-based, not rendered.
- Click-through flows: opening the search dropdown and clicking a result, opening the user menu, adding an item to the Smart Sales cart, submitting a form, etc.
- Permission-denied *behavior for a restricted user* — only `Administrator` (which has every role) was available to test with; no second, lower-privileged account exists on this site and creating one was judged out of scope for a UI verification pass.
- The ~180 total generated reports — only General Ledger-adjacent groups were sampled (Sales Register was run end-to-end with real data; others were not individually executed). This matches the mission's own instruction to record wider report coverage as separate remaining work.
- Calendar and Kanban — genuinely not implemented anywhere in this codebase yet (confirmed via `UniversalSpecialPage.vue`'s own honest placeholder text: "Reports, Workspaces, dashboards, Kanban, calendars and trees require specialised rendering... does not open Desk"). Nothing to test; this is accurately blocked, not skipped.

See `SMJ_BROWSER_ISSUES_FIXED.md` for the defects the code-review half of this
pass found and fixed.
