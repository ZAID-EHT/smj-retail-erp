# Pre-universal frontend recovery checkpoint

Created: 2026-07-13

Starting commit: `9349636c617939361d29c1bf8091e175660cfaa6`

Recovery tag: `pre-universal-frontend-engine`

Complete site backup:

- site configuration: `/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-site_config_backup.json` (236 B)
- database: `/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-database.sql.gz` (1.1 MiB)
- public files: `/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-files.tar` (50 KiB)
- private files: `/home/zaidh/frappe-bench/sites/site1.local/private/backups/20260713_140620-site1_local-private-files.tar` (20 KiB)

No migration, restart, schema or site-configuration change was required by the
universal foundation. The normal recovery path is therefore:

1. stop application traffic using the deployment's normal maintenance method;
2. restore the app checkout to `pre-universal-frontend-engine` using a safe new
   branch or an approved non-destructive revert;
3. run `npm run build` in `apps/my_store_ui/frontend`;
4. clear only the normal Frappe website/asset cache if the deployment requires
   it, then verify `/retail-erp/home` and `/app/retail-erp/home`;
5. restore the database/public/private backup only if later database changes
   also need reversal, using the standard `bench --site site1.local restore`
   workflow during a maintenance window.

Never reset a dirty worktree or restore the database without confirming and
preserving subsequent user data first.
