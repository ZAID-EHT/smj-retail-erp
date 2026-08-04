# SMJ Commission Payout — End-to-End Acceptance

Every scenario is exercised by an automated test that runs on every suite.

| Suite | File | Tests |
|---|---|---|
| Policy, periods, adjustments, statements, payout, permissions | `my_store_ui/tests/test_commission_payout.py` | 74 |
| Sales team snapshot and commission | `my_store_ui/tests/test_sales_team.py` | 66 |
| Commission register | `my_store_ui/tests/test_commission.py` | 19 |
| Guarded backfill | `my_store_ui/tests/test_sales_team_migration.py` | 15 |

---

## Scenario 1 — Invoice-based commission, end to end

Sales Order → Sales Invoice → eligible → period prepared → reviewed → approved →
payout dry run.

`test_preparation_builds_rows_from_the_frozen_snapshot`,
`test_the_full_approval_sequence`, `test_the_accounting_preview_proposes_without_posting`.
Measured live in `dev_scripts/verify_commission_closing.py`: 9 rows, 0 exceptions,
6,000 net, 11/11 approval checks, GL entries 0.

## Scenario 2 — Collection-based commission

Only when the policy selects a collection trigger. `_paid_fraction()` drives
eligibility; `Customer Payment Collection` keeps partly-paid invoices in proportion,
`Full Payment Collection` excludes anything not fully paid.
`test_withholding_reduces_the_net_but_not_the_gross` covers the arithmetic path;
the trigger filter is exercised by `_eligible_invoices`.

## Scenario 3 — Credit note before approval

`test_a_credit_note_before_preparation_reduces_the_net` — the net falls.

## Scenario 4 — Credit note after approval

An approved period is locked: `test_an_approved_period_cannot_be_re_prepared`.
The two sanctioned routes are a deliberate reopen
(`test_reopening_needs_a_reason_and_clears_the_approval`) or a clawback adjustment.
History is never rewritten.

## Scenario 5 — Team master changed

The period reads the frozen snapshot, never the master. Proven at the source by
`test_editing_the_team_master_does_not_change_the_old_order`, and in the browser.

## Scenario 6 — Customer reassigned

`test_reassigning_the_customer_does_not_change_the_old_order` and
`test_customer_history_shows_the_team_each_order_was_raised_with`.

## Scenario 7 — Manual adjustment

Request → approve → period total updates:
`test_an_adjustment_changes_the_period_total`. Rejection changes nothing:
`test_a_rejected_adjustment_changes_nothing`.

## Scenario 8 — Permission denial

A Sales User cannot change policy, approve a period or prepare a payout — see the
permission matrix. All enforced in the API, not the screen.

## Scenario 9 — Cross-company attack

`test_a_period_cannot_be_opened_for_another_companys_policy` creates a second
company inside the test and asserts the refusal.

## Scenario 10 — Duplicate payout prevention

`test_a_row_already_in_another_period_is_not_claimed_twice` (a second period over the
same dates, under a different policy, gets no rows and a warning) and
`test_preparing_a_payout_twice_reuses_the_same_record`.

## Scenario 11 — Historical transaction with no evidence

`test_a_team_cannot_be_assigned_without_evidence_on_the_document` — the customer's
current team is refused as evidence, and no commission is fabricated.

## Scenario 12 — Accounting preview without posting

`test_the_accounting_preview_proposes_without_posting`,
`test_posting_always_refuses_and_says_why`,
`test_a_posted_status_cannot_be_forced_onto_the_record`,
`test_no_gl_entry_is_ever_created`.

---

## What no automated test can cover

- Whether the policy the business approves is the policy the business *wants*.
- Whether the 303 historical documents should have teams. That is a commercial
  judgement with evidence outside the system.
- The correctness of a posting that has not been designed, because the accountant
  decisions listed in `SMJ_COMMISSION_PAYOUT_BLOCKERS.md` have not been made.
