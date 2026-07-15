"""Permission-aware APIs for the metadata-driven Retail ERP foundation.

Only features explicitly classified by ``universal.registry`` can reach these
methods.  Frappe documents and controllers remain authoritative for reads,
writes, validation, workflows and document state transitions.
"""

from __future__ import annotations

import json
import shutil
from copy import deepcopy
from typing import Any
from urllib.parse import quote, urlencode

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate

from my_store_ui.universal.registry import (
	ALL_GENERATED_DOCTYPES,
	SUPPORTED_FIELD_TYPES,
	feature_is_permitted,
	get_feature,
	get_generated_feature,
	get_registry_records,
)


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_LINK_RESULTS = 20
MAX_TIMELINE_ROWS = 30
SAFE_FILTER_OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "like", "not like", "in", "not in", "between", "is"}
LAYOUT_FIELDS = {"Section Break", "Column Break", "Tab Break"}
NUMERIC_FIELDS = {"Currency", "Float", "Int", "Percent", "Duration", "Rating"}

# Fixed server-owned mappings. The browser sends only these symbolic action
# keys; dotted Python methods are never accepted from a request.
MAPPED_ACTIONS = {
	"Quotation": {
		"make_sales_order": {"label": _("Create Sales Order"), "target": "Sales Order", "method": "quotation_sales_order"},
		"make_sales_invoice": {"label": _("Create Sales Invoice"), "target": "Sales Invoice", "method": "quotation_sales_invoice"},
	},
	"Material Request": {
		"make_request_for_quotation": {"label": _("Create Request for Quotation"), "target": "Request for Quotation", "method": "material_request_rfq"},
		"make_purchase_order": {"label": _("Create Purchase Order"), "target": "Purchase Order", "method": "material_request_purchase_order"},
		"make_stock_entry": {"label": _("Create Stock Entry"), "target": "Stock Entry", "method": "material_request_stock_entry"},
	},
	"Request for Quotation": {
		"make_supplier_quotation": {"label": _("Create Supplier Quotation"), "target": "Supplier Quotation", "method": "rfq_supplier_quotation", "requires_parameters": ["supplier"]},
	},
	"Supplier Quotation": {
		"make_purchase_order": {"label": _("Create Purchase Order"), "target": "Purchase Order", "method": "supplier_quotation_purchase_order"},
	},
	"Purchase Order": {
		"make_purchase_receipt": {"label": _("Create Purchase Receipt"), "target": "Purchase Receipt", "method": "purchase_order_receipt"},
		"make_purchase_invoice": {"label": _("Create Purchase Invoice"), "target": "Purchase Invoice", "method": "purchase_order_invoice"},
	},
	"Purchase Receipt": {
		"make_purchase_invoice": {"label": _("Create Purchase Invoice"), "target": "Purchase Invoice", "method": "purchase_receipt_invoice"},
		"make_purchase_return": {"label": _("Create Purchase Return"), "target": "Purchase Receipt", "method": "purchase_receipt_return"},
		"make_lcv": {"label": _("Create Landed Cost Voucher"), "target": "Landed Cost Voucher", "method": "purchase_receipt_lcv"},
	},
	"Purchase Invoice": {
		"make_payment_entry": {"label": _("Create Payment Entry"), "target": "Payment Entry", "method": "purchase_invoice_payment"},
		"make_debit_note": {"label": _("Create Debit Note"), "target": "Purchase Invoice", "method": "purchase_invoice_debit_note"},
	},
	"Journal Entry": {
		"make_reverse_journal_entry": {"label": _("Reverse Journal Entry"), "target": "Journal Entry", "method": "journal_entry_reverse"},
	},
	"Opportunity": {
		"make_quotation": {"label": _("Create Quotation"), "target": "Quotation", "method": "opportunity_quotation"},
	},
	"Lead": {
		"make_customer": {"label": _("Create Customer"), "target": "Customer", "method": "lead_customer"},
	},
	"Dunning": {
		"payment": {"label": _("Create Payment Entry"), "target": "Payment Entry", "method": "dunning_payment"},
	},
}


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _parse(value: Any, expected: type, label: str):
	if isinstance(value, str):
		try:
			value = json.loads(value)
		except (TypeError, ValueError):
			frappe.throw(_("{0} must be valid JSON.").format(label), frappe.ValidationError)
	if not isinstance(value, expected):
		frappe.throw(_("{0} has an invalid format.").format(label), frappe.ValidationError)
	return value


def _permlevels(meta, permission: str) -> set[int]:
	try:
		return {cint(value) for value in meta.get_permlevel_access(permission, user=frappe.session.user)}
	except Exception:
		return {0}


def _readable_fields(meta) -> list:
	levels = _permlevels(meta, "read")
	return [field for field in meta.fields if field.fieldtype in SUPPORTED_FIELD_TYPES and cint(field.permlevel) in levels]


def _writable_fields(meta) -> list:
	levels = _permlevels(meta, "write")
	return [
		field for field in meta.fields
		if field.fieldtype in SUPPORTED_FIELD_TYPES
		and field.fieldtype not in LAYOUT_FIELDS | {"HTML", "Button"}
		and not field.read_only and not field.hidden and cint(field.permlevel) in levels
	]


def _permissions(doctype: str, doc=None) -> dict:
	meta = frappe.get_meta(doctype)
	def allowed(ptype: str) -> bool:
		return bool(frappe.has_permission(doctype, ptype, doc=doc))
	return {
		"can_read": allowed("read"), "can_create": allowed("create"), "can_write": allowed("write"),
		"can_delete": allowed("delete"), "can_submit": bool(meta.is_submittable and allowed("submit")), "can_cancel": bool(meta.is_submittable and allowed("cancel")),
		"can_print": allowed("print"), "can_email": allowed("email"), "can_export": allowed("export"),
	}


def _safe_options(field) -> Any:
	if field.fieldtype == "Select":
		return [value for value in (field.options or "").splitlines() if value]
	if field.fieldtype in {"Link", "Table", "Table MultiSelect"}:
		return field.options
	if field.fieldtype == "Dynamic Link":
		return field.options
	return None


