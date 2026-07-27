# SMJ Email Setup

Route: `/retail-erp/admin/email` (System Manager only). Backend:
`my_store_ui/email_admin.py`. Tests: `test_email_admin` (4, green).

## Current status on staging: NOT configured

No outgoing `Email Account` exists (`enable_outgoing=1` count = 0), no site-config
SMTP fallback. Welcome and password-reset emails cannot be delivered; onboarding uses
administrator-set passwords. The admin surface reports this truthfully.

## What the surface shows

- Delivery status (outgoing configured / enabled / default account / can-send).
- Email Queue counts by status over 7 days (no recipients, no content).
- Email templates (name + subject).
- Notifications with a wholesale-relevance flag, and per-event coverage.

**No credential is ever returned or logged** — asserted by test.

## External requirement — SMTP credentials

Configuring a real outgoing account is an **external administrator step** (the
credentials are not something this repository can supply):

1. Create an `Email Account` (Frappe): set `email_id`, SMTP host/port, TLS/SSL,
   username, password, `enable_outgoing = 1`, `default_outgoing = 1`.
2. Confirm `awaiting_password` clears (credentials accepted).
3. The status surface flips to "Email delivery is available" with no code change.

Until then the system is fully usable via administrator-set passwords.
