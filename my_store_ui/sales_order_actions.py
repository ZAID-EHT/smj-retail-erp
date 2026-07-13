"""Server-owned Sales Order lifecycle and official mapped-document actions."""

from __future__ import annotations

import json
from copy import copy
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.entity_api import _require_login
from my_store_ui.services.permissions import get_document_permissions


ACTION_REGISTRY = {
	"submit": {"label": _("Submit Sales Order"), "requires": "can_submit", "docstatus": 0, "confirm": True},
	"cancel": {"label": _("Cancel Sales Order"), "requires": "can_cancel", "docstatus": 1, "confirm": True},
	"amend": {"label": _("Amend Sales Order"), "requires": "can_create", "docstatus": 2, "confirm": True},
	"hold": {"label": _("Hold Sales Order"), "requires": "can_submit", "docstatus": 1, "confirm": True},
	"resume": {"label": _("Resume Sales Order"), "requires": "can_submit", "docstatus": 1, "confirm": True},
	"close": {"label": _("Close Sales Order"), "requires": "can_submit", "docstatus": 1, "confirm": True},
	"reopen": {"label": _("Re-open Sales Order"), "requires": "can_submit", "docstatus": 1, "confirm": True},
	"create_delivery_note": {"label": _("Create Delivery Note"), "requires": "can_create_delivery_note", "docstatus": 1, "confirm": False},
	"create_sales_invoice": {"label": _("Create Sales Invoice"), "requires": "can_create_sales_invoice", "docstatus": 1, "confirm": False},
}

MAPPED_TARGETS = {
	"delivery_note": {
		"doctype": "Delivery Note", "entity_key": "delivery_notes", "route": "/sales/delivery-notes/{name}/edit",
		"method": "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
	},
	"sales_invoice": {
		"doctype": "Sales Invoice", "entity_key": "sales_invoices", "route": "/sales/invoices/{name}/edit",
		"method": "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
	},
}


def _load_sales_order(name: str):
	_require_login()
	if not isinstance(name, str) or not name.strip() or len(name) > 140:
		frappe.throw(_("Invalid Sales Order."), frappe.ValidationError)
	if not frappe.has_permission("Sales Order", "read"):
		frappe.throw(_("You do not have permission to access Sales Orders."), frappe.PermissionError)
	rows = frappe.get_list("Sales Order", filters={"name": name.strip()}, pluck="name", limit_page_length=1)
	if not rows:
		frappe.throw(_("Sales Order not found or unavailable."), frappe.DoesNotExistError)
	doc = frappe.get_doc("Sales Order", rows[0])
	if not frappe.has_permission("Sales Order", "read", doc=doc):
		frappe.throw(_("Sales Order not found or unavailable."), frappe.DoesNotExistError)
	return doc


def _active_workflow() -> str | None:
	return frappe.db.get_value("Workflow", {"document_type": "Sales Order", "is_active": 1}, "name")


def _is_mappable(doc, target: str) -> bool:
	if doc.docstatus != 1 or doc.status in {"Closed", "On Hold", "Cancelled"}:
		return False
	if target == "delivery_note":
		return bool(flt(doc.per_delivered) < 100 and not cint(doc.skip_delivery_note))
	return bool(flt(doc.per_billed) < 100)


def _available_actions(doc) -> list[dict]:
	permissions = get_document_permissions(doc)
	workflow = _active_workflow()
	actions = []
	for key, definition in ACTION_REGISTRY.items():
		if doc.docstatus != definition["docstatus"]:
			continue
		if key in {"submit", "cancel", "hold", "resume", "close", "reopen"} and workflow:
			continue
		if key == "hold" and doc.status in {"On Hold", "Closed"}:
			continue
		if key == "resume" and doc.status != "On Hold":
			continue
		if key == "close" and (doc.status == "Closed" or (flt(doc.per_delivered) >= 100 and flt(doc.per_billed) >= 100)):
			continue
		if key == "reopen" and doc.status != "Closed":
			continue
		if key == "create_delivery_note":
			allowed = frappe.has_permission("Delivery Note", "create") and _is_mappable(doc, "delivery_note")
		elif key == "create_sales_invoice":
			allowed = frappe.has_permission("Sales Invoice", "create") and _is_mappable(doc, "sales_invoice")
		else:
			allowed = bool(permissions.get(definition["requires"]))
		if allowed:
			actions.append({"key": key, "label": definition["label"], "confirm": definition["confirm"]})
	return actions


