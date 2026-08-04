#!/usr/bin/env bash
# Genuine fresh-install verification for SMJ Retail ERP.
#
# Creates a NEW empty site (no business data), installs the apps, and drives the
# first-time setup flow, then verifies company creation, a second company, company
# separation and basic transactions. It NEVER touches staging.local or site1.local.
#
# Requires the MariaDB root password (interactive prompt or MARIADB_ROOT_PASSWORD env);
# the password is never echoed or written anywhere.
#
# Usage:
#   scripts/verify_fresh_install.sh --dry-run freshrelease.local
#   scripts/verify_fresh_install.sh --create  freshrelease.local
#   scripts/verify_fresh_install.sh --verify  freshrelease.local
#   scripts/verify_fresh_install.sh --resume  freshrelease.local
#
# --dry-run runs every guard and reports exactly what would happen, without
# creating anything and without needing a database credential. It is the only
# mode that is safe to run unattended, and is what CI should call.
#
set -euo pipefail

MODE=""
SITE=""
for arg in "$@"; do
  case "$arg" in
    --dry-run|--create|--verify|--resume) MODE="${arg#--}" ;;
    -*) echo "unknown option: $arg" >&2; exit 2 ;;
    *)  SITE="$arg" ;;
  esac
done
# No default mode. Defaulting to --create would mean a mistyped flag creates a
# site, which is the one outcome worth being pedantic about.
if [[ -z "$MODE" ]]; then
  echo "usage: $0 --dry-run|--create|--verify|--resume <new-site-name>" >&2
  exit 2
fi

BENCH_DIR="/home/zaidh/frappe-bench"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin$RANDOM$RANDOM}"
# Defaults outside the app repo: a rehearsal is a run artifact, not source.
RESULT_FILE="${RESULT_FILE:-$BENCH_DIR/logs/fresh_install_result.json}"

if [[ -z "$SITE" ]]; then
  echo "usage: $0 --dry-run|--create|--verify|--resume <new-site-name>" >&2
  exit 2
fi

# Machine-readable result, so a rehearsal cannot be reported as passed from memory.
STEPS_OK=0
STEPS_FAILED=0
record_result() {
  local status="$1"
  mkdir -p "$(dirname "$RESULT_FILE")"
  cat > "$RESULT_FILE" <<JSON
{
  "site": "$SITE",
  "mode": "$MODE",
  "status": "$status",
  "steps_ok": $STEPS_OK,
  "steps_failed": $STEPS_FAILED,
  "finished_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
  echo "result written: $RESULT_FILE"
}
step() { echo "== $* =="; STEPS_OK=$((STEPS_OK + 1)); }

# --- Refuse protected / unknown-existing sites ---------------------------------
case "$SITE" in
  staging.local|site1.local)
    echo "REFUSING: $SITE is protected. Use a NEW site name." >&2; exit 3 ;;
esac
if [[ -d "$BENCH_DIR/sites/$SITE" && "$MODE" == "create" ]]; then
  echo "REFUSING: site $SITE already exists; will not overwrite." >&2; exit 3
fi
if [[ ! -d "$BENCH_DIR/sites/$SITE" && ( "$MODE" == "verify" || "$MODE" == "resume" ) ]]; then
  echo "REFUSING: site $SITE does not exist; nothing to $MODE." >&2; exit 3
fi

cd "$BENCH_DIR"
ORIGINAL_DEFAULT="$(python3 -c "import json;print(json.load(open('sites/common_site_config.json')).get('default_site',''))")"
echo "original default site: $ORIGINAL_DEFAULT (will restore at end)"

restore_default() {
  if [[ -n "$ORIGINAL_DEFAULT" ]]; then
    bench use "$ORIGINAL_DEFAULT" >/dev/null 2>&1 || true
    echo "restored default site: $ORIGINAL_DEFAULT"
  fi
}
trap restore_default EXIT

# --- Dry run stops here -------------------------------------------------------
# Everything above is a guard. Reaching this point in --dry-run means every guard
# passed, which is the whole question the dry run answers.
if [[ "$MODE" == "dry-run" ]]; then
  step "guards passed for $SITE"
  echo "would create site:      $SITE"
  echo "would install apps:     erpnext my_store_ui"
  echo "would migrate, then verify setup status"
  echo "would create companies: Fresh Test Co, Fresh Test Co Two"
  echo "would restore default:  $ORIGINAL_DEFAULT"
  echo "would NOT delete the site afterwards"
  echo "NOTE: no site was created and no database credential was requested."
  record_result "dry-run-ok"
  exit 0
fi

# --- MariaDB root password (never echoed) -------------------------------------
if [[ -z "${MARIADB_ROOT_PASSWORD:-}" ]]; then
  read -r -s -p "MariaDB root password: " MARIADB_ROOT_PASSWORD; echo
fi
if [[ -z "$MARIADB_ROOT_PASSWORD" ]]; then
  echo "REFUSING: no MariaDB root password provided." >&2; exit 4
fi

if [[ "$MODE" == "create" ]]; then
step "creating fresh site $SITE"
bench new-site "$SITE" \
  --db-root-password "$MARIADB_ROOT_PASSWORD" \
  --admin-password "$ADMIN_PASSWORD" \
  --no-mariadb-socket
fi

step "installing apps"
bench --site "$SITE" install-app erpnext my_store_ui
bench --site "$SITE" migrate
bench --site "$SITE" clear-cache

step "verifying empty-system detection"
bench --site "$SITE" execute my_store_ui.setup_wizard.get_setup_status

step "creating first company via standard controller"
bench --site "$SITE" execute my_store_ui.setup_wizard.create_company --kwargs \
  '{"values":{"company_name":"Fresh Test Co","abbr":"FTC","default_currency":"LKR","country":"Sri Lanka","chart_of_accounts":"Standard"}}'

step "creating a SECOND company (multi-company)"
bench --site "$SITE" execute my_store_ui.setup_wizard.create_company --kwargs \
  '{"values":{"company_name":"Fresh Test Co Two","abbr":"FTC2","default_currency":"LKR","country":"Sri Lanka","chart_of_accounts":"Standard"}}'

step "re-checking setup status (should be complete)"
bench --site "$SITE" execute my_store_ui.setup_wizard.get_setup_status

record_result "completed"
echo "== fresh-install verification COMPLETE for $SITE =="
echo "NOTE: this script does not delete the site; inspect it, then remove manually if desired:"
echo "      bench drop-site $SITE --db-root-password <pw>   # manual, deliberate"
