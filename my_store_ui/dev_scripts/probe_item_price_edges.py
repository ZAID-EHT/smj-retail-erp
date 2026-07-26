"""Probe Item Price edge-case behaviour inside a rolled-back savepoint.

Answers the Phase 7 audit questions: who can read/create Item Price, whether the
purchase cost is already exposed on the Item itself, what ERPNext defaults
valid_from/currency/buying/selling to, and whether duplicate rows are reachable.
Writes nothing -- everything happens inside a savepoint that is rolled back.
"""

import frappe


def run():
	frappe.set_user("Administrator")

	print("=== Item Price DocPerm (permlevel 0) ===")
	for row in frappe.get_all(
		"DocPerm", filters={"parent": "Item Price"},
		fields=["role", "permlevel", "read", "write", "create", "delete"], order_by="role asc",
	):
		print(f"  {dict(row)}")

	print("\n=== Item custom price fields: permlevel + hidden ===")
	meta = frappe.get_meta("Item")
	for fieldname in (
		"custom_purchase_price", "custom_additional_cost", "custom_total_cost",
		"custom_retail_price", "custom_wholesale_price",
	):
		field = meta.get_field(fieldname)
		if field:
			print(f"  {fieldname:38} permlevel={field.permlevel} hidden={field.hidden} type={field.fieldtype}")
		else:
			print(f"  {fieldname:38} MISSING")

	print("\n=== has_permission by role-bearing probe users ===")
	for role in ("Sales User", "Stock User", "Purchase User", "Item Manager"):
		users = frappe.get_all(
			"Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent", limit_page_length=5
		)
		print(f"  role={role!r} example_users={users}")

	print("\n=== Item Price meta defaults ===")
	ip_meta = frappe.get_meta("Item Price")
	for fieldname in ("uom", "valid_from", "valid_upto", "currency", "buying", "selling", "batch_no"):
		field = ip_meta.get_field(fieldname)
		if field:
			print(f"  {fieldname:12} default={field.default!r} reqd={field.reqd} fetch_from={field.fetch_from!r}")

	sp = "probe_edges"
	frappe.db.savepoint(sp)
	try:
		group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		frappe.get_doc({
			"doctype": "Item", "item_code": "ZZ-PROBE-EDGE", "item_name": "probe edge",
			"item_group": group, "stock_uom": "Nos", "is_stock_item": 1,
		}).insert()

		created = frappe.get_doc({
			"doctype": "Item Price", "item_code": "ZZ-PROBE-EDGE",
			"price_list": "Retail Price List", "price_list_rate": 111,
		}).insert()
		print("\n=== Item Price created with NO uom passed ===")
		print("  ", frappe.db.get_value(
			"Item Price", created.name,
			["uom", "valid_from", "valid_upto", "currency", "buying", "selling"], as_dict=True,
		))

		print("\n=== Wholesale (buying=1 AND selling=1) row flags ===")
		wholesale = frappe.get_doc({
			"doctype": "Item Price", "item_code": "ZZ-PROBE-EDGE",
			"price_list": "Wholesale Price List", "price_list_rate": 222,
		}).insert()
		print("  ", frappe.db.get_value(
			"Item Price", wholesale.name, ["uom", "buying", "selling", "currency"], as_dict=True
		))

		print("\n=== Duplicate attempt (same item/list/uom) ===")
		try:
			frappe.get_doc({
				"doctype": "Item Price", "item_code": "ZZ-PROBE-EDGE",
				"price_list": "Retail Price List", "price_list_rate": 999,
			}).insert()
			print("   DUPLICATE ALLOWED -- convergence logic must handle multiple rows")
		except Exception as exc:
			print(f"   blocked by ERPNext: {type(exc).__name__}: {str(exc)[:160]}")

		print("\n=== Duplicate attempt with a DIFFERENT uom ===")
		try:
			other_uom = frappe.get_all(
				"UOM", filters={"name": ["!=", "Nos"]}, pluck="name", limit_page_length=1
			)[0]
			frappe.get_doc({
				"doctype": "Item Price", "item_code": "ZZ-PROBE-EDGE",
				"price_list": "Retail Price List", "price_list_rate": 888, "uom": other_uom,
			}).insert()
			print(f"   allowed for uom={other_uom!r} -- must NOT be overwritten by sync")
		except Exception as exc:
			print(f"   blocked: {type(exc).__name__}: {str(exc)[:160]}")

		print("\n=== Rows now present ===")
		for row in frappe.get_all(
			"Item Price", filters={"item_code": "ZZ-PROBE-EDGE"},
			fields=["price_list", "uom", "price_list_rate", "customer", "supplier", "batch_no"],
		):
			print("  ", dict(row))
	finally:
		frappe.db.rollback(save_point=sp)
		print("\n(rolled back -- nothing persisted)")