def _assert_fresh(doc, expected_modified: str | None) -> None:
	if expected_modified and str(doc.modified) != str(expected_modified):
		frappe.throw(_("This Sales Order has changed. Refresh before continuing."), frappe.ValidationError)


def _parse_params(params: str | dict | None) -> dict:
	if not params:
		return {}
	if isinstance(params, str):
		try:
			params = json.loads(params)
		except ValueError:
			frappe.throw(_("Action parameters must be valid JSON."), frappe.ValidationError)
	if not isinstance(params, dict):
		frappe.throw(_("Action parameters must be an object."), frappe.ValidationError)
	return params


@frappe.whitelist()
def get_document_actions(name: str):
	"""Return actions only for one permitted Sales Order; no arbitrary DocType."""
	doc = _load_sales_order(name)
	return {
		"name": doc.name,
		"docstatus": doc.docstatus,
		"status": doc.status,
		"modified": str(doc.modified),
		"workflow": _active_workflow(),
		"actions": _available_actions(doc),
		"print": {
			"can_print": bool(frappe.has_permission("Sales Order", "print", doc=doc)),
			"formats": _print_formats("Sales Order") if frappe.has_permission("Sales Order", "print", doc=doc) else [],
		},
	}


def _print_formats(doctype: str) -> list[dict]:
	formats = [{"name": "Standard", "label": _("Standard")}]
	for row in frappe.get_list("Print Format", filters={"doc_type": doctype, "disabled": 0}, fields=["name", "print_format_type"], order_by="name asc"):
		formats.append({"name": row.name, "label": row.name})
	return formats


@frappe.whitelist()
def execute_document_action(name: str, action: str, expected_modified: str | None = None, params: str | dict | None = None):
	doc = _load_sales_order(name)
	if action not in {"submit", "cancel", "amend", "hold", "resume", "close", "reopen"}:
		frappe.throw(_("Unsupported document action."), frappe.ValidationError)
	_assert_fresh(doc, expected_modified)
	definition = ACTION_REGISTRY[action]
	if doc.docstatus != definition["docstatus"]:
		frappe.throw(_("This action is not available for the current document state."), frappe.ValidationError)
	if action == "submit":
		if _active_workflow():
			frappe.throw(_("An active workflow controls submission for this Sales Order."), frappe.PermissionError)
		if not frappe.has_permission("Sales Order", "submit", doc=doc):
			frappe.throw(_("You do not have permission to submit this Sales Order."), frappe.PermissionError)
		doc.submit()
		route = f"/sales/orders/{quote(doc.name, safe='')}"
	elif action == "cancel":
		if _active_workflow():
			frappe.throw(_("An active workflow controls cancellation for this Sales Order."), frappe.PermissionError)
		if not frappe.has_permission("Sales Order", "cancel", doc=doc):
			frappe.throw(_("You do not have permission to cancel this Sales Order."), frappe.PermissionError)
		reason = _parse_params(params).get("reason", "")
		doc.cancel()
		if isinstance(reason, str) and reason.strip():
			doc.add_comment("Comment", text=_("Cancellation reason: {0}").format(reason.strip()[:500]))
		route = f"/sales/orders/{quote(doc.name, safe='')}"
	elif action == "amend":
		if not frappe.has_permission("Sales Order", "create"):
			frappe.throw(_("You do not have permission to amend Sales Orders."), frappe.PermissionError)
		amendment = frappe.copy_doc(doc)
		amendment.amended_from = doc.name
		amendment.docstatus = 0
		amendment.insert()
		doc = amendment
		route = f"/sales/orders/{quote(doc.name, safe='')}/edit"
	else:
		if _active_workflow() or not frappe.has_permission("Sales Order", "submit", doc=doc):
			frappe.throw(_("You do not have permission to update this Sales Order status."), frappe.PermissionError)
		status = {"hold": "On Hold", "resume": "Draft", "close": "Closed", "reopen": "Draft"}[action]
		doc.update_status(status)
		doc.reload()
		route = f"/sales/orders/{quote(doc.name, safe='')}"
	return {"name": doc.name, "route": route, "docstatus": doc.docstatus, "status": doc.status, "modified": str(doc.modified), "actions": _available_actions(doc)}


