# SMJ Commission Statements

Per-member statements for a period. Reached from the **Statements** tab on the
commission period screen.

## Content

Member · role · team · period · opening carry-forward · gross commission · returns ·
withholding · adjustments · net payable · paid amount · outstanding · closing
carry-forward.

Transaction table: date · customer · Sales Order · Sales Invoice · Payment Entry ·
eligible base · rate · allocation % · gross · reversal · net.

Approved adjustments are listed separately with their type and reason, so a member
can see *why* their figure differs from the raw calculation.

## Permission filtering

| Who | Sees |
|---|---|
| System Manager, Sales Manager, Accounts Manager | every member |
| Anyone else with period read | only the Sales Person linked to their own Employee |
| A user with no linked Sales Person | nothing — not everyone else's earnings |

Requesting another member's statement raises `PermissionError`, not an empty result:
`test_a_member_cannot_read_another_members_statement`.

The user → person link is `User → Employee.user_id → Sales Person.employee`.

## Carry-forward

A balance below the policy's minimum payout is **carried, not lost** — when
`carry_forward_small_balance` is set. The closing carry-forward on one statement
becomes the opening carry-forward on the next period's.

## Paid and outstanding

`paid_amount` is always `0.00` in this build, so `outstanding` always equals net
payable. Only an accounting-backed payout can move it, and none exists. See
`SMJ_COMMISSION_PAYOUT_BOUNDARY.md`.

## Export and print

The statement renders as a normal page and prints through the browser. CSV export of
the underlying rows is available through the commission register
(`/retail-erp/sales/commissions`), under the same permission scoping. Emailing is
deliberately not wired: staging has no outgoing Email Account, so an email action
would silently do nothing.
