# SMJ Final Production-Readiness — Mission State

**Resumable state.** Machine-readable companion: `SMJ_FINAL_READINESS_MISSION_STATE.json`.

## Repository
- Branch: `full-feature-parity`
- Mission start commit: `8202289` (verified current HEAD, not historical)
- Recovery tag: `pre-smj-final-readiness-20260726-1848`
- Test site: `staging.local` (default site; per-site DB password available)
- Protected: `site1.local` (never written)
- Backup before this mission: `sites/staging.local/private/backups/20260726_184814-staging_local-*`

## Environment limitation recorded at Phase 0

**MariaDB root password is not available** in any site config, and password
guessing is (correctly) blocked. `bench new-site` / `bench restore` both require it
to create and grant a database. Therefore the two **fresh/QA-site** requirements —
`financefix.local` (Phase 6) and `freshsetup.local` (Phase 7) — cannot be created in
this environment. Consequences and mitigation:

- Phase 6 P&L work: full **read-only audit on staging** + a **guarded, dry-run,
  reversible** correction script that is verified on staging inside a savepoint;
  irreversible application is gated on the audit outcome and documented.
- Phase 7 setup wizard: **built and unit-tested** against the real ERPNext Company
  controller; the empty-system code path is exercised by mocking "no Company exists"
  rather than by a physically empty site. The gap (a physically fresh site) is
  documented as an environment limitation, not a code gap.

This is an **environment** limitation, explicitly distinguished from ordinary
development work.

## Baseline reverified (Phase 1)

164 backend tests across 16 modules, **all green**:
`test_item_price_sync` 14, `test_access_management` 28, `test_core_acceptance` 3,
`test_standalone_frontend` 12, `test_smart_sales_core` 5, `test_wholesale_credit` 7,
`test_stock_action_parity` 7, `test_navigation_search` 11, `test_quick_create` 4,
`test_purchase_workflow` 7, `test_create_routes` 11, `test_universal_frontend` 24,
`test_form_api` 14, `test_frontend_layout` 9, `test_reservation_retry` 3,
`test_wholesale_integration` 5. Frontend build clean (204 modules).

## Phase status

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Preflight, backup, mission state | done |
| 1 | Reverify baseline | done — 164 green |
| 2 | Live two-process reservation concurrency | in progress |
| 3 | Continuous reservation lifecycle trace | pending |
| 4 | Wider role-denial matrix | pending |
| 5 | Seven remaining Product-form fields | pending |
| 6 | P&L opening-stock reconciliation | pending (QA site blocked; read-only + guarded correction) |
| 7 | First-time company setup wizard | pending (fresh site blocked; code + unit tests) |
| 8 | Printing & Branding frontend | pending |
| 9 | Email & Notifications frontend | pending |
| 10 | Data import/export frontend | pending |
| 11 | Finance frontend audit | pending |
| 12 | System health & backups | pending |
| 13 | Wholesale-launch frontend audit | pending |
| 14 | Complete acceptance suite | pending |
| 15 | Full regression | pending |
| 16 | Six-viewport browser matrix | pending |

## Safety invariants
- Writes only to `staging.local`; `site1.local` untouched.
- No `ignore_permissions=True` in endpoints; standard controllers only.
- No direct GL/SLE/Bin/outstanding writes; no raw ledger SQL.
- No sudo / killall / pkill / taskkill / Windows Chrome; browser closed via Playwright API.
- Test credentials generated per run, never written to a document or the repo.
- Config changes re-verified as unreferenced first; applying scripts refuse if not.
