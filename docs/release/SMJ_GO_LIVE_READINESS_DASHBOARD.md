# SMJ Go-Live Readiness Dashboard

Route: `/retail-erp/admin/readiness` (System Manager only). Backend:
`launch_readiness.py`. Tests: `test_launch_readiness` (6, green).

## Truthful by construction
Reports the real state of each launch item across **Code & release, Finance, Setup,
Infrastructure, Business approval**. External items are never marked complete because
a document exists:

- Accountant approval → **Awaiting approval**
- Correction submitted → **Awaiting approval** (until applied)
- Fresh-site test → **Credential required** (MariaDB root)
- SMTP → **Credential required** (until an Email Account is configured)
- Hetzner / DNS / HTTPS / backups → **Credential required**
- Client UAT / management approval → **Not started**

Verified items (backend tests, build, browser, secret scan, migrations, two-company
separation, printing, data) show **Verified/Complete**.

Each item carries owner, action, route/doc and risk. The page supports print,
download, refresh, category grouping and a "blockers only" filter. No credentials or
private paths are exposed (asserted).
