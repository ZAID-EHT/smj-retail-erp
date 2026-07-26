"""Make `Wholesale Price List` selling-only, re-verifying safety before writing.

The list carried `buying=1` as well as `selling=1`. ERPNext stamps those flags onto
every Item Price row, so a wholesale (marked-up) price was selectable as a purchase
rate -- retail/wholesale/purchase prices must stay separate.

Refuses to change anything if the list is referenced anywhere, so it is safe to
re-run. Idempotent: a no-op once the list is already selling-only.
"""

import frappe

PRICE_LIST = "Wholesale Price List"


def _references() -> dict:
	counts = {
		"item_prices": frappe.db.count("Item Price", {"price_list": PRICE_LIST}),
		"customers": frappe.db.count("Customer", {"default_price_list": PRICE_LIST}),
		"suppliers": frappe.db.count("Supplier", {"default_price_list": PRICE_LIST}),
		"customer_groups": frappe.db.count("Customer Group", {"default_price_list": PRICE_LIST}),
	}
	for doctype, field in (
		("Purchase Order", "buying_price_list"),
		("Purchase Invoice", "buying_price_list"),
		("Purchase Receipt", "buying_price_list"),
		("Supplier Quotation", "buying_price_list"),
	):
		counts[f"{doctype}.{field}"] = frappe.db.count(doctype, {field: PRICE_LIST})
	return counts


def run():
	frappe.set_user("Administrator")
	if not frappe.db.exists("Price List", PRICE_LIST):
		print(f"{PRICE_LIST!r} does not exist -- nothing to do.")
		return

	before = frappe.db.get_value("Price List", PRICE_LIST, ["buying", "selling", "enabled"], as_dict=True)
	print(f"before: {dict(before)}")
	if not before.buying:
		print("already selling-only -- no change made.")
		return

	counts = _references()
	print("references:", counts)
	blocking = {key: value for key, value in counts.items() if value}
	# A buying reference would break if the flag were removed, so never force it.
	if blocking:
		print(f"REFUSING to change: {PRICE_LIST!r} is referenced -> {blocking}")
		return

	doc = frappe.get_doc("Price List", PRICE_LIST)
	doc.buying = 0
	doc.save()
	frappe.db.commit()
	after = frappe.db.get_value("Price List", PRICE_LIST, ["buying", "selling", "enabled"], as_dict=True)
	print(f"after: {dict(after)}")
