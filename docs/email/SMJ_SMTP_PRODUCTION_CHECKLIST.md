# SMJ SMTP Production Checklist

## Current state
No outgoing Email Account is configured on staging (`enable_outgoing` count = 0). The
in-app Email admin (`/retail-erp/admin/email`, System Manager only) reports this
truthfully. Onboarding works via administrator-set passwords until SMTP is connected.

## Security (verified — `test_email_admin`, 4 tests)
- Email admin endpoints are **System Manager only** — a Sales user is rejected.
- The overview **never returns a credential** — no password, SMTP host, username, API
  key or token (asserted).
- Nothing logs a credential.
- Email Queue is summarised as counts by status only (no recipients, no content).
- Truthful unconfigured state; temporary-password onboarding remains available.

## Configuring outgoing email (EXTERNAL — real SMTP credentials required)

Do this through the standard Frappe **Email Account** form, which natively treats the
password as **write-only** (stored encrypted, never returned):

1. Create an `Email Account`:
   - Email address, SMTP host, port, TLS/SSL as required by the provider
   - Username, **Password** (write-only — never displayed after save)
   - `Enable Outgoing = 1`, `Default Outgoing = 1`
2. Confirm `awaiting_password = 0` (credentials accepted).
3. In `/retail-erp/admin/email`, status flips to **"Email delivery is available"** —
   no code change.

## Verify delivery (only after credentials are set)
```
# Confirm an enabled, credentialled default outgoing account exists:
bench --site <site> execute my_store_ui.email_admin.get_email_overview
# Send a test email via Frappe's standard mechanism (real credentials only):
bench --site <site> execute frappe.sendmail --kwargs '{"recipients":["you@example.com"],"subject":"SMJ SMTP test","message":"ok"}'
```

## Do NOT
- Do not commit or print SMTP passwords.
- Do not build a bespoke credential-write endpoint — the standard Email Account form
  already handles write-only password storage safely.

## Status
Email administration/visibility: **implemented + security-verified**. Actual SMTP
credentials: **external requirement** — recorded in the blockers.
