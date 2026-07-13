"""Allowlisted Delivery Note and Sales Invoice lifecycle actions.

This module deliberately exposes entity keys, not arbitrary DocTypes or
controller methods.  ERPNext documents remain responsible for stock,
accounting, serial/batch, workflow, and linked-document validation.
"""

from __future__ import annotations

import json
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.entity_api import _require_login
from my_store_ui.services.permissions import get_document_permissions


ENTITY_REGISTRY = {
	"delivery_notes": {
		"doctype": "Delivery Note", "route": "/sales/delivery-notes/{name}",
		"actions": {
			"submit": {"permission": "can_submit", "docstatus": 0, "confirm": True},
			"cancel": {"permission": "can_cancel", "docstatus": 1, "confirm": True},
			"amend": {"permission": "can_create", "docstatus": 2, "confirm": True},
			"close": {"permission": "can_submit", "docstatus": 1, "confirm": True},
			"reopen": {"permission": "can_submit", "docstatus": 1, "confirm": True},
		},
		"mapped": {
			"sales_invoice": {"doctype": "Sales Invoice", "route": "/sales/invoices/{name}/edit"},
			"return": {"doctype": "Delivery Note", "route": "/sales/delivery-notes/{name}/edit"},
		},
	},
	"sales_invoices": {
		"doctype": "Sales Invoice", "route": "/sales/invoices/{name}",
		"actions": {
			"submit": {"permission": "can_submit", "docstatus": 0, "confirm": True},
			"cancel": {"permission": "can_cancel", "docstatus": 1, "confirm": True},
			"amend": {"permission": "can_create", "docstatus": 2, "confirm": True},
		},
		"mapped": {
			"return": {"doctype": "Sales Invoice", "route": "/sales/invoices/{name}/edit"},
			"payment_entry": {"doctype": "Payment Entry", "route": "/finance/payments/{name}/edit"},
		},
	},
	"payment_entries": {
		"doctype": "Payment Entry", "route": "/finance/payments/{name}",
		"actions": {
			"submit": {"permission": "can_submit", "docstatus": 0, "confirm": True},
			"cancel": {"permission": "can_cancel", "docstatus": 1, "confirm": True},
			"amend": {"permission": "can_create", "docstatus": 2, "confirm": True},
		}, "mapped": {},
	},
}


def _parse_json(value, label, default=None):
	if value is None:
		return default
	if isinstance(value, str):
		try:
			return json.loads(value)
		except ValueError:
			frappe.throw(_("{0} must be valid JSON.").format(label), frappe.ValidationError)
	return value


def _definition(entity_key):
	if entity_key not in ENTITY_REGISTRY:
		frappe.throw(_("Unsupported Retail ERP document."), frappe.ValidationError)
	return ENTITY_REGISTRY[entity_key]


def _load(entity_key, name):
	_require_login()
	definition = _definition(entity_key)
	if not isinstance(name, str) or not name.strip() or len(name) > 140:
		frappe.throw(_("Invalid document name."), frappe.ValidationError)
	doctype = definition["doctype"]
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("You do not have permission to access this document."), frappe.PermissionError)
	# get_list applies User Permissions and avoids leaking inaccessible names.
	if not frappe.get_list(doctype, filters={"name": name.strip()}, pluck="name", limit_page_length=1):
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)
	doc = frappe.get_doc(doctype, name.strip())
	if not frappe.has_permission(doctype, "read", doc=doc):
		frappe.throw(_("Record not found or unavailable."), frappe.DoesNotExistError)
	return doc, definition


def _workflow(doctype):
	return frappe.db.get_value("Workflow", {"document_type": doctype, "is_active": 1}, "name")


def _fresh(doc, expected_modified):
	if expected_modified and str(doc.modified) != str(expected_modified):
		frappe.throw(_("This document has changed. Refresh before continuing."), frappe.ValidationError)


