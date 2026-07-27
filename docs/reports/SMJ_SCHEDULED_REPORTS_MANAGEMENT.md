# SMJ Scheduled Reports Management

Route: `/retail-erp/reports/scheduled`. Backend: `scheduled_reports.py` over the
standard `Auto Email Report`. Tests: `test_scheduled_reports` (7, green).

## Features
List (search / status filter), create, enable/disable. Choose report, frequency
(Daily/Weekly/Monthly), format (HTML/XLSX/CSV), recipients, day of week.

## Security & truthfulness
- Only reports the caller may run are offered (`Report` + ref-doctype read permission);
  a schedule can never email data its creator cannot see.
- Creating a schedule re-checks report access; scheduling a blocked report is refused.
- **When email is not configured**, new schedules are created **DISABLED**, and a
  disabled schedule **cannot be enabled** — the surface never claims delivery works.
- No arbitrary Python/method execution; only the standard Auto Email Report doctype.

## SMTP dependency
Delivery requires a configured outgoing Email Account (external). Until then, schedules
can be defined but stay disabled — see `docs/email/SMJ_SMTP_PRODUCTION_CHECKLIST.md`.
