# Remaining Approval and Environment Blockers

## Corrected required-222 mission

There are no remaining approval- or environment-blocked items inside the
corrected required scope:

- `required_but_missing = 0`
- `unclassified = 0`
- registry `blocked = 0`

## Production-readiness gates outside that corrected scope

These remain real and must not be confused with parity completion:

1. Customer credit/non-credit and shared wholesale transaction-ID Custom Fields
   require explicit schema/fixture approval.
2. Stock reservation configuration and concurrency behaviour require staging
   approval and behavioural testing.
3. `allow_tests` is disabled on `site1.local`; a dedicated staging/test site is
   still required for rollback-safe full Frappe test execution.
4. Browser automation is unavailable in this environment. Desktop/mobile,
   keyboard, role, session-expiry and destructive-action flows remain manual/UAT.
5. Server PDF remains dependent on a working `wkhtmltopdf` installation and
   visual verification.
6. Backup restore, load/concurrency testing, accountant verification, data
   migration rehearsal and client acceptance remain unproven.

The broad strict inventory audit also remains red (`unmapped_user_facing =
1683`). Those entries include optional, platform, standard-Desk and lower-priority
surfaces outside the corrected required-222 target; see the generated feature
inventory and parity registry for their explicit classifications.
