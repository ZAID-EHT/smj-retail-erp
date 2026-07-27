# SMJ Production Cutover Plan

1. **Freeze**: announce a maintenance window.
2. **Backup** the current source of truth (staging or prior prod).
3. **Accountant sign-off**: apply the opening-stock reclassification (runbook) so
   production launches with correct P&L.
4. **Fresh site or restore**: create the production site (fresh, via the setup wizard)
   or restore an approved dataset.
5. **SMTP**: configure the outgoing Email Account (external credentials).
6. **Enable scheduler** (`bench enable-scheduler`).
7. **DNS + TLS**: point the domain, verify HTTPS.
8. **Smoke test** + a short **client UAT** pass (external participants).
9. **Go live**; monitor error log / health for the first days.

Blocking externals: accountant sign-off, SMTP, Hetzner/DNS, client UAT.
