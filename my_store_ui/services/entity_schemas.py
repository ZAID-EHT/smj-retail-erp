from __future__ import annotations

from copy import deepcopy

import frappe
from frappe import _


ENTITY_SCHEMAS = {
	"customers": {
		"doctype": "Customer",
		"title": _("Customers"),
		"description": _("Browse customer identities, groups, territories and contact information."),
		"fields": (
			"name",
			"customer_name",
			"customer_group",
			"territory",
			"customer_type",
			"custom_business_nature",
			"default_price_list",
			"mobile_no",
			"disabled",
			"modified",
		),
		"search_fields": ("name", "customer_name", "mobile_no", "custom_br_no"),
		"filters": {
			"customer_group": {"label": _("Customer Group"), "type": "Link", "options": "Customer Group"},
			"territory": {"label": _("Territory"), "type": "Link", "options": "Territory"},
			"customer_type": {
				"label": _("Customer Type"),
				"type": "Select",
				"values": (("Company", _("Company")), ("Individual", _("Individual"))),
			},
			"disabled": {
				"label": _("Record State"),
				"type": "Select",
				"values": (("0", _("Enabled")), ("1", _("Disabled"))),
			},
		},
		"sortable_fields": ("customer_name", "modified", "name"),
		"default_sort": ("customer_name", "asc"),
		"status_field": "disabled",
		"primary_field": "customer_name",
		"secondary_field": "name",
		"columns": (
			("customer_name", _("Customer"), "text"),
			("name", _("Customer ID"), "code"),
			("customer_group", _("Customer Group"), "text"),
			("territory", _("Territory"), "text"),
			("custom_business_nature", _("Business Nature"), "text"),
			("mobile_no", _("Contact"), "text"),
			("default_price_list", _("Price Category"), "text"),
			("disabled", _("Status"), "enabled_status"),
		),
		"mobile_fields": ("custom_business_nature", "mobile_no", "default_price_list", "disabled"),
		"detail_route": "/sales/customers/{name}",
		"desk_route": "/app/customer/{name}",
	},
	"items": {
		"doctype": "Item",
		"title": _("Products"),
		"description": _("Browse ERPNext Items and their core product attributes."),
		"fields": (
			"name",
			"item_name",
			"item_group",
			"brand",
			"stock_uom",
			"is_stock_item",
			"disabled",
			"modified",
			"image",
			# The SKU and the price code that issued it. Both are columns below, and
			# leaving them out of the query is what made every SKU cell read as a dash.
			"custom_sku",
			"custom_price_code",
		),
		"search_fields": ("name", "item_code", "item_name", "custom_sku"),
		"barcode_search": True,
		"filters": {
			"item_group": {"label": _("Item Group"), "type": "Link", "options": "Item Group"},
			"brand": {"label": _("Brand"), "type": "Link", "options": "Brand"},
			"is_stock_item": {
				"label": _("Stock Type"),
				"type": "Select",
				"values": (("1", _("Stock Item")), ("0", _("Non-stock Item"))),
			},
			"disabled": {
				"label": _("Record State"),
				"type": "Select",
				"values": (("0", _("Enabled")), ("1", _("Disabled"))),
			},
		},
		"sortable_fields": ("item_name", "name", "modified"),
		"default_sort": ("item_name", "asc"),
		"status_field": "disabled",
		"primary_field": "item_name",
		"secondary_field": "name",
		"columns": (
			("image", _("Image"), "image"),
			("name", _("Product ID"), "code"),
			("custom_sku", _("SKU"), "text"),
			("custom_price_code", _("Price Code"), "text"),
			("item_name", _("Product Name"), "text"),
			("item_group", _("Item Group"), "text"),
			("brand", _("Brand"), "text"),
			("stock_uom", _("Stock UOM"), "text"),
			("is_stock_item", _("Stock Item"), "boolean"),
			("disabled", _("Status"), "enabled_status"),
		),
		"mobile_fields": ("custom_sku", "item_group", "brand", "stock_uom", "disabled"),
		"detail_route": "/inventory/products/{name}",
		"desk_route": "/app/item/{name}",
	},
	"delivery_notes": {
		"doctype": "Delivery Note", "title": _("Delivery Notes"), "description": _("Manage delivery documents, billing progress, returns and stock-aware fulfilment."),
		"fields": ("name", "customer", "customer_name", "posting_date", "company", "status", "is_return", "currency", "total_qty", "grand_total", "per_billed", "modified"),
		"search_fields": ("name", "customer", "customer_name"), "filters": {"status": {"label": _("Status"), "type": "Select", "values": (("Draft", _("Draft")), ("To Bill", _("To Bill")), ("Partially Billed", _("Partially Billed")), ("Completed", _("Completed")), ("Return", _("Return")), ("Cancelled", _("Cancelled")))}, "posting_date": {"label": _("Posting Date"), "type": "DateRange"}, "company": {"label": _("Company"), "type": "Link", "options": "Company"}, "is_return": {"label": _("Return Status"), "type": "Select", "values": (("0", _("Regular")), ("1", _("Return")))}, "per_billed": {"label": _("Billing"), "type": "Select", "values": (("0", _("Not Billed")), ("100", _("Fully Billed")))}},
		"sortable_fields": ("modified", "posting_date", "name", "grand_total", "total_qty"), "default_sort": ("modified", "desc"), "status_field": "status", "primary_field": "name", "secondary_field": "customer_name",
		"columns": (("name", _("Delivery Note"), "code"), ("customer_name", _("Customer"), "text"), ("posting_date", _("Posting Date"), "date"), ("status", _("Status"), "status"), ("total_qty", _("Quantity"), "number"), ("grand_total", _("Grand Total"), "currency"), ("per_billed", _("Billed"), "percent")), "mobile_fields": ("customer_name", "posting_date", "grand_total", "status"), "detail_route": "/sales/delivery-notes/{name}", "desk_route": "/app/delivery-note/{name}",
	},
	"sales_invoices": {
		"doctype": "Sales Invoice", "title": _("Sales Invoices"), "description": _("Manage draft and posted invoices using ERPNext accounting controls."),
		"fields": ("name", "customer", "customer_name", "posting_date", "due_date", "company", "status", "is_return", "currency", "grand_total", "paid_amount", "outstanding_amount", "modified"),
		"search_fields": ("name", "customer", "customer_name"), "filters": {"status": {"label": _("Status"), "type": "Select", "values": (("Draft", _("Draft")), ("Unpaid", _("Unpaid")), ("Partly Paid", _("Partly Paid")), ("Paid", _("Paid")), ("Overdue", _("Overdue")), ("Return", _("Return")), ("Credit Note Issued", _("Credit Note Issued")), ("Cancelled", _("Cancelled")))}, "posting_date": {"label": _("Posting Date"), "type": "DateRange"}, "due_date": {"label": _("Due Date"), "type": "DateRange"}, "company": {"label": _("Company"), "type": "Link", "options": "Company"}, "is_return": {"label": _("Return / Credit"), "type": "Select", "values": (("0", _("Invoice")), ("1", _("Return / Credit Note")))}},
		"sortable_fields": ("modified", "posting_date", "name", "grand_total"), "default_sort": ("modified", "desc"), "status_field": "status", "primary_field": "name", "secondary_field": "customer_name",
		"columns": (("name", _("Sales Invoice"), "code"), ("customer_name", _("Customer"), "text"), ("posting_date", _("Posting Date"), "date"), ("due_date", _("Due Date"), "date"), ("status", _("Status"), "status"), ("grand_total", _("Grand Total"), "currency"), ("paid_amount", _("Paid"), "currency"), ("outstanding_amount", _("Outstanding"), "currency")), "mobile_fields": ("customer_name", "posting_date", "grand_total", "status"), "detail_route": "/sales/invoices/{name}", "desk_route": "/app/sales-invoice/{name}",
	},
	"payment_entries": {
		"doctype": "Payment Entry", "title": _("Payment Entries"), "description": _("Review payment records and draft allocations."),
		"fields": ("name", "payment_type", "party_type", "party", "posting_date", "company", "mode_of_payment", "paid_amount", "received_amount", "unallocated_amount", "difference_amount", "docstatus", "modified"),
		"search_fields": ("name", "party"), "filters": {"payment_type": {"label": _("Payment Type"), "type": "Select", "values": (("Receive", _("Receive")), ("Pay", _("Pay")), ("Internal Transfer", _("Internal Transfer")))}, "party_type": {"label": _("Party Type"), "type": "Select", "values": (("Customer", _("Customer")), ("Supplier", _("Supplier")), ("Employee", _("Employee")))}, "posting_date": {"label": _("Posting Date"), "type": "DateRange"}, "company": {"label": _("Company"), "type": "Link", "options": "Company"}, "mode_of_payment": {"label": _("Mode of Payment"), "type": "Link", "options": "Mode of Payment"}, "docstatus": {"label": _("Status"), "type": "Select", "values": (("0", _("Draft")), ("1", _("Submitted")), ("2", _("Cancelled")))}},
		"sortable_fields": ("modified", "posting_date", "name"), "default_sort": ("modified", "desc"), "status_field": "docstatus", "primary_field": "name", "secondary_field": "party",
		"columns": (("name", _("Payment Entry"), "code"), ("party", _("Party"), "text"), ("posting_date", _("Posting Date"), "date"), ("payment_type", _("Type"), "text"), ("paid_amount", _("Paid"), "currency"), ("received_amount", _("Received"), "currency"), ("unallocated_amount", _("Unallocated"), "currency"), ("docstatus", _("Status"), "status")), "mobile_fields": ("party", "posting_date", "paid_amount", "docstatus"), "detail_route": "/finance/payments/{name}", "desk_route": "/app/payment-entry/{name}",
	},
	"sales_orders": {
		"doctype": "Sales Order",
		"title": _("Sales Orders"),
		"description": _("Review sales order status, value, delivery and billing progress."),
		"fields": (
			"name",
			"customer",
			"customer_name",
			"transaction_date",
			"delivery_date",
			"status",
			"currency",
			"grand_total",
			"per_delivered",
			"per_billed",
			"modified",
		),
		"search_fields": ("name", "customer", "customer_name"),
		"filters": {
			"status": {
				"label": _("Status"),
				"type": "Select",
				"values": (
					("Draft", _("Draft")),
					("To Deliver and Bill", _("To Deliver and Bill")),
					("To Deliver", _("To Deliver")),
					("To Bill", _("To Bill")),
					("Completed", _("Completed")),
					("On Hold", _("On Hold")),
					("Closed", _("Closed")),
					("Cancelled", _("Cancelled")),
				),
			},
			"transaction_date": {"label": _("Transaction Date"), "type": "DateRange"},
			"delivery_date": {"label": _("Delivery Date"), "type": "DateRange"},
		},
		"sortable_fields": ("modified", "transaction_date", "delivery_date", "name", "grand_total"),
		"default_sort": ("modified", "desc"),
		"status_field": "status",
		"primary_field": "name",
		"secondary_field": "customer_name",
		"columns": (
			("name", _("Sales Order"), "code"),
			("customer_name", _("Customer"), "text"),
			("transaction_date", _("Order Date"), "date"),
			("delivery_date", _("Delivery Date"), "date"),
			("status", _("Status"), "status"),
			("grand_total", _("Grand Total"), "currency"),
			("per_delivered", _("Delivered"), "percent"),
			("per_billed", _("Billed"), "percent"),
		),
		"mobile_fields": ("customer_name", "transaction_date", "grand_total", "status"),
		"detail_route": "/sales/orders/{name}",
		"desk_route": "/app/sales-order/{name}",
	},
}


