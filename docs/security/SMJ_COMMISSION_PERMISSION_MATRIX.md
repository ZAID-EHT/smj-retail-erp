# SMJ Commission — Permission Matrix

Enforced in `commission_policy.py`, `commission_period.py`, `commission_payout.py`
and the doctype permissions. Covered by `test_commission_payout.py` (74 tests).

## The rule that shapes everything

**A hidden button is not a security boundary.** Every capability is enforced
server-side in the API or the controller, so bypassing the screen — posting straight
at the Frappe REST API, or replaying an altered payload — changes nothing.

## Capabilities

| Capability | System Manager | Accounts Manager | Sales Manager | Accounts User | Sales User |
|---|---|---|---|---|---|
| View own commission | yes | yes | yes | yes | yes* |
| View team commission | yes | yes | yes | no | no |
| View all commission | yes | yes | yes | no | no |
| Manage commission policy | yes | yes | **no** | no | no |
| Approve commission policy | yes | yes | **no** | no | no |
| Prepare period | yes | yes | yes | no | no |
| Review period | yes | yes | yes | no | no |
| Approve period | yes | yes | **no** | no | no |
| Request adjustment | yes | yes | yes | no | no |
| Approve adjustment | yes | yes | **no** | no | no |
| Prepare payout | yes | yes | **no** | no | no |
| View accounting preview | yes | yes | no | no | no |
| **Post payout** | **no** | **no** | **no** | **no** | **no** |
| Review historical transactions | yes | yes | yes | no | no |
| Export commission data | yes | yes | yes | own lines | no |

\* only their own lines, and only with Sales Invoice read — which Sales User alone
does not have in ERPNext v15. See `SMJ_SALES_TEAM_PERMISSION_MATRIX.md`.

## Segregation of duties

| Rule | Enforced by |
|---|---|
| A preparer cannot review their own period | `review_commission_period` |
| A preparer cannot approve their own period | `approve_commission_period` |
| A requester cannot approve their own adjustment | `approve_commission_adjustment` |
| A Sales Manager cannot approve a period at all | `APPROVER_ROLES` |
| A Sales Manager cannot prepare a payout | `PAYOUT_PREPARE_ROLES` |
| Nobody can post | `post_commission_payout`, and the payout controller |

Only System Manager may override the first three, and that is deliberate: someone
has to be able to unstick a one-person site.

## Required denials, and what proves them

| Attempt | Result | Test |
|---|---|---|
| Sales User changes policy | `PermissionError` | `test_a_sales_user_cannot_change_policy` |
| Sales Manager approves policy | `PermissionError` | `test_a_sales_manager_cannot_approve_a_policy` |
| Sales Manager approves period | `PermissionError` | `test_a_sales_manager_cannot_approve_a_period` |
| Sales Manager prepares payout | `PermissionError` | `test_a_sales_manager_cannot_prepare_a_payout` |
| Preparer reviews own period | `PermissionError` | `test_the_preparer_cannot_review_or_approve_their_own_period` |
| Requester approves own adjustment | `PermissionError` | `test_a_requester_cannot_approve_their_own_adjustment` |
| Member reads another's statement | `PermissionError` | `test_a_member_cannot_read_another_members_statement` |
| User with no Sales Person reads statements | empty, not others' | `test_a_user_with_no_sales_person_sees_nothing` |
| Payload sets its own approval | ignored | `test_a_payload_cannot_set_its_own_approval` |
| Payload forces `Posted` | `ValidationError` | `test_a_posted_status_cannot_be_forced_onto_the_record` |
| Period for another company's policy | `ValidationError` | `test_a_period_cannot_be_opened_for_another_companys_policy` |
| Assign a historical team with no evidence | `ValidationError` | `test_a_team_cannot_be_assigned_without_evidence_on_the_document` |
| Guest calls anything | `AuthenticationError` | `test_guest_is_rejected_everywhere` |
| Approve past a blocking exception | `ValidationError` | `test_a_blocking_exception_prevents_approval` |
| Approve with an adjustment pending | `ValidationError` | `test_an_adjustment_awaiting_approval_blocks_period_approval` |
| Post a payout | `ValidationError`, always | `test_posting_always_refuses_and_says_why` |

## Disabled users

A disabled user cannot authenticate, so every endpoint is unreachable — the
framework's own boundary, not a second one bolted on.

## Route guards

Each screen is registered against the doctype its own API reads, so the guard and
the API require the same thing and a page can never render and then 403:

| Route | Guarded on |
|---|---|
| `/admin/sales/commission-policy` | `Retail Commission Policy` |
| `/sales/commission-periods` | `Retail Commission Period` |
| `/sales/commissions` | `Sales Invoice` |
| `/sales/commissions/historical-review` | `Sales Invoice` |

## Cross-company

A period's policy must belong to the same company. A team pinned to another company
cannot reach a transaction. Company is carried onto the payout from the period and
never accepted from a payload.

## What is deliberately not restricted

The **accounting preview**'s structure — accounts, party types, amounts — is visible
to anyone who may prepare a payout. It is a proposal, not a posting, and hiding it
would defeat the point of asking an accountant to check it.
