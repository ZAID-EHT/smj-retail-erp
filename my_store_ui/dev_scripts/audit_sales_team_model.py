"""Audit the current Sales Team data model against ERPNext's standard structures.

Reports what exists today so the integration design is based on the actual schema
rather than assumption.
"""

from __future__ import annotations

import frappe

CUSTOM_DOCTYPES = ("Retail Sales Team", "Retail Sales Team Member")
STANDARD = ("Sales Person", "Sales Team")
TRANSACTIONS = ("Sales Order", "Delivery Note", "Sales Invoice", "Quotation")


def _fields(doctype):
	meta = frappe.get_meta(doctype, cached=False)
	return {f.fieldname: f for f in meta.fields}


def run():
	frappe.set_user("Administrator")

	print("=== CUSTOM MASTER ===")
	for dt in CUSTOM_DOCTYPES:
		if not frappe.db.exists("DocType", dt):
			print(f"{dt}: MISSING")
			continue
		fields = _fields(dt)
		print(f"{dt}: {len(fields)} fields")
		for name, f in fields.items():
			if f.fieldtype in ("Section Break", "Column Break"):
				continue
			print(f"   {name:22} {f.fieldtype:12} reqd={int(f.reqd or 0)} ro={int(f.read_only or 0)} opts={f.options or ''}")
		print(f"   records: {frappe.db.count(dt) if not frappe.get_meta(dt).istable else 'child'}")

	print("\n=== ERPNEXT STANDARD ===")
	for dt in STANDARD:
		fields = _fields(dt)
		print(f"{dt}: {[n for n in fields if fields[n].fieldtype not in ('Section Break','Column Break')]}")
	print("Sales Person records:", frappe.db.count("Sales Person"))

	print("\n=== CUSTOM FIELDS ON CUSTOMER / TRANSACTIONS ===")
	for dt in ("Customer",) + TRANSACTIONS:
		rows = frappe.get_all(
			"Custom Field", filters={"dt": dt, "fieldname": ["like", "%sales_team%"]},
			fields=["fieldname", "fieldtype", "options", "read_only", "label"],
			order_by="idx",
		)
		extra = frappe.get_all(
			"Custom Field", filters={"dt": dt, "fieldname": ["like", "%commission%"]},
			fields=["fieldname", "fieldtype", "options", "read_only", "label"],
		)
		print(f"{dt}:")
		for r in rows + extra:
			print(f"   {r.fieldname:32} {r.fieldtype:12} ro={r.read_only} {r.options or ''}")
		std = _fields(dt)
		if "sales_team" in std:
			print(f"   [standard] sales_team -> {std['sales_team'].options}")

	print("\n=== DATA POSITION ===")
	print("Customers:", frappe.db.count("Customer"))
	print("Customers with custom_sales_team:",
	      frappe.db.count("Customer", {"custom_sales_team": ["is", "set"]}))
	print("Retail Sales Teams:", frappe.db.count("Retail Sales Team"))
	print("Active teams:", frappe.db.count("Retail Sales Team", {"is_active": 1}))
	for dt in TRANSACTIONS:
		meta = frappe.get_meta(dt, cached=False)
		if meta.get_field("custom_sales_team_snapshot"):
			total = frappe.db.count(dt)
			withsnap = frappe.db.count(dt, {"custom_sales_team_snapshot": ["is", "set"]})
			submitted = frappe.db.count(dt, {"docstatus": 1})
			print(f"{dt}: total={total} submitted={submitted} with_snapshot={withsnap}")
		else:
			print(f"{dt}: no snapshot field")
