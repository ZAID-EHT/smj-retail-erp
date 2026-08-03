# SMJ Sales Team — Permission Matrix

Enforced in `my_store_ui/sales_team.py`, `my_store_ui/commission.py` and the
`Retail Sales Team` doctype permissions. Covered by
`test_sales_team.py`, `test_commission.py` and `test_sales_team_migration.py`.

## The rule that shapes everything

**A hidden menu is not a security boundary.** Every capability below is enforced
server-side, in the API or in the document hook, so bypassing the screen — posting
straight at the Frappe REST API, or replaying an altered payload — changes nothing.
The navigation and buttons only mirror what the server already decided.

## Capabilities

| Capability | System Manager | Sales Manager | Sales User | Accounts Manager | Accounts User | Enforced by |
|---|---|---|---|---|---|---|
| View sales teams | yes | yes | yes | yes | no | `Retail Sales Team` read |
| Create / edit a team | yes | yes | **no** | no | no | `_require_manage()` |
| Deactivate a team | yes | yes | **no** | no | no | `_require_manage()` |
| Assign a team to a customer | yes | yes | **no** | no | no | `_require_manage()` + Customer write |
| Override the team for one transaction | yes | yes | **no** | no | no | `_resolve_document_team()` in `before_validate` |
| Give an override reason | required | required | n/a | n/a | n/a | `_resolve_document_team()` |
| See the frozen team on a document | yes | yes | yes | yes | yes | document read |
| View the commission register | yes | all lines | **refused** | all lines | own lines only | `commission.list_commissions` |
| Export the register | yes | yes | refused | yes | own lines only | Sales Invoice `export` |
| Edit a submitted snapshot | **no** | **no** | **no** | **no** | **no** | `guard_snapshot_after_submit` |
| Approve a payout | — | — | — | — | — | not implemented; see the payout boundary |

## Two results that look surprising and are correct

### Sales User cannot see the commission register

The register reports Sales Invoice data, so it requires Sales Invoice read. In
ERPNext v15 the Sales User role does not have it. An ordinary counter user
therefore needs Accounts User as well before they can see even their own line.

The alternative — reading invoice figures out to someone who cannot open the
invoice — would be a leak dressed up as a feature. Asserted by
`test_a_user_without_invoice_read_is_refused_outright`.

### A user with no linked Sales Person sees an empty register

Not everyone else's earnings, and not an error. The user → person link is
`User → Employee.user_id → Sales Person.employee`. No link means no lines.
Asserted by `test_a_user_with_no_sales_person_sees_an_empty_register`.

## Attack surface and what stops it

| Attempt | Result | Asserted by |
|---|---|---|
| Sales User creates a team via the API | `PermissionError` | `test_a_sales_user_can_read_but_not_change_a_team` |
| Sales User assigns a team to a customer | `PermissionError` | same |
| Sales User posts a Sales Order with another team set | `PermissionError` — the check is in the document hook, not the screen | `test_an_ordinary_sales_user_cannot_override_even_by_posting_directly` |
| Override with no reason | `ValidationError` | `test_an_override_without_a_reason_is_rejected` |
| Raise a new document on an inactive team | `ValidationError` | `test_an_inactive_team_cannot_be_used_on_a_new_document` |
| Use a team pinned to another company | `PermissionError` | `test_a_team_pinned_to_another_company_is_refused` |
| Offer a cross-company team in the picker | Filtered out before it is shown | `test_search_hides_a_team_pinned_to_another_company` |
| Save shares totalling 90 or 110 | `ValidationError`, server-side | `test_shares_totalling_90_are_rejected`, `..._110_...` |
| Put the same person in a team twice | `ValidationError` | `test_duplicate_person_is_rejected` |
| Give a team two managers, or none | `ValidationError` | `test_two_managers_are_rejected`, `test_a_team_needs_an_active_manager` |
| Edit the team on a submitted document | `ValidationError` | `test_a_submitted_snapshot_cannot_be_edited_in_place` |
| Change the master to alter an old order | No effect — the snapshot is frozen | `test_editing_the_team_master_does_not_change_the_old_order` |
| Reassign the customer to alter an old order | No effect | `test_reassigning_the_customer_does_not_change_the_old_order` |
| Read another person's commission | Filtered server-side | `test_a_sales_user_sees_only_their_own_lines` |
| Call any endpoint as Guest | `AuthenticationError` | `test_guest_is_rejected` (both suites) |
| Run the backfill against `site1.local` | `MigrationRefused` | `test_a_protected_site_is_refused_for_being_protected` |

## Route guards

A Vue route is not enough: `frontend/src/main.js` sends every navigation through
`my_store_ui.standalone.authorize_frontend_route`, which matches `ROUTE_REGISTRY`.
Both sales-team routes are registered with the doctype their own API reads, so the
guard and the API require the same thing and a page can never render and then 403:

| Route | Guarded on |
|---|---|
| `/sales/teams` | `Retail Sales Team` read |
| `/sales/commissions` | `Sales Invoice` read |

## What is deliberately *not* restricted

- **Reading the frozen team on a document a user can already open.** If they can
  see the order, they can see who it was raised for. Withholding it would hide the
  audit trail from the people who need it.
- **Team names, codes and member names.** These are operational, not private. No
  salary, employee record or other HR field is exposed anywhere — the snapshot
  carries the Sales Person and their display name, nothing more.

## Roles used

`System Manager` is a Frappe role and carries **no** ERPNext selling rights on its
own. Anything that needs to read a Sales Order or Sales Invoice must hold the
ERPNext role too. The browser-verification user is given the full operator role set
for exactly this reason.
