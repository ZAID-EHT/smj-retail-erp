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
| Phases completed | 0, 1 (backend/frontend), 2, 3, 4 |
| Phases not started | 5–19 |
| Commits created this mission | 3 (`177b420`, `f847545`, `ac1a18e`) |
| Backend tests | **860 ran, OK, 6 skipped, 0 failures, 0 errors** (358.4s), final run after every change |
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

### Not started

Phases 5–19: commission decision package, unified accounting preparation service,
external-action tracker, production configuration checker, fresh-install hardening, SMTP
rehearsal, automated UAT, human UAT workspace, deployment audit, backup/restore audit,
performance audit, security audit, acceptance matrix, six-viewport browser matrix,
release package, release tag.

No release tag was created. The tag conditions in the brief require the browser matrix,
security audit and performance audit to have passed; none of them were run.

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
