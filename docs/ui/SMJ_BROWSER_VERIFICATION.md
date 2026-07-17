# SMJ Retail ERP — Browser Verification Results

## 2026-07-18 — real Linux-native Playwright automation (supersedes all prior sessions)

**This is the authoritative browser verification.** Every previous entry
in this file (below) used either no browser at all (HTTP-only) or
Windows Chrome reached through `/mnt/c/` via WSL interop — both
explicitly disallowed for this pass. This session used **only** the
Linux-native Chromium binary installed by Playwright inside WSL
(`~/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome`, located
via Playwright's own `chromium.executablePath()` API, never guessed),
launched with `chromium.launchServer()`/`chromium.connect()` so the
real OS process ID could be recorded and cleanly closed every time.

### Method

- Real UI login: navigated to `/login`, filled the actual form fields
  (`#login_email`, `#login_password`), clicked the real submit button,
  and confirmed a genuine `sid` session cookie was issued — not an API
  shortcut.
- Ephemeral Chromium profile per run (Playwright's own managed profile,
  created and destroyed automatically), never a persistent profile.
- Every browser process was closed via `browser.close()` +
  `browserServer.close()` (Playwright's own graceful shutdown), and the
  exact PID was logged and confirmed gone via `ps -p <pid>` afterward.
  No `taskkill`, `pkill`, or process-name kill used anywhere in this
  pass.
- Credentials: a fresh Administrator password was set for this session
  via `bench set-admin-password` (a local dev site, not shared
  infrastructure) and passed to the browser only through an environment
  variable, never printed to a log or committed to any file. A second,
  disposable test account (`smj.browser.restricted.test@smjretail.local`,
  role `Sales User` only) was created for the permission-denied check
  and fully deleted afterward.

### Full 108-point sweep (18 workspaces × 6 viewports)

Every one of the mission's 18 named workspaces was loaded at every one
of the 6 required viewports (1920×1080, 1440×900, 1024×768, 768×1024,
390×844, 360×800) — **108 real page loads**, not simulated. For each:
horizontal-overflow detection (`scrollWidth` vs `innerWidth`), console
error capture, uncaught page-error capture, failed-request/5xx capture,
and an interactive-element inventory (buttons/links/tables/inputs
present).

**Result: 108/108 clean.** Zero overflow, zero console errors, zero page
errors, zero failed requests, zero navigation errors, across every
workspace at every viewport. Raw data:
`docs/ui/evidence/runtime/2026-07-17T22-07-20-504Z/results.json`
(curated desktop+mobile screenshot pairs committed alongside it; the
full 108-screenshot set was generated locally during the run).

**A real routing bug was found and fixed during this pass, not
glossed over:** the first attempt at this audit used guessed URLs for 6
of the 18 workspaces (Wholesale Transaction Register, Purchase Orders,
Purchase Receipts, Purchase Invoices, Stock Entries, Stock
Reconciliation) based on an incorrect assumption that they used the
`/generated/:feature` engine. All 6 silently redirected to
`/retail-erp/not-found` — caught precisely because this pass checks
`finalUrl`, not just "did the request return 200" (which it did, since
`not-found` is itself a valid page). The real routes were found by
reading `my_store_ui/services/priority_registry.py`'s own
`CANONICAL_ROUTE_BY_DOCTYPE`/`SPECIAL_ROUTES` tables — not guessed a
second time — and the corrected re-run confirmed all 18 resolve to real
content with real buttons/tables/data.

### Deep interaction verification (not just "the route exists")

Per the mission's explicit rule against shallow verification, a second
pass exercised real interactive behavior. Full detail:
`docs/ui/SMJ_HOME_BROWSER_EVIDENCE.md`. Summary:

| Check | Result |
|---|---|
| Module nav dropdown | Opens, real teleported menu becomes visible |
| Global search | Typing "customer" produces a visible results dropdown |
| User menu | Opens, real menu becomes visible |
| KPI card click | Navigates from Home to a real destination (`/sales/invoices`), confirmed by URL change |
| Keyboard focus (Tab×3) | Lands on a real focusable link with a visible focus ring (`box-shadow` present) — accessible, not `outline: none` with nothing else |
| Sales Orders row click → detail | Navigates to the real record (`/sales/orders/SAL-ORD-2026-00102`) |
| Browser back button | Returns cleanly to the list view |
| Pagination / filter controls | Present and detected on the list page |
| Invalid record URL | Serves a real, non-crashing error page with intact navigation, not a blank screen or stack trace |
| Restricted-user permission-denied | A real second account (`Sales User` role only) correctly sees a filtered nav menu (no Purchases/Operations/Admin) and a proper "Permission Denied" page when directly navigating to `/admin` — server-owned, not a frontend-only guess |
| Two previously-uncertain mobile CSS issues | **Both confirmed genuinely fixed** — see `SMJ_RESPONSIVE_RESULTS.md` |

### Backend test suite (also run this session)

`bench --site staging.local run-tests --app my_store_ui`: **201 tests,
198 passed, 3 skipped, 0 failures, 0 errors** after fixing 3 real
defects found along the way (see `SMJ_MASTER_BATCH_LOG.md` for full
detail — a test-infrastructure `frappe.destroy()` cascade affecting 13
files, one account-type test-fixture bug, and 5 dead registry entries
pointing at DocTypes not installed in this ERPNext version).

### Truthful status legend used throughout this pass

`browser_verified` — actually rendered and interacted with in the real
Linux Chromium instance this session. `http_verified` — confirmed via
direct HTTP/API call, not rendered. `source_verified` — confirmed by
reading the actual source/registry, not executed. `implemented_unverified`
— code exists but this pass didn't exercise it. `blocked` — genuinely
could not be tested (state the reason). `failed` — tested and found
broken (state the defect and its fix status).

---

## 2026-07-16 (later session) — real browser screenshots achieved

Everything below this line describes the *first* 2026-07-16 session, where
Playwright could not be installed and only HTTP-level verification ran. A
follow-up session the same day found real Chrome/Edge binaries on the
Windows host, reachable from WSL at
`/mnt/c/Program Files/Google/Chrome/Application/chrome.exe` (and Edge at
`/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`), and
got headless screenshots working end-to-end, including authenticated
pages. See `SMJ_STRICT_VISUAL_PARITY.md` and `SMJ_RESPONSIVE_RESULTS.md`
for what was actually verified with real renders this way. Authentication
was handled by logging in through the real `/api/method/login` endpoint
and writing the resulting session cookie into an ephemeral Chrome profile
under `C:\Windows\Temp\claude-shots-<random>\` — approved by the user
after an earlier attempt to keep the profile on the WSL side failed
(Chrome's sandbox can't write its cookie/cache databases over the
`\\wsl.localhost\` network path; profiles need a genuine local disk path).
The profile is deleted at the end of that session.

**Note (2026-07-18):** the Windows-Chrome-via-WSL method used in this
session is no longer permitted for this project — the 2026-07-18 session
above found Linux-native Playwright Chromium installs and works cleanly,
which is now the standard method.

This means Playwright/`npm install` is *still* blocked (unchanged — see
the network diagnosis below), but that stopped being the only path to a
real browser in this environment.

## First 2026-07-16 session (HTTP-only) — method

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

**Note (2026-07-18):** this blocker no longer applies — `npx playwright
install chromium` succeeded cleanly in the 2026-07-18 session, downloading
a real Chromium binary with no network issues. Whatever blocked npm's
registry access in this earlier session is no longer present, or was
specific to the `@playwright/test` package path rather than Playwright's
browser-download CDN.

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

## What was NOT verified (honest gaps) — RESOLVED 2026-07-18

- ~~Real console output~~ — now verified, see above (0 console errors across 108 checks).
- ~~Actual rendered layout/overflow at any viewport~~ — now verified, see above (0 overflow across 108 checks).
- ~~Click-through flows~~ — now verified, see "Deep interaction verification" above.
- ~~Permission-denied behavior for a restricted user~~ — now verified with a real second account, see above.
- The ~180 total generated reports — still only sampled (Sales Register + this session's Phase 8 report reconciliation, which covered 14 more reports through the real Report API — see `docs/verification/SMJ_ACCOUNTING_VERIFICATION.md`). Full exhaustive coverage of all ~180 remains future work.
- Calendar and Kanban — still genuinely not implemented anywhere in this codebase (unchanged).

See `SMJ_BROWSER_ISSUES_FIXED.md` for the defects the code-review half of this
pass found and fixed.
