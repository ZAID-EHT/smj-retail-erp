#!/usr/bin/env bash
# Lightweight health probe for monitoring/cron.
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
set -a; source .env; set +a
docker compose ps
docker compose exec -T backend bench --site "$SITE_NAME" execute my_store_ui.system_operations.get_system_health
