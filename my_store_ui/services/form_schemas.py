"""Server-owned, deliberately small form allowlists for the Retail ERP pilots."""

from __future__ import annotations

from copy import deepcopy

import frappe
from frappe import _


def field(fieldname, label, fieldtype, *, required=False, read_only=False, options=None, default=None, section="general"):
	return {
		"fieldname": fieldname, "label": label, "fieldtype": fieldtype, "required": required,
		"read_only": read_only, "options": options, "default": default, "section": section,
	}


FORM_SCHEMAS = {
	"customers": {
		"doctype": "Customer", "title": _("Customer"), "back_route": "/sales/customers", "detail_route": "/sales/customers/{name}",
		"draft_only": False,
		"fields": (
			field("customer_name", _("Customer Name"), "Data", required=True, section="basic"),
			field("customer_type", _("Customer Type"), "Select", options=("Company", "Individual"), default="Company", section="basic"),
			field("customer_group", _("Customer Group"), "Link", required=True, options="Customer Group", section="basic"),
			field("territory", _("Territory"), "Link", required=True, options="Territory", section="basic"),
			field("default_currency", _("Default Currency"), "Link", options="Currency", section="basic"),
			field("tax_id", _("Tax ID"), "Data", section="basic"),
			field("disabled", _("Disabled"), "Check", default=0, section="basic"),
			field("mobile_no", _("Mobile Number"), "Data", section="contact"),
			field("email_id", _("Email Address"), "Data", section="contact"),
			field("website", _("Website"), "Data", section="contact"),
			field("default_price_list", _("Default Price List"), "Link", options="Price List", section="sales"),
			field("payment_terms", _("Payment Terms Template"), "Link", options="Payment Terms Template", section="sales"),
		),
		"sections": (("basic", _("Basic Information")), ("contact", _("Contact Information")), ("sales", _("Sales Information"))),
	},
	"items": {
		"doctype": "Item", "title": _("Product"), "back_route": "/inventory/products", "detail_route": "/inventory/products/{name}",
		"draft_only": False,
		"fields": (
			field("item_code", _("Item Code / SKU"), "Data", required=True, section="basic"),
			field("item_name", _("Item Name"), "Data", required=True, section="basic"),
			field("item_group", _("Item Group"), "Link", required=True, options="Item Group", section="basic"),
			field("brand", _("Brand"), "Link", options="Brand", section="basic"),
			field("description", _("Description"), "Text", section="basic"),
			field("stock_uom", _("Stock UOM"), "Link", required=True, options="UOM", section="product"),
			field("is_stock_item", _("Is Stock Item"), "Check", default=1, section="product"),
			field("disabled", _("Disabled"), "Check", default=0, section="product"),
			field("image", _("Image URL"), "Data", section="product"),
			field("barcodes", _("Barcode"), "Data", section="product"),
			field("country_of_origin", _("Country of Origin"), "Link", options="Country", section="product"),
			field("custom_product_material", _("Product Material"), "Data", section="product"),
			field("custom_product_size", _("Product Size"), "Data", section="product"),
			field("custom_supplier", _("Supplier"), "Link", options="Supplier", section="product"),
			field("custom_sku_prefix", _("SKU Prefix"), "Data", section="product"),
			field("custom_purchase_price", _("Purchase Price"), "Currency", default=0, section="pricing"),
			field("custom_additional_cost", _("Additional Cost"), "Currency", default=0, section="pricing"),
			field("custom_total_cost", _("Total Cost"), "Currency", read_only=True, section="pricing"),
			field("custom_retail_profit_percentage", _("Retail Profit Percentage"), "Percent", default=30, section="pricing"),
			field("custom_wholesale_profit_percentage", _("Wholesale Profit Percentage"), "Percent", default=15, section="pricing"),
			field("custom_retail_price", _("Retail Price"), "Currency", read_only=True, section="pricing"),
			field("custom_wholesale_price", _("Wholesale Price"), "Currency", read_only=True, section="pricing"),
		),
		"sections": (("basic", _("Basic Information")), ("product", _("Product Details")), ("pricing", _("Pricing"))),
	},
	"delivery_notes": {
		"doctype": "Delivery Note", "title": _("Delivery Note"), "back_route": "/sales/delivery-notes", "detail_route": "/sales/delivery-notes/{name}", "draft_only": True, "create_via_mapping_only": True,
		"fields": (
			field("customer", _("Customer"), "Link", required=True, options="Customer", section="delivery"), field("company", _("Company"), "Link", required=True, options="Company", section="delivery"), field("posting_date", _("Posting Date"), "Date", required=True, section="delivery"), field("set_warehouse", _("Default Warehouse"), "Link", options="Warehouse", section="delivery"), field("customer_address", _("Customer Address"), "Link", options="Address", section="delivery"), field("shipping_address_name", _("Shipping Address"), "Link", options="Address", section="delivery"), field("instructions", _("Instructions"), "Text", section="notes"),
		),
		"sections": (("delivery", _("Delivery Information")), ("notes", _("Notes"))),
		"child_tables": {"items": {"doctype": "Delivery Note Item", "title": _("Items"), "min_rows": 1, "fields": (field("name", "Row ID", "Data", read_only=True), field("item_code", _("Item"), "Data", read_only=True), field("item_name", _("Item Name"), "Data", read_only=True), field("description", _("Description"), "Text"), field("qty", _("Quantity"), "Float", required=True), field("uom", _("UOM"), "Link", options="UOM"), field("warehouse", _("Warehouse"), "Link", options="Warehouse"), field("rate", _("Rate"), "Currency", read_only=True), field("amount", _("Amount"), "Currency", read_only=True))}},
	},
	"sales_invoices": {
		"doctype": "Sales Invoice", "title": _("Sales Invoice"), "back_route": "/sales/invoices", "detail_route": "/sales/invoices/{name}", "draft_only": True, "create_via_mapping_only": True,
		"fields": (
			field("customer", _("Customer"), "Link", required=True, options="Customer", section="invoice"), field("company", _("Company"), "Link", required=True, options="Company", section="invoice"), field("posting_date", _("Posting Date"), "Date", required=True, section="invoice"), field("due_date", _("Due Date"), "Date", section="invoice"), field("currency", _("Currency"), "Link", options="Currency", section="invoice"), field("selling_price_list", _("Selling Price List"), "Link", options="Price List", section="invoice"), field("set_warehouse", _("Default Warehouse"), "Link", options="Warehouse", section="invoice"), field("taxes_and_charges", _("Taxes Template"), "Link", options="Sales Taxes and Charges Template", section="invoice"), field("remarks", _("Remarks"), "Text", section="notes"), field("terms", _("Terms"), "Text", section="notes"),
		),
		"sections": (("invoice", _("Invoice Information")), ("notes", _("Terms and Notes"))),
		"child_tables": {"items": {"doctype": "Sales Invoice Item", "title": _("Items"), "min_rows": 1, "fields": (field("name", "Row ID", "Data", read_only=True), field("item_code", _("Item"), "Data", read_only=True), field("item_name", _("Item Name"), "Data", read_only=True), field("description", _("Description"), "Text"), field("qty", _("Quantity"), "Float", required=True), field("uom", _("UOM"), "Link", options="UOM"), field("warehouse", _("Warehouse"), "Link", options="Warehouse"), field("rate", _("Rate"), "Currency", read_only=True), field("amount", _("Amount"), "Currency", read_only=True))}},
	},
	"sales_orders": {
		"doctype": "Sales Order", "title": _("Sales Order"), "back_route": "/sales/orders", "detail_route": "/sales/orders/{name}",
		"draft_only": True,
		"fields": (
			field("customer", _("Customer"), "Link", required=True, options="Customer", section="order"),
			field("company", _("Company"), "Link", required=True, options="Company", section="order"),
			field("transaction_date", _("Transaction Date"), "Date", required=True, section="order"),
			field("delivery_date", _("Delivery Date"), "Date", required=True, section="order"),
			field("currency", _("Currency"), "Link", options="Currency", section="order"),
			field("selling_price_list", _("Selling Price List"), "Link", options="Price List", section="order"),
			field("set_warehouse", _("Default Warehouse"), "Link", options="Warehouse", section="order"),
			field("taxes_and_charges", _("Taxes and Charges Template"), "Link", options="Sales Taxes and Charges Template", section="order"),
			field("order_type", _("Order Type"), "Select", options=("Sales", "Maintenance", "Shopping Cart"), default="Sales", section="order"),
			field("po_no", _("Customer Purchase Order Number"), "Data", section="notes"),
			field("tc_name", _("Terms Template"), "Link", options="Terms and Conditions", section="notes"),
			field("terms", _("Terms and Notes"), "Text", section="notes"),
		),
		"sections": (("order", _("Order Information")), ("notes", _("Terms and Notes"))),
		"child_tables": {
			"items": {
				"doctype": "Sales Order Item", "title": _("Items"), "min_rows": 1,
				"fields": (
					field("item_code", _("Item"), "Link", required=True, options="Item"),
					field("item_name", _("Item Name"), "Data", read_only=True),
					field("description", _("Description"), "Text"),
					field("qty", _("Quantity"), "Float", required=True, default=1),
					field("uom", _("UOM"), "Link", options="UOM"),
					field("conversion_factor", _("Conversion Factor"), "Float", default=1),
					field("warehouse", _("Warehouse"), "Link", options="Warehouse"),
					field("rate", _("Rate"), "Currency", read_only=True),
					field("discount_percentage", _("Discount Percentage"), "Percent", default=0),
					field("amount", _("Amount"), "Currency", read_only=True),
					field("delivery_date", _("Delivery Date"), "Date"),
				),
			},
		},
	},
}


def get_entity_form_schema(entity_key: str) -> dict:
	if entity_key not in FORM_SCHEMAS:
		frappe.throw(_("Unknown Retail ERP entity."), frappe.ValidationError)
	return deepcopy(FORM_SCHEMAS[entity_key])


def validate_form_registry_against_metadata() -> None:
	for schema in FORM_SCHEMAS.values():
		meta = frappe.get_meta(schema["doctype"])
		available = {df.fieldname for df in meta.fields} | {"name"}
		missing = {f["fieldname"] for f in schema["fields"]} - available
		if missing:
			frappe.throw(_("Retail ERP form schema for {0} contains missing fields: {1}").format(schema["doctype"], ", ".join(sorted(missing))))
		for table in schema.get("child_tables", {}).values():
			child_available = {df.fieldname for df in frappe.get_meta(table["doctype"]).fields} | {"name"}
			missing_child = {f["fieldname"] for f in table["fields"]} - child_available
			if missing_child:
				frappe.throw(_("Retail ERP child form schema contains missing fields: {0}").format(", ".join(sorted(missing_child))))