def _field_definition(field, *, writable: set[str], depth: int = 0) -> dict:
	definition = {
		"fieldname": field.fieldname, "label": field.label or field.fieldname,
		"fieldtype": field.fieldtype, "required": bool(field.reqd),
		"read_only": bool(field.read_only or field.fieldname not in writable), "hidden": bool(field.hidden),
		"default": field.default, "options": _safe_options(field), "description": field.description,
		"precision": field.precision, "length": field.length, "permlevel": cint(field.permlevel),
		"depends_on": field.depends_on, "mandatory_depends_on": field.mandatory_depends_on,
		"read_only_depends_on": field.read_only_depends_on, "fetch_from": field.fetch_from,
		"fetch_if_empty": bool(field.fetch_if_empty), "non_negative": bool(field.non_negative),
		"unique": bool(field.unique), "unsupported_client_behavior": False,
	}
	# Button handlers and arbitrary client expressions are never executed by Vue.
	if field.fieldtype == "Button" or any(
		isinstance(definition.get(key), str) and definition[key].strip().startswith("eval:")
		for key in ("depends_on", "mandatory_depends_on", "read_only_depends_on")
	):
		definition["unsupported_client_behavior"] = True
	if field.fieldtype in {"Table", "Table MultiSelect"} and field.options and depth == 0:
		child_meta = frappe.get_meta(field.options)
		child_write = {item.fieldname for item in _writable_fields(child_meta)}
		definition["child_fields"] = [
			_field_definition(item, writable=child_write, depth=1)
			for item in _readable_fields(child_meta)
			if item.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML"}
		]
	return definition


def _metadata(feature: str) -> tuple[dict, Any, list, set[str]]:
	record = get_generated_feature(feature)
	meta = frappe.get_meta(record["doctype"])
	readable = _readable_fields(meta)
	writable = {field.fieldname for field in _writable_fields(meta)}
	return record, meta, readable, writable


def _public_feature(record: dict) -> dict:
	return {key: deepcopy(value) for key, value in record.items() if key not in {"required_permissions", "source_location"}}


def _record_route(record: dict, name: str | None = None, suffix: str | None = None) -> str:
	"""Return the registered clean route, retaining /generated as compatibility."""
	base = record.get("route") or record.get("list_route") or f"/generated/{record['route_key']}"
	if name:
		base = f"{base.rstrip('/')}/{quote(name, safe='')}"
	if suffix:
		base = f"{base.rstrip('/')}/{suffix}"
	return base


@frappe.whitelist(methods=["GET"])
def get_feature_registry(module: str | None = None, implementation_type: str | None = None, start: int = 0, page_length: int = 50):
	_require_login()
	page_length = min(max(cint(page_length) or 50, 1), 100)
	start = max(cint(start), 0)
	allowed_types = {"custom", "generated", "generated_provisional", "special"}
	if implementation_type and implementation_type not in allowed_types:
		frappe.throw(_("Unsupported implementation type."), frappe.ValidationError)
	records = [
		record for record in get_registry_records()
		if record.get("user_facing") and record.get("implementation_type") in allowed_types and (not module or record.get("module") == module)
		and (not implementation_type or record.get("implementation_type") == implementation_type)
		and feature_is_permitted(record)
	]
	return {"records": [_public_feature(record) for record in records[start:start + page_length]], "total": len(records), "start": start, "page_length": page_length}


@frappe.whitelist(methods=["GET"])
def get_feature_definition(feature: str):
	_require_login()
	record = get_feature(feature)
	if not feature_is_permitted(record):
		frappe.throw(_("Feature is not available."), frappe.PermissionError)
	return _public_feature(record)


@frappe.whitelist(methods=["GET"])
def get_doctype_metadata(feature: str):
	_require_login()
	record, meta, readable, writable = _metadata(feature)
	defaults = {}
	if frappe.has_permission(meta.name, "create"):
		new_doc = frappe.new_doc(meta.name)
		for field in readable:
			if field.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML"} and new_doc.get(field.fieldname) is not None:
				defaults[field.fieldname] = new_doc.get(field.fieldname)
	return {
		"feature": _public_feature(record), "doctype": meta.name, "label": meta.get("label") or meta.name,
		"title_field": meta.title_field or "name", "image_field": meta.image_field,
		"is_submittable": bool(meta.is_submittable), "is_tree": bool(meta.is_tree), "is_single": bool(meta.issingle),
		"track_changes": bool(meta.track_changes), "search_fields": [value.strip() for value in (meta.search_fields or "").split(",") if value.strip()],
		"fields": [_field_definition(field, writable=writable) for field in readable],
		"defaults": defaults,
		"permissions": _permissions(meta.name),
		"client_script_policy": "not_executed",
		"presentation": record.get("presentation") or {},
	}


