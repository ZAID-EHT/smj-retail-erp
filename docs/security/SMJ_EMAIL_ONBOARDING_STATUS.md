# SMJ Email and Onboarding Status

Verified on `staging.local`, 2026-07-26.

## Current state — email delivery is NOT configured

| Check | Result |
|-------|--------|
| `Email Account` records with `enable_outgoing = 1` | **0** |
| Default outgoing account | **none** |
| Site-config SMTP fallback (`mail_server` / `mail_login`) | **not set** |
| Can a welcome or reset email be delivered? | **No** |

**Consequence:** any flow that depends on a welcome or password-reset email does
nothing. Onboarding must use an administrator-set password.

The Access Control screen states exactly this:

> Email delivery is not configured. Use an administrator-set temporary password.

## The schema trap this surface hit

`Email Account` has **no `disabled` field**. The first implementation filtered on
`{"enable_outgoing": 1, "disabled": 0}`, which raised
`OperationalError (1054) Unknown column 'tabEmail Account.disabled'` on *every*
call and took the whole user-access overview down with it.

The real fields are:

| Field | Meaning |
|-------|---------|
| `enable_outgoing` | the account is meant to send |
| `default_outgoing` | it is the default sender |
| `awaiting_password` | it exists but has **no working credentials**, so it cannot send |

`awaiting_password` matters: without it, an account that is configured but silently
dead reports as healthy. Frappe's own `User.set_new_password` checks
`{"default_outgoing": 1, "awaiting_password": 0}` before claiming it emailed anyone,
so this surface reports the same condition.

## What the endpoint returns

`my_store_ui.access_management.get_email_configuration_status` returns
`outgoing_configured`, `outgoing_enabled`, `default_outgoing_account`,
`site_config_fallback`, `can_send_welcome_email`, a per-account list
(`name`, `email_id`, `default_outgoing`, `awaiting_password`) and an actionable
`message` when delivery is unavailable.

**No credential is ever read or returned** — no password, SMTP host, API key or
token. Asserted by `test_email_status_never_returns_credentials`. The endpoint is
System Manager gated (`test_email_status_is_not_readable_by_a_non_manager`).

## Onboarding without email

1. Create the user at `/retail-erp/admin/users` — username, password and role are the
   only required inputs on the curated add form.
2. The password is set through the write-only `new_password` input; it is accepted on
   save and never returned on any read path.
3. Communicate it out of band and require a change at first login.

This is verified end to end by
`test_core_acceptance.test_scenario_11_user_lifecycle_end_to_end`.

## To enable email later

Create an `Email Account` with `enable_outgoing = 1` and `default_outgoing = 1`, and
supply working credentials so `awaiting_password` clears. The status surface will
flip to available with no code change. **This is external setup — it is not a code
defect and nothing in this repository can complete it.**
