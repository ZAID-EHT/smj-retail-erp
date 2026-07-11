from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.services.entity_schemas import get_entity_schema
from my_store_ui.services.permissions import can_open_standard_desk, get_doctype_permissions


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _parse_filters(filters: str | dict | None) -> dict:
	if not filters:
		return {}
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except (TypeError, ValueError):
			frappe.throw(_("Filters must be valid JSON."), frappe.ValidationError)
	if not isinstance(filters, dict):
		frappe.throw(_("Filters must be an object."), frappe.ValidationError)
	return filters


def _coerce_filter_value(fieldname: str, definition: dict, value: Any):
	field_type = definition["type"]
	if field_type == "DateRange":
		if not isinstance(value, dict) or not ({"from", "to"} & set(value)):
			frappe.throw(_("Invalid date range for {0}.").format(fieldname), frappe.ValidationError)
		start = value.get("from")
		end = value.get("to")
		if start and end:
			return [fieldname, "between", [start, end]]
		if start:
			return [fieldname, ">=", start]
		if end:
			return [fieldname, "<=", end]
	if fieldname in {"disabled", "is_stock_item"}:
		if str(value) not in {"0", "1"}:
			frappe.throw(_("Invalid value for {0}.").format(fieldname), frappe.ValidationError)
		value = cint(value)
	return [fieldname, "=", value]


def _build_filters(schema: dict, requested: dict) -> list:
	allowed = schema["filters"]
	unknown = set(requested) - set(allowed)
	if unknown:
		frappe.throw(_("Unsupported filter."), frappe.ValidationError)

	query_filters = []
	for fieldname, value in requested.items():
		if value in (None, "", [], {}):
			continue
		query_filters.append(_coerce_filter_value(fieldname, allowed[fieldname], value))
	return query_filters


def _get_barcode_item_names(search: str) -> list[str]:
	# Query through the permitted Item parent while filtering its barcode child
	# table, so candidate names also obey Item match conditions/user permissions.
	return frappe.get_list(
		"Item",
		filters=[["Item Barcode", "barcode", "like", f"%{search}%"]],
		pluck="name",
		limit_page_length=200,
	)


def _build_search(schema: dict, search: str) -> list:
	if not search:
		return []
	search = search.strip()[:140]
	if not search:
		return []
	like = f"%{search}%"
	or_filters = [[fieldname, "like", like] for fieldname in schema["search_fields"]]
	if schema.get("barcode_search"):
		barcode_items = _get_barcode_item_names(search)
		if barcode_items:
			or_filters.append(["name", "in", barcode_items])
	return or_filters


def _serialize_filter_definitions(schema: dict) -> list[dict]:
	definitions = []
	for fieldname, definition in schema["filters"].items():
		item = {"fieldname": fieldname, **definition}
		values = definition.get("values")
		if values:
			item["values"] = [
				{"value": value[0], "label": value[1]} if isinstance(value, tuple) else {"value": value, "label": value}
				for value in values
			]
		elif definition["type"] == "Link" and frappe.has_permission(definition["options"], "read"):
			item["values"] = [
				{"value": value, "label": value}
				for value in frappe.get_list(
					definition["options"], pluck="name", order_by="name asc", limit_page_length=250
				)
			]
		else:
			item["values"] = []
		definitions.append(item)
	return definitions


def _public_schema(entity_key: str, schema: dict, allow_desk: bool) -> dict:
	return {
		"key": entity_key,
		"title": schema["title"],
		"description": schema["description"],
		"columns": [
			{"fieldname": fieldname, "label": label, "type": field_type}
			for fieldname, label, field_type in schema["columns"]
		],
		"filters": _serialize_filter_definitions(schema),
		"sortable_fields": list(schema["sortable_fields"]),
		"default_sort": {"field": schema["default_sort"][0], "order": schema["default_sort"][1]},
		"status_field": schema["status_field"],
		"primary_field": schema["primary_field"],
		"secondary_field": schema["secondary_field"],
		"mobile_fields": list(schema["mobile_fields"]),
		"detail_route": schema["detail_route"],
		"desk_route": schema["desk_route"] if allow_desk else None,
	}


@frappe.whitelist()
def get_entity_list(
	entity_key: str,
	search: str = "",
	filters: str | dict | None = None,
	sort_field: str | None = None,
	sort_order: str | None = None,
	page: int = 1,
	page_size: int = DEFAULT_PAGE_SIZE,
	fields: Any = None,
):
	"""Return a permission-filtered page from a server-owned entity schema."""
	_require_login()
	if fields is not None:
		frappe.throw(_("Custom field selection is not supported."), frappe.ValidationError)

	schema = get_entity_schema(entity_key)
	doctype = schema["doctype"]
	permissions = get_doctype_permissions(doctype)
	if not permissions["can_read"]:
		frappe.throw(_("You do not have permission to view this list."), frappe.PermissionError)

	page = max(cint(page), 1)
	page_size = min(max(cint(page_size) or DEFAULT_PAGE_SIZE, 1), MAX_PAGE_SIZE)
	sort_field = sort_field or schema["default_sort"][0]
	sort_order = (sort_order or schema["default_sort"][1]).lower()
	if sort_field not in schema["sortable_fields"] or sort_order not in {"asc", "desc"}:
		frappe.throw(_("Unsupported sort selection."), frappe.ValidationError)

	query_filters = _build_filters(schema, _parse_filters(filters))
	or_filters = _build_search(schema, search)
	query_args = {
		"filters": query_filters,
		"or_filters": or_filters,
	}
	count_result = frappe.get_list(
		doctype,
		fields=["count(name) as total"],
		limit_page_length=1,
		**query_args,
	)
	total = cint(count_result[0].total) if count_result else 0
	records = frappe.get_list(
		doctype,
		fields=list(schema["fields"]),
		order_by=f"{sort_field} {sort_order}",
		limit_start=(page - 1) * page_size,
		limit_page_length=page_size,
		**query_args,
	)

	return {
		"entity": _public_schema(entity_key, schema, can_open_standard_desk()),
		"permissions": permissions,
		"records": records,
		"pagination": {
			"page": page,
			"page_size": page_size,
			"total": total,
			"pages": max((total + page_size - 1) // page_size, 1),
			"has_next": page * page_size < total,
			"has_previous": page > 1,
		},
	}
