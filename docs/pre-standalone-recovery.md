# Pre-standalone recovery checkpoint

Checkpoint created 2026-07-13 before standalone routing activation.

## Git recovery point

- Tag: `pre-standalone-retail-erp`
- Commit: `110d1fb97f41e573a8c5ec4c27b81a74754b0697`

## Site backup

- Config: `sites/site1.local/private/backups/20260713_113116-site1_local-site_config_backup.json` (236 B)
- Database: `sites/site1.local/private/backups/20260713_113116-site1_local-database.sql.gz` (1.1 MiB)
- Public files: `sites/site1.local/private/backups/20260713_113116-site1_local-files.tar` (50 KiB)
- Private files: `sites/site1.local/private/backups/20260713_113116-site1_local-private-files.tar` (20 KiB)

The backup completed successfully with `bench --site site1.local backup --with-files`. Site and common configuration were inspected; standalone implementation changed neither file.

## Application rollback

1. Preserve any later work in a separate branch or commit.
2. Revert the standalone implementation commit, or create a recovery branch from `pre-standalone-retail-erp`.
3. Run `npm run build` in `apps/my_store_ui/frontend` to restore the tagged Desk-compatible bundle.
4. Run `bench --site site1.local clear-cache`.
5. Reload `/app/retail-erp/home`; the tagged Desk Page mount remains complete.

No database restore is needed for this routing-only implementation. If disaster recovery requires restoring the site backup, stop Bench and obtain explicit approval before using `bench restore` or replacing file archives.

## Configuration rollback

No site configuration, Nginx, database schema, Workspace or core file changed. Reverting the app commit removes `home_page`, website route rules and the request guard together.
