"""Point the site's favicon and app logo at the SMJ mark.

The Retail ERP SPA sets its own icon links, but every other page the site serves
-- the login screen, the desk, any website page, a printed PDF's header -- takes
its icon from Website Settings. Without this the tab shows the Frappe default on
those pages, so the branding is right in the app and wrong everywhere else.

Idempotent, and deliberately non-destructive: a site that has already set its own
favicon or logo keeps it. This patch fills blanks and replaces the known Frappe
defaults, nothing more.
"""

from __future__ import annotations

import frappe

FAVICON = "/assets/my_store_ui/images/favicon.ico"
LOGO = "/assets/my_store_ui/images/smj-logo.png"
APP_NAME = "SMJ ERP"

# Values that mean "nobody chose this" -- safe to replace. "Frappe" is the stock
# app_name every site ships with, so it counts as unset for our purposes.
REPLACEABLE = {
	"",
	None,
	"Frappe",
	"Retail ERP",
	"/assets/frappe/images/frappe-favicon.svg",
	"/assets/frappe/images/frappe-framework-logo.png",
	"/assets/frappe/images/frappe-logo.png",
	"/assets/erpnext/images/erpnext-logo.svg",
	"/assets/my_store_ui/images/product-placeholder.svg",
}


def _set_if_unclaimed(doctype: str, field: str, value: str) -> bool:
	# These are Single DocTypes: they have no table of their own, so the field has
	# to be checked through the meta rather than with has_column.
	if not frappe.get_meta(doctype).has_field(field):
		return False
	current = frappe.db.get_single_value(doctype, field)
	if current not in REPLACEABLE:
		return False
	frappe.db.set_single_value(doctype, field, value)
	return True


def execute():
	changed = []
	for doctype, field, value in (
		("Website Settings", "favicon", FAVICON),
		("Website Settings", "app_logo", LOGO),
		# Names the product in the title of every page Frappe renders itself.
		("Website Settings", "app_name", APP_NAME),
		("Navbar Settings", "app_logo", LOGO),
	):
		if not frappe.db.exists("DocType", doctype):
			continue
		if _set_if_unclaimed(doctype, field, value):
			changed.append(f"{doctype}.{field}")

	if changed:
		frappe.clear_cache()
