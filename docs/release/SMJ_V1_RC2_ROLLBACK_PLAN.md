# SMJ v1.0.0-rc2 Rollback Plan

## Code rollback
- Recovery tag before this mission: `pre-smj-final-readiness-20260726-1848`.
- `git checkout pre-smj-final-readiness-20260726-1848` (or reset the branch to it),
  rebuild the frontend, and `bench migrate`.

## Data rollback (staging)
- Full backup taken before write testing:
  `sites/staging.local/private/backups/20260726_184814-staging_local-*`
  (database + public + private files + site config).
- Restore (server-only, needs MariaDB root):
  `bench --site staging.local restore <that database.sql.gz> --with-public-files … --with-private-files …`

## Opening-stock correction rollback
- If the reclassification Journal Entry has been applied, undo it by **cancelling**
  that Journal Entry (marked `SMJ opening-stock reclassification`). No ledger surgery
  is needed — it is a standard submitted document.

## Verify after rollback
- 333 backend tests green; frontend build clean; `/retail-erp` loads.
