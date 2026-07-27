#!/usr/bin/env bash
# Restore-drill into a THROWAWAY site to prove backups are usable. Never touches prod.
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
set -a; source .env; set +a
DRILL="restore-drill.local"
[[ "$DRILL" == "$SITE_NAME" ]] && { echo "REFUSING: drill name equals prod site"; exit 1; }
echo "== restore drill into $DRILL (requires latest backup + DB root) =="
echo "manual, deliberate:"
echo "  docker compose exec backend bench new-site $DRILL --db-root-password \$DB_ROOT_PASSWORD --admin-password <pw>"
echo "  docker compose exec backend bench --site $DRILL restore <db.sql.gz> --with-public-files <f.tar> --with-private-files <p.tar> --db-root-password \$DB_ROOT_PASSWORD"
echo "  docker compose exec backend bench --site $DRILL execute frappe.ping"
echo "  docker compose exec backend bench drop-site $DRILL --db-root-password \$DB_ROOT_PASSWORD   # cleanup"
