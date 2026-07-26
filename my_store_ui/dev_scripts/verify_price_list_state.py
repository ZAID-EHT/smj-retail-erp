"""Read-only audit of the Price List / Item Price state on a site.

Confirms the claims recorded in SMJ_CORE_WORKFLOW_BLOCKERS.md about the
Wholesale Price List change. Writes nothing.
"""

import frappe


def run():
	frappe.set_user("Administrator")
	print("=== PRICE LISTS ===")
	for row in frappe.get_all(
		"Price List", fields=["name", "enabled", "buying", "selling", "currency"], order_by="name asc"
	):
		count = frappe.db.count("Item Price", {"price_list": row.name})
		print(
			f"  {row.name!r:28} enabled={row.enabled} buying={row.buying} "
			f"selling={row.selling} currency={row.currency} item_prices={count}"
		)

	print("\n=== BUYING SETTINGS ===")
	print("  buying_price_list =", frappe.db.get_single_value("Buying Settings", "buying_price_list"))
	print("  selling default   =", frappe.db.get_single_value("Selling Settings", "selling_price_list"))

	print("\n=== TOTAL ITEM PRICE COUNT ===")
	print("  total =", frappe.db.count("Item Price"))

	print("\n=== CUSTOMERS BY DEFAULT PRICE LIST ===")
	counts = {}
	for row in frappe.get_all("Customer", fields=["default_price_list"]):
		key = row.default_price_list or "(none)"
		counts[key] = counts.get(key, 0) + 1
	for key, value in sorted(counts.items()):
		print(f"  {key!r:28} customers={value}")

	print("\n=== SUPPLIERS BY DEFAULT PRICE LIST ===")
	counts = {}
	for row in frappe.get_all("Supplier", fields=["default_price_list"]):
		key = row.default_price_list or "(none)"
		counts[key] = counts.get(key, 0) + 1
	for key, value in sorted(counts.items()):
		print(f"  {key!r:28} suppliers={value}")

	print("\n=== REFERENCES TO 'Wholesale Price List' ===")
	print("  customers =", frappe.db.count("Customer", {"default_price_list": "Wholesale Price List"}))
	print("  suppliers =", frappe.db.count("Supplier", {"default_price_list": "Wholesale Price List"}))
	print("  item_prices =", frappe.db.count("Item Price", {"price_list": "Wholesale Price List"}))
	print("  customer_groups =", frappe.db.count("Customer Group", {"default_price_list": "Wholesale Price List"}))

	print("\n=== ITEM PRICE UOM SHAPE (first 10) ===")
	for row in frappe.get_all(
		"Item Price", fields=["name", "item_code", "price_list", "uom", "customer", "supplier", "batch_no"],
		limit_page_length=10,
	):
		print(f"  {dict(row)}")
