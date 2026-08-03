# SMJ Sales Team Integration — Execution Log

## Phase 0 — Preflight

| Step | Result |
|---|---|
| Branch | `full-feature-parity` |
| Commit | `65ecf4bc5d903a308feb9818c4c05ab0a02b4e43` |
| Tracked worktree | clean; `git diff --check` and `git diff --cached --check` both silent |
| Untracked | 4 paths carried from the previous session, all kept (see mission state) |
| Recovery tag | `pre-smj-sales-team-integration-20260803-1813` already existed at HEAD — **not overwritten** |
| Staging backup | `20260803_182238` database 2.4 MiB + files + private files + config |
| site1.local fingerprint | SHA `f51fed…d9c3`, `MATCHES_BASELINE True` |

## Phase 1 — Baseline reproduction

Every number below was measured, not assumed.

| Check | Reported | Measured | Verdict |
|---|---|---|---|
| Focused Sales Team backend tests | 37/37 | **37 tests, OK**, 7.9 s | matches |
| Full backend suite | 673, 0 failures | **Ran 673 tests in 244.1 s — OK (skipped=6)** | matches |
| Frontend build | passes | **✓ built in 4.49 s**, 244 modules | matches |
| Sales Team browser tests | 52/52 | **total=52 failures=0** | matches |
| Six-viewport matrix | 210/210 | **total checks=210 failures=0** | matches |
| Customer picker | 15/15 | **total=15 failures=0** | matches |
| Button audit | 9/9 | **total=10 failures=0** (1 skip: Payment Entries create button is permission-gated) | legitimately increased to 10 |

No unexplained regression. The single difference is the button audit growing from 9
checks to 10, which is an increase in coverage, not a failure.

### Reproduction notes

- The full suite must be captured to a file. Piping it through `tail` loses the
  `Ran N tests` summary behind the diagnostic output some tests print.
- The browser harnesses need `PLAYWRIGHT_PATH` pointing at the npx-cached
  Playwright (`/home/zaidh/.npm/_npx/e41f203b7505f1fb/node_modules/playwright`);
  it is not a frontend dependency and ESM ignores `NODE_PATH`.
- Credentials come from `dev_scripts/browser_check_user.create`, which prints a
  per-run password to stdout and never persists it.

## Phase 2 — Data model audit

Recorded in `docs/sales/SMJ_SALES_TEAM_DATA_MAPPING.md`. Two findings changed the
design:

1. **`Sales Team.commission_rate` is `Data`, read-only, `fetch_from:
   sales_person.commission_rate`.** The pre-existing `_apply_team_rows()` wrote the
   *team* rate into it, which Frappe silently overwrites with the sales person's
   own rate on save. Corrected in this mission.
2. **ERPNext v15 already computes the whole commission chain** in
   `selling_controller.calculate_commission` / `calculate_contribution`. The retail
   model supplies the document `commission_rate` and the allocation percentages and
   lets ERPNext derive the eligible amount, the pool and the contribution, instead
   of duplicating the arithmetic.

Live data position on staging at the start:

```
Customers 30, with a sales team 1
Retail Sales Teams 2 (both active), Sales Persons 10, Companies 1
Sales Order   103 total, 103 submitted, 0 with a snapshot
Delivery Note 101 total, 100 submitted, 0 with a snapshot
Sales Invoice 100 total, 100 submitted, 0 with a snapshot
Sales Order Item 249 total, 249 with grant_commission = 1
Sales Team rows on transactions: 0
```