def _list_fields(meta, readable: list) -> list[str]:
	available = {field.fieldname: field for field in readable if field.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML"}}
	preferred = ["name", meta.title_field, "status", "workflow_state", "disabled", "company", "modified"]
	result = []
	for fieldname in preferred + list(available):
		if fieldname and fieldname not in result and (fieldname == "name" or fieldname in available):
			result.append(fieldname)
		if len(result) >= 8:
			break
	return result or ["name", "modified"]


def _available_list_fields(readable: list) -> list:
	return [field for field in readable if field.fieldtype not in LAYOUT_FIELDS | {"Table", "Table MultiSelect", "Button", "HTML", "Text Editor", "Code", "Long Text", "Text"} and not field.hidden]


@frappe.whitelist(methods=["GET"])
def get_list_configuration(feature: str):
	_require_login()
	record, meta, readable, _writable = _metadata(feature)
	available = _available_list_fields(readable)
	available_names = {field.fieldname for field in available} | {"name", "modified"}
	presentation = record.get("presentation") or {}
	requested_defaults = presentation.get("default_columns") or []
	fields = [fieldname for fieldname in requested_defaults if fieldname in available_names]
	if not fields:
		fields = _list_fields(meta, readable)
	if "name" not in fields:
		fields.insert(0, "name")
	field_map = {field.fieldname: field for field in readable}
	all_columns = [{"fieldname": name, "label": (field_map[name].label if name in field_map else "ID" if name == "name" else name.title()), "fieldtype": (field_map[name].fieldtype if name in field_map else "Datetime" if name == "modified" else "Data"), "options": _safe_options(field_map[name]) if name in field_map else None} for name in ["name", *[field.fieldname for field in available], "modified"] if name not in {"creation", "owner", "modified_by"}]
	# Deduplicate metadata fields that overlap standard fields.
	all_columns = list({column["fieldname"]: column for column in all_columns}.values())
	filter_fields = [_field_definition(field, writable=set()) for field in readable if field.fieldtype in {"Link", "Select", "Date", "Datetime", "Check"} and not field.hidden]
	filter_map = {field["fieldname"]: field for field in filter_fields}
	main_filters = [filter_map[name] for name in presentation.get("main_filters", []) if name in filter_map][:5]
	if not main_filters:
		main_filters = filter_fields[:5]
	main_names = {field["fieldname"] for field in main_filters}
	return {
		"feature": _public_feature(record), "doctype": meta.name,
		"columns": [{
			"fieldname": name,
			"label": field_map[name].label if name in field_map else "ID" if name == "name" else "Modified" if name == "modified" else name.replace("_", " ").title(),
			"fieldtype": field_map[name].fieldtype if name in field_map else "Datetime" if name == "modified" else "Data",
		} for name in fields],
		"all_columns": all_columns, "default_columns": fields,
		"filter_fields": filter_fields, "main_filters": main_filters,
		"more_filters": [field for field in filter_fields if field["fieldname"] not in main_names],
		"sortable_fields": [column["fieldname"] for column in all_columns], "default_sort": {"field": "modified", "order": "desc"},
		"title_field": meta.title_field or "name", "permissions": _permissions(meta.name),
		"presentation": presentation,
	}


def _validated_filters(filters: Any, meta, readable_names: set[str]) -> list:
	if not filters:
		return []
	filters = _parse(filters, list, "Filters")
	result = []
	for item in filters:
		if not isinstance(item, list) or len(item) != 3:
			frappe.throw(_("Invalid filter."), frappe.ValidationError)
		fieldname, operator, value = item
		if fieldname not in readable_names or str(operator).lower() not in SAFE_FILTER_OPERATORS:
			frappe.throw(_("Unsupported filter."), frappe.ValidationError)
		result.append([fieldname, str(operator).lower(), value])
	return result


@frappe.whitelist(methods=["GET", "POST"])
def get_document_list(feature: str, search: str = "", filters: Any = None, columns: Any = None, sort_field: str = "modified", sort_order: str = "desc", page: int = 1, page_size: int = DEFAULT_PAGE_SIZE):
	_require_login()
	record, meta, readable, _writable = _metadata(feature)
	if not frappe.has_permission(meta.name, "read"):
		frappe.throw(_("Feature is not available."), frappe.PermissionError)
	available_columns = {field.fieldname for field in _available_list_fields(readable)} | {"name", "modified"}
	if columns:
		columns = _parse(columns, list, "Columns")
		if not columns or len(columns) > 12 or any(not isinstance(field, str) or field not in available_columns for field in columns):
			frappe.throw(_("Unsupported column selection."), frappe.ValidationError)
		columns = list(dict.fromkeys(columns))
	else:
		columns = [column["fieldname"] for column in get_list_configuration(feature)["columns"]]
	readable_names = {field.fieldname for field in readable} | {"name", "modified"}
	filterable_names = {
		field.fieldname for field in readable
		if field.fieldtype in {"Link", "Select", "Date", "Datetime", "Check"} and not field.hidden
	}
	if sort_field not in available_columns or sort_order.lower() not in {"asc", "desc"}:
		frappe.throw(_("Unsupported sort selection."), frappe.ValidationError)
	query_filters = _validated_filters(filters, meta, filterable_names)
	or_filters = []
	search = (search or "").strip()[:140]
	if search:
		searchable = ["name", meta.title_field] + [value.strip() for value in (meta.search_fields or "").split(",") if value.strip()]
		or_filters = [[fieldname, "like", f"%{search}%"] for fieldname in dict.fromkeys(searchable) if fieldname in readable_names]
	page = max(cint(page), 1)
	page_size = min(max(cint(page_size) or DEFAULT_PAGE_SIZE, 1), MAX_PAGE_SIZE)
	args = {"filters": query_filters, "or_filters": or_filters}
	count = frappe.get_list(meta.name, fields=["count(name) as total"], limit_page_length=1, **args)
	total = cint(count[0].total) if count else 0
	rows = frappe.get_list(meta.name, fields=columns, order_by=f"`tab{meta.name}`.`{sort_field}` {sort_order.lower()}", limit_start=(page - 1) * page_size, limit_page_length=page_size, **args)
	configuration = get_list_configuration(feature)
	column_map = {column["fieldname"]: column for column in configuration["all_columns"]}
	for column in configuration["columns"]:
		column_map.setdefault(column["fieldname"], column)
	# Default columns come from _list_fields, which may include a valid but
	# text/hidden field that _available_list_fields (all_columns) omits. Fall
	# back to a synthesised column so any servable DocType renders safely.
	readable_by_name = {field.fieldname: field for field in readable}
	def _column_for(name: str) -> dict:
		if name in column_map:
			return column_map[name]
		field = readable_by_name.get(name)
		return {
			"fieldname": name,
			"label": (field.label if field and field.label else "ID" if name == "name" else "Modified" if name == "modified" else name.replace("_", " ").title()),
			"fieldtype": (field.fieldtype if field else "Datetime" if name == "modified" else "Data"),
		}
	return {"feature": _public_feature(record), "records": rows, "columns": [_column_for(name) for name in columns], "permissions": _permissions(meta.name), "pagination": {"page": page, "page_size": page_size, "total": total, "pages": max((total + page_size - 1) // page_size, 1)}}


def _visible_doc(doc, meta, readable: list) -> dict:
	result = {"name": doc.name, "doctype": doc.doctype, "docstatus": doc.docstatus, "creation": doc.creation, "modified": doc.modified, "owner": doc.owner, "modified_by": doc.modified_by}
	for field in readable:
		if field.fieldtype in LAYOUT_FIELDS | {"Button", "HTML"}:
			continue
		value = doc.get(field.fieldname)
		if field.fieldtype in {"Table", "Table MultiSelect"}:
			allowed = {child["fieldname"] for child in _field_definition(field, writable=set()).get("child_fields", [])}
			result[field.fieldname] = [{key: row.get(key) for key in allowed if row.get(key) is not None} | {"name": row.name, "idx": row.idx} for row in (value or [])]
		else:
			result[field.fieldname] = value
	return result


def _get_permitted_doc(doctype: str, name: str, permission: str = "read"):
	# get_list applies match conditions first, avoiding an existence oracle.
	visible = frappe.get_list(doctype, filters={"name": name}, pluck="name", limit_page_length=1)
	if not visible:
		frappe.throw(_("Record was not found or is unavailable."), frappe.DoesNotExistError)
	doc = frappe.get_doc(doctype, name)
	if not frappe.has_permission(doctype, permission, doc=doc):
		frappe.throw(_("Record was not found or is unavailable."), frappe.PermissionError)
	return doc


@frappe.whitelist(methods=["GET"])
def get_document_detail(feature: str, name: str):
	_require_login()
	record, meta, readable, writable = _metadata(feature)
	doc = _get_permitted_doc(meta.name, name)
	return {"feature": _public_feature(record), "metadata": get_doctype_metadata(feature), "document": _visible_doc(doc, meta, readable), "permissions": _permissions(meta.name, doc=doc), "actions": [*_available_actions(meta, doc), *_available_workflow_actions(doc)], "route": _record_route(record, doc.name)}


def _coerce_value(field, value):
	if value is None:
		return None
	if field.fieldtype == "Check":
		return cint(value)
	if field.fieldtype in NUMERIC_FIELDS:
		value = flt(value)
		if field.non_negative and value < 0:
			frappe.throw(_("{0} cannot be negative.").format(field.label), frappe.ValidationError)
		return value
	if field.fieldtype == "Date" and value:
		return str(getdate(value))
	if field.fieldtype == "Select" and value not in [item for item in (field.options or "").splitlines() if item]:
		frappe.throw(_("Invalid value for {0}.").format(field.label), frappe.ValidationError)
	if field.fieldtype == "Link" and value:
		if not frappe.has_permission(field.options, "read") or not frappe.get_list(field.options, filters={"name": value}, pluck="name", limit_page_length=1):
			frappe.throw(_("Invalid or unavailable {0}.").format(field.label), frappe.ValidationError)
	if isinstance(value, str):
		return value[: cint(field.length) or 100000]
	return value


def _validate_dynamic_links(meta, clean: dict, existing=None) -> None:
	for field in meta.fields:
		if field.fieldtype != "Dynamic Link" or not clean.get(field.fieldname):
			continue
		target_doctype = clean.get(field.options) or (existing.get(field.options) if existing else None)
		if not target_doctype or not frappe.db.exists("DocType", target_doctype) or not frappe.has_permission(target_doctype, "read"):
			frappe.throw(_("Invalid or unavailable {0} type.").format(field.label), frappe.ValidationError)
		if not frappe.get_list(target_doctype, filters={"name": clean[field.fieldname]}, pluck="name", limit_page_length=1):
			frappe.throw(_("Invalid or unavailable {0}.").format(field.label), frappe.ValidationError)


def _clean_payload(meta, payload: Any, existing=None) -> dict:
	payload = _parse(payload, dict, "Document")
	writable = {field.fieldname: field for field in _writable_fields(meta)}
	unknown = set(payload) - set(writable)
	if unknown:
		frappe.throw(_("Unsupported or read-only field: {0}").format(", ".join(sorted(unknown))), frappe.ValidationError)
	clean = {}
	for fieldname, value in payload.items():
		field = writable[fieldname]
		if field.fieldtype in {"Table", "Table MultiSelect"}:
			if not isinstance(value, list):
				frappe.throw(_("{0} must contain rows.").format(field.label), frappe.ValidationError)
			child_meta = frappe.get_meta(field.options)
			child_write = {child.fieldname: child for child in _writable_fields(child_meta)}
			rows = []
			for row in value:
				if not isinstance(row, dict) or set(row) - set(child_write) - {"name", "idx"}:
					frappe.throw(_("Unsupported child-table field."), frappe.ValidationError)
				clean_row = {key: _coerce_value(child_write[key], item) for key, item in row.items() if key in child_write}
				_validate_dynamic_links(child_meta, clean_row)
				rows.append(clean_row)
			clean[fieldname] = rows
		else:
			clean[fieldname] = _coerce_value(field, value)
	_validate_dynamic_links(meta, clean, existing)
	return clean


@frappe.whitelist(methods=["POST"])
def create_document(feature: str, values: Any):
	_require_login()
	record = get_generated_feature(feature, "create")
	meta = frappe.get_meta(record["doctype"])
	if not frappe.has_permission(meta.name, "create"):
		frappe.throw(_("You cannot create this record."), frappe.PermissionError)
	doc = frappe.new_doc(meta.name)
	doc.update(_clean_payload(meta, values))
	doc.insert()
	return {"name": doc.name, "route": _record_route(record, doc.name), "modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def update_document(feature: str, name: str, values: Any, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	meta = frappe.get_meta(record["doctype"])
	doc = _get_permitted_doc(meta.name, name, "write")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before saving."), frappe.TimestampMismatchError)
	doc.update(_clean_payload(meta, values, doc))
	doc.save()
	return {"name": doc.name, "route": _record_route(record, doc.name), "modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def delete_document(feature: str, name: str, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name, "delete")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before deleting."), frappe.TimestampMismatchError)
	frappe.delete_doc(doc.doctype, doc.name)
	return {"deleted": True, "route": _record_route(record)}


def _available_actions(meta, doc) -> list[dict]:
	actions = []
	if doc.docstatus == 0 and meta.is_submittable and frappe.has_permission(meta.name, "submit", doc=doc):
		actions.append({"action": "submit", "label": _("Submit"), "destructive": False})
	if doc.docstatus == 1 and frappe.has_permission(meta.name, "cancel", doc=doc):
		actions.append({"action": "cancel", "label": _("Cancel"), "destructive": True})
	if doc.docstatus == 2 and meta.is_submittable and frappe.has_permission(meta.name, "create"):
		actions.append({"action": "amend", "label": _("Amend"), "destructive": False})
	if doc.docstatus == 0 and frappe.has_permission(meta.name, "delete", doc=doc):
		actions.append({"action": "delete", "label": _("Delete"), "destructive": True})
	if frappe.has_permission(meta.name, "create"):
		actions.append({"action": "duplicate", "label": _("Duplicate"), "destructive": False})
	if meta.allow_rename and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "rename", "label": _("Rename"), "destructive": False, "requires_parameters": ["new_name"]})
	if doc.doctype == "Opportunity" and doc.docstatus == 0 and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.status == "Open":
			actions.append({"action": "close", "label": _("Close"), "destructive": False})
		else:
			actions.append({"action": "reopen", "label": _("Reopen"), "destructive": False})
	if doc.doctype == "Supplier" and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "resume" if doc.on_hold else "hold", "label": _("Resume") if doc.on_hold else _("Hold"), "destructive": False})
	if doc.doctype == "Material Request" and doc.docstatus == 1 and frappe.has_permission(meta.name, "submit", doc=doc):
		actions.append({"action": "reopen" if doc.status == "Stopped" else "stop", "label": _("Reopen") if doc.status == "Stopped" else _("Stop"), "destructive": doc.status != "Stopped"})
	if doc.doctype == "Purchase Order" and doc.docstatus == 1 and frappe.has_permission(meta.name, "submit", doc=doc):
		if doc.status == "On Hold":
			actions.append({"action": "resume", "label": _("Resume"), "destructive": False})
		elif doc.status in {"Closed", "Delivered"}:
			actions.append({"action": "reopen", "label": _("Reopen"), "destructive": False})
		else:
			actions.extend([
				{"action": "hold", "label": _("Hold"), "destructive": False, "requires_parameters": ["reason_for_hold"]},
				{"action": "close", "label": _("Close"), "destructive": True},
			])
	if doc.doctype == "Lead" and frappe.has_permission("Opportunity", "create"):
		actions.append({"action": "make_opportunity", "label": _("Create Opportunity"), "destructive": False, "mapping_target": "Opportunity"})
	if doc.doctype == "Opportunity" and frappe.has_permission("Customer", "create"):
		actions.append({"action": "make_customer", "label": _("Create Customer"), "destructive": False, "mapping_target": "Customer"})
	# Chart of Accounts admin actions (account.js) - real erpnext controller
	# methods, matched by exact scanner action key.
	if doc.doctype == "Account":
		actions.append({"action": "chart_of_accounts", "label": _("Chart of Accounts"), "destructive": False})
		if not cint(doc.is_group) and frappe.has_permission("GL Entry", "read"):
			actions.append({"action": "general_ledger", "label": _("General Ledger"), "destructive": False})
		if frappe.has_permission(meta.name, "write", doc=doc) and doc.parent_account:
			if cint(doc.is_group):
				actions.append({"action": "convert_to_non_group", "label": _("Convert to Non-Group"), "destructive": False})
			else:
				actions.append({"action": "convert_to_group", "label": _("Convert to Group"), "destructive": False})
			actions.append({"action": "merge_account", "label": _("Merge Account"), "destructive": True, "requires_parameters": ["new_account"]})
			actions.append({"action": "update_account_name_number", "label": _("Update Account Name / Number"), "destructive": False, "requires_parameters": ["account_name", "account_number"]})
	if doc.doctype == "Cost Center":
		actions.append({"action": "chart_of_cost_centers", "label": _("Chart of Cost Centers"), "destructive": False})
		if frappe.has_permission("Budget", "read"):
			actions.append({"action": "budget", "label": _("Budget"), "destructive": False})
		if frappe.has_permission(meta.name, "write", doc=doc):
			if cint(doc.is_group):
				actions.append({"action": "convert_to_non_group", "label": _("Convert to Non-Group"), "destructive": False})
			else:
				actions.append({"action": "convert_to_group", "label": _("Convert to Group"), "destructive": False})
			actions.append({"action": "update_cost_center_name_number", "label": _("Update Cost Center Name / Number"), "destructive": False, "requires_parameters": ["cost_center_name", "cost_center_number"]})
	# Ledger navigation shortcuts (journal_entry.js / period_closing_voucher.js /
	# warehouse.js) - pure navigation to the already-routed General Ledger
	# report with prefilled filters; no document is created or changed.
	if doc.doctype == "Journal Entry" and doc.docstatus > 0 and frappe.has_permission("GL Entry", "read"):
		actions.append({"action": "ledger", "label": _("Ledger"), "destructive": False})
	if doc.doctype == "Period Closing Voucher" and doc.docstatus > 0 and frappe.has_permission("GL Entry", "read"):
		actions.append({"action": "ledger", "label": _("Ledger"), "destructive": False})
	if doc.doctype == "Warehouse" and not cint(doc.is_group) and frappe.has_permission("GL Entry", "read"):
		if frappe.db.exists("Account", {"warehouse": doc.name, "company": doc.company}):
			actions.append({"action": "general_ledger", "label": _("General Ledger"), "destructive": False})
	# Company-level shortcuts (company.js) - navigation to the already-routed
	# Account/Cost Center trees, pre-filtered by this company.
	if doc.doctype == "Company":
		if frappe.has_permission("Cost Center", "read"):
			actions.append({"action": "cost_centers", "label": _("Cost Centers"), "destructive": False})
		if frappe.has_permission("Account", "read"):
			actions.append({"action": "chart_of_accounts", "label": _("Chart of Accounts"), "destructive": False})
	# Exchange Rate Revaluation's own idempotency check (check_journal_entry_condition)
	# gates the button in erpnext's own Desk UI - reproduced here so the
	# action is only offered when erpnext itself would offer it.
	if doc.doctype == "Exchange Rate Revaluation" and doc.docstatus == 1 and frappe.has_permission("Journal Entry", "create"):
		if doc.check_journal_entry_condition():
			actions.append({"action": "make_jv_entries", "label": _("Journal Entries"), "destructive": False})
	if doc.doctype == "Dunning" and doc.docstatus == 1 and doc.status == "Unresolved" and frappe.has_permission(meta.name, "write", doc=doc):
		actions.append({"action": "resolve", "label": _("Resolve"), "destructive": False})
	# Process Period Closing Voucher background-job controls
	# (process_period_closing_voucher.js Start/Pause/Resume buttons).
	# "cancel_pcv_processing" is not a separate button - it is erpnext's own
	# on_cancel() hook, already triggered by the standard "cancel" lifecycle
	# action (GENERIC_LIFECYCLE_ACTIONS) once this doctype is routed.
	if doc.doctype == "Purchase Invoice" and not doc.is_return and doc.docstatus == 1 and flt(doc.outstanding_amount) != 0 and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.on_hold:
			actions.append({"action": "change_release_date", "label": _("Change Release Date"), "destructive": False, "requires_parameters": ["release_date"]})
			actions.append({"action": "unblock_invoice", "label": _("Unblock Invoice"), "destructive": False})
		else:
			actions.append({"action": "block_invoice", "label": _("Block Invoice"), "destructive": True, "requires_parameters": ["release_date"]})
	if doc.doctype == "Process Period Closing Voucher" and doc.docstatus == 1 and frappe.has_permission(meta.name, "write", doc=doc):
		if doc.status == "Queued":
			actions.append({"action": "start_pcv_processing", "label": _("Start"), "destructive": False})
		elif doc.status == "Running":
			actions.append({"action": "pause_pcv_processing", "label": _("Pause"), "destructive": False})
		elif doc.status == "Paused":
			actions.append({"action": "resume_pcv_processing", "label": _("Resume"), "destructive": False})
	for key, mapping in MAPPED_ACTIONS.get(doc.doctype, {}).items():
		if key in {item["action"] for item in actions}:
			continue
		# ERPNext mapped transaction methods require submitted source documents;
		# CRM conversions operate on their normal saved draft state.
		if doc.doctype not in {"Lead", "Opportunity"} and doc.docstatus != 1:
			continue
		if frappe.has_permission(mapping["target"], "create"):
			actions.append({
				"action": key, "label": mapping["label"], "destructive": False,
				"mapping_target": mapping["target"],
				"requires_parameters": mapping.get("requires_parameters") or [],
			})
	return actions


