# SMJ Commission Payout — Browser Verification Matrix

Linux-native Playwright Chromium, headless, driven against the live staging site.
No Windows Chrome, no process killed by name, every browser closed through the
Playwright API.

```
chromium executable: /home/zaidh/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome

PLAYWRIGHT_PATH=/home/zaidh/.npm/_npx/e41f203b7505f1fb/node_modules/playwright \
ERP_USER=… ERP_PW=… node e2e/commission_payout.mjs
                       node e2e/viewport_matrix.mjs
                       node e2e/sales_team.mjs
                       node e2e/customer_picker.mjs
                       node e2e/button_audit.mjs
```

Credentials come from `dev_scripts/browser_check_user.create`, which refuses to run
on any site but `staging.local`, prints a per-run password to stdout only, and is
removed again with `.remove` when the run finishes. No password is written to this
document or the repository.

## Results

| Harness | Checks | Failures |
|---|---|---|
| `e2e/commission_payout.mjs` | **52** | 0 |
| `e2e/viewport_matrix.mjs` (six viewports) | **246** | 0 |
| `e2e/sales_team.mjs` | **73** | 0 |
| `e2e/customer_picker.mjs` | **15** | 0 |
| `e2e/button_audit.mjs` | **10** | 0 (1 skip: Payment Entries has no create button) |
| **Total** | **396** | **0** |

The viewport matrix grew from 228 to 246: three new routes — Commission Periods,
Historical Commission Review and Commission Policy — across six viewports. Its 41
entries cover 39 unique routes; `/sales/teams` and the new-team form each appear
twice, carried over from successive missions, which costs a little time and proves
nothing extra but weakens nothing either.

## Viewports

| Name | Size | Class | Route checks | Failures |
|---|---|---|---|---|
| desktop-1920 | 1920 × 1080 | desktop | 41 | 0 |
| desktop-1440 | 1440 × 900 | desktop | 41 | 0 |
| laptop-1024 | 1024 × 768 | desktop | 41 | 0 |
| tablet-768 | 768 × 1024 | tablet | 41 | 0 |
| mobile-390 | 390 × 844 | mobile | 41 | 0 |
| mobile-360 | 360 × 800 | mobile | 41 | 0 |

## Pages covered

| Page | Where it is checked |
|---|---|
| Commission Policy | viewport matrix (6) + `commission_payout.mjs` |
| Commission Register | viewport matrix (6) |
| Commission Periods (list) | viewport matrix (6) + `commission_payout.mjs` |
| Period detail | `commission_payout.mjs`, all six viewports |
| Exceptions tab | `commission_payout.mjs`, all six viewports |
| Adjustments tab | `commission_payout.mjs`, all six viewports |
| Statements tab | `commission_payout.mjs`, all six viewports |
| Payout preparation tab | `commission_payout.mjs`, all six viewports |
| Accounting preview | `commission_payout.mjs`, all six viewports |
| Historical review | viewport matrix (6) + `commission_payout.mjs` |
| Sales Team detail | `sales_team.mjs` |
| Customer detail | `sales_team.mjs`, `customer_picker.mjs` |
| Sales Invoice detail | `sales_team.mjs` |

The period detail, exceptions, adjustments, statements, payout and accounting
preview are tabs on one route, so no static URL sweep can reach them. They are
driven through the real tab controls instead, at each of the six viewports, against
a period the harness creates and deletes itself.

## What each viewport pass asserts

- The page does not scroll sideways (`scrollWidth − clientWidth ≤ 1`).
- No table is wider than its own box outside a `.smj-table-scroll` container —
  a clipped table is not a scrollable one.
- No console error and no page error.
- No HTTP ≥ 400 on the route.
- No dead route, no unexpected permission denial.
- No stored secret rendered into the DOM.
- **No fake `Paid` status anywhere**, at any width.

## The accounting boundary, checked in the browser

| Assertion | Result |
|---|---|
| A brand-new policy has no earning trigger selected | pass — the field is empty |
| The policy page names every unanswered decision | pass — 6 named, none defaulted |
| A complete policy is `Ready for Review`, not `Active` | pass |
| A complete policy still cannot post | pass |
| An approved, enabled policy becomes `Active` | pass |
| An `Active` policy still cannot post | pass — expense account, payable account, payee party type missing |
| The payout says plainly why posting is blocked | pass — "Policy configuration is incomplete: Commission Expense Account, Commission Payable Account" |
| Every payout line is `Blocked` | pass — no payee party type, no payee, no expense account, no payable account, no cost centre |
| The accounting preview says it would not post | pass — document "not chosen", would post **no** |
| `post_commission_payout` refuses when called directly | pass — HTTP 417 |
| GL entries for the period | **0** |

The measured closing, from the harness's own data: a 100,000 sale at 2% gives a
2,000 pool, split 1,000 / 500 / 500 across a manager and two representatives — the
model in the brief, arrived at by the product rather than asserted by the test.

## Defects found by this matrix

Two, and both were invisible to the backend suite.

**`buildPayout()` wiped the payout it had just prepared.** The handler prepared the
payout, assigned it to `payout.value`, then called `loadDetail()` to refresh the
period totals — and `loadDetail()` begins by setting `payout.value = null`. The
request succeeded every time, the payout record was created every time, and the
screen stayed empty every time. A user would have clicked *Prepare payout*
repeatedly and concluded the feature was broken.

Found by three failing checks in the first run of `commission_payout.mjs`; the
backend suite could not see it because the backend was never wrong. Fixed by
refreshing the period first and publishing the payout after, with the ordering
constraint recorded at the line that depends on it. Re-run: 52/52.

The harness's payout diagnostic also read a `<main>` element this app does not
render, so it silently printed nothing at the moment it was needed most. It reads
the body now.

**The harness's own cleanup left residue and reported success.** It deleted payouts
by *period* name — which never matches, because a payout is named for itself — so
the period could not be deleted either, and both errors went into `.catch(() => {})`.
Five periods, five payouts and five policies had accumulated on staging across runs
while every run printed `failures=0`.

Fixed by looking payouts up through their period, deleting them first, and printing
whatever could not be removed instead of hiding it. The leaked records were deleted.
What the harness now reports as undeleted is correct and expected: the customer,
sales team, item and sales people that a *submitted* invoice links to. Frappe
refuses to delete those, and it is right to — the alternative is orphaning an
accounting document. The run says so out loud rather than implying it tidied up:

```
=== NOT DELETED (expected for anything a submitted document links to) ===
  Customer E2E CPCust …: LinkExistsError
  Retail Sales Team STM-00025: LinkExistsError
  Item P100298: LinkExistsError
  Sales Person E2E CP …-0/-1/-2: LinkExistsError
```

Verified after the final run: 0 policies, 0 periods, 0 payouts on staging, and the
throwaway browser user removed.
