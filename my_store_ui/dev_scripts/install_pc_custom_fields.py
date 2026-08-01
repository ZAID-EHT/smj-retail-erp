"""Install Product/Customer quick-entry custom fields.

Two selling prices only (Wholesale + Retail); no Department Price. Idempotent
(standard create_custom_fields). Staging/allowlisted sites only.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

ALLOWED = {"staging.local", "financeqa.local", "freshrelease.local"}

ITEM_FIELDS = [
	{"fieldname": "custom_sku", "label": "SKU", "fieldtype": "Data", "insert_after": "item_code",
	 "read_only": 1, "unique": 1, "in_standard_filter": 1, "in_list_view": 1,
	 "description": "Auto-generated stock-keeping unit."},
	{"fieldname": "custom_image_2", "label": "Image 2", "fieldtype": "Attach Image", "insert_after": "image"},
	{"fieldname": "custom_carton_qty", "label": "Carton Qty", "fieldtype": "Float", "insert_after": "custom_product_colour",
	 "description": "Number of stock units in one carton."},
	{"fieldname": "custom_margin", "label": "Margin %", "fieldtype": "Percent", "insert_after": "custom_additional_cost",
	 "description": "Reference margin for this product."},
	{"fieldname": "custom_stock_location_1", "label": "Stock Location 1", "fieldtype": "Link", "options": "Warehouse", "insert_after": "safety_stock"},
	{"fieldname": "custom_stock_location_2", "label": "Stock Location 2", "fieldtype": "Link", "options": "Warehouse", "insert_after": "custom_stock_location_1"},
	{"fieldname": "custom_stock_location_3", "label": "Stock Location 3", "fieldtype": "Link", "options": "Warehouse", "insert_after": "custom_stock_location_2"},
]

CUSTOMER_FIELDS = [
	{"fieldname": "custom_whatsapp_no", "label": "WhatsApp No", "fieldtype": "Data", "insert_after": "mobile_no"},
	{"fieldname": "custom_accounts_department_no", "label": "Account Dept No", "fieldtype": "Data", "insert_after": "custom_whatsapp_no",
	 "description": "Phone number for the customer's accounts department."},
	{"fieldname": "custom_transport_method", "label": "Transport Method", "fieldtype": "Select",
	 "options": "\nCustomer Pickup\nCompany Delivery\nOwn Vehicle\nCourier\nThird-Party Transport\nOther",
	 "insert_after": "custom_accounts_department_no"},
	{"fieldname": "custom_transport_detail", "label": "Transport Detail", "fieldtype": "Small Text", "insert_after": "custom_transport_method"},
	{"fieldname": "custom_br_no", "label": "BR No", "fieldtype": "Data", "insert_after": "tax_id",
	 "in_standard_filter": 1, "description": "Business Registration Number."},
	{"fieldname": "custom_business_nature", "label": "Business Nature", "fieldtype": "Select",
	 "options": "\nRetailer\nWholesaler\nDepartment Store\nContractor\nHotel\nOffice\nDistributor\nOther",
	 "insert_after": "custom_br_no", "in_standard_filter": 1},
	{"fieldname": "custom_credit_days", "label": "Credit Days", "fieldtype": "Int", "insert_after": "custom_credit_type"},
]

TRANSPORT_OPTIONS = "\nCustomer Pickup\nCompany Delivery\nOwn Vehicle\nCourier\nThird-Party Transport\nOther"

# The dispatch documents carry their own transport details: the customer master
# holds the default, the document records what actually happened.
DELIVERY_NOTE_FIELDS = [
	{"fieldname": "custom_transport_method", "label": "Transport Method", "fieldtype": "Select",
	 "options": TRANSPORT_OPTIONS, "insert_after": "driver_name"},
	{"fieldname": "custom_transport_detail", "label": "Transport Detail", "fieldtype": "Small Text",
	 "insert_after": "custom_transport_method"},
]

# Idempotency key for create-document endpoints. Held in the database, not the
# cache: a lost cache key would otherwise let a retried request dispatch the same
# goods twice. no_copy so amending never inherits a used key.
REQUEST_ID_FIELD = {
	"fieldname": "custom_request_id", "label": "Client Request ID", "fieldtype": "Data",
	"read_only": 1, "no_copy": 1, "print_hide": 1, "search_index": 1,
	"description": "Idempotency key from the originating request.",
}


def run():
	frappe.set_user("Administrator")
	if frappe.local.site not in ALLOWED:
		raise RuntimeError(f"refusing on {frappe.local.site!r}; allowlisted sites only")
	request_id_targets = ["Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
	                      "Purchase Order", "Purchase Receipt", "Purchase Invoice",
	                      "Landed Cost Voucher"]
	fields = {
		"Item": ITEM_FIELDS,
		"Customer": CUSTOMER_FIELDS,
		"Delivery Note": list(DELIVERY_NOTE_FIELDS),
	}
	for doctype in request_id_targets:
		fields.setdefault(doctype, [])
		fields[doctype] = list(fields[doctype]) + [dict(REQUEST_ID_FIELD)]
	create_custom_fields(fields, ignore_validate=True)

	frappe.db.commit()
	meta = frappe.get_meta("Item", cached=False)
	cust = frappe.get_meta("Customer", cached=False)
	note = frappe.get_meta("Delivery Note", cached=False)
	print("Item fields ok:", all(meta.get_field(f["fieldname"]) for f in ITEM_FIELDS))
	print("Customer fields ok:", all(cust.get_field(f["fieldname"]) for f in CUSTOMER_FIELDS))
	print("Delivery Note fields ok:", all(note.get_field(f["fieldname"]) for f in DELIVERY_NOTE_FIELDS))
	print("Request ID fields ok:", all(
		frappe.get_meta(dt, cached=False).get_field("custom_request_id") for dt in request_id_targets))
