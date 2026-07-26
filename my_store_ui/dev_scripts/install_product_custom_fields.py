"""Install the Colour and Published Item custom fields on staging (idempotent).

Uses Frappe's standard create_custom_fields helper, not raw SQL. Safe to re-run.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def run():
	frappe.set_user("Administrator")
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing on {frappe.local.site!r}; staging only")
	create_custom_fields({
		"Item": [
			{"fieldname": "custom_product_colour", "label": "Product Colour", "fieldtype": "Data", "insert_after": "custom_product_size"},
			{"fieldname": "custom_published", "label": "Published (visible in catalogue)", "fieldtype": "Check", "insert_after": "custom_product_colour",
			 "description": "Internal catalogue visibility flag; this site has no public storefront."},
		]
	}, ignore_validate=True)
	frappe.db.commit()
	meta = frappe.get_meta("Item", cached=False)
	print("custom_product_colour:", bool(meta.get_field("custom_product_colour")))
	print("custom_published:", bool(meta.get_field("custom_published")))
