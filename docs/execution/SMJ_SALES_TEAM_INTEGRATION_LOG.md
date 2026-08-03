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

## Phases 3–15 — implementation

Committed in six focused commits on `full-feature-parity`:

| Commit | Scope |
|---|---|
| `cd8bbe6` | `fix:` ship the sales team doctype package files |
| `27c1ec1` | `docs:` audit the sales team and commission data model |
| `7da77ff` | `feat:` snapshot the sales team and commission split on sales documents |
| `9258f69` | `feat:` choose another sales team for one order, with a reason |
| `e6dd2eb` | `feat:` add the commission register, team performance and customer history |
| `e7130a7` | `data:` add the guarded sales team backfill |
| `9dcc637` | `test:` complete acceptance, browser and viewport coverage |

## Defects found and fixed

Six, four of which no existing test could have caught.

| # | Defect | How it was found | Fix |
|---|---|---|---|
| 1 | `_apply_team_rows` wrote the team rate into `Sales Team.commission_rate`, which is `Data`, read-only and `fetch_from sales_person.commission_rate` — the write was silently discarded | Schema audit against the live doctype, not assumption | Stopped writing it; the member's commission amount lives in the retail-owned snapshot row instead |
| 2 | ERPNext compares the standard `sales_team` rows against `100.0` **exactly**; a legal 33.333 × 3 split passes our own ±0.01 tolerance and then blocks the order | Reading `selling_controller.calculate_contribution` | Percentages are balanced to exactly 100 before the standard rows are written, residue on the largest share |
| 3 | A field named `company` is auto-filled by Frappe from the user's default company, making "works for every company" unreachable | A test asserted blank and got `SMJ Retail ERP` | Renamed to `restrict_to_company`, which Frappe leaves alone |
| 4 | A disabled Sales Person in an active team makes ERPNext throw on **every** new order for that team, at the counter | Reading `validate_sales_team` | Refused on the master, where a manager can fix it, with a message naming the person |
| 5 | `_snapshot_from_source` subscripted a child Document, breaking every invoice raised without a team | New commission tests | `.get()` |
| 6 | The customer-history test could not observe the Version trail at all — Frappe sets `ignore_version = frappe.flags.in_test` on every save | The test failed with an empty trail; probed rather than assumed | The test clears the flag so it exercises the production path |

Two further defects were in the browser harness rather than the product: CSRF was
not carried after the first page boot, and the commission checks would have passed
vacuously against a zero-priced fixture. The second is recorded because it would
have made a real defect invisible.

## Phases 16–19 — verification

| Check | Baseline | Final |
|---|---|---|
| Backend suite | 673, 0 failures, 6 skipped | **736, 0 failures, 6 skipped** |
| Sales Team focused | 37/37 | **66/66** |
| Commission | — | **19/19** |
| Backfill | — | **15/15** |
| Sales Team browser | 52/52 | **73/73** |
| Six-viewport matrix | 210/210 | **228/228** |
| Customer picker | 15/15 | **15/15** |
| Button audit | 10, 0 failures | **10, 0 failures** |
| Frontend build | passes | passes |
| Secret scan | clean | clean |
| site1.local | SHA `f51fed…d9c3` | **identical** |
| Staging residue | — | none; counts unchanged after every suite |
