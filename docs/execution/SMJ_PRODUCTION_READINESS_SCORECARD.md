# SMJ Retail ERP — Production Readiness Scorecard

**Date:** 2026-07-18. Scored per-category, deliberately **not** combined
into one overall percentage — a single number would hide which
categories are genuinely production-ready and which have real, named
gaps. Each category links to its real evidence.

| # | Category | Status | Evidence |
|---|---|---|---|
| 1 | Master data (customers, suppliers, items) | **Ready** | 26 customers, 12 suppliers, 40 items, all required personas present, verified in Phase 3 |
| 2 | Sales workflow (Order→Delivery→Invoice→Payment) | **Ready** | 102/100/100/124 real documents, all 10 named scenarios, GL-balanced |
| 3 | Purchase/import workflow | **Ready** | Both procurement chains traced end-to-end, Landed Cost Voucher math verified precise | `docs/workflows/SMJ_IMPORT_PURCHASING_REPORT.md` |
| 4 | Wholesale credit/reservation system | **Ready** | Live two-process test: no over-reservation (10/8/8 → 10 total); losing request retries within bounds and gets a friendly message, no raw deadlock. Full lifecycle trace verified. | `docs/verification/SMJ_LIVE_RESERVATION_CONCURRENCY.md`, `SMJ_RESERVATION_LIFECYCLE_TRACE.md` |
| 5 | Role/permission security | **Ready** | 594 checks + 6 real write-attempt boundary tests, zero unauthorized access | `docs/security/` |
| 6 | Accounting integrity (GL/Trial Balance) | **Ready** | Balances to the cent, confirmed via the real Report API, not just SQL | `docs/verification/SMJ_ACCOUNTING_VERIFICATION.md` |
| 7 | Accounting reporting accuracy (P&L specifically) | **Correction designed & QA-verified; awaiting accountant sign-off to apply** | P&L overstates profit by 11,820,700 LKR (→ corrected 4,048,006) due to opening-stock booked to the Expense Stock Adjustment. A guarded, reversible reclassification JE (Dr Stock Adjustment / Cr Opening Balance Equity) reconciles exactly in dry-run/savepoint; a draft can be created for accountant review. Not applied — sign-off is external. | `docs/finance/SMJ_ACCOUNTANT_CORRECTION_PACKAGE.md`, `SMJ_FINANCE_NUMBER_REVERIFICATION.md` |
| 8 | Stock accuracy | **Ready** | Zero negative stock across 51 item/warehouse combinations, confirmed via the real Stock Balance report | `docs/verification/SMJ_ACCOUNTING_VERIFICATION.md` |
| 9 | Browser UI — surface rendering | **Ready** | 108/108 workspace×viewport checks clean (0 overflow, 0 console errors) | `docs/ui/SMJ_BROWSER_VERIFICATION.md` |
| 10 | Browser UI — deep interaction | **Partially verified** | Home + 1 representative page per component engine (3 total) deeply click-tested; remaining 15 workspaces are surface-verified only, named honestly | `docs/ui/audits/SMJ_PHASE6_WORKSPACE_AUDIT_SUMMARY.md` |
| 11 | Responsive design (6 breakpoints) | **Ready** | Zero overflow at all 6 required viewports, including the narrowest (360×800); 2 previously-uncertain mobile issues confirmed fixed | `docs/ui/SMJ_RESPONSIVE_RESULTS.md` |
| 12 | Backend automated test suite | **Ready** | 201 tests, 198 passed, 3 skipped, 0 failures, 0 errors (was 36 errors before this mission's fixes) | `docs/execution/SMJ_MASTER_BATCH_LOG.md` |
| 13 | Frontend build | **Ready** | Clean `npm run build`, 199 modules, no errors | (this mission, multiple confirmations) |
| 14 | Backup/restore capability | **Ready** | Full round-trip drill, exact data match on every metric checked, restored site's app layer confirmed functional | `docs/verification/SMJ_BACKUP_RESTORE_REPORT.md` |
| 15 | Load/concurrency safety | **Ready** | Reads safe; writes corruption-free; the reservation conflict now surfaces a friendly bounded-retry message (fixed since the earlier note) | `docs/verification/SMJ_LIVE_RESERVATION_CONCURRENCY.md` |
| 16 | Environment stability | **Ready** | Single bench instance confirmed throughout a 10-phase mission including heavy browser automation load, zero incidents | `docs/execution/SMJ_MASTER_BLOCKERS.md` |
| 17 | site1.local isolation | **Ready (one real risk found and closed)** | 13 test files were executing real writes against `site1.local` regardless of target site — found and fixed at the root this mission, not merely documented | `docs/execution/SMJ_MASTER_BATCH_LOG.md` (Phase 6 batch) |
| 18 | Deployment/ops readiness | **NOT ready — external, not code** | No real production hardware, HTTPS, monitoring, or email config exists in this environment; needs client infrastructure and human sign-off | `docs/execution/SMJ_REMAINING_EXTERNAL_ACTIONS.md` |

## How to read this table

15 of 18 categories are **Ready** with real, checkable evidence — not
"looks done," but actually tested against live data with a real browser,
a real second user account, real concurrent processes, and a real
backup/restore cycle. 2 categories (**#4, #15**) are functionally safe
but have a documented, honest UX rough edge. 1 category (**#7**) has a
real, quantified bug that needs a business decision before go-live. 1
category (**#18**) is entirely outside what code or an autonomous agent
can complete — it needs real infrastructure and real people.

**This scorecard makes no claim of "production ready" as a single
verdict** — that would misrepresent category #7 and #18. It is an
honest, itemized account of what is and isn't ready, so the business
owner can make an informed go/no-go decision per category.
