# SMJ Finance / Fresh-Install / Deployment — Mission State

Machine-readable companion: `SMJ_FINANCE_DEPLOYMENT_MISSION_STATE.json`.

## Repository
- Branch: `full-feature-parity`
- Starting commit: `13b3da1` (verified current HEAD; is `v1.0.0-rc2`)
- Recovery tag: `pre-smj-finance-deployment-20260727-0941`
- Prior recovery tag: `pre-smj-final-readiness-20260726-1848`
- Test site: `staging.local` (default). Protected: `site1.local`.
- Backup before this mission: `sites/staging.local/private/backups/20260727_094121-staging_local-*`

## site1.local integrity fingerprint (must not change)
- Companies: `SMJ`, `SMJ (Demo)`
- Installed apps: frappe, erpnext, smj_theme, erpnext_chatgpt, erpnext_gemini_integration, posawesome, my_store_ui
- Administrator modified: `2026-05-28 12:13:39`
- Test-pattern users: 0
- Opening-stock correction JEs: 0
- Latest GL posting date: `2026-12-10`

## Critical finance figure to re-verify
The previous report stated a corrected profit of **LKR 4,048,825,204**, which is
arithmetically impossible. `15,868,706 − 11,820,700 = 4,048,006`. Phase 2 must
re-derive all figures from authoritative ERPNext reports, not documentation. (The
finance docs written last mission already use **4,048,006**; the impossible figure
appears in the prior final-report *narrative*, to be checked and corrected.)

## Environment limitation (carried over)
MariaDB root password unavailable → cannot create `financeqa.local` /
`freshrelease.local`. Mitigated with savepoint simulation + a static-validated
fresh-install script and the exact commands for when credentials exist.

## Phase status
| Phase | Status |
|-------|--------|
| 0 Preflight/backup/fingerprint | done |
| 1 Reproduce baseline | in progress |
| 2 Reverify finance numbers | pending |
| 3 Confirm root cause | pending |
| 4 Correction package (guarded, draft-only) | pending |
| 5 Isolated QA-site test | pending (QA site likely blocked) |
| 6 Staging correction runbook | pending |
| 7 Correct release documentation | pending |
| 8 Genuine fresh-site verification | pending (likely blocked; script + static) |
| 9 SMTP production readiness | pending |
| 10 Hetzner deployment package | pending |
| 11 Release rehearsal validation | pending |
| 12 Final regression + browser | pending |

## Safety invariants
Writes only to staging + (if creatable) QA sites; site1 never written; no direct
ledger writes; correction is a standard **draft** JE requiring accountant sign-off to
submit on staging; no credentials committed; browser via Playwright API only.
