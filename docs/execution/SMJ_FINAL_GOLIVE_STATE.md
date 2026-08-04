# SMJ Final Go-Live — Mission State

Live state record for the final go-live execution mission. Machine-readable twin:
`SMJ_FINAL_GOLIVE_STATE.json`.

## Starting point (verified, not assumed)

| Fact | Verified value | How verified |
|---|---|---|
| Bench | `/home/zaidh/frappe-bench` | `ls` |
| App | `apps/my_store_ui` | `ls` |
| Branch | `full-feature-parity` | `git branch --show-current` |
| Starting commit | `2eb5980ca6f3081fdc2e4cefc7cdc8bda73be0e2` | `git rev-parse HEAD` |
| Starting release tag | `v1.0.0-rc10` | `git tag --list`; `git rev-list -n 1 v1.0.0-rc10` = same commit |
| Worktree at start | Clean — zero entries | `git status --short` returned no lines |
| Whitespace errors | None | `git diff --check`, `git diff --cached --check` both silent |
| Recovery tag | `pre-smj-final-golive-20260804-1657` | created this mission; no pre-existing tag of that name |
| Test site | `staging.local` | `sites/staging.local` present |
| Protected site | `site1.local` | `sites/site1.local` present — read-only for this mission |

Every reported baseline value in the mission brief that concerns the repository was
checked directly and matched. Test, browser and feature claims are verified in Phase 1
and are **not** carried forward as assumptions.

## Platform versions

```
erpnext                      15.108.3
erpnext_chatgpt              0.0.1
erpnext_gemini_integration   0.1.0
frappe                       15.108.0
my_store_ui                  0.0.1
posawesome                   15.30.0
smj_theme                    0.0.1
```

Services observed running: `mariadbd` (1), `redis-server` (3).

## Staging backup taken before any change

| Artefact | Path (relative to `sites/`) | Size | SHA256 |
|---|---|---|---|
| Database | `staging.local/private/backups/20260804_165748-staging_local-database.sql.gz` | 2.9 MiB | `2dada3992f1da2a52bb0074c0ecef92c31d2fbb1549db6c04f98de32a59d03d2` |
| Public files | `…-files.tar` | 10 KiB | `b1f4bcb063430576d4be77c11236b6bd84d8e0b66cc4321f8be8466b15559e0d` |
| Private files | `…-private-files.tar` | 50 KiB | `586d765008d7973550856ee1f0b592242759e880fe1008ad4cbab7dd72b337c2` |
| Site config | `…-site_config_backup.json` | 116 B | — |

Backup timestamp: `2026-08-04 16:57:51`. Backups are **not** committed (they live under
`sites/`, outside the app repository).

## site1.local fingerprint — taken at mission start

Captured with SELECT-only queries through `bench --site site1.local console`. No write,
no patch, no migrate was run against this site.

| Metric | Value at start |
|---|---|
| Companies | `SMJ`, `SMJ (Demo)` |
| Installed apps | erpnext, erpnext_chatgpt, erpnext_gemini_integration, frappe, my_store_ui, posawesome, smj_theme |
| Administrator `modified` | `2026-05-28 12:13:39.040427` |
| Latest GL posting date | `2026-12-10` |
| GL Entry count | 44 |
| Latest Stock Ledger posting date | `2026-12-10` |
| Stock Ledger Entry count | 17 |
| Journal Entry count | 0 |
| Submitted Journal Entries | 0 |
| Opening-stock correction JEs | 0 |
| Payment Entry count | 5 |
| Sales Invoice count | 7 |
| Users | 3 |
| Test-pattern users | 0 |
| SMJ Commission Policy / Period / Payout tables | absent (site never migrated to the commission schema) |

This fingerprint is re-taken at the end of the mission and the two are compared field by
field. Any difference is a safety failure, not a finding.

## Progress

| Field | Value |
|---|---|
| Phases completed | 0–9 |
| Phases not started | 10–17, 19 (18 partial) |
| Commits created this mission | 10 total (4 in session 1, 6 in session 2) |
| Backend tests | **941 ran, OK, 6 skipped, 0 failures, 0 errors** (383.7s), final run after every change |
| Frontend build | Clean (`vite build`, 256 modules, 4.89s) |
| site1.local | Re-fingerprinted at end — identical to start, field for field |
| Last completed action | Final regression green; documents finalised |
| Last update | 2026-08-04 18:05 |