def _parse_selected_items(doc, target: str, selected_items: str | list | None) -> dict[str, float]:
	if isinstance(selected_items, str):
		try:
			selected_items = json.loads(selected_items)
		except ValueError:
			frappe.throw(_("Selected items must be valid JSON."), frappe.ValidationError)
	if selected_items is None:
		selected_items = [{"name": row.name} for row in doc.items]
	if not isinstance(selected_items, list):
		frappe.throw(_("Selected items must be a list."), frappe.ValidationError)
	rows = {row.name: row for row in doc.items}
	result = {}
	for selected in selected_items:
		if not isinstance(selected, dict) or selected.get("name") not in rows:
			frappe.throw(_("Invalid Sales Order item selection."), frappe.ValidationError)
		row = rows[selected["name"]]
		remaining = flt(row.qty) - flt(row.delivered_qty) if target == "delivery_note" else (
			flt(row.qty) - flt(row.returned_qty) - (flt(row.billed_amt) / flt(row.rate) if flt(row.rate) else 0)
		)
		qty = flt(selected.get("qty") or remaining)
		if qty <= 0 or qty > flt(row.qty):
			frappe.throw(_("Invalid quantity for item {0}.").format(row.item_code), frappe.ValidationError)
		result[row.name] = qty
	return result


def _map_document(doc, target: str, selected: dict[str, float]):
	if target not in MAPPED_TARGETS or not _is_mappable(doc, target):
		frappe.throw(_("This mapped action is not available."), frappe.ValidationError)
	if target == "delivery_note":
		from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
		mapped = make_delivery_note(doc.name, kwargs={"filtered_children": list(selected)})
	else:
		from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
		mapped = make_sales_invoice(doc.name, args={"filtered_children": list(selected)})
	for row in mapped.items:
		if row.get("so_detail") in selected:
			row.qty = min(flt(row.qty), selected[row.so_detail])
	mapped.run_method("calculate_taxes_and_totals")
	return mapped


def _preview_payload(doc, target: str, mapped, selected: dict[str, float]) -> dict:
	return {
		"target": target, "target_doctype": MAPPED_TARGETS[target]["doctype"], "source": doc.name, "customer": doc.customer,
		"currency": mapped.currency or doc.currency, "warnings": [],
		"items": [{"source_row": row.name, "item_code": row.item_code, "item_name": row.item_name, "ordered_qty": row.qty, "delivered_qty": row.delivered_qty, "billed_amt": row.billed_amt, "transfer_qty": selected.get(row.name, 0), "warehouse": row.warehouse} for row in doc.items if row.name in selected],
		"totals": {"net_total": mapped.net_total, "taxes": mapped.total_taxes_and_charges, "grand_total": mapped.grand_total},
	}


@frappe.whitelist()
def get_mapped_document_preview(name: str, target: str, selected_items: str | list | None = None, expected_modified: str | None = None):
	doc = _load_sales_order(name)
	_assert_fresh(doc, expected_modified)
	if target not in MAPPED_TARGETS or not frappe.has_permission(MAPPED_TARGETS[target]["doctype"], "create"):
		frappe.throw(_("You do not have permission to create this mapped document."), frappe.PermissionError)
	selected = _parse_selected_items(doc, target, selected_items)
	mapped = _map_document(doc, target, selected)
	return _preview_payload(doc, target, mapped, selected)


@frappe.whitelist()
def create_mapped_document(name: str, target: str, selected_items: str | list | None = None, expected_modified: str | None = None):
	doc = _load_sales_order(name)
	_assert_fresh(doc, expected_modified)
	if target not in MAPPED_TARGETS or not frappe.has_permission(MAPPED_TARGETS[target]["doctype"], "create"):
		frappe.throw(_("You do not have permission to create this mapped document."), frappe.PermissionError)
	selected = _parse_selected_items(doc, target, selected_items)
	mapped = _map_document(doc, target, selected)
	if not mapped.items:
		frappe.throw(_("No eligible items remain to map."), frappe.ValidationError)
	# The official Sales Invoice mapper uses this flag internally while
	# calculating defaults. Creation itself must still enforce DocPerm.
	mapped.flags.ignore_permissions = False
	mapped.insert()
	definition = MAPPED_TARGETS[target]
	return {"name": mapped.name, "doctype": mapped.doctype, "route": definition["route"].format(name=quote(mapped.name, safe="")), "docstatus": mapped.docstatus, "preview": _preview_payload(doc, target, mapped, selected)}
