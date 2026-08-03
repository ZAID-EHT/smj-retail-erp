"""Audit ERPNext's own commission fields on the selling documents.

Establishes whether the standard commission chain (eligible amount -> rate ->
total commission -> per-person allocation -> incentives) is present and usable,
so the Retail commission model can reuse it instead of duplicating the maths.
"""

from __future__ import annotations

import frappe

DOCTYPES = ("Sales Order", "Delivery Note", "Sales Invoice")
DOC_FIELDS = ("amount_eligible_for_commission", "commission_rate", "total_commission", "sales_team")
ITEM_FIELDS = ("grant_commission", "base_net_amount")
ROW_FIELDS = ("sales_person", "allocated_percentage", "allocated_amount", "commission_rate", "incentives")


def _show(doctype, fieldnames):
	meta = frappe.get_meta(doctype, cached=False)
	for fieldname in fieldnames:
		field = meta.get_field(fieldname)
		if not field:
			print(f"   {fieldname:34} MISSING")
			continue
		print(f"   {fieldname:34} {field.fieldtype:12} default={field.default!r} ro={int(field.read_only or 0)} opts={field.options or ''}")


def run():
	for doctype in DOCTYPES:
		print(f"=== {doctype} ===")
		_show(doctype, DOC_FIELDS)
		print(f"--- {doctype} Item ---")
		_show(f"{doctype} Item", ITEM_FIELDS)

	print("=== Sales Team row ===")
	_show("Sales Team", ROW_FIELDS)

	print("=== Company / currency scoping ===")
	print("Companies:", frappe.get_all("Company", pluck="name"))
	print("Retail Sales Team has company field:",
	      bool(frappe.get_meta("Retail Sales Team", cached=False).get_field("company")))

	print("=== Live sample: how many SO items grant commission ===")
	total = frappe.db.count("Sales Order Item")
	granting = frappe.db.count("Sales Order Item", {"grant_commission": 1})
	print(f"Sales Order Item: total={total} grant_commission=1 -> {granting}")

	print("=== Existing Sales Team rows on transactions ===")
	for doctype in DOCTYPES:
		rows = frappe.db.count("Sales Team", {"parenttype": doctype})
		print(f"{doctype}: {rows} sales_team rows")
