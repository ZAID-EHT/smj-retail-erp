# SMJ Retail ERP — Final Production-Readiness Report

Mission: final production-readiness completion. Date: 2026-07-27.
Branch: `full-feature-parity`. Start commit: `8202289`. Candidate: `2b40c49`.
Recovery tag: `pre-smj-final-readiness-20260726-1848`. Backup:
`20260726_184814-staging_local-*`.

## Phase status (all 16)

| Phase | Status |
|-------|--------|
| 0 Preflight/backup/state | ✅ done |
| 1 Baseline reverify | ✅ 164 → (final 333) green |
| 2 Live two-process concurrency | ✅ verified (no over-reservation) |
| 3 Continuous reservation lifecycle | ✅ verified (invariants hold every step) |
| 4 Wider role-denial matrix | ✅ 7 tests, 9 roles × 10 endpoints |
| 5 Seven Product fields | ✅ implemented + 4 tests |
| 6 P&L opening-stock | ✅ root-caused + reconciled (dry-run); apply held for accountant |
| 7 First-time setup wizard | ✅ code + 6 tests; fresh-site run env-blocked |
| 8 Printing & Branding | ✅ landing + preview + 6 tests |
| 9 Email & Notifications | ✅ status/templates/coverage + 4 tests |
| 10 Data import/export | ✅ allowlisted + 7 tests |
| 11 Finance frontend | ✅ audited — already covered by generated + adapters |
| 12 System health/backups | ✅ read-only dashboard + 5 tests |
| 13 Launch frontend audit | ✅ matrix, no launch-critical gap |
| 14 Acceptance suite (24) | ✅ all have results; 11 original fully verified |
| 15 Full regression | ✅ 333 tests / 42 modules green |
| 16 Six-viewport browser | ✅ 90/90, 0 problems |

## Verification totals
- Backend: **333 tests, 42 modules, 0 failures**.
- Frontend build: **clean**.
- Browser: **90/90** across six viewports (15 pages).

## Environment / external requirements (not code gaps)
1. **MariaDB root password** — needed for isolated QA (`financefix.local`) and
   fresh-install (`freshsetup.local`) sites. Mitigated with savepoint reconciliation
   and controller-level testing.
2. **SMTP credentials** — email delivery. System usable via admin-set passwords.
3. **Accountant sign-off** — the opening-stock reclassification booking.
4. **Hetzner / DNS** — deployment.

## Ordinary remaining development (not launch-critical)
- Two-company end-to-end separation test on a fresh site.
- Live second-session session-revocation demonstration.
- Scheduled reports; storefront/integrations (not needed for wholesale launch).

## Safety confirmations
- `site1.local` never written.
- No direct GL/SLE/Bin/outstanding writes; opening-stock correction is a standard JE.
- No permission bypass; no `ignore_permissions` in endpoints.
- No credentials committed; test credentials generated per run, never persisted.
- No Windows Chrome; browser closed via Playwright API; no process killed by name.
- Backups exist; rollback tag + backup recorded.
- Staging clean: no residual test users/items/companies; three empty test warehouses
  disabled (cannot hard-delete due to cancelled-SLE history — purging SLEs is forbidden).

## Status ladder (precise — no overstatement)

| Item | State |
|------|-------|
| Code implemented | ✅ |
| Backend verified (333+ tests) | ✅ |
| Browser verified (90/90, 6 viewports) | ✅ |
| Financial correction **designed** | ✅ |
| Financial correction **QA-tested (dry-run / savepoint)** | ✅ reconciles to 4,048,006 |
| Financial correction **applied** | ❌ not applied — held for accountant sign-off |
| **Accountant approved** | ❌ external |
| Fresh-site **code** verified (savepoint/controller) | ✅ |
| Fresh-site **on a physically empty site** | ❌ external (MariaDB root) |
| SMTP configured | ❌ external |
| Hetzner rehearsal deployed | ❌ external (package prepared) |
| Client UAT completed | ❌ external |
| Production live | ❌ external |

## Verdict
**Code-complete release candidate awaiting accountant-approved financial
reclassification, genuine fresh-install verification (needs MariaDB root), SMTP
configuration, deployment rehearsal and client UAT.** No launch-critical *development*
item remains open; the outstanding items are external (credentials, accountant, DNS).
The opening-stock correction is designed and QA-verified (dry-run reconciles to
4,048,006) but **not applied** — it is a draft awaiting sign-off.
