from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, strip_html

from my_store_ui.services.entity_schemas import get_entity_detail_schema, get_entity_schema
from my_store_ui.services.permissions import (
	can_open_standard_desk,
	get_doctype_permissions,
	get_document_permissions,
)


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
RELATED_LIMIT = 5
RELATED_SCAN_LIMIT = 200


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


def _has_any_role(required_roles: tuple[str, ...] | list[str] | None) -> bool:
	if not required_roles or frappe.session.user == "Administrator":
		return True
	return bool(set(required_roles) & set(frappe.get_roles()))


def _safe_document_value(doc, fieldname: str):
	value = doc.get(fieldname)
	field = doc.meta.get_field(fieldname)
	if field and field.fieldtype in {"Text Editor", "HTML Editor", "HTML"} and value:
		return strip_html(value)
	return value


def _serialize_fields(doc, schema: dict) -> dict:
	restricted_fields = schema.get("restricted_fields", {})
	allowed_fields = list(schema["fields"])
	for fieldname in schema.get("optional_custom_fields", ()):
		if doc.meta.has_field(fieldname):
			allowed_fields.append(fieldname)

	result = {}
	for fieldname in allowed_fields:
		if fieldname in restricted_fields and not _has_any_role(restricted_fields[fieldname]):
			continue
		field = doc.meta.get_field(fieldname)
		if field and field.fieldtype == "Table":
			continue
		result[fieldname] = _safe_document_value(doc, fieldname)

	if schema["doctype"] == "Item":
		defaults = doc.get("item_defaults") or []
		result["default_warehouse"] = next((row.default_warehouse for row in defaults if row.default_warehouse), None)
	return result


def _serialize_field_definition(field: tuple, values: dict) -> dict | None:
	fieldname, label, field_type = field
	if fieldname not in values:
		return None
	return {"fieldname": fieldname, "label": label, "type": field_type, "value": values.get(fieldname)}


def _serialize_sections(doc, schema: dict, values: dict) -> list[dict]:
	sections = []
	for section in schema["sections"]:
		fields = [item for field in section["fields"] if (item := _serialize_field_definition(field, values))]
		if fields:
			sections.append({"key": section["key"], "title": section["title"], "fields": fields})

	optional_fields = []
	for fieldname in schema.get("optional_custom_fields", ()):
		if fieldname not in values:
			continue
		field = doc.meta.get_field(fieldname)
		optional_fields.append(
			{"fieldname": fieldname, "label": field.label, "type": "text", "value": values[fieldname]}
		)
	if optional_fields:
		product_section = next((section for section in sections if section["key"] == "product"), None)
		if product_section:
			product_section["fields"].extend(optional_fields)
	return sections


def _serialize_child_tables(doc, schema: dict) -> list[dict]:
	tables = []
	for definition in schema["child_tables"]:
		if not _has_any_role(definition.get("required_roles_any")):
			continue
		rows = []
		for child in doc.get(definition["fieldname"]) or []:
			row = {}
			for fieldname, _label, field_type in definition["columns"]:
				value = child.get(fieldname)
				if field_type == "multiline" and value:
					value = strip_html(value)
				row[fieldname] = value
			rows.append(row)
		tables.append(
			{
				"fieldname": definition["fieldname"],
				"title": definition["title"],
				"columns": [
					{"fieldname": fieldname, "label": label, "type": field_type}
					for fieldname, label, field_type in definition["columns"]
				],
				"rows": rows,
				"count": len(rows),
			}
		)
	return tables


def _relation_filters(definition: dict, document_name: str) -> list[list]:
	filters = []
	for entry in definition["filters"]:
		resolved = [document_name if value == "{name}" else value for value in entry]
		filters.append(resolved)
	return filters


def _desk_form_url(doctype: str, name: str) -> str:
	return f"/app/{frappe.scrub(doctype).replace('_', '-')}/{quote(name, safe='')}"


def _serialize_related_documents(schema: dict, document_name: str, allow_desk: bool) -> list[dict]:
	related = []
	for definition in schema["related"]:
		doctype = definition["doctype"]
		if not frappe.has_permission(doctype, "read"):
			continue
		rows = frappe.get_list(
			doctype,
			filters=_relation_filters(definition, document_name),
			fields=list(definition["fields"]),
			order_by=f"`tab{doctype}`.`modified` desc",
			limit_page_length=RELATED_SCAN_LIMIT + 1,
			distinct=True,
		)
		count_is_limited = len(rows) > RELATED_SCAN_LIMIT
		if count_is_limited:
			rows = rows[:RELATED_SCAN_LIMIT]
		recent = []
		for row in rows[:RELATED_LIMIT]:
			record = dict(row)
			if definition.get("custom_route"):
				record["custom_route"] = definition["custom_route"].format(name=quote(row.name, safe=""))
			if allow_desk:
				record["desk_route"] = _desk_form_url(doctype, row.name)
			recent.append(record)
		related.append(
			{
				"title": definition["title"],
				"doctype": doctype,
				"count": len(rows),
				"count_is_limited": count_is_limited,
				"records": recent,
			}
		)
	return related


@frappe.whitelist()
def get_entity_detail(entity_key: str, name: str):
	"""Return one permission-filtered document using an approved detail schema."""
	_require_login()
	if not isinstance(name, str) or not name.strip() or len(name) > 140 or "\x00" in name:
		frappe.throw(_("Invalid document name."), frappe.ValidationError)

	schema = get_entity_detail_schema(entity_key)
	doctype = schema["doctype"]
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("You do not have permission to view this record."), frappe.PermissionError)

	name = name.strip()
	accessible = frappe.get_list(doctype, filters={"name": name}, pluck="name", limit_page_length=1)
	if not accessible:
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)

	doc = frappe.get_doc(doctype, name)
	permissions = get_document_permissions(doc)
	if not permissions["can_read"]:
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)

	allow_desk = can_open_standard_desk()
	values = _serialize_fields(doc, schema)
	return {
		"entity": {
			"key": entity_key,
			"doctype": doctype,
			"title": schema["singular_title"],
			"title_field": schema["title_field"],
			"subtitle_field": schema["subtitle_field"],
			"status_field": schema["status_field"],
			"status_type": schema["status_type"],
			"image_field": schema.get("image_field"),
			# Further image slots the record may carry, so the header can page
			# through them rather than showing only the first.
			"extra_image_fields": list(schema.get("extra_image_fields", ())),
			"back_route": schema["back_route"],
			"desk_route": schema["desk_route"].format(name=quote(name, safe="")) if allow_desk else None,
			"draft_only": bool(schema.get("draft_only", False)),
		},
		"document": values,
		"summary": [
			item for field in schema["summary"] if (item := _serialize_field_definition(field, values))
		],
		"sections": _serialize_sections(doc, schema, values),
		"child_tables": _serialize_child_tables(doc, schema),
		"related": _serialize_related_documents(schema, name, allow_desk),
		"activity": {
			"owner": doc.owner,
			"created": doc.creation,
			"modified_by": doc.modified_by,
			"modified": doc.modified,
		},
		"permissions": permissions,
	}
