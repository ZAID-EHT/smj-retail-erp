# SMJ Final Go-Live — Execution Log

Append-only record of what was actually run and what it returned. Entries are written
after the command completes, never before.

---

## Phase 0 — Preflight, tag audit, backup and recovery

**2026-08-04 16:56 — Repository verification**

```
git branch --show-current   -> full-feature-parity
git rev-parse HEAD          -> 2eb5980ca6f3081fdc2e4cefc7cdc8bda73be0e2
git status --short          -> (no output; 0 lines)
git diff --stat             -> (no output)
git diff --check            -> (no output)
git diff --cached --check   -> (no output)
git rev-list -n 1 v1.0.0-rc10 -> 2eb5980ca6f3081fdc2e4cefc7cdc8bda73be0e2
```

Result: the brief's reported branch, commit, tag and clean worktree are all correct.
The rc10 tag points at the current HEAD exactly. Nothing was reset, cleaned or stashed.

Existing tags observed (29 total), most recent first: `v1.0.0-rc10`,
`pre-smj-commission-payout-20260804-0018`, `v1.0.0-rc9`,
`pre-smj-sales-team-integration-20260803-1813`, `v1.0.0-rc8`, … back to
`stage-0-baseline`. No `v1.0.0-rc11` exists, so that number is free for this mission's
release tag if the tag conditions are met.

**2026-08-04 16:57 — Recovery tag**

```
git tag -a pre-smj-final-golive-20260804-1657 -m "Recovery point before SMJ final go-live mission"
-> CREATED pre-smj-final-golive-20260804-1657
```

The name was checked with `git rev-parse` first; it did not exist, so nothing was
overwritten.

**2026-08-04 16:57 — Platform versions**

```
frappe 15.108.0 · erpnext 15.108.3 · my_store_ui 0.0.1
posawesome 15.30.0 · smj_theme 0.0.1
erpnext_chatgpt 0.0.1 · erpnext_gemini_integration 0.1.0
```

Services observed: `mariadbd` ×1, `redis-server` ×3, plus a running `honcho start`
bench stack (web on :8000, socketio, watch, schedule, worker). The bench stack was left
running — no process was terminated by name or otherwise.

**2026-08-04 16:57 — Staging backup**

```
bench --site staging.local backup --with-files
-> Backup Summary for staging.local at 2026-08-04 16:57:51
   Database: 20260804_165748-staging_local-database.sql.gz        2.9MiB
   Public  : 20260804_165748-staging_local-files.tar              10.0KiB
   Private : 20260804_165748-staging_local-private-files.tar      50.0KiB
   Config  : 20260804_165748-staging_local-site_config_backup.json  116.0B
```

SHA256 recorded in `SMJ_FINAL_GOLIVE_STATE.md`. Backups live under `sites/` and are not
part of the app repository, so there is no risk of committing them.

**2026-08-04 16:58 — site1.local fingerprint (read-only)**

Captured through `bench --site site1.local console` using SELECT statements only. No
write, migrate or patch was issued against the protected site.

Key values: 2 companies (`SMJ`, `SMJ (Demo)`), 44 GL Entries, 17 Stock Ledger Entries,
0 Journal Entries, 0 submitted Journal Entries, 0 opening-stock correction JEs, 5 Payment
Entries, 7 Sales Invoices, 3 users, 0 test-pattern users, Administrator `modified` =
`2026-05-28 12:13:39.040427`, latest GL and SLE posting date `2026-12-10`.

Notable: the `SMJ Commission Policy`, `SMJ Commission Period` and `SMJ Commission Payout`
tables are **absent** on site1.local — that site has never been migrated onto the
commission schema. This is recorded as a fact, not a defect; it also means the protected
site cannot be accidentally touched by commission code paths.

**Phase 0 status: complete.** State, JSON twin, blockers and this log were created.

---

## Phase 1 — Reproduce the rc10 baseline

**2026-08-04 16:59 — Full backend suite started**

```
bench --site staging.local run-tests --app my_store_ui
```

Started in the background. The bench worker and scheduler are running concurrently; per
previously established behaviour on this bench, a MariaDB 1213 deadlock inside a long
suite is lock contention with the worker rather than a product defect, and the affected
module is re-run individually to confirm. Result recorded below when the run finishes.

_(run in progress at time of writing)_
