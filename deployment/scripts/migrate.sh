#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
set -a; source .env; set +a
echo "== bench migrate =="
docker compose exec -T backend bench --site "$SITE_NAME" migrate
docker compose exec -T backend bench --site "$SITE_NAME" clear-cache
