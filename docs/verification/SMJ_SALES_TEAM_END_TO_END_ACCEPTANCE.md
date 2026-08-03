# SMJ Sales Team — End-to-End Acceptance

Every scenario below is exercised by an automated test that runs on every suite.
None of them is a manual checklist item.

| Suite | File | Tests |
|---|---|---|
| Sales team, snapshot, override, commission | `my_store_ui/tests/test_sales_team.py` | 66 |
| Commission register, performance, history | `my_store_ui/tests/test_commission.py` | 19 |
| Guarded backfill | `my_store_ui/tests/test_sales_team_migration.py` | 15 |
| Real browser | `frontend/e2e/sales_team.mjs` | 74 checks |

---

## Scenario 1 — The customer's own team

Create a team → assign it to a customer → select the customer → raise an order →
the snapshot matches → submit → edit the team master → the order is unchanged.

| Step | Proven by |
|---|---|
| The order freezes the customer's team | `test_order_stores_a_snapshot` |
| Smart Sales does the same through the cart API | `test_the_cart_freezes_the_customers_team` |
| Members, roles and shares are frozen as rows | `test_snapshot_rows_keep_the_role_the_standard_table_cannot` |
| Editing the master leaves the order alone | `test_editing_the_team_master_does_not_change_the_old_order` |
| …in a real browser, end to end | browser: *editing the team master leaves the raised order untouched* |

## Scenario 2 — Reassigning the customer

Order A on team A → reassign the customer to team B → order B.
A keeps team A; B uses team B.

Proven by `test_reassigning_the_customer_does_not_change_the_old_order`, which
asserts both halves, and by
`test_customer_history_shows_the_team_each_order_was_raised_with`.

## Scenario 3 — Overriding the team for one transaction

| Rule | Proven by |
|---|---|
| A manager may use another team | `test_a_manager_may_override_with_a_reason` |
| A reason is required | `test_an_override_without_a_reason_is_rejected` |
| The order records team B | `test_the_cart_can_carry_an_authorised_override` |
| The customer master still says team A | asserted inside both tests above |
| The browser refuses a reasonless override too | browser: *an override with no reason is refused* |

## Scenario 4 — Overriding the percentages

**Deliberately not implemented.**

The requirement is conditional: *"Do not allow manual percentage editing in Smart
Sales unless a separate approved permission exists."* No such approved permission
exists, so the compliant behaviour is to withhold the capability rather than invent
an approval that nobody granted.

The percentages on a transaction can therefore only come from a team master that a
Sales Manager has already saved and validated. Changing the split for one order
means using a team with that split — which the override in Scenario 3 supports.

Adding it later needs: a new permission, a reason, a server-side re-check that the
total is exactly 100 with no duplicate member, and the snapshot stored without
touching the master. The enforcement for all of that already exists in
`RetailSalesTeam.validate` and `freeze_team`.

## Scenario 5 — An inactive team

| Rule | Proven by |
|---|---|
| History stays readable | `test_deactivating_the_team_leaves_the_submitted_order_readable` |
| A new assignment is refused | `test_inactive_team_cannot_be_assigned` |
| A new transaction is refused | `test_an_inactive_team_cannot_be_used_on_a_new_document` |
| The picker does not offer it | `test_search_only_offers_active_teams` |
| Smart Sales warns about it | `test_the_assignment_endpoint_warns_when_the_team_went_inactive` |
| The backfill leaves it for a human | `test_an_inactive_team_is_left_for_a_human` |

## Scenario 6 — Delivery Note and Sales Invoice

The order's snapshot flows through both without re-reading anything.

`test_delivery_note_inherits_the_orders_snapshot` and
`test_the_invoice_inherits_the_orders_frozen_team_and_earns_on_it`, which also
checks the invoice earns on the frozen rate (4,000 pool split 2,000/1,000/1,000)
and reports status `Earned`. The browser check confirms the panel renders on both
detail pages.

## Scenario 7 — Credit note

`test_a_credit_note_reverses_the_commission_in_proportion` — a full return of a
4,000 pool produces exactly −4,000, split −2,000/−1,000/−1,000, on the **original**
team.

`test_a_credit_note_shows_as_a_reversal_and_nets_off` — the register shows the
reversal lines and the invoice plus its credit note net to exactly zero.

A reversal cannot exceed the original because ERPNext already refuses to return
more than was invoiced.

## Scenario 8 — Permission denial

| Attempt | Proven by |
|---|---|
| Sales User creates or edits a team | `test_a_sales_user_can_read_but_not_change_a_team` |
| Sales User assigns a team to a customer | same |
| Sales User overrides by posting straight at the API | `test_an_ordinary_sales_user_cannot_override_even_by_posting_directly` |
| Sales User reads another person's commission | `test_a_sales_user_sees_only_their_own_lines` |
| A user with no linked person reads anyone's | `test_a_user_with_no_sales_person_sees_an_empty_register` |
| A user without invoice read opens the register | `test_a_user_without_invoice_read_is_refused_outright` |
| Guest calls anything | `test_guest_is_rejected` (both suites) |
| Unauthorised direct route + direct API | browser: *unauthorised direct access is denied*, *backend refuses the unauthorised user too* |

The browser check matters because a hidden menu is not a boundary: it navigates
straight to the URL and separately calls the API, and requires both to refuse.

## Scenario 9 — Cross-company

`test_a_team_pinned_to_another_company_is_refused` creates a second company inside
the test, pins a team to it, and asserts the order is refused.
`test_search_hides_a_team_pinned_to_another_company` asserts it is never even
offered. `test_a_team_with_no_company_works_for_every_company` asserts the
unrestricted case still works.

## Scenario 10 — Concurrent team edit

`test_a_team_edited_while_an_order_is_being_raised_still_saves_one_consistent_snapshot`
builds an order in memory, changes the team master before it is inserted, then
inserts it. Whichever version the snapshot captures, it must be internally
consistent — one team, its own rate, and members totalling exactly 100 — never a
half-old, half-new mixture.

---

## Responsive and visual

Six viewports (1920×1080, 1440×900, 1024×768, 768×1024, 390×844, 360×800) via
`frontend/e2e/viewport_matrix.mjs`. Results in
`docs/verification/SMJ_SALES_TEAM_BROWSER_MATRIX.md`.

## What no automated test can cover

- Whether the commission **rate** on each team is the rate the business intends.
  The system enforces 0–100 and that the split totals 100; it cannot know the
  commercial agreement.
- Whether the 29 unassigned customers *should* have a team. Listed for a human in
  `docs/data/SMJ_SALES_TEAM_MIGRATION_RESULT.md`.
- Payout. Deferred; see `docs/sales/SMJ_COMMISSION_PAYOUT_BOUNDARY.md`.
