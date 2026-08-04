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
| Current phase | Phase 0 — preflight |
| Current batch | Preflight complete; Phase 1 baseline reproduction next |
| Completed requirements | Repo verification, recovery tag, staging backup, site1 fingerprint, state documents |
| Remaining requirements | Phases 1–19 |
| Commits created this mission | 0 at time of writing |
| Last completed action | site1.local fingerprint captured and recorded |
| Next automatic action | Phase 1 — reproduce the rc10 backend/frontend/browser baseline |
| Last update | 2026-08-04 16:58 |

## Honesty rules held for this mission

- A dry run is never reported as a posting.
- Static validation is never reported as live deployment.
- An unfinished feature is never reclassified as an external blocker.
- No phase is marked complete without command output backing it.
