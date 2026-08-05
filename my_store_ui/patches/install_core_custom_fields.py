"""Install every custom field the Retail ERP code reads and writes.

Why this patch exists
---------------------
These fields used to be created by `my_store_ui/dev_scripts/install_pc_custom_fields.py`
and `install_product_custom_fields.py`. Both refuse to run anywhere outside a
hard-coded staging allowlist, and neither is registered in `patches.txt`, so on a
real site they never ran at all. The `fixtures` hook lists the same fields, but the
exported `fixtures/custom_field.json` only ever contained the four
`custom_wholesale_transaction_id` records, so migrating installed nothing either.

The result on a live site was that `Customer.custom_whatsapp_no`,
`Customer.custom_br_no`, `Item.custom_sku` and roughly thirty others simply did not
exist, while the Customer and Product forms went on reading and writing them. This
patch is the missing half: the same definitions, no allowlist, run on every site.

Ordering matters
----------------
Several fields anchor themselves after another custom field -- `custom_credit_days`
sits after `custom_credit_type`, `custom_carton_qty` after `custom_product_colour`.
The groups below are applied in dependency order so each anchor exists before
anything asks to be placed after it. That ordering is also why
`install_sales_team_fields` produced nothing when it ran first: its section break
anchored to a `custom_credit_days` that did not exist yet.

Idempotent: `create_custom_fields` upserts, so re-running is safe and is the
intended way to repair a site that is missing some of these.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

TRANSPORT_OPTIONS = "\nCustomer Pickup\nCompany Delivery\nOwn Vehicle\nCourier\nThird-Party Transport\nOther"

# Documents that accept a client-supplied idempotency key. Held in the database
# rather than the cache: a lost cache key would let a retried request dispatch the
# same goods twice. `no_copy` so amending never inherits a used key.
REQUEST_ID_TARGETS = (
	"Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
	"Purchase Order", "Purchase Receipt", "Purchase Invoice", "Landed Cost Voucher",
)
REQUEST_ID_FIELD = {
	"fieldname": "custom_request_id", "label": "Client Request ID", "fieldtype": "Data",
	"read_only": 1, "no_copy": 1, "print_hide": 1, "search_index": 1,
	"description": "Idempotency key from the originating request.",
}

# --- Item -------------------------------------------------------------------
# Attributes first: the pricing and packing fields below anchor to them.
ITEM_ATTRIBUTES = [
	{"fieldname": "custom_sku", "label": "SKU", "fieldtype": "Data", "insert_after": "item_code",
	 "read_only": 1, "unique": 1, "in_standard_filter": 1, "in_list_view": 1,
	 "description": "Auto-generated stock-keeping unit."},
	{"fieldname": "custom_image_2", "label": "Image 2", "fieldtype": "Attach Image",
	 "insert_after": "image"},
	{"fieldname": "custom_product_material", "label": "Product Material", "fieldtype": "Data",
	 "insert_after": "item_group", "in_standard_filter": 1,
	 "description": "Chosen from the admin-managed Product Material options."},
	{"fieldname": "custom_product_size", "label": "Product Size", "fieldtype": "Data",
	 "insert_after": "custom_product_material", "in_standard_filter": 1,
	 "description": "Chosen from the admin-managed Product Size options."},
	{"fieldname": "custom_product_colour", "label": "Product Colour", "fieldtype": "Data",
	 "insert_after": "custom_product_size"},
	{"fieldname": "custom_published", "label": "Published (visible in catalogue)",
	 "fieldtype": "Check", "insert_after": "custom_product_colour",
	 "description": "Internal catalogue visibility flag; this site has no public storefront."},
	{"fieldname": "custom_carton_qty", "label": "Carton Qty", "fieldtype": "Float",
	 "insert_after": "custom_published",
	 "description": "Number of stock units in one carton."},
	{"fieldname": "custom_supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier",
	 "insert_after": "custom_carton_qty"},
	{"fieldname": "custom_sku_prefix", "label": "SKU Prefix", "fieldtype": "Data",
	 "insert_after": "custom_supplier"},
]

ITEM_PRICING = [
	{"fieldname": "custom_purchase_price", "label": "Purchase Price", "fieldtype": "Currency",
	 "insert_after": "custom_sku_prefix", "default": "0"},
	{"fieldname": "custom_additional_cost", "label": "Additional Cost", "fieldtype": "Currency",
	 "insert_after": "custom_purchase_price", "default": "0"},
	{"fieldname": "custom_total_cost", "label": "Total Cost", "fieldtype": "Currency",
	 "insert_after": "custom_additional_cost", "read_only": 1},
	{"fieldname": "custom_margin", "label": "Margin %", "fieldtype": "Percent",
	 "insert_after": "custom_total_cost",
	 "description": "Reference margin for this product."},
	{"fieldname": "custom_retail_profit_percentage", "label": "Retail Profit Percentage",
	 "fieldtype": "Percent", "insert_after": "custom_margin", "default": "30"},
	{"fieldname": "custom_wholesale_profit_percentage", "label": "Wholesale Profit Percentage",
	 "fieldtype": "Percent", "insert_after": "custom_retail_profit_percentage", "default": "15"},
	{"fieldname": "custom_retail_price", "label": "Retail Price", "fieldtype": "Currency",
	 "insert_after": "custom_wholesale_profit_percentage", "read_only": 1},
	{"fieldname": "custom_wholesale_price", "label": "Wholesale Price", "fieldtype": "Currency",
	 "insert_after": "custom_retail_price", "read_only": 1},
]

ITEM_STOCK = [
	{"fieldname": "custom_stock_location_1", "label": "Stock Location 1", "fieldtype": "Link",
	 "options": "Warehouse", "insert_after": "safety_stock"},
	{"fieldname": "custom_stock_location_2", "label": "Stock Location 2", "fieldtype": "Link",
	 "options": "Warehouse", "insert_after": "custom_stock_location_1"},
	{"fieldname": "custom_stock_location_3", "label": "Stock Location 3", "fieldtype": "Link",
	 "options": "Warehouse", "insert_after": "custom_stock_location_2"},
]

# --- Customer ---------------------------------------------------------------
# Contact first, then the credit classification, because the sales-assignment
# section installed by `install_sales_team_fields` anchors after custom_credit_days.
CUSTOMER_CONTACT = [
	{"fieldname": "custom_whatsapp_no", "label": "WhatsApp No", "fieldtype": "Data",
	 "insert_after": "mobile_no",
	 "description": "Unique per customer: it is the channel the business messages them on."},
	{"fieldname": "custom_accounts_department_no", "label": "Account Dept No", "fieldtype": "Data",
	 "insert_after": "custom_whatsapp_no",
	 "description": "Phone number for the customer's accounts department."},
	{"fieldname": "custom_transport_method", "label": "Transport Method", "fieldtype": "Data",
	 "insert_after": "custom_accounts_department_no",
	 "description": "Chosen from the admin-managed Transport Method options."},
	{"fieldname": "custom_transport_detail", "label": "Transport Detail", "fieldtype": "Small Text",
	 "insert_after": "custom_transport_method"},
	{"fieldname": "custom_br_no", "label": "BR No", "fieldtype": "Data", "insert_after": "tax_id",
	 "in_standard_filter": 1, "description": "Business Registration Number."},
	{"fieldname": "custom_business_nature", "label": "Business Nature", "fieldtype": "Data",
	 "insert_after": "custom_br_no", "in_standard_filter": 1,
	 "description": "Chosen from the admin-managed Business Nature options."},
]

CUSTOMER_CREDIT = [
	{"fieldname": "custom_credit_type", "label": "Credit Type", "fieldtype": "Select",
	 "options": "\nCredit Customer\nNon-Credit Customer",
	 "insert_after": "custom_business_nature", "in_standard_filter": 1,
	 "description": "Non-Credit customers pay before dispatch."},
	{"fieldname": "custom_credit_days", "label": "Credit Days", "fieldtype": "Int",
	 "insert_after": "custom_credit_type"},
]

# --- Delivery Note ----------------------------------------------------------
# The customer master holds the default; the dispatch document records what
# actually happened.
DELIVERY_NOTE_FIELDS = [
	{"fieldname": "custom_transport_method", "label": "Transport Method", "fieldtype": "Select",
	 "options": TRANSPORT_OPTIONS, "insert_after": "driver_name"},
	{"fieldname": "custom_transport_detail", "label": "Transport Detail", "fieldtype": "Small Text",
	 "insert_after": "custom_transport_method"},
]


def _apply(fields: dict) -> None:
	"""Create one group, skipping DocTypes this site does not have."""
	present = {dt: rows for dt, rows in fields.items() if frappe.db.exists("DocType", dt)}
	if present:
		create_custom_fields(present, ignore_validate=True)


def execute() -> None:
	# Applied group by group so a field can safely anchor after one created in an
	# earlier group. create_custom_fields resolves insert_after against what already
	# exists, so a single combined call would place several of these arbitrarily.
	_apply({"Item": ITEM_ATTRIBUTES})
	_apply({"Item": ITEM_PRICING})
	_apply({"Item": ITEM_STOCK})
	_apply({"Customer": CUSTOMER_CONTACT})
	_apply({"Customer": CUSTOMER_CREDIT})
	_apply({"Delivery Note": DELIVERY_NOTE_FIELDS})
	_apply({dt: [dict(REQUEST_ID_FIELD)] for dt in REQUEST_ID_TARGETS})
	frappe.clear_cache()