def _run_mapped_action(doc, action: str, parameters: dict):
	mapping = MAPPED_ACTIONS[doc.doctype][action]
	if not frappe.has_permission(mapping["target"], "create"):
		frappe.throw(_("You cannot create the mapped document."), frappe.PermissionError)
	method = mapping["method"]
	if method == "quotation_sales_order":
		from erpnext.selling.doctype.quotation.quotation import make_sales_order
		target = make_sales_order(doc.name)
	elif method == "quotation_sales_invoice":
		from erpnext.selling.doctype.quotation.quotation import make_sales_invoice
		target = make_sales_invoice(doc.name)
	elif method == "material_request_rfq":
		from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation
		target = make_request_for_quotation(doc.name)
	elif method == "material_request_purchase_order":
		from erpnext.stock.doctype.material_request.material_request import make_purchase_order
		target = make_purchase_order(doc.name)
	elif method == "rfq_supplier_quotation":
		supplier = str(parameters.get("supplier") or "").strip()
		if not supplier or not frappe.has_permission("Supplier", "read") or not frappe.get_list("Supplier", filters={"name": supplier}, pluck="name", limit_page_length=1):
			frappe.throw(_("A permitted Supplier is required."), frappe.ValidationError)
		allowed_suppliers = {row.supplier for row in (doc.get("suppliers") or []) if row.supplier}
		if allowed_suppliers and supplier not in allowed_suppliers:
			frappe.throw(_("The Supplier is not registered on this request."), frappe.ValidationError)
		from erpnext.buying.doctype.request_for_quotation.request_for_quotation import make_supplier_quotation_from_rfq
		target = make_supplier_quotation_from_rfq(doc.name, for_supplier=supplier)
	elif method == "supplier_quotation_purchase_order":
		from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order
		target = make_purchase_order(doc.name)
	elif method == "purchase_order_receipt":
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		target = make_purchase_receipt(doc.name)
	elif method == "purchase_order_invoice":
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice
		target = make_purchase_invoice(doc.name)
	elif method == "purchase_receipt_invoice":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
		target = make_purchase_invoice(doc.name)
	elif method == "purchase_receipt_return":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return
		target = make_purchase_return(doc.name)
	elif method == "purchase_receipt_lcv":
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_lcv
		target = frappe.get_doc(make_lcv(doc.doctype, doc.name))
	elif method == "material_request_stock_entry":
		from erpnext.stock.doctype.material_request.material_request import make_stock_entry
		target = make_stock_entry(doc.name)
	elif method == "purchase_invoice_debit_note":
		from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_debit_note
		target = make_debit_note(doc.name)
	elif method == "journal_entry_reverse":
		from erpnext.accounts.doctype.journal_entry.journal_entry import make_reverse_journal_entry
		target = make_reverse_journal_entry(doc.name)
	elif method == "purchase_invoice_payment":
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		target = get_payment_entry(doc.doctype, doc.name)
	elif method == "dunning_payment":
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		target = get_payment_entry(doc.doctype, doc.name)
	elif method == "opportunity_quotation":
		from erpnext.crm.doctype.opportunity.opportunity import make_quotation
		target = make_quotation(doc.name)
	elif method == "lead_customer":
		from erpnext.crm.doctype.lead.lead import make_customer
		target = make_customer(doc.name)
	else:
		frappe.throw(_("Mapped action is not available."), frappe.PermissionError)
	target.insert()
	target_record = get_feature(frappe.scrub(target.doctype).replace("_", "-"))
	return {
		"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus,
		"modified": target.modified, "route": _record_route(target_record, target.name, "edit"),
	}


