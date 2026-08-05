"""Custom fields behind the price code, the carpet category and the per-customer
commission rate.

Idempotent: `create_custom_fields` upserts, so re-running this patch is safe.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

ITEM_FIELDS = [
	{
		"fieldname": "custom_price_code", "label": "Price Code", "fieldtype": "Link",
		"options": "Retail Price Code", "insert_after": "custom_sku", "read_only": 1,
		"in_standard_filter": 1,
		"description": "The category-wise price code this product's SKU was issued from.",
	},
	{
		"fieldname": "custom_carpet_category", "label": "Carpet Category", "fieldtype": "Data",
		"insert_after": "custom_product_material", "depends_on": "eval:doc.item_group=='Carpets'",
		"in_standard_filter": 1,
		"description": "Carpets only. Chosen from the admin-managed Carpet Category options.",
	},
]

CUSTOMER_FIELDS = [
	{
		"fieldname": "custom_commission_rate", "label": "Commission Rate", "fieldtype": "Percent",
		"insert_after": "custom_sales_team",
		"description": "This customer's own commission rate. Leave blank to use the sales "
		               "manager's team rate.",
	},
]


def execute() -> None:
	create_custom_fields({"Item": ITEM_FIELDS, "Customer": CUSTOMER_FIELDS}, ignore_validate=True)
	# A blank Percent field defaults to 0 in Frappe, which would silently mean "0%
	# commission" for every customer that has never been touched. The field must
	# start genuinely empty so "not set" stays distinguishable from "zero".
	frappe.db.set_value("Custom Field", {"dt": "Customer", "fieldname": "custom_commission_rate"},
	                    "default", None, update_modified=False)