### Completed

| Phase | What was actually delivered |
|---|---|
| 0 | Repo verified against the brief, recovery tag `pre-smj-final-golive-20260804-1657`, staging backup with SHA256, site1 read-only fingerprint, state/log/blocker documents |
| 1 | Full backend suite reproduced (857 tests OK, 6 skipped); frontend build clean. **Method correction:** `bench run-tests` exits 0 even when tests fail, so exit status alone is not evidence — the unittest summary is now always captured |
| 2 | Accountant Decision Centre: DocType, capability matrix, 14-question catalogue, API, SPA page and service, 45 tests |
| 3 | Segregation of duties enforced in the controller; two app roles created; permission matrix documented |
| 4 | Opening-stock final accountant package with **re-measured** figures, plus four tests that keep it honest |
| 5 | Commission decision package: options, accounting impact and risk per decision; current value separated from decision; final package document; 7 tests |
| 6 | Guarded accounting preparation service — five modes, no submit mode; 30 tests |
| 7 | External action tracker — 16 seeded actions, evidence-gated verification; 27 tests |
| 8 | Production configuration checker — 32 fixed-purpose checks, no command endpoint; 17 tests |
| 9 | Fresh-install rehearsal hardened with `--dry-run/--create/--verify/--resume`; dry run executed and passing |

### Not started

| Phase | Work |
|---|---|
| 10 | SMTP sandbox rehearsal |
| 11 | Automated business UAT (`scripts/run_uat_checks.py`) |
| 12 | Human UAT evidence workspace |
| 13 | Deployment package audit |
| 14 | Backup and restore audit |
| 15 | Performance and reliability audit |
| 16 | Security audit as a phase (permission denial is covered inside the module suites) |
| 17 | Final acceptance matrix |
| 19 | Six-viewport browser matrix |
| — | rc11 release package documents |

Phase 18 is **partial**: the full regression was run and
`docs/verification/SMJ_FINAL_TEST_MANIFEST.json` written, but the separate per-area
suites the brief lists were not individually run.

No release tag was created. The brief's tag conditions require a passing browser matrix,
security audit, performance audit, automated UAT, human UAT workspace, deployment audit
and backup/restore audit. None of those ran, so `v1.0.0-rc11` would have been a claim
rather than a fact. The tag name remains unused.

### Defects found and fixed in this session's own work

| Defect | Consequence had it shipped |
|---|---|
| `prepare_draft()` commits mid-test, destroying the savepoint | A test run left a real draft Journal Entry, then eighteen **Approved** opening-stock decisions, on staging. Approved decisions are the worse residue: left in place they would satisfy the preparation guard for real work later. Both were removed and the suite now cleans committed residue after the rollback. |
| `cancel_draft` deleted any draft by name | Could have removed an unrelated draft. Now proves the correction marker first. |
| `Retail Finance Verifier` / `Accounts Manager` lacked DocType write | Verification failed with a permission error. |
| Two routes registered with no SPA page (session 1) | Dead routes; both removed, and a test now walks bespoke routes. |

## Material finding — a published figure had gone stale

Re-measuring the ledger for the accountant package found that the post-correction profit
of **4,048,006**, published in the July 2026 finance documents, is no longer true.

| | July 2026 docs | Measured 2026-08-04 |
|---|---|---|
| Profit before correction | 15,868,706 | **17,418,706** |
| Correction amount | 11,820,700 | 11,820,700 (unchanged) |
| Profit after correction | 4,048,006 | **5,598,006** |

The arithmetic was right; its inputs aged, because staging took on further trading
between the two dates. An accountant approving against 4,048,006 would have reconciled
after posting and found a 1,550,000 discrepancy with nothing to explain it.

`docs/finance/SMJ_OPENING_STOCK_FINAL_ACCOUNTANT_PACKAGE.md` is now the figure of record
and lists the documents still carrying the superseded number. Four tests fail if the
package and the ledger ever drift apart again.

## Honesty rules held for this mission

- A dry run is never reported as a posting.
- Static validation is never reported as live deployment.
- An unfinished feature is never reclassified as an external blocker.
- No phase is marked complete without command output backing it.
