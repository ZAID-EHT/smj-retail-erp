#!/usr/bin/env bash
# Post-deploy smoke test. Non-destructive.
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
set -a; source .env; set +a
echo "== ping =="
docker compose exec -T backend bench --site "$SITE_NAME" execute frappe.ping
echo "== system readiness =="
docker compose exec -T backend bench --site "$SITE_NAME" execute my_store_ui.system_operations.get_readiness
echo "== HTTP frontend =="
code=$(curl -s -o /dev/null -w '%{http_code}' -H "Host: $SITE_NAME" http://127.0.0.1:8080/api/method/frappe.ping || echo 000)
echo "frontend ping HTTP $code"
[[ "$code" == "200" ]]