DETAIL_SCHEMAS = {
	"customers": {
		"doctype": "Customer",
		"singular_title": _("Customer"),
		"title_field": "customer_name",
		"subtitle_field": "name",
		"status_field": "disabled",
		"status_type": "enabled_status",
		"image_field": "image",
		"back_route": "/sales/customers",
		"desk_route": "/app/customer/{name}",
		"fields": (
			"name", "customer_name", "customer_type", "customer_group", "territory", "mobile_no",
			"email_id", "default_currency", "customer_primary_address", "primary_address",
			"customer_primary_contact", "tax_id", "disabled", "image", "owner", "creation", "modified",
			"modified_by", "credit_limits",
		),
		"summary": (
			("customer_group", _("Customer Group"), "text"),
			("territory", _("Territory"), "text"),
			("mobile_no", _("Mobile"), "text"),
			("email_id", _("Email"), "text"),
			("default_currency", _("Currency"), "text"),
		),
		"sections": (
			{
				"key": "basic",
				"title": _("Basic Information"),
				"fields": (
					("name", _("Customer ID"), "code"),
					("customer_name", _("Customer Name"), "text"),
					("customer_type", _("Customer Type"), "text"),
					("customer_group", _("Customer Group"), "text"),
					("territory", _("Territory"), "text"),
					("tax_id", _("Tax ID"), "text"),
				),
			},
			{
				"key": "contact",
				"title": _("Contact Information"),
				"fields": (
					("mobile_no", _("Mobile Number"), "text"),
					("email_id", _("Email Address"), "text"),
					("customer_primary_contact", _("Primary Contact"), "link"),
				),
			},
			{
				"key": "address",
				"title": _("Address Information"),
				"fields": (
					("customer_primary_address", _("Primary Address"), "link"),
					("primary_address", _("Formatted Address"), "multiline"),
				),
			},
			{
				"key": "sales",
				"title": _("Sales Information"),
				"fields": (("default_currency", _("Default Currency"), "text"),),
			},
		),
		"child_tables": (
			{
				"fieldname": "credit_limits",
				"title": _("Credit Limits"),
				"doctype": "Customer Credit Limit",
				"required_roles_any": ("Accounts User", "Accounts Manager", "Sales Manager", "System Manager"),
				"columns": (
					("company", _("Company"), "text"),
					("credit_limit", _("Credit Limit"), "currency"),
				),
			},
		),
		"related": (
			{"title": _("Quotations"), "doctype": "Quotation", "filters": (("quotation_to", "=", "Customer"), ("party_name", "=", "{name}")), "fields": ("name", "status", "transaction_date", "currency", "grand_total")},
			{"title": _("Sales Orders"), "doctype": "Sales Order", "filters": (("customer", "=", "{name}"),), "fields": ("name", "status", "transaction_date", "currency", "grand_total"), "custom_route": "/sales/orders/{name}"},
			{"title": _("Delivery Notes"), "doctype": "Delivery Note", "filters": (("customer", "=", "{name}"),), "fields": ("name", "status", "posting_date", "currency", "grand_total")},
			{"title": _("Sales Invoices"), "doctype": "Sales Invoice", "filters": (("customer", "=", "{name}"),), "fields": ("name", "status", "posting_date", "currency", "grand_total", "outstanding_amount")},
			{"title": _("Payment Entries"), "doctype": "Payment Entry", "filters": (("party_type", "=", "Customer"), ("party", "=", "{name}")), "fields": ("name", "status", "posting_date", "paid_amount")},
		),
	},
	"items": {
		"doctype": "Item",
		"singular_title": _("Product"),
		"title_field": "item_name",
		"subtitle_field": "name",
		"status_field": "disabled",
		"status_type": "enabled_status",
		"image_field": "image",
		# The product form offers a second image slot. Naming it here is what lets
		# the record header page between the two instead of showing only the first.
		"extra_image_fields": ("custom_image_2",),
		"back_route": "/inventory/products",
		"desk_route": "/app/item/{name}",
		"fields": (
			"name", "item_code", "item_name", "item_group", "brand", "stock_uom", "is_stock_item",
			"disabled", "description", "country_of_origin", "image", "custom_image_2",
			"custom_sku", "custom_price_code", "valuation_rate", "standard_rate",
			"barcodes", "supplier_items", "item_defaults", "owner", "creation", "modified", "modified_by",
		),
		"optional_custom_fields": (
			"custom_product_material", "custom_product_size", "custom_product_colour", "custom_product_color"
		),
		"restricted_fields": {
			"valuation_rate": ("Stock Manager", "Accounts User", "Accounts Manager", "System Manager"),
			"standard_rate": ("Sales Manager", "Stock Manager", "Accounts User", "Accounts Manager", "System Manager"),
		},
		"computed_fields": ("default_warehouse",),
		"summary": (
			("item_group", _("Item Group"), "text"),
			("brand", _("Brand"), "text"),
			("stock_uom", _("Stock UOM"), "text"),
			("default_warehouse", _("Default Warehouse"), "text"),
			("valuation_rate", _("Valuation Rate"), "currency"),
			("standard_rate", _("Standard Rate"), "currency"),
		),
		"sections": (
			{"key": "basic", "title": _("Basic Information"), "fields": (("name", _("Product ID"), "code"), ("custom_sku", _("SKU"), "code"), ("custom_price_code", _("Price Code"), "text"), ("item_name", _("Item Name"), "text"), ("item_group", _("Item Group"), "text"), ("brand", _("Brand"), "text"), ("description", _("Description"), "multiline"))},
			{"key": "product", "title": _("Product Details"), "fields": (("stock_uom", _("Stock UOM"), "text"), ("country_of_origin", _("Country of Origin"), "text"), ("is_stock_item", _("Stock Item"), "boolean"))},
			{"key": "stock", "title": _("Stock Information"), "fields": (("default_warehouse", _("Default Warehouse"), "text"), ("valuation_rate", _("Valuation Rate"), "currency"))},
			{"key": "pricing", "title": _("Pricing Information"), "fields": (("standard_rate", _("Standard Rate"), "currency"),)},
		),
		"child_tables": (
			{"fieldname": "item_defaults", "title": _("Company Defaults"), "doctype": "Item Default", "columns": (("company", _("Company"), "text"), ("default_warehouse", _("Default Warehouse"), "text"), ("default_supplier", _("Default Supplier"), "text"))},
			{"fieldname": "barcodes", "title": _("Barcodes"), "doctype": "Item Barcode", "columns": (("barcode", _("Barcode"), "code"), ("uom", _("UOM"), "text"))},
			{"fieldname": "supplier_items", "title": _("Supplier Information"), "doctype": "Item Supplier", "columns": (("supplier", _("Supplier"), "text"), ("supplier_part_no", _("Supplier Part Number"), "code"))},
		),
		"related": (
			{"title": _("Item Prices"), "doctype": "Item Price", "filters": (("item_code", "=", "{name}"),), "fields": ("name", "price_list", "currency", "price_list_rate", "valid_from")},
			{"title": _("Stock Ledger Entries"), "doctype": "Stock Ledger Entry", "filters": (("item_code", "=", "{name}"),), "fields": ("name", "posting_date", "warehouse", "actual_qty", "qty_after_transaction", "voucher_type", "voucher_no")},
			{"title": _("Purchase Orders"), "doctype": "Purchase Order", "filters": (("Purchase Order Item", "item_code", "=", "{name}"),), "fields": ("name", "status", "transaction_date", "currency", "grand_total")},
			{"title": _("Sales Orders"), "doctype": "Sales Order", "filters": (("Sales Order Item", "item_code", "=", "{name}"),), "fields": ("name", "status", "transaction_date", "currency", "grand_total"), "custom_route": "/sales/orders/{name}"},
			{"title": _("Purchase Invoices"), "doctype": "Purchase Invoice", "filters": (("Purchase Invoice Item", "item_code", "=", "{name}"),), "fields": ("name", "status", "posting_date", "currency", "grand_total")},
			{"title": _("Sales Invoices"), "doctype": "Sales Invoice", "filters": (("Sales Invoice Item", "item_code", "=", "{name}"),), "fields": ("name", "status", "posting_date", "currency", "grand_total")},
		),
	},
	"sales_orders": {
		"doctype": "Sales Order",
		"singular_title": _("Sales Order"),
		"title_field": "name",
		"subtitle_field": "customer_name",
		"status_field": "status",
		"status_type": "status",
		"back_route": "/sales/orders",
		"draft_only": True,
		"desk_route": "/app/sales-order/{name}",
		"fields": (
			"name", "docstatus", "customer", "customer_name", "customer_group", "territory", "tax_id", "transaction_date",
			"delivery_date", "company", "status", "currency", "total", "net_total", "total_taxes_and_charges",
			"grand_total", "rounded_total", "per_delivered", "per_billed", "shipping_address_name",
			"shipping_address", "tc_name", "terms", "items", "taxes", "owner", "creation", "modified", "modified_by",
		),
		"summary": (
			("currency", _("Currency"), "text"),
			("net_total", _("Net Total"), "currency"),
			("total_taxes_and_charges", _("Taxes"), "currency"),
			("grand_total", _("Grand Total"), "currency"),
			("rounded_total", _("Rounded Total"), "currency"),
			("per_delivered", _("Delivered"), "percent"),
			("per_billed", _("Billed"), "percent"),
		),
		"sections": (
			{"key": "customer", "title": _("Customer Information"), "fields": (("customer", _("Customer ID"), "link"), ("customer_name", _("Customer Name"), "text"), ("customer_group", _("Customer Group"), "text"), ("territory", _("Territory"), "text"), ("tax_id", _("Tax ID"), "text"))},
			{"key": "order", "title": _("Order Information"), "fields": (("transaction_date", _("Transaction Date"), "date"), ("delivery_date", _("Delivery Date"), "date"), ("company", _("Company"), "text"), ("status", _("Status"), "status"))},
			{"key": "delivery", "title": _("Delivery Information"), "fields": (("shipping_address_name", _("Shipping Address"), "link"), ("shipping_address", _("Address Details"), "multiline"), ("per_delivered", _("Delivered"), "percent"))},
			{"key": "billing", "title": _("Billing Information"), "fields": (("per_billed", _("Billed"), "percent"), ("grand_total", _("Grand Total"), "currency"), ("rounded_total", _("Rounded Total"), "currency"))},
			{"key": "terms", "title": _("Terms and Notes"), "fields": (("tc_name", _("Terms Template"), "link"), ("terms", _("Terms and Conditions"), "multiline"))},
		),
		"child_tables": (
			{
				"fieldname": "items", "title": _("Items"), "doctype": "Sales Order Item",
				"columns": (("item_code", _("Item Code"), "code"), ("item_name", _("Item Name"), "text"), ("description", _("Description"), "multiline"), ("qty", _("Quantity"), "number"), ("uom", _("UOM"), "text"), ("warehouse", _("Warehouse"), "text"), ("rate", _("Rate"), "currency"), ("discount_percentage", _("Discount"), "percent"), ("amount", _("Amount"), "currency"), ("delivered_qty", _("Delivered Qty"), "number"), ("billed_amt", _("Billed Amount"), "currency")),
			},
			{
				"fieldname": "taxes", "title": _("Taxes and Charges"), "doctype": "Sales Taxes and Charges",
				"columns": (("charge_type", _("Charge Type"), "text"), ("account_head", _("Account"), "text"), ("description", _("Description"), "multiline"), ("rate", _("Rate"), "percent"), ("tax_amount", _("Tax Amount"), "currency"), ("total", _("Total"), "currency")),
			},
		),
		"related": (
			{"title": _("Delivery Notes"), "doctype": "Delivery Note", "filters": (("Delivery Note Item", "against_sales_order", "=", "{name}"),), "fields": ("name", "status", "posting_date", "currency", "grand_total")},
			{"title": _("Sales Invoices"), "doctype": "Sales Invoice", "filters": (("Sales Invoice Item", "sales_order", "=", "{name}"),), "fields": ("name", "status", "posting_date", "currency", "grand_total", "outstanding_amount")},
			{"title": _("Payment Entries"), "doctype": "Payment Entry", "filters": (("Payment Entry Reference", "reference_doctype", "=", "Sales Order"), ("Payment Entry Reference", "reference_name", "=", "{name}")), "fields": ("name", "status", "posting_date", "paid_amount")},
			{"title": _("Pick Lists"), "doctype": "Pick List", "filters": (("Pick List Item", "sales_order", "=", "{name}"),), "fields": ("name", "status", "purpose", "modified")},
		),
	},
}


