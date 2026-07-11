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
			"mobile_no",
			"disabled",
			"modified",
		),
		"search_fields": ("name", "customer_name", "mobile_no"),
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
			("customer_type", _("Type"), "text"),
			("mobile_no", _("Mobile"), "text"),
			("disabled", _("Status"), "enabled_status"),
			("modified", _("Modified"), "datetime"),
		),
		"mobile_fields": ("customer_group", "territory", "mobile_no", "disabled"),
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
		),
		"search_fields": ("name", "item_code", "item_name"),
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
			("name", _("Item Code"), "code"),
			("item_name", _("Item Name"), "text"),
			("item_group", _("Item Group"), "text"),
			("brand", _("Brand"), "text"),
			("stock_uom", _("Stock UOM"), "text"),
			("is_stock_item", _("Stock Item"), "boolean"),
			("disabled", _("Status"), "enabled_status"),
		),
		"mobile_fields": ("item_group", "brand", "stock_uom", "disabled"),
		"detail_route": "/inventory/products/{name}",
		"desk_route": "/app/item/{name}",
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


def get_entity_schema(entity_key: str) -> dict:
	if entity_key not in ENTITY_SCHEMAS:
		frappe.throw(_("Unknown Retail ERP entity."), frappe.ValidationError)
	return deepcopy(ENTITY_SCHEMAS[entity_key])


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
