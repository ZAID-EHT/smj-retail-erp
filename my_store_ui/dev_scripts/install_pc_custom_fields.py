"""Install Product/Customer quick-entry custom fields + Department Price List.

Idempotent (standard create_custom_fields). Staging/allowlisted sites only.
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
	{"fieldname": "custom_department_price", "label": "Department Price", "fieldtype": "Currency", "insert_after": "custom_retail_price",
	 "permlevel": 0},
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


def run():
	frappe.set_user("Administrator")
	if frappe.local.site not in ALLOWED:
		raise RuntimeError(f"refusing on {frappe.local.site!r}; allowlisted sites only")
	create_custom_fields({"Item": ITEM_FIELDS, "Customer": CUSTOMER_FIELDS}, ignore_validate=True)

	# Department Price List (selling only), created once.
	if not frappe.db.exists("Price List", "Department Price List"):
		frappe.get_doc({"doctype": "Price List", "price_list_name": "Department Price List",
		                "enabled": 1, "selling": 1, "buying": 0, "currency": "LKR"}).insert(ignore_permissions=True)

	frappe.db.commit()
	meta = frappe.get_meta("Item", cached=False)
	cust = frappe.get_meta("Customer", cached=False)
	print("Item fields ok:", all(meta.get_field(f["fieldname"]) for f in ITEM_FIELDS))
	print("Customer fields ok:", all(cust.get_field(f["fieldname"]) for f in CUSTOMER_FIELDS))
	print("Department Price List:", frappe.db.get_value("Price List", "Department Price List", ["selling", "buying"], as_dict=True))
