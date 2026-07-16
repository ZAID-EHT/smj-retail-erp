# SMJ Retail ERP — Page Implementation Matrix

No routes were remapped or added for this UI pass. This matrix records how
each page family receives the new theme, not a parity/feature audit — see
`docs/full-parity/PROGRESS.md` for that (unchanged: `required_but_missing =
222`, `unclassified = 0`).

| Page family | Files | Theme source | Status |
|---|---|---|---|
| Universal list (metadata-driven) | `pages/generated/UniversalListPage.vue` | `generated-ux.css` | Tokens applied, empty-state icon added, banner gradients fixed to use SMJ module colours |
| Universal detail/form/report | `pages/generated/Universal{Detail,Form,Report}Page.vue` | `generated-ux.css` | Tokens applied (shared stylesheet) |
| Universal special (kanban/calendar placeholder) | `pages/generated/UniversalSpecialPage.vue` | `universal.css` | Honest placeholder, unchanged — no kanban/calendar implementation exists yet, so nothing to theme beyond the shared tokens it already inherits |
| Entity list/detail/form (second universal implementation) | `pages/entities/Entity{List,Detail,Form}Page.vue` | `base.css` | Tokens applied, empty-state icon added |
| Tree | `pages/priority/PriorityTreePage.vue`, `components/priority/PriorityTreeNode.vue` | `priority-pages.css` | Tokens applied via shared stylesheet |
| Report hub / report viewer | `pages/priority/PriorityReportHubPage.vue`, `PriorityReportPage.vue` | `priority-pages.css` | Tokens applied |
| Home / module dashboard | `pages/priority/ModuleDashboardPage.vue` | `priority-pages.css` | Tokens applied, glyph icons replaced with SMJ icons |
| Smart Sales | `pages/priority/SmartSalesPage.vue` | `priority-pages.css` | Tokens applied, product placeholder + cart remove glyphs replaced with SMJ icons |
| Wholesale Transaction Register | `pages/priority/WholesaleTransactionsPage.vue` | `priority-pages.css` | Tokens applied via shared stylesheet |
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

## Explicitly not attempted

Pixel-for-pixel layout matching against the 9 reference preview images
(`01_home_dashboard.png` … `09_reports_analytics.png`) was not done. That
requires visual iteration against a running, authenticated app, which needs
either a human eyeballing the pages or browser automation — Playwright is
not installed in this environment and installing it was out of scope
("do not install system packages without approval"). What was verified is
structural: the same token values, spacing scale and icon set the previews
were generated from are now the values driving the real app.
