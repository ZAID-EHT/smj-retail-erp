# Backup Strategy

- **Daily**: `scripts/backup.sh` → `bench backup --with-files` (database + public +
  private files), then copy offsite (encrypted) to a Hetzner Storage Box or S3-compatible
  target (`BACKUP_DESTINATION`, external).
- **Retention**: keep 7 daily, 4 weekly, 6 monthly (configure in the copy step).
- **Server snapshots**: enable Hetzner snapshots as a second layer (external).
- **Restore drill**: run `scripts/restore-test.sh` monthly into a throwaway
  `restore-drill.local` site to prove backups are usable; never restore over prod
  casually.
- **Encryption**: encrypt offsite copies (rclone crypt / age); never commit backups.
