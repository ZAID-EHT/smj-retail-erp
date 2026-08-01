"""Delivery preparation from a Sales Order: FIFO batches, gates and dispatch.

Nothing here posts stock or accounting by hand. Batch selection uses ERPNext's own
allocator (``get_auto_batch_nos``, which orders by batch creation = FIFO and already
excludes stock reserved elsewhere), and the Delivery Note is built by the standard
``make_delivery_note`` mapping so the Stock Ledger, reservation release and billing
status are all maintained by ERPNext.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.wholesale import idempotency
from my_store_ui.wholesale.credit import evaluate_sales_order_delivery_gate, require_manager
from my_store_ui.wholesale.uom import conversion_factor

# A delivery line short by less than this is treated as fully delivered.
TOLERANCE = 0.001


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def fifo_batches(item_code: str, warehouse: str, qty: float, company: str | None = None) -> list[dict]:
	"""FIFO batch allocation for one line, in stock units.

	Returns oldest-first batches with the quantity to take from each. An item that
	is not batch-managed returns an empty list -- the caller simply does not set a
	batch on that line.
	"""
	if not frappe.db.get_value("Item", item_code, "has_batch_no"):
		return []
	from erpnext.stock.doctype.serial_and_batch_bundle.serial_and_batch_bundle import get_auto_batch_nos

	kwargs = frappe._dict({
		"item_code": item_code,
		"warehouse": warehouse,
		"qty": flt(qty),
		"based_on": "FIFO",
		"company": company,
	})
	rows = get_auto_batch_nos(kwargs) or []
	return [
		{"batch_no": r.get("batch_no"), "qty": flt(r.get("qty")), "warehouse": r.get("warehouse") or warehouse}
		for r in rows
		if flt(r.get("qty")) > 0
	]


@frappe.whitelist(methods=["GET"])
def get_fifo_allocation(item_code: str, warehouse: str, qty: float, uom: str | None = None):
	"""FIFO batch recommendation for one product, quantity entered in ``uom``."""
	_require_login()
	if not frappe.has_permission("Item", "read", doc=item_code):
		frappe.throw(_("You do not have permission to read this product."), frappe.PermissionError)
	factor = conversion_factor(item_code, uom)
	stock_qty = flt(qty) * factor
	batches = fifo_batches(item_code, warehouse, stock_qty)
	allocated = sum(b["qty"] for b in batches)
	return {
		"item_code": item_code, "warehouse": warehouse, "uom": uom, "conversion_factor": factor,
		"requested_stock_qty": stock_qty, "allocated_qty": allocated,
		"shortfall": max(stock_qty - allocated, 0.0),
		"fully_allocated": allocated + TOLERANCE >= stock_qty,
		"batches": batches,
	}


@frappe.whitelist(methods=["GET"])
def prepare_delivery(sales_order: str):
	"""Everything the delivery screen needs for one Sales Order."""
	_require_login()
	if not frappe.has_permission("Sales Order", "read", doc=sales_order):
		frappe.throw(_("You do not have permission to read this order."), frappe.PermissionError)
	order = frappe.get_doc("Sales Order", sales_order)
	if order.docstatus != 1:
		frappe.throw(_("Only a submitted Sales Order can be delivered."), frappe.ValidationError)

	gate = evaluate_sales_order_delivery_gate(sales_order)
	lines = []
	for row in order.items:
		remaining = flt(row.qty) - flt(row.delivered_qty)
		if remaining <= TOLERANCE:
			remaining = 0.0
		factor = flt(row.conversion_factor) or 1.0
		remaining_stock = remaining * factor
		batches = fifo_batches(row.item_code, row.warehouse, remaining_stock, order.company) if remaining_stock else []
		allocated = sum(b["qty"] for b in batches)
		available = _available_to_sell(row.item_code, row.warehouse)
		lines.append({
			"idx": row.idx, "item_code": row.item_code, "item_name": row.item_name,
			"warehouse": row.warehouse, "uom": row.uom, "stock_uom": row.stock_uom,
			"conversion_factor": factor,
			"ordered_qty": flt(row.qty), "delivered_qty": flt(row.delivered_qty),
			"remaining_qty": remaining, "remaining_stock_qty": remaining_stock,
			"actual_qty": available["actual_qty"], "reserved_qty": available["reserved_qty"],
			"available_to_sell": available["available_to_sell"],
			"batches": batches, "allocated_qty": allocated,
			"shortfall": max(remaining_stock - allocated, 0.0) if frappe.db.get_value(
				"Item", row.item_code, "has_batch_no") else 0.0,
		})

	return {
		"sales_order": sales_order, "customer": order.customer, "customer_name": order.customer_name,
		"company": order.company, "currency": order.currency,
		"status": order.status, "per_delivered": flt(order.per_delivered),
		"transport_method": frappe.db.get_value("Customer", order.customer, "custom_transport_method"),
		"transport_detail": frappe.db.get_value("Customer", order.customer, "custom_transport_detail"),
		"shipping_address": order.get("shipping_address_name") or order.get("customer_address"),
		"contact_person": order.get("contact_person"),
		"gate": gate,
		"lines": lines,
		"fully_delivered": all(line["remaining_qty"] <= TOLERANCE for line in lines),
	}


def _available_to_sell(item_code: str, warehouse: str | None) -> dict:
	actual = reserved = 0.0
	if frappe.has_permission("Bin", "read"):
		filters = {"item_code": item_code}
		if warehouse:
			filters["warehouse"] = warehouse
		for row in frappe.get_all("Bin", filters=filters, fields=["actual_qty", "reserved_stock"]):
			actual += flt(row.actual_qty)
			reserved += flt(row.reserved_stock)
	return {"actual_qty": actual, "reserved_qty": reserved, "available_to_sell": actual - reserved}


@frappe.whitelist(methods=["POST"])
def create_delivery_note(sales_order: str, lines=None, transport_method: str | None = None,
                         transport_detail: str | None = None, override_reason: str | None = None,
                         submit: int = 0, request_id: str | None = None):
	"""Create (optionally submit) a Delivery Note from a Sales Order.

	``lines`` is an optional list of {idx, qty} to deliver less than the full
	outstanding quantity. Quantities are in the Sales Order line's own UOM.
	"""
	_require_login()
	if not frappe.has_permission("Delivery Note", "create"):
		frappe.throw(_("You cannot create deliveries."), frappe.PermissionError)
	if not frappe.has_permission("Sales Order", "read", doc=sales_order):
		frappe.throw(_("You do not have permission to read this order."), frappe.PermissionError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Delivery Note", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Delivery Note", existing, "docstatus")}

	order = frappe.get_doc("Sales Order", sales_order)
	if order.docstatus != 1:
		frappe.throw(_("Only a submitted Sales Order can be delivered."), frappe.ValidationError)
	if flt(order.per_delivered) >= 100:
		frappe.throw(_("This order is already fully delivered."), frappe.ValidationError)

	# --- payment / credit clearance ---
	gate = evaluate_sales_order_delivery_gate(sales_order)
	if not gate["allowed"]:
		if not gate.get("requires_manager_approval"):
			frappe.throw(gate["reason"], frappe.ValidationError)
		reason = (override_reason or "").strip()
		if not reason:
			frappe.throw(
				_("{0} A manager override with a reason is required.").format(gate["reason"]),
				frappe.ValidationError,
			)
		require_manager()

	requested = _requested_map(lines)

	sp = "wholesale_delivery"
	frappe.db.savepoint(sp)
	try:
		from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note

		note = make_delivery_note(sales_order)
		note.set("items", _delivery_items(note, order, requested))
		if not note.get("items"):
			frappe.throw(_("Nothing is left to deliver on this order."), frappe.ValidationError)
		_set_transport(note, transport_method, transport_detail)
		idempotency.stamp(note, request_id)
		note.insert()
		if cint(submit):
			note.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	if not gate["allowed"]:
		_record_override(note.name, sales_order, gate, override_reason)
	idempotency.remember("Delivery Note", request_id, note.name)
	return {
		"name": note.name, "docstatus": note.docstatus, "duplicate": False,
		"overridden": not gate["allowed"], "gate": gate,
	}


def _set_transport(note, method: str | None, detail: str | None) -> None:
	"""Record transport on the dispatch document.

	Setting an unknown attribute on a Frappe Document is silently discarded, so the
	field is checked against the meta and a missing fixture is reported rather than
	swallowed.
	"""
	meta = frappe.get_meta("Delivery Note")
	for fieldname, value in (("custom_transport_method", method), ("custom_transport_detail", detail)):
		if not value:
			continue
		if not meta.get_field(fieldname):
			frappe.throw(
				_("Delivery Note is missing {0}. Run install_pc_custom_fields.").format(fieldname),
				frappe.ValidationError,
			)
		note.set(fieldname, value)


def _requested_map(lines) -> dict[int, float] | None:
	if lines in (None, "", []):
		return None
	rows = json.loads(lines) if isinstance(lines, str) else lines
	if not isinstance(rows, list):
		frappe.throw(_("Invalid delivery lines."), frappe.ValidationError)
	out: dict[int, float] = {}
	for row in rows:
		idx = cint((row or {}).get("idx"))
		qty = flt((row or {}).get("qty"))
		if idx <= 0:
			frappe.throw(_("Each delivery line needs the Sales Order line number."), frappe.ValidationError)
		if qty < 0:
			frappe.throw(_("A delivery quantity cannot be negative."), frappe.ValidationError)
		out[idx] = out.get(idx, 0.0) + qty
	return out


def _delivery_items(note, order, requested: dict[int, float] | None) -> list:
	"""Trim the mapped Delivery Note to what is actually being dispatched."""
	so_line_by_name = {row.name: row for row in order.items}
	kept = []
	for row in note.items:
		so_row = so_line_by_name.get(row.get("so_detail"))
		if not so_row:
			kept.append(row)
			continue
		outstanding = flt(so_row.qty) - flt(so_row.delivered_qty)
		if outstanding <= TOLERANCE:
			continue
		qty = outstanding if requested is None else flt(requested.get(so_row.idx, 0.0))
		if qty <= TOLERANCE:
			continue
		if qty > outstanding + TOLERANCE:
			frappe.throw(
				_("Line {0}: cannot deliver {1} when only {2} is outstanding.").format(
					so_row.idx, qty, outstanding),
				frappe.ValidationError,
			)
		row.qty = qty
		_apply_fifo(row, order.company)
		kept.append(row)
	return kept


def _apply_fifo(row, company: str | None) -> None:
	"""Attach a FIFO batch to a delivery line when the item is batch-managed."""
	if not frappe.db.get_value("Item", row.item_code, "has_batch_no"):
		return
	factor = flt(row.conversion_factor) or 1.0
	stock_qty = flt(row.qty) * factor
	batches = fifo_batches(row.item_code, row.warehouse, stock_qty, company)
	if not batches:
		frappe.throw(
			_("No batch stock is available for {0} in {1}.").format(row.item_code, row.warehouse),
			frappe.ValidationError,
		)
	allocated = sum(b["qty"] for b in batches)
	if allocated + TOLERANCE < stock_qty:
		frappe.throw(
			_("Only {0} of {1} is available in batches for {2}.").format(allocated, stock_qty, row.item_code),
			frappe.ValidationError,
		)
	# One batch covers the line: set it directly. Several batches need ERPNext's
	# Serial and Batch Bundle, which the controller builds from this hint.
	if len(batches) == 1:
		row.batch_no = batches[0]["batch_no"]
	else:
		row.batch_no = None
		row.serial_and_batch_bundle = None
		row.set("use_serial_batch_fields", 0)
		row.set("pick_serial_and_batch", 1)


def _record_override(delivery_note: str, sales_order: str, gate: dict, reason: str | None) -> None:
	"""Audit a manager override in the standard comment trail."""
	frappe.get_doc({
		"doctype": "Comment", "comment_type": "Info", "reference_doctype": "Delivery Note",
		"reference_name": delivery_note,
		"content": _("Credit/payment override by {0}: {1} (order {2}, unpaid {3}). Reason: {4}").format(
			frappe.session.user, gate.get("reason"), sales_order, gate.get("unpaid_amount"), reason),
	}).insert(ignore_permissions=True)
