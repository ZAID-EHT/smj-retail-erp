#!/usr/bin/env bash
# Deploy an immutable image. Enables maintenance, pulls, migrates, smoke-tests,
# then disables maintenance only on success. Never removes volumes.
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/preflight.sh
# shellcheck disable=SC1091
set -a; source .env; set +a
echo "== enabling maintenance mode =="
docker compose exec -T backend bench --site "$SITE_NAME" set-maintenance-mode on || true
echo "== pulling immutable image $IMAGE =="
docker compose pull
echo "== starting services =="
docker compose up -d
./scripts/migrate.sh
if ./scripts/smoke-test.sh; then
  docker compose exec -T backend bench --site "$SITE_NAME" set-maintenance-mode off
  echo "== deploy OK =="
else
  echo "== smoke test FAILED — leaving maintenance mode ON; investigate or rollback =="
  exit 1
fi
