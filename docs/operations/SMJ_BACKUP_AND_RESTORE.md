# SMJ Backup & Restore

## Backup status (in-app)

`/retail-erp/admin/system` shows backup history (count, latest age, recent files by
basename). The data comes from the site's own `private/backups` directory via
`system_operations.get_backup_status` — no path, no credential is exposed.

## Taking a backup

Backups use Frappe's own supported mechanism:

```
bench --site staging.local backup --with-files
```

The in-app dashboard reports the resulting files. A web-triggered backup action can
be added later using the same supported mechanism; an **unrestricted web restore is
deliberately not implemented**.

## Restore (server-only, controlled)

Restore is a controlled administrator/server operation, never a web action:

```
bench --site <site> restore <path-to-database.sql.gz> \
  --with-public-files <files.tar> --with-private-files <private-files.tar>
```

Requires the MariaDB root password. In this environment that password is not
available to the app, which is why QA/fresh-site creation is an environment
limitation (see FINAL_READINESS_BLOCKERS).

## Rollback point for this mission

- Backup: `20260726_184814-staging_local-*`
- Tag: `pre-smj-final-readiness-20260726-1848`
