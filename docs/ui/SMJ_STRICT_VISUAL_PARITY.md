# SMJ Retail ERP — Strict Visual Parity (2026-07-16)

## Method

Real browser screenshots, not HTTP checks. Chrome (found on the Windows
host at `/mnt/c/Program Files/Google/Chrome/Application/chrome.exe`,
reachable from WSL) was driven headless via `--screenshot`. An
authenticated session was created by logging in through the real
`/api/method/login` endpoint and writing the resulting session cookie into
an ephemeral Chrome profile under `C:\Windows\Temp\claude-shots-<random>\`
(the user approved this specific approach and location after an earlier
attempt to keep the profile WSL-side failed — Chrome's sandbox cannot write
its cookie/cache databases over the `\\wsl.localhost\` network path). The
profile is deleted at the end of this session — see
`SMJ_BROWSER_VERIFICATION.md` for the full trail.

## Reference vs implementation — Home dashboard

Reference: `01_home_dashboard.png`. Before this pass, `/retail-erp/home`
rendered the generic, metadata-driven `ModuleDashboardPage.vue` — a
"permitted record counts + quick action buttons + important pages" layout
with no charts, no KPI trend indicators, and no resemblance to the
reference's KPI/chart dashboard. This was confirmed with a real screenshot,
not assumed.

Rebuilt as a dedicated `HomeDashboardPage.vue` (wired into `/home` in
`routes.js`, `ModuleDashboardPage` still serves every other module
dashboard — see `SMJ_PAGE_IMPLEMENTATION_MATRIX.md`). Structural match
against the reference, confirmed via a real 1440×1300 screenshot:

| Reference element | Status |
|---|---|
| Greeting + quick-action buttons row | ✅ built (Sales Invoice / Purchase Order / Payment) |
| 6 KPI cards (Total Sales, Receivables, Gross Profit, Reserved Stock, Available-to-Sell, Pending Deliveries) with trend % and sparkline | ✅ built, live data |
| Sales Trend line chart (this year vs last year) | ✅ built, live data, hover tooltip |
| Payment Collection donut | ✅ built, live data |
| Top Selling Categories bar chart | ✅ built, live data |
| Recent Transactions table | ✅ built, live data |
| Stock Overview mini-stats | ✅ built, live data |
| Low Stock Alerts | ✅ built, live data (empty state confirmed genuine — nothing is actually low right now) |
| Top Customers / Top Products ranked lists | ✅ built, live data |
| Sales by Region (Sri Lanka map) | ❌ not attempted — replicating custom cartography wasn't a reasonable use of remaining time; the KPI row was widened to use the space instead |
| "Mobile Ready" promo card + phone mockup illustration | ❌ not built — this is marketing chrome in the reference, not a real dashboard widget |

Module header pill colours were also found to be **wrong relative to the
reference** during this pass (Purchases showed orange instead of purple,
Inventory showed green instead of orange, Finance showed purple instead of
gold, Sales showed blue instead of green) — a real, confirmed, screenshot-driven
defect, not a guess. Fixed in both `routes.js` and the server-side
`frontend_routes.py` navigation payload; see `SMJ_BROWSER_ISSUES_FIXED.md`.

## Other reference pages

Smart Sales has since received a dedicated reference-style workspace:
customer and credit context, actual/reserved/available stock KPIs, catalogue
cards, and a responsive sticky cart, all backed by the pre-existing live
ERPNext APIs. The Wholesale Transaction Register also gained a live KPI strip.

Sales Orders, Products, Customer Credit, Purchases, Finance and Reports still
use their functional shared layouts and do **not** yet have every specialised
KPI/sidebar/chart composition shown in their individual previews. They now
share the final `smj-page-system.css` composition (module headings, cards,
tables, forms and responsive rules), but exact preview-specific analytics and
right rails remain real page-specific follow-up work.

## Screenshots

Not committed to the repository (large binaries, contains live demo
business data). Captured under
`/tmp/claude-.../scratchpad/shots/` for this session only:
`home-rebuilt.png` (1440×1400, after), `home-desktop-final.png`
(1440×1300, after all fixes), `home-mobile-final3.png` (390×2200, after
mobile fixes — see the honest caveat in `SMJ_RESPONSIVE_RESULTS.md`).