def _can_map(doc, target):
	if doc.docstatus != 1:
		return False
	if doc.doctype == "Delivery Note":
		if target == "sales_invoice":
			return doc.status != "Closed" and not cint(doc.is_return) and flt(doc.per_billed) < 100
		return not cint(doc.is_return) and flt(doc.per_returned) < 100
	if target == "payment_entry":
		return not cint(doc.is_return) and flt(doc.outstanding_amount) > 0
	return not cint(doc.is_return)


def _available(doc, definition):
	permissions = get_document_permissions(doc)
	workflow = _workflow(doc.doctype)
	result = []
	for key, action in definition["actions"].items():
		if doc.docstatus != action["docstatus"] or workflow:
			continue
		if key == "close" and getattr(doc, "status", "") == "Closed":
			continue
		if key == "reopen" and getattr(doc, "status", "") != "Closed":
			continue
		if permissions.get(action["permission"]):
			result.append({"key": key, "label": key.replace("_", " ").title(), "confirm": action["confirm"]})
	for key, target in definition["mapped"].items():
		if _can_map(doc, key) and frappe.has_permission(target["doctype"], "create"):
			result.append({"key": f"create_{key}", "label": ("Create Return" if key == "return" else f"Create {target['doctype']}"), "confirm": False})
	return result


def _print_formats(doctype):
	formats = [{"name": "Standard", "label": _("Standard")}]
	for row in frappe.get_list("Print Format", filters={"doc_type": doctype, "disabled": 0}, fields=["name"], order_by="name asc"):
		formats.append({"name": row.name, "label": row.name})
	return formats


def _result(doc, definition):
	return {
		"name": doc.name, "doctype": doc.doctype,
		"route": definition["route"].format(name=quote(doc.name, safe="")),
		"docstatus": doc.docstatus, "status": doc.get("status"), "modified": str(doc.modified),
		"actions": _available(doc, definition),
	}


@frappe.whitelist()
def get_document_actions(entity_key, name):
	doc, definition = _load(entity_key, name)
	return {
		**_result(doc, definition), "workflow": _workflow(doc.doctype),
		"print": {"can_print": bool(frappe.has_permission(doc.doctype, "print", doc=doc)), "formats": _print_formats(doc.doctype) if frappe.has_permission(doc.doctype, "print", doc=doc) else []},
		"email_prepared": doc.doctype == "Sales Invoice",
	}


@frappe.whitelist()
def execute_document_action(entity_key, name, action, expected_modified=None, params=None):
	doc, definition = _load(entity_key, name)
	if action not in definition["actions"]:
		frappe.throw(_("Unsupported document action."), frappe.ValidationError)
	_fresh(doc, expected_modified)
	action_def = definition["actions"][action]
	if doc.docstatus != action_def["docstatus"]:
		frappe.throw(_("This action is not available for the current document state."), frappe.ValidationError)
	if _workflow(doc.doctype):
		frappe.throw(_("An active workflow controls this document."), frappe.PermissionError)
	if not get_document_permissions(doc).get(action_def["permission"]):
		frappe.throw(_("You do not have permission for this action."), frappe.PermissionError)
	if action == "submit":
		doc.submit()
	elif action == "cancel":
		doc.cancel()
	elif action == "amend":
		amendment = frappe.copy_doc(doc)
		amendment.amended_from = doc.name
		amendment.docstatus = 0
		amendment.insert()
		doc = amendment
	elif action in {"close", "reopen"}:
		doc.update_status("Closed" if action == "close" else "Submitted")
		doc.reload()
	return _result(doc, definition)


def _selected_rows(doc, selected_items):
	selected_items = _parse_json(selected_items, _("Selected items"), None)
	if selected_items is None:
		return [row.name for row in doc.items]
	if not isinstance(selected_items, list):
		frappe.throw(_("Selected items must be a list."), frappe.ValidationError)
	known = {row.name for row in doc.items}
	selected = []
	for entry in selected_items:
		if not isinstance(entry, dict) or entry.get("name") not in known:
			frappe.throw(_("Invalid item selection."), frappe.ValidationError)
		if entry.get("qty") is not None and flt(entry["qty"]) <= 0:
			frappe.throw(_("Transfer quantity must be greater than zero."), frappe.ValidationError)
		selected.append(entry["name"])
	return selected


