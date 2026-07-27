#!/usr/bin/env bash
# Validate the environment before a deploy. Read-only; no changes.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== preflight =="
[[ -f .env ]] || { echo "MISSING .env (copy .env.example)"; exit 1; }
# shellcheck disable=SC1091
set -a; source .env; set +a
: "${IMAGE:?IMAGE not set}"; : "${SITE_NAME:?SITE_NAME not set}"; : "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD not set}"
[[ "$IMAGE" == *:*  ]] || { echo "IMAGE must be an explicit :tag (no floating latest)"; exit 1; }
[[ "$IMAGE" == *:latest ]] && { echo "REFUSING floating :latest tag"; exit 1; }
command -v docker >/dev/null || { echo "docker not installed"; exit 1; }
docker compose -f compose.yaml config >/dev/null && echo "compose config OK"
echo "preflight OK for $SITE_NAME using $IMAGE"
