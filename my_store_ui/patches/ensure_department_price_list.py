"""Ensure the third selling Price List exists.

ACCOUNT CREATION.docx lists three selling prices on the Product form -- Wholesale,
Retail and Department -- and names Department Price List as a Customer Price
Category. An earlier change removed it; this restores it reproducibly.

Idempotent: creating an existing Price List is skipped, and an existing one is only
re-enabled for selling, never renamed or deleted.
"""

from __future__ import annotations

import frappe

PRICE_LIST = "Department Price List"


def execute():
	if frappe.db.exists("Price List", PRICE_LIST):
		row = frappe.db.get_value(
			"Price List", PRICE_LIST, ["enabled", "selling"], as_dict=True
		)
		if row and (not row.enabled or not row.selling):
			doc = frappe.get_doc("Price List", PRICE_LIST)
			doc.enabled = 1
			doc.selling = 1
			doc.save(ignore_permissions=True)
		return

	currency = frappe.db.get_single_value("Global Defaults", "default_currency") or "LKR"
	doc = frappe.new_doc("Price List")
	doc.price_list_name = PRICE_LIST
	doc.currency = currency
	doc.enabled = 1
	doc.selling = 1
	doc.buying = 0
	doc.insert(ignore_permissions=True)
