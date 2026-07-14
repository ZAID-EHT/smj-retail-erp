#!/usr/bin/env bash
# Turn-key staging/test-site setup for the wholesale core.
# Requires the MariaDB root password (the one thing the agent could not self-provision).
# Run from the bench directory: bash apps/my_store_ui/docs/full-parity/setup_staging.sh
set -euo pipefail

BENCH="/home/zaidh/frappe-bench"
SOURCE_SITE="site1.local"
STAGING_SITE="${STAGING_SITE:-staging.local}"
ADMIN_PW="${ADMIN_PW:-admin}"

cd "$BENCH"

echo ">> Backing up source site"
bench --site "$SOURCE_SITE" backup --with-files

echo ">> Creating staging site $STAGING_SITE (will prompt for MariaDB root password)"
bench new-site "$STAGING_SITE" --admin-password "$ADMIN_PW" --install-app erpnext

echo ">> Restoring $SOURCE_SITE data into $STAGING_SITE"
LATEST_DB=$(ls -t "sites/$SOURCE_SITE/private/backups/"*-database.sql.gz | head -1)
bench --site "$STAGING_SITE" --force restore "$LATEST_DB"

echo ">> Installing my_store_ui + applying fixtures (custom fields)"
bench --site "$STAGING_SITE" install-app my_store_ui || true
bench --site "$STAGING_SITE" migrate

echo ">> Enabling stock reservation and allow_tests ON STAGING ONLY"
bench --site "$STAGING_SITE" set-config allow_tests true
bench --site "$STAGING_SITE" execute frappe.client.set_value \
  --kwargs '{"doctype":"Stock Settings","name":"Stock Settings","fieldname":"enable_stock_reservation","value":1}'

echo ">> Verifying custom fields applied"
bench --site "$STAGING_SITE" execute my_store_ui.tests.test_wholesale_integration._reservation_ready

echo ">> Running the wholesale test suite"
bench --site "$STAGING_SITE" run-tests --app my_store_ui \
  --module my_store_ui.tests.test_wholesale_integration
bench --site "$STAGING_SITE" run-tests --app my_store_ui \
  --module my_store_ui.tests.test_wholesale_credit

echo ">> Done. Staging site: $STAGING_SITE"
echo ">> Reservation expiry override (optional): set 'wholesale_reservation_expiry_days' in site config."
