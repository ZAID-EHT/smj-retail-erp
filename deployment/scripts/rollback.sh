#!/usr/bin/env bash
# Roll back to a previous immutable image tag. Never removes data volumes.
set -euo pipefail
cd "$(dirname "$0")/.."
PREV="${1:-}"
[[ -z "$PREV" ]] && { echo "usage: rollback.sh <previous-image:tag>"; exit 2; }
# shellcheck disable=SC1091
set -a; source .env; set +a
echo "== rolling back to $PREV =="
IMAGE="$PREV" docker compose pull
IMAGE="$PREV" docker compose up -d
IMAGE="$PREV" ./scripts/migrate.sh
IMAGE="$PREV" ./scripts/smoke-test.sh
echo "== rollback to $PREV complete. Update .env IMAGE= to persist. =="
echo "NOTE: never run 'docker compose down -v' — it deletes the database volume."