def _available_workflow_actions(doc) -> list[dict]:
	from frappe.model.workflow import get_transitions, get_workflow_name
	if not get_workflow_name(doc.doctype):
		return []
	return [
		{"action": row.action, "label": row.action, "destructive": False, "kind": "workflow", "next_state": row.next_state}
		for row in (get_transitions(doc) or [])
	]


@frappe.whitelist(methods=["GET"])
def get_document_actions(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	return {"actions": [*_available_actions(doc.meta, doc), *_available_workflow_actions(doc)], "modified": doc.modified, "docstatus": doc.docstatus}


@frappe.whitelist(methods=["POST"])
def run_document_action(feature: str, name: str, action: str, modified: str | None = None, parameters: Any = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	allowed = {item["action"] for item in _available_actions(doc.meta, doc)}
	if action not in allowed:
		frappe.throw(_("Action is not available."), frappe.PermissionError)
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before continuing."), frappe.TimestampMismatchError)
	parameters = _parse(parameters or {}, dict, "Action parameters")
	if action == "submit":
		doc.submit()
	elif action == "cancel":
		doc.cancel()
	elif action == "delete":
		frappe.delete_doc(doc.doctype, doc.name)
		return {"deleted": True, "route": _record_route(record)}
	elif action == "duplicate":
		copy = frappe.copy_doc(doc, ignore_no_copy=False)
		copy.docstatus = 0
		copy.insert()
		doc = copy
	elif action == "amend":
		amendment = frappe.copy_doc(doc, ignore_no_copy=False)
		amendment.amended_from = doc.name
		amendment.docstatus = 0
		amendment.insert()
		doc = amendment
	elif action == "rename":
		new_name = str(parameters.get("new_name") or "").strip()
		if not new_name or len(new_name) > 140 or any(character in new_name for character in ("/", "\x00")):
			frappe.throw(_("A valid new name is required."), frappe.ValidationError)
		from frappe.model.rename_doc import rename_doc
		new_name = rename_doc(doc=doc, new=new_name)
		doc = frappe.get_doc(doc.doctype, new_name)
	elif action in {"close", "reopen"} and doc.doctype == "Opportunity":
		doc.status = "Closed" if action == "close" else "Open"
		if action == "reopen" and doc.meta.has_field("lost_reasons"):
			doc.set("lost_reasons", [])
		doc.save()
	elif action in {"hold", "resume"} and doc.doctype == "Supplier":
		doc.on_hold = 0 if action == "resume" else 1
		doc.hold_type = "" if action == "resume" else (doc.hold_type or "All")
		doc.save()
	elif action in {"stop", "reopen"} and doc.doctype == "Material Request":
		from erpnext.stock.doctype.material_request.material_request import update_status
		update_status(doc.name, "Stopped" if action == "stop" else "Submitted")
		doc.reload()
	elif action in {"hold", "resume", "close", "reopen"} and doc.doctype == "Purchase Order":
		from erpnext.buying.doctype.purchase_order.purchase_order import update_status
		if action == "hold":
			reason = str(parameters.get("reason_for_hold") or "").strip()
			if not reason:
				frappe.throw(_("A reason for hold is required."), frappe.ValidationError)
			doc.add_comment("Comment", _("Reason for hold: {0}").format(reason[:500]))
		status = {"hold": "On Hold", "resume": "Draft", "close": "Closed", "reopen": "Submitted"}[action]
		update_status(status, doc.name)
		doc.reload()
	elif action == "make_opportunity" and doc.doctype == "Lead":
		from erpnext.crm.doctype.lead.lead import make_opportunity
		target = make_opportunity(doc.name)
		target.insert()
		target_record = get_generated_feature("opportunity")
		return {"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus, "modified": target.modified, "route": _record_route(target_record, target.name)}
	elif action == "make_customer" and doc.doctype == "Opportunity":
		from erpnext.crm.doctype.opportunity.opportunity import make_customer
		target = make_customer(doc.name)
		target.insert()
		return {"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus, "modified": target.modified, "route": f"/sales/customers/{quote(target.name, safe='')}"}
	elif action == "chart_of_accounts" and doc.doctype == "Account":
		return {"route": "/retail-erp/finance/chart-of-accounts"}
	elif action == "chart_of_cost_centers" and doc.doctype == "Cost Center":
		return {"route": "/retail-erp/finance/cost-centers"}
	elif action == "budget" and doc.doctype == "Cost Center":
		return {"route": "/retail-erp/finance/budget"}
	elif action == "chart_of_accounts" and doc.doctype == "Company":
		return {"route": f"/retail-erp/finance/chart-of-accounts?{urlencode({'company': doc.name}, quote_via=quote)}"}
	elif action == "cost_centers" and doc.doctype == "Company":
		return {"route": f"/retail-erp/finance/cost-centers?{urlencode({'company': doc.name}, quote_via=quote)}"}
	elif action == "general_ledger" and doc.doctype in {"Account", "Warehouse"}:
		account = doc.name if doc.doctype == "Account" else frappe.db.get_value("Account", {"warehouse": doc.name, "company": doc.company}, "name")
		if not account:
			frappe.throw(_("No linked account found for General Ledger."), frappe.ValidationError)
		fiscal_year = frappe.defaults.get_user_default("fiscal_year") or frappe.defaults.get_global_default("fiscal_year")
		fiscal_year_dates = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"]) if fiscal_year else None
		from_date, to_date = fiscal_year_dates or (None, None)
		# quote_via=quote (not the default quote_plus) so the frontend's
		# route.query (decodeURIComponent-based, does not decode "+" as
		# space) reads these values back correctly.
		params = urlencode({k: v for k, v in {"account": account, "company": doc.company, "from_date": from_date, "to_date": to_date}.items() if v}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "ledger" and doc.doctype == "Journal Entry":
		params = urlencode({"voucher_no": doc.name, "company": doc.company, "from_date": str(doc.posting_date), "to_date": getdate().isoformat()}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action == "ledger" and doc.doctype == "Period Closing Voucher":
		params = urlencode({"voucher_no": doc.name, "company": doc.company, "from_date": str(doc.period_start_date), "to_date": str(doc.period_end_date)}, quote_via=quote)
		return {"route": f"/retail-erp/reports/view/{quote('General Ledger')}?{params}"}
	elif action in {"convert_to_group", "convert_to_non_group"} and doc.doctype in {"Account", "Cost Center"}:
		if action == "convert_to_group":
			doc.convert_ledger_to_group()
		else:
			doc.convert_group_to_ledger()
		doc.reload()
	elif action == "merge_account" and doc.doctype == "Account":
		new_account = str(parameters.get("new_account") or "").strip()
		if not new_account or not frappe.db.exists("Account", new_account) or not frappe.has_permission("Account", "write", doc=new_account):
			frappe.throw(_("A valid target account is required."), frappe.ValidationError)
		from erpnext.accounts.doctype.account.account import merge_account
		new_name = merge_account(doc.name, new_account) or new_account
		return {"name": new_name, "route": _record_route(record, new_name)}
	elif action == "update_account_name_number" and doc.doctype == "Account":
		account_name = str(parameters.get("account_name") or "").strip()
		account_number = str(parameters.get("account_number") or "").strip()
		if not account_name:
			frappe.throw(_("Account name is required."), frappe.ValidationError)
		from erpnext.accounts.doctype.account.account import update_account_number
		new_name = update_account_number(doc.name, account_name, account_number) or doc.name
		return {"name": new_name, "route": _record_route(record, new_name)}
	elif action == "update_cost_center_name_number" and doc.doctype == "Cost Center":
		cc_name = str(parameters.get("cost_center_name") or "").strip()
		cc_number = str(parameters.get("cost_center_number") or "").strip()
		if not cc_name:
			frappe.throw(_("Cost center name is required."), frappe.ValidationError)
		from erpnext.accounts.utils import update_cost_center
		new_name = update_cost_center(doc.name, cc_name, cc_number, doc.company, 0) or doc.name
		return {"name": new_name, "route": _record_route(record, new_name)}
	elif action == "make_jv_entries" and doc.doctype == "Exchange Rate Revaluation":
		if not doc.check_journal_entry_condition():
			frappe.throw(_("Journal entries are already up to date for this revaluation."), frappe.ValidationError)
		result = doc.make_jv_entries()
		return {"name": doc.name, "docstatus": doc.docstatus, "modified": doc.modified, "route": _record_route(record, doc.name), "created": result}
	elif action == "resolve" and doc.doctype == "Dunning":
		doc.status = "Resolved"
		doc.save()
	elif action == "block_invoice" and doc.doctype == "Purchase Invoice":
		release_date = str(parameters.get("release_date") or "").strip()
		if not release_date:
			frappe.throw(_("A release date is required."), frappe.ValidationError)
		hold_comment = str(parameters.get("hold_comment") or "").strip() or None
		doc.block_invoice(hold_comment, release_date)
		doc.reload()
	elif action == "unblock_invoice" and doc.doctype == "Purchase Invoice":
		doc.unblock_invoice()
		doc.reload()
	elif action == "change_release_date" and doc.doctype == "Purchase Invoice":
		release_date = str(parameters.get("release_date") or "").strip()
		if not release_date:
			frappe.throw(_("A release date is required."), frappe.ValidationError)
		doc.db_set("release_date", release_date)
		doc.reload()
	elif action in {"start_pcv_processing", "pause_pcv_processing", "resume_pcv_processing"} and doc.doctype == "Process Period Closing Voucher":
		from erpnext.accounts.doctype.process_period_closing_voucher import process_period_closing_voucher as pcv_module
		getattr(pcv_module, action)(doc.name)
		doc.reload()
	elif action in MAPPED_ACTIONS.get(doc.doctype, {}):
		return _run_mapped_action(doc, action, parameters)
	return {"name": doc.name, "docstatus": doc.docstatus, "modified": doc.modified, "route": _record_route(record, doc.name)}


@frappe.whitelist(methods=["GET"])
def get_workflow_actions(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	from frappe.model.workflow import get_transitions, get_workflow_name
	if not get_workflow_name(doc.doctype):
		return {"actions": []}
	return {"actions": [{"action": row.action, "next_state": row.next_state, "allowed": row.allowed} for row in (get_transitions(doc) or [])]}


@frappe.whitelist(methods=["POST"])
def run_workflow_action(feature: str, name: str, action: str, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name, "write")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it."), frappe.TimestampMismatchError)
	from frappe.model.workflow import apply_workflow, get_transitions, get_workflow_name
	if not get_workflow_name(doc.doctype):
		frappe.throw(_("Workflow action is not available."), frappe.PermissionError)
	if action not in {row.action for row in (get_transitions(doc) or [])}:
		frappe.throw(_("Workflow action is not available."), frappe.PermissionError)
	updated = apply_workflow(doc, action)
	return {"name": updated.name, "docstatus": updated.docstatus, "modified": updated.modified}


@frappe.whitelist(methods=["GET"])
def get_link_options(feature: str, fieldname: str, search: str = "", parent_fieldname: str | None = None, dynamic_doctype: str | None = None):
	_require_login()
	_record, meta, readable, _writable = _metadata(feature)
	field = meta.get_field(fieldname)
	if parent_fieldname:
		parent = meta.get_field(parent_fieldname)
		field = frappe.get_meta(parent.options).get_field(fieldname) if parent and parent.fieldtype in {"Table", "Table MultiSelect"} else None
	readable_names = {item.fieldname for item in readable}
	if not field or (not parent_fieldname and fieldname not in readable_names) or field.fieldtype not in {"Link", "Dynamic Link"} or not field.options:
		frappe.throw(_("Link field is not available."), frappe.PermissionError)
	target_doctype = field.options if field.fieldtype == "Link" else str(dynamic_doctype or "").strip()
	if field.fieldtype == "Dynamic Link":
		context_meta = frappe.get_meta(parent.options) if parent_fieldname and parent else meta
		type_field = context_meta.get_field(field.options)
		if not type_field or not target_doctype or not frappe.db.exists("DocType", target_doctype):
			frappe.throw(_("Link field is not available."), frappe.PermissionError)
		if type_field.fieldtype == "Select" and target_doctype not in [value for value in (type_field.options or "").splitlines() if value]:
			frappe.throw(_("Link field is not available."), frappe.PermissionError)
	if not frappe.has_permission(target_doctype, "read"):
		frappe.throw(_("Link field is not available."), frappe.PermissionError)
	meta_target = frappe.get_meta(target_doctype)
	search = (search or "").strip()[:140]
	search_fields = ["name", meta_target.title_field] + [value.strip() for value in (meta_target.search_fields or "").split(",") if value.strip()]
	or_filters = [[name, "like", f"%{search}%"] for name in dict.fromkeys(search_fields) if name and meta_target.has_field(name)] if search else []
	fields = ["name"] + ([meta_target.title_field] if meta_target.title_field and meta_target.has_field(meta_target.title_field) else [])
	rows = frappe.get_list(target_doctype, fields=fields, or_filters=or_filters, order_by="modified desc", limit_page_length=MAX_LINK_RESULTS)
	return {"results": [{"value": row.name, "label": row.get(meta_target.title_field) or row.name} for row in rows]}


@frappe.whitelist(methods=["GET"])
def get_related_documents(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	# The generic foundation exposes only permission-filtered Dynamic Link records.
	rows = frappe.get_list("Dynamic Link", filters={"link_doctype": doc.doctype, "link_name": doc.name}, fields=["parenttype", "parent"], limit_page_length=50)
	result = []
	for row in rows:
		if row.parenttype in ALL_GENERATED_DOCTYPES and frappe.has_permission(row.parenttype, "read") and frappe.get_list(row.parenttype, filters={"name": row.parent}, pluck="name", limit_page_length=1):
			target = get_feature(frappe.scrub(row.parenttype).replace("_", "-"))
			result.append({"doctype": row.parenttype, "name": row.parent, "route": _record_route(target, row.parent)})
	return {"records": result}


@frappe.whitelist(methods=["GET"])
def get_document_timeline(feature: str, name: str):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name)
	rows = frappe.get_list("Comment", filters={"reference_doctype": doc.doctype, "reference_name": doc.name, "comment_type": ["in", ["Comment", "Info", "Edit"]]}, fields=["name", "comment_type", "content", "owner", "creation"], order_by="creation desc", limit_page_length=MAX_TIMELINE_ROWS)
	return {"records": rows}


@frappe.whitelist(methods=["GET"])
def get_print_formats(feature: str, name: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	if name:
		_get_permitted_doc(record["doctype"], name)
	if not frappe.has_permission(record["doctype"], "print"):
		frappe.throw(_("Print is not available."), frappe.PermissionError)
	formats = frappe.get_list("Print Format", filters={"doc_type": record["doctype"], "disabled": 0}, pluck="name", order_by="name asc")
	letterheads = []
	if frappe.has_permission("Letter Head", "read"):
		letterheads = frappe.get_list("Letter Head", filters={"disabled": 0}, fields=["name", "is_default"], order_by="is_default desc, name asc", limit_page_length=100)
	language = frappe.local.lang or frappe.db.get_default("lang") or "en"
	base = {"doctype": record["doctype"], "name": name or ""}
	return {
		"formats": ["Standard", *formats], "letterheads": letterheads,
		"languages": [{"value": language, "label": language}], "default_language": language,
		"print_url": f"/printview?{urlencode(base)}" if name else None,
		"pdf_url": f"/api/method/frappe.utils.print_format.download_pdf?{urlencode(base)}" if name else None,
		"pdf_environment": {"available": bool(shutil.which("wkhtmltopdf")), "generator": "wkhtmltopdf", "installation_required": not bool(shutil.which("wkhtmltopdf"))},
	}


def _special_definition(feature: str, expected_type: str) -> tuple[dict, Any]:
	record = get_feature(feature)
	if record.get("category") != expected_type or not feature_is_permitted(record):
		frappe.throw(_("Feature is not available."), frappe.PermissionError)
	name = record.get(expected_type) or record.get("feature_label")
	return record, name


@frappe.whitelist(methods=["GET"])
def get_report_definition(feature: str):
	_require_login()
	record, name = _special_definition(feature, "report")
	from frappe.desk.query_report import get_report_doc
	report = get_report_doc(name)
	return {"feature": _public_feature(record), "name": report.name, "report_type": report.report_type, "reference_doctype": report.ref_doctype, "prepared_report": bool(report.prepared_report), "custom_filters": report.get("custom_filters") or [], "client_filter_policy": "not_executed"}


@frappe.whitelist(methods=["POST"])
def run_report(feature: str, filters: Any = None):
	_require_login()
	record, name = _special_definition(feature, "report")
	from frappe.desk.query_report import run
	return run(name, filters=_parse(filters or {}, dict, "Filters"), ignore_prepared_report=False)


@frappe.whitelist(methods=["GET"])
def get_workspace_definition(feature: str):
	_require_login()
	record, name = _special_definition(feature, "workspace")
	workspace = frappe.get_doc("Workspace", name)
	# Workspace JSON can contain targets the user cannot read.  A later adapter
	# will resolve each block independently; never return raw content meanwhile.
	return {"feature": _public_feature(record), "name": workspace.name, "title": workspace.title, "module": workspace.module, "status": "permission_filtered_adapter_required"}


@frappe.whitelist(methods=["GET"])
def get_dashboard_definition(feature: str):
	_require_login()
	record = get_feature(feature)
	if record.get("category") not in {"dashboard", "dashboard_chart", "number_card"} or not feature_is_permitted(record):
		frappe.throw(_("Dashboard is not available."), frappe.PermissionError)
	return {"feature": _public_feature(record), "status": "special_adapter_required"}