def get_entity_schema(entity_key: str) -> dict:
	if entity_key not in ENTITY_SCHEMAS:
		frappe.throw(_("Unknown Retail ERP entity."), frappe.ValidationError)
	return deepcopy(ENTITY_SCHEMAS[entity_key])


def get_entity_detail_schema(entity_key: str) -> dict:
	if entity_key not in DETAIL_SCHEMAS:
		frappe.throw(_("Unknown Retail ERP entity."), frappe.ValidationError)
	return deepcopy(DETAIL_SCHEMAS[entity_key])


def validate_registry_against_metadata() -> None:
	"""Fail fast during tests if an approved field disappears after an upgrade."""
	standard_fields = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx"}
	for schema in ENTITY_SCHEMAS.values():
		meta = frappe.get_meta(schema["doctype"])
		valid_fields = standard_fields | {field.fieldname for field in meta.fields}
		referenced_fields = (
			set(schema["fields"])
			| set(schema["search_fields"])
			| set(schema["filters"])
			| set(schema["sortable_fields"])
			| {schema["status_field"], schema["primary_field"], schema["secondary_field"]}
			| {column[0] for column in schema["columns"]}
			| set(schema["mobile_fields"])
		)
		missing = referenced_fields - valid_fields
		if missing:
			frappe.throw(
				_("Retail ERP schema for {0} contains missing fields: {1}").format(
					schema["doctype"], ", ".join(sorted(missing))
				)
			)

	for schema in DETAIL_SCHEMAS.values():
		meta = frappe.get_meta(schema["doctype"])
		valid_fields = standard_fields | {field.fieldname for field in meta.fields} | set(schema.get("computed_fields", ()))
		referenced_fields = (
			set(schema["fields"])
			| {schema["title_field"], schema["subtitle_field"], schema["status_field"]}
			| {field[0] for field in schema["summary"]}
			| {field[0] for section in schema["sections"] for field in section["fields"]}
		)
		missing = referenced_fields - valid_fields
		if missing:
			frappe.throw(
				_("Retail ERP detail schema for {0} contains missing fields: {1}").format(
					schema["doctype"], ", ".join(sorted(missing))
				)
			)
		for child in schema["child_tables"]:
			child_meta = frappe.get_meta(child["doctype"])
			valid_child_fields = standard_fields | {field.fieldname for field in child_meta.fields}
			missing_child = {column[0] for column in child["columns"]} - valid_child_fields
			if missing_child:
				frappe.throw(
					_("Retail ERP child schema for {0} contains missing fields: {1}").format(
						child["doctype"], ", ".join(sorted(missing_child))
					)
				)
		for relation in schema["related"]:
			related_meta = frappe.get_meta(relation["doctype"])
			valid_related_fields = standard_fields | {field.fieldname for field in related_meta.fields}
			missing_related = set(relation["fields"]) - valid_related_fields
			if missing_related:
				frappe.throw(
					_("Retail ERP related schema for {0} contains missing fields: {1}").format(
						relation["doctype"], ", ".join(sorted(missing_related))
					)
				)
			for relation_filter in relation["filters"]:
				filter_meta = related_meta if len(relation_filter) == 3 else frappe.get_meta(relation_filter[0])
				filter_field = relation_filter[0] if len(relation_filter) == 3 else relation_filter[1]
				if filter_field not in {field.fieldname for field in filter_meta.fields} | standard_fields:
					frappe.throw(
						_("Retail ERP related filter for {0} contains missing field: {1}").format(
							filter_meta.name, filter_field
						)
					)
