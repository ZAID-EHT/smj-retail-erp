#!/usr/bin/env bash
# Daily backup with files, copied to an offsite destination.
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
set -a; source .env; set +a
docker compose exec -T backend bench --site "$SITE_NAME" backup --with-files
echo "== backup complete; copy to offsite (${BACKUP_DESTINATION:-unset}) =="
# Example (configure): rclone copy <sites backups path> "$BACKUP_DESTINATION" --crypt
