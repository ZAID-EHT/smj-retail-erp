# SMJ RC4 — Mission State

Companion: `SMJ_RC4_MISSION_STATE.json`.

## Repository
- Branch: `full-feature-parity`
- Starting commit: `416068f` (verified HEAD)
- Starting tag: `v1.0.0-rc3` (→ `bdf0151`, 2 doc commits behind HEAD)
- Recovery tag: `pre-smj-rc4-mission-20260727-1933`
- Test site: `staging.local` (default). Protected: `site1.local`.
- Backup: `sites/staging.local/private/backups/20260727_193326-staging_local-*`

## site1.local fingerprint (must not change)
Companies SMJ + SMJ (Demo); admin modified 2026-05-28 12:13:39; 0 test users;
0 correction JEs; latest GL 2026-12-10. (Same as prior missions.)

## Scope (this mission — safe local work)
| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Preflight/backup/fingerprint | done |
| 1 | Reproduce baseline | in progress |
| 2 | Two-company end-to-end separation | pending |
| 3 | Administration landing + navigation | pending |
| 4 | Printing final + secure PDF download | pending |
| 5 | Scheduled reports management | pending |
| 6 | Go-live readiness dashboard | pending |
| 7 | Owner handoff package | pending |
| 8 | Final wholesale frontend gap audit | pending |
| 9 | Post-launch roadmap | pending |
| 10 | Acceptance additions | pending |
| 11 | Full regression | pending |
| 12 | Six-viewport browser matrix | pending |

## External (unchanged)
Accountant sign-off (finance JE), MariaDB root (QA/fresh sites), SMTP, Hetzner/DNS/
registry/git-push, client UAT.

## Safety invariants
Writes only to staging; site1 never written; no ledger writes; correction stays a
draft; no ignore_permissions in endpoints; browser via Playwright API; no credentials
committed.
