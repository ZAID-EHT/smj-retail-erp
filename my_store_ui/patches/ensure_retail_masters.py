"""Ensure the masters the Customer and Product forms now depend on exist.

Price Category offers exactly three choices, so all three selling Price Lists have
to be there; the carpet-only fields key off an Item Group called Carpets.

Idempotent: an existing record is only re-enabled where it must be, never renamed,
re-parented or deleted.
"""

from __future__ import annotations

import frappe

SELLING_PRICE_LISTS = ("Wholesale Price List", "Retail Price List", "Department Price List")
CARPET_ITEM_GROUP = "Carpets"


def _ensure_price_list(name: str) -> None:
	if frappe.db.exists("Price List", name):
		row = frappe.db.get_value("Price List", name, ["enabled", "selling"], as_dict=True)
		if row and (not row.enabled or not row.selling):
			doc = frappe.get_doc("Price List", name)
			doc.enabled = 1
			doc.selling = 1
			doc.save(ignore_permissions=True)
		return
	doc = frappe.new_doc("Price List")
	doc.price_list_name = name
	doc.currency = frappe.db.get_single_value("Global Defaults", "default_currency") or "LKR"
	doc.enabled = 1
	doc.selling = 1
	doc.buying = 0
	doc.insert(ignore_permissions=True)


def _ensure_carpet_group() -> None:
	if frappe.db.exists("Item Group", CARPET_ITEM_GROUP):
		return
	root = frappe.db.get_value(
		"Item Group", {"is_group": 1, "parent_item_group": ["in", ("", None)]}, "name")
	if not root:
		return
	doc = frappe.new_doc("Item Group")
	doc.item_group_name = CARPET_ITEM_GROUP
	doc.parent_item_group = root
	doc.is_group = 0
	doc.insert(ignore_permissions=True)


def execute() -> None:
	for name in SELLING_PRICE_LISTS:
		_ensure_price_list(name)
	_ensure_carpet_group()
	frappe.db.commit()
