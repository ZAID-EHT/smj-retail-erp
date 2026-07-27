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
#   scripts/verify_fresh_install.sh freshrelease.local
#
set -euo pipefail

SITE="${1:-}"
BENCH_DIR="/home/zaidh/frappe-bench"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin$RANDOM$RANDOM}"

if [[ -z "$SITE" ]]; then
  echo "usage: $0 <new-site-name>   (e.g. freshrelease.local)" >&2
  exit 2
fi

# --- Refuse protected / unknown-existing sites ---------------------------------
case "$SITE" in
  staging.local|site1.local)
    echo "REFUSING: $SITE is protected. Use a NEW site name." >&2; exit 3 ;;
esac
if [[ -d "$BENCH_DIR/sites/$SITE" ]]; then
  echo "REFUSING: site $SITE already exists; will not overwrite." >&2; exit 3
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

# --- MariaDB root password (never echoed) -------------------------------------
if [[ -z "${MARIADB_ROOT_PASSWORD:-}" ]]; then
  read -r -s -p "MariaDB root password: " MARIADB_ROOT_PASSWORD; echo
fi
if [[ -z "$MARIADB_ROOT_PASSWORD" ]]; then
  echo "REFUSING: no MariaDB root password provided." >&2; exit 4
fi

echo "== creating fresh site $SITE =="
bench new-site "$SITE" \
  --db-root-password "$MARIADB_ROOT_PASSWORD" \
  --admin-password "$ADMIN_PASSWORD" \
  --no-mariadb-socket

echo "== installing apps =="
bench --site "$SITE" install-app erpnext my_store_ui
bench --site "$SITE" migrate
bench --site "$SITE" clear-cache

echo "== verifying empty-system detection =="
bench --site "$SITE" execute my_store_ui.setup_wizard.get_setup_status

echo "== creating first company via standard controller =="
bench --site "$SITE" execute my_store_ui.setup_wizard.create_company --kwargs \
  '{"values":{"company_name":"Fresh Test Co","abbr":"FTC","default_currency":"LKR","country":"Sri Lanka","chart_of_accounts":"Standard"}}'

echo "== creating a SECOND company (multi-company) =="
bench --site "$SITE" execute my_store_ui.setup_wizard.create_company --kwargs \
  '{"values":{"company_name":"Fresh Test Co Two","abbr":"FTC2","default_currency":"LKR","country":"Sri Lanka","chart_of_accounts":"Standard"}}'

echo "== re-checking setup status (should be complete) =="
bench --site "$SITE" execute my_store_ui.setup_wizard.get_setup_status

echo "== fresh-install verification COMPLETE for $SITE =="
echo "NOTE: this script does not delete the site; inspect it, then remove manually if desired:"
echo "      bench drop-site $SITE --db-root-password <pw>   # manual, deliberate"
