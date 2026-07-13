"""Permission-aware Retail ERP draft form APIs.

The browser supplies only values for a fixed server registry. ERPNext document
controllers remain authoritative for all inserts, saves and totals.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import date
from typing import Any
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate, validate_email_address

from my_store_ui.entity_api import _require_login
from my_store_ui.services.form_schemas import get_entity_form_schema
from my_store_ui.services.permissions import can_open_standard_desk, get_doctype_permissions, get_document_permissions


LINK_LIMIT = 20
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,100}$")
NUMERIC_TYPES = {"Currency", "Percent", "Float", "Int"}


def _parse_object(value: str | dict | None, label: str) -> dict:
	if isinstance(value, str):
		try:
			value = json.loads(value)
		except ValueError:
			frappe.throw(_("{0} must be valid JSON.").format(label), frappe.ValidationError)
	if not isinstance(value, dict):
		frappe.throw(_("{0} must be an object.").format(label), frappe.ValidationError)
	return value


def _allowed_field_map(schema: dict) -> dict:
	return {definition["fieldname"]: definition for definition in schema["fields"]}


def _available_document(doc, doctype: str, name: str) -> bool:
	return bool(frappe.get_list(doctype, filters={"name": name}, pluck="name", limit_page_length=1))


def _validate_link(doctype: str, value: Any, label: str) -> str | None:
	if value in (None, ""):
		return None
	if not isinstance(value, str) or len(value) > 140:
		frappe.throw(_("Invalid {0}.").format(label), frappe.ValidationError)
	if not frappe.has_permission(doctype, "read") or not _available_document(None, doctype, value):
		frappe.throw(_("Invalid or unavailable {0}.").format(label), frappe.ValidationError)
	return value


def _normalise_value(definition: dict, value: Any):
	fieldtype = definition["fieldtype"]
	if definition.get("read_only"):
		return None
	if value in (None, ""):
		return None
	if fieldtype == "Link":
		return _validate_link(definition["options"], value, definition["label"])
	if fieldtype == "Select":
		if value not in set(definition.get("options") or ()):
			frappe.throw(_("Invalid value for {0}.").format(definition["label"]), frappe.ValidationError)
		return value
	if fieldtype == "Check":
		return cint(value)
	if fieldtype in NUMERIC_TYPES:
		value = flt(value)
		if fieldtype in {"Currency", "Percent"} and value < 0:
			frappe.throw(_("{0} cannot be negative.").format(definition["label"]), frappe.ValidationError)
		return value
	if fieldtype == "Date":
		try:
			return str(getdate(value))
		except Exception:
			frappe.throw(_("Invalid date for {0}.").format(definition["label"]), frappe.ValidationError)
	if not isinstance(value, str):
		frappe.throw(_("Invalid value for {0}.").format(definition["label"]), frappe.ValidationError)
	return value.strip()[:10000]


def _validate_payload(schema: dict, values: dict) -> dict:
	allowed = _allowed_field_map(schema)
	unknown = set(values) - set(allowed) - set(schema.get("child_tables", {}))
	if unknown:
		frappe.throw(_("Unsupported field: {0}.").format(", ".join(sorted(unknown))), frappe.ValidationError)
	clean = {}
	for fieldname, definition in allowed.items():
		value = _normalise_value(definition, values.get(fieldname))
		if definition.get("required") and value in (None, ""):
			frappe.throw(_("{0} is required.").format(definition["label"]), frappe.ValidationError)
		if value is not None:
			clean[fieldname] = value
	if schema["doctype"] == "Customer" and clean.get("email_id"):
		validate_email_address(clean["email_id"], throw=True)
	return clean


def _validate_items(schema: dict, values: dict) -> list[dict]:
	definition = schema.get("child_tables", {}).get("items")
	if not definition:
		return []
	rows = values.get("items", [])
	if not isinstance(rows, list) or len(rows) < definition.get("min_rows", 0):
		frappe.throw(_("At least one item is required."), frappe.ValidationError)
	allowed = {field["fieldname"]: field for field in definition["fields"]}
	clean_rows = []
	for index, row in enumerate(rows, start=1):
		if not isinstance(row, dict):
			frappe.throw(_("Invalid item row {0}.").format(index), frappe.ValidationError)
		unknown = set(row) - set(allowed)
		if unknown:
			frappe.throw(_("Unsupported item field."), frappe.ValidationError)
		clean = {}
		if row.get("name"):
			clean["_row_name"] = str(row["name"])
		for fieldname, field_definition in allowed.items():
			value = _normalise_value(field_definition, row.get(fieldname))
			if field_definition.get("required") and value in (None, ""):
				frappe.throw(_("{0} is required in item row {1}.").format(field_definition["label"], index), frappe.ValidationError)
			if value is not None:
				clean[fieldname] = value
		if flt(clean.get("qty")) <= 0:
			frappe.throw(_("Quantity must be greater than zero in item row {0}.").format(index), frappe.ValidationError)
		clean_rows.append(clean)
	return clean_rows


def _apply_item_pricing(doc) -> None:
	purchase = flt(doc.get("custom_purchase_price"))
	additional = flt(doc.get("custom_additional_cost"))
	retail_pct = flt(doc.get("custom_retail_profit_percentage"))
	wholesale_pct = flt(doc.get("custom_wholesale_profit_percentage"))
	if min(purchase, additional, retail_pct, wholesale_pct) < 0:
		frappe.throw(_("Cost and profit values cannot be negative."), frappe.ValidationError)
	total = purchase + additional
	retail = total + total * retail_pct / 100
	wholesale = total + total * wholesale_pct / 100
	if retail < total or wholesale < total or wholesale > retail:
		frappe.throw(_("Wholesale price cannot exceed retail price or fall below cost."), frappe.ValidationError)
	doc.custom_total_cost = total
	doc.custom_retail_price = retail
	doc.custom_wholesale_price = wholesale


def _set_safe_values(doc, schema: dict, values: dict) -> None:
	for fieldname, value in values.items():
		if schema["doctype"] == "Item" and fieldname == "barcodes":
			continue
		doc.set(fieldname, value)
	if schema["doctype"] == "Item":
		barcode = values.get("barcodes")
		if barcode is not None:
			doc.set("barcodes", [{"barcode": barcode}]) if barcode else doc.set("barcodes", [])
		_apply_item_pricing(doc)


def _hydrate_sales_order_items(doc, rows: list[dict]) -> None:
	from erpnext.stock.get_item_details import get_item_details

	doc.set("items", [])
	for submitted in rows:
		# Prices, descriptions and UOMs are taken from ERPNext's item-detail service.
		args = {
			"doctype": "Sales Order", "company": doc.company, "customer": doc.customer,
			"selling_price_list": doc.selling_price_list, "currency": doc.currency,
			"transaction_date": doc.transaction_date, "delivery_date": submitted.get("delivery_date") or doc.delivery_date,
			"item_code": submitted["item_code"], "qty": submitted.get("qty", 1),
			"uom": submitted.get("uom"), "warehouse": submitted.get("warehouse") or doc.set_warehouse,
			"conversion_rate": doc.conversion_rate or 1,
		}
		details = get_item_details(args, doc=doc, for_validate=True)
		row = doc.append("items", {})
		for key in ("item_code", "item_name", "description", "uom", "stock_uom", "conversion_factor", "warehouse", "rate", "price_list_rate"):
			if details.get(key) is not None:
				row.set(key, details[key])
		row.qty = submitted["qty"]
		row.delivery_date = submitted.get("delivery_date") or doc.delivery_date
		row.discount_percentage = submitted.get("discount_percentage", 0)
		# Never trust a browser-supplied rate. The item-detail service above owns
		# price-list pricing; ERPNext recalculates totals again on save.
		if submitted.get("warehouse"):
			row.warehouse = submitted["warehouse"]
		doc.run_method("set_missing_values")
	doc.run_method("calculate_taxes_and_totals")


def _apply_existing_draft_items(doc, rows: list[dict]) -> None:
	"""Allow only approved changes to already mapped Draft transaction rows."""
	existing = {row.name: row for row in doc.get("items", [])}
	if len(rows) != len(existing) or any(row.get("_row_name") not in existing for row in rows):
		frappe.throw(_("Mapped item rows cannot be added, removed, or replaced."), frappe.ValidationError)
	for submitted in rows:
		row = existing[submitted["_row_name"]]
		for fieldname in ("description", "qty", "uom", "warehouse"):
			if fieldname in submitted:
				row.set(fieldname, submitted[fieldname])
		if flt(row.qty) <= 0:
			frappe.throw(_("Quantity must be greater than zero."), frappe.ValidationError)
	doc.run_method("set_missing_values")
	doc.run_method("calculate_taxes_and_totals")


def _form_document_values(doc, schema: dict) -> dict:
	values = {}
	for definition in schema["fields"]:
		fieldname = definition["fieldname"]
		if schema["doctype"] == "Item" and fieldname == "barcodes":
			values[fieldname] = (doc.get("barcodes") or [{}])[0].get("barcode") if doc.get("barcodes") else ""
		else:
			values[fieldname] = doc.get(fieldname)
	if "items" in schema.get("child_tables", {}):
		values["items"] = [{field["fieldname"]: (row.name if field["fieldname"] == "name" else row.get(field["fieldname"])) for field in schema["child_tables"]["items"]["fields"]} for row in doc.get("items", [])]
	return values


def _public_schema(schema: dict) -> dict:
	return {
		"doctype": schema["doctype"], "title": schema["title"], "back_route": schema["back_route"],
		"detail_route": schema["detail_route"], "draft_only": schema["draft_only"],
		"fields": list(schema["fields"]), "sections": [{"key": key, "title": title} for key, title in schema["sections"]],
		"child_tables": deepcopy(schema.get("child_tables", {})),
	}


def _load_editable_document(schema: dict, name: str):
	if not name or not isinstance(name, str) or len(name) > 140:
		frappe.throw(_("Invalid document name."), frappe.ValidationError)
	if not _available_document(None, schema["doctype"], name):
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)
	doc = frappe.get_doc(schema["doctype"], name)
	if not frappe.has_permission(schema["doctype"], "write", doc=doc):
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)
	if schema.get("draft_only") and cint(doc.docstatus) != 0:
		frappe.throw(_("Only Draft Sales Orders can be edited in Retail ERP."), frappe.PermissionError)
	return doc


@frappe.whitelist()
def get_entity_form(entity_key: str, name: str | None = None):
	_require_login()
	schema = get_entity_form_schema(entity_key)
	permissions = get_doctype_permissions(schema["doctype"])
	if name:
		doc = _load_editable_document(schema, name)
		permissions = get_document_permissions(doc)
		if not permissions["can_write"]:
			frappe.throw(_("You do not have permission to edit this record."), frappe.PermissionError)
	else:
		if schema.get("create_via_mapping_only"):
			frappe.throw(_("Create this document from a submitted Sales Order."), frappe.PermissionError)
		if not permissions["can_create"]:
			frappe.throw(_("You do not have permission to create this record."), frappe.PermissionError)
		doc = frappe.new_doc(schema["doctype"])
		if schema["doctype"] == "Sales Order":
			doc.transaction_date = nowdate()
			doc.delivery_date = nowdate()
	return {"entity": _public_schema(schema), "document": _form_document_values(doc, schema), "is_new": not bool(name), "permissions": permissions, "desk_route": None if not can_open_standard_desk() else f"/app/{frappe.scrub(schema['doctype']).replace('_', '-')}"}


@frappe.whitelist()
def get_mapped_draft_detail(entity_key: str, name: str):
	"""Read-only approved detail shape for mapped Delivery Notes and Invoices."""
	_require_login()
	if entity_key not in {"delivery_notes", "sales_invoices"}:
		frappe.throw(_("Unsupported mapped document."), frappe.ValidationError)
	schema = get_entity_form_schema(entity_key)
	if not frappe.has_permission(schema["doctype"], "read"):
		frappe.throw(_("You do not have permission to view this document."), frappe.PermissionError)
	if not _available_document(None, schema["doctype"], name):
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)
	doc = frappe.get_doc(schema["doctype"], name)
	if not frappe.has_permission(schema["doctype"], "read", doc=doc):
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)
	values = _form_document_values(doc, schema)
	values["name"] = doc.name
	return {"entity": _public_schema(schema), "document": values, "permissions": get_document_permissions(doc), "docstatus": doc.docstatus, "status": doc.status, "totals": {"currency": doc.currency, "net_total": doc.net_total, "taxes": doc.total_taxes_and_charges, "grand_total": doc.grand_total}, "modified": str(doc.modified)}


@frappe.whitelist()
def search_link_options(entity_key: str, fieldname: str, search: str = ""):
	_require_login()
	schema = get_entity_form_schema(entity_key)
	fields = _allowed_field_map(schema)
	for table in schema.get("child_tables", {}).values():
		fields.update({field["fieldname"]: field for field in table["fields"]})
	definition = fields.get(fieldname)
	if not definition or definition["fieldtype"] != "Link":
		frappe.throw(_("Unsupported Link field."), frappe.ValidationError)
	doctype = definition["options"]
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("You do not have permission to search this field."), frappe.PermissionError)
	search = (search or "").strip()[:80]
	filters = [["name", "like", f"%{search}%"]] if search else []
	meta = frappe.get_meta(doctype)
	title_field = meta.title_field if meta.title_field and meta.title_field != "name" else None
	result_fields = ["name"] + ([title_field] if title_field else [])
	rows = frappe.get_list(doctype, filters=filters, fields=result_fields, order_by="name asc", limit_page_length=LINK_LIMIT)
	return [{"value": row.name, "label": row.get(title_field) or row.name} for row in rows]


@frappe.whitelist()
def save_entity_form(entity_key: str, values: str | dict, name: str | None = None, request_id: str | None = None):
	_require_login()
	schema = get_entity_form_schema(entity_key)
	payload = _parse_object(values, _("Values"))
	if request_id and not REQUEST_ID_PATTERN.match(request_id):
		frappe.throw(_("Invalid request identifier."), frappe.ValidationError)
	cache_key = f"retail_erp_form:{frappe.session.user}:{entity_key}:{request_id}" if request_id else None
	if cache_key and (saved_name := frappe.cache.get_value(cache_key)):
		return {"name": saved_name, "route": schema["detail_route"].format(name=quote(saved_name, safe="")), "duplicate": True}

	if name:
		doc = _load_editable_document(schema, name)
		if not frappe.has_permission(schema["doctype"], "write", doc=doc):
			frappe.throw(_("You do not have permission to edit this record."), frappe.PermissionError)
	else:
		if schema.get("create_via_mapping_only"):
			frappe.throw(_("Create this document from a submitted Sales Order."), frappe.PermissionError)
		if not frappe.has_permission(schema["doctype"], "create"):
			frappe.throw(_("You do not have permission to create this record."), frappe.PermissionError)
		doc = frappe.new_doc(schema["doctype"])

	clean = _validate_payload(schema, payload)
	items = _validate_items(schema, payload) if schema.get("child_tables") else []
	if schema["doctype"] == "Sales Order":
		if clean.get("delivery_date") and clean.get("transaction_date") and getdate(clean["delivery_date"]) < getdate(clean["transaction_date"]):
			frappe.throw(_("Delivery Date cannot be before Transaction Date."), frappe.ValidationError)
	_set_safe_values(doc, schema, clean)
	if schema["doctype"] == "Sales Order":
		_hydrate_sales_order_items(doc, items)
	elif schema.get("child_tables"):
		_apply_existing_draft_items(doc, items)
	if doc.is_new():
		doc.insert()
	else:
		doc.save()
	if cache_key:
		frappe.cache.set_value(cache_key, doc.name, expires_in_sec=300)
	return {"name": doc.name, "route": schema["detail_route"].format(name=quote(doc.name, safe="")), "duplicate": False, "totals": {"currency": doc.get("currency"), "grand_total": doc.get("grand_total"), "net_total": doc.get("net_total")}}
