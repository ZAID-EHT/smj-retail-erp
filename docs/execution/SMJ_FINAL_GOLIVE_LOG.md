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

**2026-08-04 17:08 — First run finished, and a method problem was found**

The run exited 0. The unittest summary was lost: the command was piped through
`tail -80`, and because the suite's `print()` output on stdout flushes at exit while the
unittest summary goes to stderr earlier, the last 80 lines contained JSON from a test
rather than the result line.

That turned out to matter more than a lost summary. When the same pattern was used on a
small module shortly afterwards, the summary read `FAILED (failures=2, errors=1)` while
the command still exited **0**.

**`bench run-tests` returns exit code 0 even when tests fail.** Exit status is not
evidence on this bench. Every test result in this mission is therefore taken from the
captured `Ran N tests` / `OK` / `FAILED` lines, never from `$?`. All later runs redirect
the full stream to a file instead of piping through `tail`.

**2026-08-04 17:52 — Full backend suite, captured properly**

```
bench --site staging.local run-tests --app my_store_ui   (full stream to file)
-> Ran 857 tests in 510.853s
-> OK (skipped=6)
-> grep -c "^(FAIL|ERROR): " = 0
```

857 = the 810 baseline plus the 47 tests added by this mission. Zero failures, zero
errors, six skips — the skip count matches the reported baseline exactly.

**2026-08-04 17:20 — Frontend build**

```
npm run build   (scripts discovered first: dev, build, check -- no lint or test script exists)
-> vite v6.4.3, 256 modules transformed, built in 4.89s
```

No lint, type-check, unit-test or Playwright script exists in `frontend/package.json`, so
none was invented. The browser matrix in Phase 19 was not run.

---

## Phase 2 — Accountant Decision Centre

**2026-08-04 17:10–17:35**

Built `Retail Accountant Decision` (DocType + controller), the capability matrix and
14-question catalogue in `my_store_ui/finance/accountant_decisions.py`, the SPA page and
service, and 45 tests.

First test run: `Ran 42 tests`, `FAILED (failures=2, errors=1)`. Three genuine defects in
the new code, all fixed:

1. `mark_verified` raised a permission error — `Retail Finance Verifier` had read-only
   DocType permission but the workflow needs to save. Granted `write`.
2. and 3. `{"superseded_by": ["in", ["", None]]}` never matches a NULL in MariaDB, because
   `IN ('', NULL)` is not a null test. This silently broke both the live-decision lookup
   and the duplicate-proposal check. Replaced with `["is", "not set"]` in all three
   places.

After the fixes: `Ran 42 tests`, `OK`. After adding route tests: `Ran 45 tests`, `OK`.

Migration ran clean; the DocType and both roles were verified present on staging with 4
permission rows.

**Dead-route correction.** Routes had been registered for the external-action tracker and
the UAT workspace before either feature existed. A route registered server-side with no
SPA component resolves fine and lands the user on a blank screen. Both registrations were
removed, and a test now walks the bespoke routes and fails if any lacks a page.

---

## Phase 4 — Opening-stock final accountant package

**2026-08-04 17:40 — Re-measurement, and a stale figure**

```
opening_stock_correction.inspect()  -> profit 17,418,706.00; opening amount 11,820,700.00
opening_stock_correction.dry_run()  -> after profit 5,598,006.00; persisted: false
                                       balanced before and after; would_be_je ACC-JV-2026-00004
```

The July 2026 documents publish **4,048,006** as the post-correction profit. That figure
came from a profit-before of 15,868,706. Profit before now measures **17,418,706**, so the
correct post-correction figure is **5,598,006** — a difference of 1,550,000 caused by
trading posted to staging between 2026-07-27 and 2026-08-04.

The correction amount itself has not moved. The old arithmetic was sound; its inputs aged.

Stock evidence captured for the package: 573 active Stock Ledger Entries, stock value
20,382,196.00, total bin quantity 4,729.000 — none of which a reclassification Journal
Entry can change.

Package written to `docs/finance/SMJ_OPENING_STOCK_FINAL_ACCOUNTANT_PACKAGE.md` with the
re-measured figures, the list of documents still carrying the superseded number, and the
sign-off block. Four tests added: profit must fall by exactly the correction amount, the
stock ledger must not move, the package must quote the currently measured post-correction
profit, and the superseded figure may be named as stale but never offered as the answer.

`Ran 10 tests`, `OK` on `test_opening_stock_correction`.

---

## Phase 3 — Segregation and audit

Enforced in `RetailAccountantDecision.validate` rather than in the UI. Documented in
`docs/security/SMJ_ACCOUNTANT_DECISION_PERMISSION_MATRIX.md`.

Two holes in the capability matrix are deliberate and tested: System Manager cannot
record an accountant decision, and no role at all can submit an accounting correction
(`CAP_SUBMIT_CORRECTION` is an empty tuple, which `has_capability` can never satisfy).

---

## Safety check at end of session

**site1.local re-fingerprinted** with the same read-only script used at the start. Every
field is identical: 2 companies, 44 GL Entries, 17 Stock Ledger Entries, 0 Journal
Entries, 0 opening-stock correction JEs, 5 Payment Entries, 7 Sales Invoices, 3 users,
Administrator `modified` unchanged at `2026-05-28 12:13:39.040427`.

The protected site was not touched.

---

## Phases not started

5–19. Nothing in them was begun, and nothing in them is recorded as blocked. They are
simply not done: commission decision package, unified accounting preparation service,
external-action tracker, production configuration checker, fresh-install hardening, SMTP
rehearsal, automated UAT, human UAT workspace, deployment audit, backup/restore audit,
performance audit, security audit, acceptance matrix, six-viewport browser matrix,
release package and release tag.

No release tag was created, because the brief's tag conditions require a passing browser
matrix, security audit and performance audit, and none of the three was run.
