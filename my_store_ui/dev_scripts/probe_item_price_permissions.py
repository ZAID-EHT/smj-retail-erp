"""Does the Item Price sync break product creation for non-Master-Manager roles?

Also checks every remaining reference to the Wholesale Price List before any
decision about its `buying` flag. Runs inside a savepoint and rolls back.
"""

import frappe

PROBE_USER = "zz-probe-perm@example.com"
ROLE_SETS = (
	("Item Manager",),
	("Stock Manager",),
	("System Manager",),
	("Item Manager", "Sales Master Manager", "Purchase Master Manager"),
)


def run():
	frappe.set_user("Administrator")

	print("=== Custom DocPerm on Item Price ===")
	rows = frappe.get_all(
		"Custom DocPerm", filters={"parent": "Item Price"},
		fields=["role", "permlevel", "read", "write", "create", "delete"],
	)
	print("  ", rows or "(none)")

	print("\n=== DocPerm on Item (who can create products) ===")
	for row in frappe.get_all(
		"DocPerm", filters={"parent": "Item", "permlevel": 0},
		fields=["role", "read", "write", "create"], order_by="role asc",
	):
		print("  ", dict(row))

	print("\n=== Wholesale Price List references across transactions ===")
	for doctype, field in (
		("Pricing Rule", "price_list"),
		("Sales Order", "selling_price_list"),
		("Quotation", "selling_price_list"),
		("Sales Invoice", "selling_price_list"),
		("Delivery Note", "selling_price_list"),
		("Purchase Order", "buying_price_list"),
		("Purchase Invoice", "buying_price_list"),
		("Purchase Receipt", "buying_price_list"),
		("Supplier Quotation", "buying_price_list"),
		("Customer Group", "default_price_list"),
		("Supplier Group", "default_price_list"),
	):
		if not frappe.db.exists("DocType", doctype):
			continue
		meta = frappe.get_meta(doctype)
		if not meta.get_field(field):
			print(f"  {doctype:20}.{field:20} (field absent)")
			continue
		count = frappe.db.count(doctype, {field: "Wholesale Price List"})
		print(f"  {doctype:20}.{field:20} = {count}")

	sp = "probe_perm"
	frappe.db.savepoint(sp)
	try:
		if not frappe.db.exists("User", PROBE_USER):
			frappe.get_doc({
				"doctype": "User", "email": PROBE_USER, "first_name": "ZZ Probe",
				"send_welcome_email": 0, "enabled": 1,
			}).insert(ignore_permissions=True)

		for roles in ROLE_SETS:
			doc = frappe.get_doc("User", PROBE_USER)
			doc.set("roles", [])
			for role in roles:
				doc.append("roles", {"role": role})
			doc.save(ignore_permissions=True)
			frappe.clear_cache(user=PROBE_USER)

			item_create = frappe.has_permission("Item", "create", user=PROBE_USER)
			ip_create = frappe.has_permission("Item Price", "create", user=PROBE_USER)
			ip_write = frappe.has_permission("Item Price", "write", user=PROBE_USER)
			ip_delete = frappe.has_permission("Item Price", "delete", user=PROBE_USER)
			ip_read = frappe.has_permission("Item Price", "read", user=PROBE_USER)
			verdict = "OK" if (not item_create or ip_create) else "*** BREAKS PRODUCT CREATION ***"
			print(
				f"\n  roles={roles}\n    Item.create={item_create} ItemPrice.create={ip_create} "
				f"write={ip_write} delete={ip_delete} read={ip_read}  -> {verdict}"
			)
	finally:
		frappe.db.rollback(save_point=sp)
		frappe.clear_cache(user=PROBE_USER)
		print("\n(rolled back -- nothing persisted)")
