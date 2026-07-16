# SMJ Retail ERP — Page Implementation Matrix

No routes were remapped or added for this UI pass. This matrix records how
each page family receives the new theme, not a parity/feature audit — see
`docs/full-parity/PROGRESS.md` for that (unchanged: `required_but_missing =
222`, `unclassified = 0`).

| Page family | Files | Theme source | Status |
|---|---|---|---|
| Universal list (metadata-driven) | `pages/generated/UniversalListPage.vue` | `generated-ux.css`, `smj-page-system.css` | Shared SMJ work surface, module-accent heading, filters, sticky table header, internal table overflow and mobile layout |
| Universal detail/form/report | `pages/generated/Universal{Detail,Form,Report}Page.vue` | `generated-ux.css`, `smj-page-system.css` | Shared module heading, section cards, focus states, responsive form/detail composition and sticky actions |
| Universal special (kanban/calendar placeholder) | `pages/generated/UniversalSpecialPage.vue` | `universal.css` | Honest placeholder, unchanged — no kanban/calendar implementation exists yet, so nothing to theme beyond the shared tokens it already inherits |
| Entity list/detail/form (handcrafted workflow implementation) | `pages/entities/Entity{List,Detail,Form}Page.vue` | `base.css`, `smj-page-system.css` | Shared SMJ module heading, work cards, tables, forms and mobile rules; document APIs/actions unchanged |
| Tree | `pages/priority/PriorityTreePage.vue`, `components/priority/PriorityTreeNode.vue` | `priority-pages.css` | Tokens applied via shared stylesheet |
| Report hub / report viewer | `pages/priority/PriorityReportHubPage.vue`, `PriorityReportPage.vue` | `priority-pages.css` | Tokens applied |
| Home / module dashboard | `pages/priority/ModuleDashboardPage.vue` | `priority-pages.css` | Tokens applied, glyph icons replaced with SMJ icons |
| Smart Sales | `pages/priority/SmartSalesPage.vue` | `priority-pages.css`, `smj-page-system.css` | Rebuilt as reference-style customer/credit + actual/reserved/available stock + catalogue + sticky cart workspace using the existing live APIs |
| Wholesale Transaction Register | `pages/priority/WholesaleTransactionsPage.vue` | `priority-pages.css`, `smj-page-system.css` | Shared register layout plus live record/delivery/payment/page-value KPI strip; existing permission-filtered register retained |
| Bank Reconciliation | `pages/priority/BankReconciliationPage.vue` | `priority-pages.css` | Tokens applied via shared stylesheet |
| Payment Reconciliation | `pages/priority/PaymentReconciliationPage.vue` | `priority-pages.css` | Tokens applied via shared stylesheet |
| Special adapters | `pages/priority/PrioritySpecialPage.vue`, `pages/priority/PriorityRoutePage.vue` | `priority-pages.css` / `generated-ux.css` | Tokens applied via shared stylesheet |
| Login | `pages/LoginPage.vue` | `standalone.css` | Tokens applied, danger/warning colours corrected to SMJ semantic tokens |

"Tokens applied via shared stylesheet" means: no hardcoded hex colours were
present in that page's own template (verified — a full-repo grep for hex
literals and inline colour styles across `src/pages` returned zero matches
both before and after this pass, confirming every page already delegated
colour to the shared CSS files that were rewritten). What changed for those
pages is entirely inside `frontend/src/design/*.css`.

## 2026-07-16 — HTTP-level backend verification (not rendering)

A follow-up pass exercised the real backend APIs behind several of these
pages with an authenticated session (see `SMJ_BROWSER_VERIFICATION.md` for
the full harness). This is not the same as browser verification (no
rendering was observed), but it does confirm the data layer works, not just
that the frontend compiles:

- Home dashboard: real, non-hardcoded counts returned
- All 9 module dashboards: consistent 200 + correct shape
- Global search: real record found for a real query, correct route shape
- Universal engine (generated doctype `asset`): list configuration, column
  metadata and document list all correct, including a genuine empty state
  (0 records exist in the demo data — not an error)
- Tree (Chart of Accounts): real account hierarchy returned
- Report viewer (Sales Register): executed end-to-end with real filters,
  returned 2 real rows plus columns/chart/summary
- Universal engine missing-record handling: clean 404 with a safe message

## 2026-07-16 shared page-system pass

`frontend/src/design/smj-page-system.css` is loaded last and now composes all
current page families around the same reference vocabulary: calm white page
headings with module accents, compact KPI cards, rounded work surfaces,
44px controls, 48px table rows, internal table overflow, responsive forms and
mobile cards. `PageContainer.vue` publishes the current module/accent to this
layer, so this applies to handcrafted and generated routes without changing
their APIs or permissions.

This is a shared-system and Smart Sales structural pass, not a claim that all
nine previews are pixel-for-pixel replicas. Home and Smart Sales have the
deepest dedicated reference composition. The specialised Sales Orders,
Products/Credit, Purchases, Finance and Reports dashboards still require
page-specific chart/right-rail work if exact preview parity is required.
