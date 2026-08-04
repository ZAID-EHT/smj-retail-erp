# SMJ Commission Payout — Execution Log

## Phase 0 — Preflight

| Step | Result |
|---|---|
| Branch | `full-feature-parity` |
| Commit | `d19a0273c53cee558075d5ec54b80edbd68c24f7` |
| `v1.0.0-rc9` target | verified identical to HEAD |
| Worktree | clean; both `--check` runs silent |
| Recovery tag | `pre-smj-commission-payout-20260804-0018` (new) |
| Staging backup | `20260804_001837`, database 2.6 MiB + files |
| site1.local | SHA `f51fed…d9c3`, `MATCHES_BASELINE True` |

## Phase 1 — Baseline reproduced

| Check | Reported | Measured |
|---|---|---|
| Backend suite | 736, 0 failures | **Ran 736 tests — OK (skipped=6)** |
| Frontend build | clean | **✓ built in 5.64 s** |

## Phase 2 — Current-state audit

Recorded in `docs/sales/SMJ_COMMISSION_CURRENT_STATE_AUDIT.md`. Three findings
shaped the work:

1. **Cancellation already removes commission, and keeps the evidence.** Measured: a
   submitted invoice gave 3 register lines totalling 2,000; after `cancel()` it gave
   0, while the snapshot survived. So a period approved after a late cancellation
   holds a row whose source no longer qualifies — handled as a clawback, not a
   rewrite.
2. **Payment Entry has no sales team field.** Collection-based eligibility must join
   Payment Entry Reference → Sales Invoice rather than stamp the payment.
3. **The historical export is 331 rows, not the 333 reported.** The count is read
   from the file every time, never carried forward.

## Defects found and fixed

| # | Defect | How it was found | Fix |
|---|---|---|---|
| 1 | `RetailCommissionPeriod.is_locked()` shadowed Frappe's `is_locked` **property**, which backs `check_if_locked`. A bound method is always truthy, so every period save looked locked and then crashed stat-ing a lock file that had never been created. | End-to-end run failed on the first `prepare`; instrumented the lock state rather than guessing | Renamed to `is_closed()`, with the reason recorded at the definition |
| 2 | `_terms_changed` relied on `get_doc_before_save()`, which Frappe only populates *inside* `save()` — long after the comparison is made. Editing an approved policy's rate silently kept the old approval. | A test asserted the approval was withdrawn and it was not | Capture the previous values before anything is mutated |

Two more were found later, in the browser, and are recorded under Phases 17–21.

Three further failures were test-side, not product-side: a period covers a date
range, so it legitimately picks up invoices staging already had, and two assertions
had to scope to the members the test created. A fourth test constructed an
impossible scenario (two overlapping periods under one policy, which the controller
correctly refuses) and now uses a second policy.

## Phases 3–16 — implementation

| Commit | Scope |
|---|---|
| `985784e` | `feat:` commission policy configuration |
| `21de3b4` | `feat:` period closing, review and approval |
| `a67209e` | `feat:` adjustments, statements and payout preparation |
| `6257548` | `feat:` historical review, dashboards and the closing screens |

Seven new doctypes: Policy, Period, Period Detail, Exception, Adjustment, Payout,
Payout Line. Three new API modules: `commission_policy`, `commission_period`,
`commission_payout`. Three new screens.

## The measured closing

```
policy status with nothing chosen     Draft
missing for calculation               6 decisions, none defaulted
status once complete                  Ready for Review
may post                              False
status after approval                 Active
complete for posting                  False

simulated lines / net / persisted     9 / 6000.0 / False
matches current calculation           True

period id                             COM-PER-2026-000001
prepared rows / exceptions            9 / 0
rows after preparing twice            9
approval checks                       11 total, 0 failed
period status                         Approved

statement gross / withholding / net   1000.0 / 0.0 / 1000.0
payout total net payable              6000.0
every line                            Blocked (no payee party type)
accounting preview would_post         False
posting                               refused, listing the missing decisions
GL entries for the period             0
```

## Phases 17–21 — verification

Run after the implementation commits, on `staging.local`, with the throwaway
browser user created and removed around the run.

### Backend

```
bench --site staging.local run-tests --app my_store_ui
Ran 810 tests in 474.544s
OK (skipped=6)
```

736 at the baseline, 810 now: **+74**, all in `tests/test_commission_payout.py`.
Zero failures, zero errors.

### Browser

| Harness | Checks | Failures |
|---|---|---|
| `e2e/commission_payout.mjs` | 52 | 0 |
| `e2e/viewport_matrix.mjs` (41 routes × 6 viewports) | 246 | 0 |
| `e2e/sales_team.mjs` | 73 | 0 |
| `e2e/customer_picker.mjs` | 15 | 0 |
| `e2e/button_audit.mjs` | 10 | 0 |
| **Total** | **396** | **0** |

The viewport matrix went from 228 to 246 — three new routes at six viewports.
Full detail in `docs/verification/SMJ_COMMISSION_PAYOUT_BROWSER_MATRIX.md`.

### Everything else

| Check | Result |
|---|---|
| `npm run build` | ✓ built in 4.96 s, 253 modules |
| Secret scan | clean |
| `site1.local` fingerprint | SHA `f51fed…d9c3`, `MATCHES_BASELINE True` — identical to the pre-mission read |
| Test residue on staging | none: 0 policies, 0 periods, 0 payouts, browser user removed |

## Two more defects, both found only by the browser

| # | Defect | How it was found | Fix |
|---|---|---|---|
| 3 | `buildPayout()` prepared the payout, assigned it, then called `loadDetail()` — which opens by setting `payout.value = null`. Every preparation succeeded and none of them ever rendered. | Three failing checks on the first browser run | Refresh the period first, publish the payout after, with the ordering constraint recorded at the line that depends on it |
| 4 | The harness's own cleanup deleted payouts by *period* name, which never matches, so the period then could not go either — and both errors were swallowed by `.catch(() => {})`. Five periods, payouts and policies had accumulated across runs while the harness reported success. | Counted the commission doctypes on staging after the run | Look payouts up by their period, delete them first, and print anything that could not be removed instead of hiding it |

Defect 3 is the one that matters to a user: the backend suite could not have caught
it, because the backend was never wrong. Defect 4 is the one that matters to
everyone who trusts a green run — a cleanup that swallows every error reports
success and leaves residue.

The five leaked periods, payouts and policies were removed. The customer, team,
item and sales people a submitted invoice links to are deliberately left in place;
Frappe refuses to delete them and it is right to. The harness now says so out loud
rather than pretending it tidied up.
