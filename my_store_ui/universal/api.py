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
	GENERATED_ALLOWLIST,
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
		and field.fieldtype not in LAYOUT_FIELDS | {"HTML", "Button", "Dynamic Link"}
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
	return {"feature": _public_feature(record), "records": rows, "columns": [column_map[name] for name in columns], "permissions": _permissions(meta.name), "pagination": {"page": page, "page_size": page_size, "total": total, "pages": max((total + page_size - 1) // page_size, 1)}}


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
	return {"feature": _public_feature(record), "metadata": get_doctype_metadata(feature), "document": _visible_doc(doc, meta, readable), "permissions": _permissions(meta.name, doc=doc), "actions": [*_available_actions(meta, doc), *_available_workflow_actions(doc)], "route": f"/generated/{record['route_key']}/{quote(doc.name, safe='')}"}


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


def _clean_payload(meta, payload: Any) -> dict:
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
				rows.append({key: _coerce_value(child_write[key], item) for key, item in row.items() if key in child_write})
			clean[fieldname] = rows
		else:
			clean[fieldname] = _coerce_value(field, value)
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
	return {"name": doc.name, "route": f"/generated/{record['route_key']}/{quote(doc.name, safe='')}", "modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def update_document(feature: str, name: str, values: Any, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	meta = frappe.get_meta(record["doctype"])
	doc = _get_permitted_doc(meta.name, name, "write")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before saving."), frappe.TimestampMismatchError)
	doc.update(_clean_payload(meta, values))
	doc.save()
	return {"name": doc.name, "route": f"/generated/{record['route_key']}/{quote(doc.name, safe='')}", "modified": doc.modified}


@frappe.whitelist(methods=["POST"])
def delete_document(feature: str, name: str, modified: str | None = None):
	_require_login()
	record = get_generated_feature(feature)
	doc = _get_permitted_doc(record["doctype"], name, "delete")
	if modified and str(doc.modified) != str(modified):
		frappe.throw(_("This record changed after you opened it. Refresh before deleting."), frappe.TimestampMismatchError)
	frappe.delete_doc(doc.doctype, doc.name)
	return {"deleted": True, "route": f"/generated/{record['route_key']}"}


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
	if doc.doctype == "Lead" and frappe.has_permission("Opportunity", "create"):
		actions.append({"action": "make_opportunity", "label": _("Create Opportunity"), "destructive": False, "mapping_target": "Opportunity"})
	if doc.doctype == "Opportunity" and frappe.has_permission("Customer", "create"):
		actions.append({"action": "make_customer", "label": _("Create Customer"), "destructive": False, "mapping_target": "Customer"})
	return actions


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
		return {"deleted": True, "route": f"/generated/{record['route_key']}"}
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
	elif action == "make_opportunity" and doc.doctype == "Lead":
		from erpnext.crm.doctype.lead.lead import make_opportunity
		target = make_opportunity(doc.name)
		target.insert()
		target_record = get_generated_feature("opportunity")
		return {"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus, "modified": target.modified, "route": f"/generated/{target_record['route_key']}/{quote(target.name, safe='')}"}
	elif action == "make_customer" and doc.doctype == "Opportunity":
		from erpnext.crm.doctype.opportunity.opportunity import make_customer
		target = make_customer(doc.name)
		target.insert()
		return {"name": target.name, "doctype": target.doctype, "docstatus": target.docstatus, "modified": target.modified, "route": f"/sales/customers/{quote(target.name, safe='')}"}
	return {"name": doc.name, "docstatus": doc.docstatus, "modified": doc.modified, "route": f"/generated/{record['route_key']}/{quote(doc.name, safe='')}"}


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
def get_link_options(feature: str, fieldname: str, search: str = "", parent_fieldname: str | None = None):
	_require_login()
	_record, meta, readable, _writable = _metadata(feature)
	field = meta.get_field(fieldname)
	if parent_fieldname:
		parent = meta.get_field(parent_fieldname)
		field = frappe.get_meta(parent.options).get_field(fieldname) if parent and parent.fieldtype in {"Table", "Table MultiSelect"} else None
	readable_names = {item.fieldname for item in readable}
	if not field or (not parent_fieldname and fieldname not in readable_names) or field.fieldtype != "Link" or not field.options:
		frappe.throw(_("Link field is not available."), frappe.PermissionError)
	if not frappe.has_permission(field.options, "read"):
		frappe.throw(_("Link field is not available."), frappe.PermissionError)
	meta_target = frappe.get_meta(field.options)
	search = (search or "").strip()[:140]
	search_fields = ["name", meta_target.title_field] + [value.strip() for value in (meta_target.search_fields or "").split(",") if value.strip()]
	or_filters = [[name, "like", f"%{search}%"] for name in dict.fromkeys(search_fields) if name and meta_target.has_field(name)] if search else []
	fields = ["name"] + ([meta_target.title_field] if meta_target.title_field and meta_target.has_field(meta_target.title_field) else [])
	rows = frappe.get_list(field.options, fields=fields, or_filters=or_filters, order_by="modified desc", limit_page_length=MAX_LINK_RESULTS)
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
		if row.parenttype in GENERATED_ALLOWLIST and frappe.has_permission(row.parenttype, "read") and frappe.get_list(row.parenttype, filters={"name": row.parent}, pluck="name", limit_page_length=1):
			target = get_feature(frappe.scrub(row.parenttype).replace("_", "-"))
			result.append({"doctype": row.parenttype, "name": row.parent, "route": f"/generated/{target['route_key']}/{quote(row.parent, safe='')}"})
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