def _map(doc, target, selected):
	if not _can_map(doc, target):
		frappe.throw(_("This mapped action is not available."), frappe.ValidationError)
	if doc.doctype == "Delivery Note" and target == "sales_invoice":
		from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
		return make_sales_invoice(doc.name, args={"filtered_children": selected})
	if target == "return":
		from erpnext.controllers.sales_and_purchase_return import make_return_doc
		return make_return_doc(doc.doctype, doc.name)
	if doc.doctype == "Sales Invoice" and target == "payment_entry":
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		return get_payment_entry("Sales Invoice", doc.name)
	frappe.throw(_("Unsupported mapped document."), frappe.ValidationError)


def _preview(doc, target, mapped, selected):
	return {
		"target": target, "target_doctype": mapped.doctype, "source": doc.name, "customer": doc.get("customer"), "currency": mapped.get("currency") or doc.get("currency"),
		"warnings": [], "items": [{"source_row": row.name, "item_code": row.item_code, "item_name": row.item_name, "transfer_qty": abs(flt(row.qty)), "warehouse": row.get("warehouse")} for row in mapped.get("items", [])],
		"references": [{"reference_doctype": row.reference_doctype, "reference_name": row.reference_name, "allocated_amount": row.allocated_amount} for row in mapped.get("references", [])],
		"totals": {"net_total": mapped.get("net_total"), "taxes": mapped.get("total_taxes_and_charges"), "grand_total": mapped.get("grand_total"), "paid_amount": mapped.get("paid_amount")},
	}


@frappe.whitelist()
def get_mapped_document_preview(entity_key, name, target, selected_items=None, expected_modified=None):
	doc, definition = _load(entity_key, name)
	_fresh(doc, expected_modified)
	if target not in definition["mapped"] or not frappe.has_permission(definition["mapped"][target]["doctype"], "create"):
		frappe.throw(_("You do not have permission to create this mapped document."), frappe.PermissionError)
	selected = _selected_rows(doc, selected_items)
	mapped = _map(doc, target, selected)
	return _preview(doc, target, mapped, selected)


@frappe.whitelist()
def create_mapped_document(entity_key, name, target, selected_items=None, expected_modified=None, request_id=None):
	doc, definition = _load(entity_key, name)
	_fresh(doc, expected_modified)
	if target not in definition["mapped"] or not frappe.has_permission(definition["mapped"][target]["doctype"], "create"):
		frappe.throw(_("You do not have permission to create this mapped document."), frappe.PermissionError)
	if request_id:
		cache_key = f"retail_erp_mapped:{frappe.session.user}:{entity_key}:{name}:{target}:{request_id}"
		if saved_name := frappe.cache.get_value(cache_key):
			mapped_target = definition["mapped"][target]
			return {"name": saved_name, "route": mapped_target["route"].format(name=quote(saved_name, safe="")), "duplicate": True}
	selected = _selected_rows(doc, selected_items)
	mapped = _map(doc, target, selected)
	if mapped.get("items") is not None and not mapped.get("items") and target != "payment_entry":
		frappe.throw(_("No eligible items remain to map."), frappe.ValidationError)
	mapped.flags.ignore_permissions = False
	mapped.insert()
	if request_id:
		frappe.cache.set_value(cache_key, mapped.name, expires_in_sec=300)
	mapped_target = definition["mapped"][target]
	return {"name": mapped.name, "doctype": mapped.doctype, "route": mapped_target["route"].format(name=quote(mapped.name, safe="")), "docstatus": mapped.docstatus, "preview": _preview(doc, target, mapped, selected), "duplicate": False}
