# SMJ Production Operations

## Readiness checklist (from /retail-erp/admin/system)

| Item | Staging now | Production target |
|------|-------------|-------------------|
| Database connected | ✓ | ✓ |
| Redis connected | ✓ | ✓ |
| Scheduler enabled | ✗ (disabled) | **must be enabled** |
| Developer mode off | ✓ | ✓ |
| Pending migrations | none | none |
| Email configured | ✗ | configure SMTP (external) |
| Backups recent | ✓ | scheduled + offsite |

## Operational notes

- **Scheduler must be enabled in production** so reservation-expiry release and other
  scheduled jobs run (`bench --site <site> enable-scheduler`).
- **Email**: configure an outgoing Email Account (external SMTP credentials).
- **Backups**: schedule regular backups and copy them offsite.
- All operational status is available read-only in-app to System Managers; no shell
  access is exposed through the web.
