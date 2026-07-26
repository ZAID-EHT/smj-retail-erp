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
			field("custom_product_colour", _("Product Colour"), "Data", section="product"),
			field("custom_supplier", _("Supplier"), "Link", options="Supplier", section="product"),
			field("custom_sku_prefix", _("SKU Prefix"), "Data", section="product"),
			field("custom_published", _("Published in catalogue"), "Check", default=0, section="product"),
			# Standard Item fields, previously missing from the curated form.
			field("purchase_uom", _("Purchase UOM"), "Link", options="UOM", section="stock"),
			field("sales_uom", _("Selling UOM"), "Link", options="UOM", section="stock"),
			field("safety_stock", _("Safety Stock"), "Float", default=0, section="stock"),
			# Flat inputs backed by child tables (item_defaults / reorder_levels),
			# handled explicitly in form_api._apply_item_child_defaults.
			field("default_warehouse", _("Default Warehouse"), "Link", options="Warehouse", section="stock"),
			field("reorder_level", _("Reorder Level"), "Float", default=0, section="stock"),
			field("reorder_qty", _("Reorder Quantity"), "Float", default=0, section="stock"),
			field("custom_purchase_price", _("Purchase Price"), "Currency", default=0, section="pricing"),
			field("custom_additional_cost", _("Additional Cost"), "Currency", default=0, section="pricing"),
			field("custom_total_cost", _("Total Cost"), "Currency", read_only=True, section="pricing"),
			field("custom_retail_profit_percentage", _("Retail Profit Percentage"), "Percent", default=30, section="pricing"),
			field("custom_wholesale_profit_percentage", _("Wholesale Profit Percentage"), "Percent", default=15, section="pricing"),
			field("custom_retail_price", _("Retail Price"), "Currency", read_only=True, section="pricing"),
			field("custom_wholesale_price", _("Wholesale Price"), "Currency", read_only=True, section="pricing"),
		),
		"sections": (("basic", _("Basic Information")), ("product", _("Product Details")), ("stock", _("Stock & UOM")), ("pricing", _("Pricing"))),
	},
	"delivery_notes": {
		"doctype": "Delivery Note", "title": _("Delivery Note"), "back_route": "/sales/delivery-notes", "detail_route": "/sales/delivery-notes/{name}", "draft_only": True,
		"fields": (field("customer", _("Customer"), "Link", required=True, options="Customer", section="delivery"), field("company", _("Company"), "Link", required=True, options="Company", section="delivery"), field("posting_date", _("Posting Date"), "Date", required=True, section="delivery"), field("posting_time", _("Posting Time"), "Time", section="delivery"), field("currency", _("Currency"), "Link", options="Currency", section="delivery"), field("set_warehouse", _("Default Warehouse"), "Link", options="Warehouse", section="delivery"), field("is_return", _("Is Return"), "Check", section="delivery"), field("return_against", _("Return Against"), "Link", options="Delivery Note", section="delivery"), field("customer_address", _("Customer Address"), "Link", options="Address", section="delivery"), field("shipping_address_name", _("Shipping Address"), "Link", options="Address", section="delivery"), field("contact_person", _("Contact"), "Link", options="Contact", section="delivery"), field("transporter", _("Transporter"), "Link", options="Supplier", section="shipping"), field("driver", _("Driver"), "Link", options="Driver", section="shipping"), field("vehicle_no", _("Vehicle Number"), "Data", section="shipping"), field("taxes_and_charges", _("Taxes Template"), "Link", options="Sales Taxes and Charges Template", section="notes"), field("instructions", _("Instructions"), "Text", section="notes"), field("terms", _("Terms"), "Text", section="notes")),
		"sections": (("delivery", _("Delivery Information")), ("shipping", _("Shipping Information")), ("notes", _("Terms and Notes"))),
		"child_tables": {"items": {"doctype": "Delivery Note Item", "title": _("Items"), "min_rows": 1, "fields": (field("name", "Row ID", "Data", read_only=True), field("item_code", _("Item"), "Link", required=True, options="Item"), field("item_name", _("Item Name"), "Data", read_only=True), field("description", _("Description"), "Text"), field("qty", _("Quantity"), "Float", required=True), field("uom", _("UOM"), "Link", options="UOM"), field("conversion_factor", _("Conversion Factor"), "Float"), field("warehouse", _("Warehouse"), "Link", options="Warehouse"), field("against_sales_order", _("Sales Order"), "Link", options="Sales Order"), field("so_detail", _("Sales Order Item"), "Data", read_only=True), field("rate", _("Rate"), "Currency"), field("discount_percentage", _("Discount %"), "Percent"), field("amount", _("Amount"), "Currency", read_only=True), field("serial_and_batch_bundle", _("Serial and Batch Bundle"), "Link", options="Serial and Batch Bundle"), field("batch_no", _("Batch Number"), "Link", options="Batch"), field("serial_no", _("Serial Number"), "Data"), field("cost_center", _("Cost Center"), "Link", options="Cost Center"))}},
	},
	"sales_invoices": {
		"doctype": "Sales Invoice", "title": _("Sales Invoice"), "back_route": "/sales/invoices", "detail_route": "/sales/invoices/{name}", "draft_only": True,
		"fields": (field("customer", _("Customer"), "Link", required=True, options="Customer", section="invoice"), field("company", _("Company"), "Link", required=True, options="Company", section="invoice"), field("posting_date", _("Posting Date"), "Date", required=True, section="invoice"), field("due_date", _("Due Date"), "Date", section="invoice"), field("currency", _("Currency"), "Link", options="Currency", section="invoice"), field("selling_price_list", _("Selling Price List"), "Link", options="Price List", section="invoice"), field("update_stock", _("Update Stock"), "Check", section="invoice"), field("set_warehouse", _("Default Warehouse"), "Link", options="Warehouse", section="invoice"), field("payment_terms_template", _("Payment Terms Template"), "Link", options="Payment Terms Template", section="invoice"), field("taxes_and_charges", _("Taxes Template"), "Link", options="Sales Taxes and Charges Template", section="invoice"), field("debit_to", _("Debit To"), "Link", options="Account", section="accounting"), field("cost_center", _("Cost Center"), "Link", options="Cost Center", section="accounting"), field("project", _("Project"), "Link", options="Project", section="accounting"), field("is_return", _("Is Return"), "Check", section="invoice"), field("return_against", _("Return Against"), "Link", options="Sales Invoice", section="invoice"), field("remarks", _("Remarks"), "Text", section="notes"), field("terms", _("Terms"), "Text", section="notes")),
		"sections": (("invoice", _("Invoice Information")), ("accounting", _("Accounting Information")), ("notes", _("Terms and Notes"))),
		"child_tables": {"items": {"doctype": "Sales Invoice Item", "title": _("Items"), "min_rows": 1, "fields": (field("name", "Row ID", "Data", read_only=True), field("item_code", _("Item"), "Link", required=True, options="Item"), field("item_name", _("Item Name"), "Data", read_only=True), field("description", _("Description"), "Text"), field("qty", _("Quantity"), "Float", required=True), field("uom", _("UOM"), "Link", options="UOM"), field("conversion_factor", _("Conversion Factor"), "Float"), field("warehouse", _("Warehouse"), "Link", options="Warehouse"), field("sales_order", _("Sales Order"), "Link", options="Sales Order"), field("so_detail", _("Sales Order Item"), "Data", read_only=True), field("delivery_note", _("Delivery Note"), "Link", options="Delivery Note"), field("dn_detail", _("Delivery Note Item"), "Data", read_only=True), field("rate", _("Rate"), "Currency"), field("discount_percentage", _("Discount %"), "Percent"), field("amount", _("Amount"), "Currency", read_only=True), field("income_account", _("Income Account"), "Link", options="Account"), field("cost_center", _("Cost Center"), "Link", options="Cost Center"), field("project", _("Project"), "Link", options="Project"))}},
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
	"payment_entries": {
		"doctype": "Payment Entry", "title": _("Payment Entry"), "back_route": "/finance/payments", "detail_route": "/finance/payments/{name}", "draft_only": True,
		"fields": (field("payment_type", _("Payment Type"), "Select", options=("Receive", "Pay", "Internal Transfer"), required=True, section="payment"), field("posting_date", _("Posting Date"), "Date", required=True, section="payment"), field("company", _("Company"), "Link", options="Company", required=True, section="payment"), field("mode_of_payment", _("Mode of Payment"), "Link", options="Mode of Payment", section="payment"), field("party_type", _("Party Type"), "Data", section="payment"), field("party", _("Party"), "Data", section="payment"), field("party_name", _("Party Name"), "Data", read_only=True, section="payment"), field("paid_from", _("Paid From"), "Link", options="Account", section="accounts"), field("paid_to", _("Paid To"), "Link", options="Account", section="accounts"), field("paid_from_account_currency", _("Paid From Currency"), "Link", options="Currency", read_only=True, section="accounts"), field("paid_to_account_currency", _("Paid To Currency"), "Link", options="Currency", read_only=True, section="accounts"), field("paid_amount", _("Paid Amount"), "Currency", required=True, section="payment"), field("received_amount", _("Received Amount"), "Currency", required=True, section="payment"), field("source_exchange_rate", _("Source Exchange Rate"), "Float", section="payment"), field("target_exchange_rate", _("Target Exchange Rate"), "Float", section="payment"), field("reference_no", _("Reference Number"), "Data", section="notes"), field("reference_date", _("Reference Date"), "Date", section="notes"), field("cost_center", _("Cost Center"), "Link", options="Cost Center", section="accounts"), field("project", _("Project"), "Link", options="Project", section="accounts"), field("remarks", _("Remarks"), "Text", section="notes"), field("unallocated_amount", _("Unallocated Amount"), "Currency", read_only=True, section="payment"), field("difference_amount", _("Difference Amount"), "Currency", read_only=True, section="payment")),
		"sections": (("payment", _("Payment Information")), ("accounts", _("Accounts")), ("notes", _("Notes"))),
		"child_tables": {"references": {"doctype": "Payment Entry Reference", "title": _("References"), "min_rows": 0, "fields": (field("name", "Row ID", "Data", read_only=True), field("reference_doctype", _("Reference Type"), "Data", read_only=True), field("reference_name", _("Reference"), "Data", read_only=True), field("due_date", _("Due Date"), "Date", read_only=True), field("total_amount", _("Total Amount"), "Currency", read_only=True), field("outstanding_amount", _("Outstanding"), "Currency", read_only=True), field("allocated_amount", _("Allocated Amount"), "Currency"), field("exchange_rate", _("Exchange Rate"), "Float", read_only=True), field("payment_term", _("Payment Term"), "Link", options="Payment Term", read_only=True))}, "deductions": {"doctype": "Payment Entry Deduction", "title": _("Deductions"), "min_rows": 0, "fields": (field("name", "Row ID", "Data", read_only=True), field("account", _("Account"), "Link", options="Account"), field("cost_center", _("Cost Center"), "Link", options="Cost Center"), field("amount", _("Amount"), "Currency"), field("description", _("Description"), "Text"))}},
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
