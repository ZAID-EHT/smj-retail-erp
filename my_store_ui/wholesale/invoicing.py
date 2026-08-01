"""Final Sales Invoice from delivery, with advance allocation.

The invoice is always produced by ERPNext's own mapping (``make_sales_invoice``
from a Delivery Note or a Sales Order) so billing status, stock relief and the GL
are handled by standard controllers. Nothing here computes an accounting entry.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.wholesale import idempotency
from my_store_ui.wholesale.credit import sales_order_paid_amount

TOLERANCE = 0.01


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


@frappe.whitelist(methods=["GET"])
def get_invoice_position(sales_order: str):
	"""What is delivered, what is invoiced and what is still to bill."""
	_require_login()
	if not frappe.has_permission("Sales Order", "read", doc=sales_order):
		frappe.throw(_("You do not have permission to read this order."), frappe.PermissionError)
	order = frappe.get_doc("Sales Order", sales_order)

	delivered_not_invoiced = []
	for row in order.items:
		pending = flt(row.delivered_qty) - flt(row.billed_amt) / (flt(row.rate) or 1)
		if flt(row.delivered_qty) > 0 and flt(row.billed_amt) < flt(row.amount) - TOLERANCE:
			delivered_not_invoiced.append({
				"idx": row.idx, "item_code": row.item_code, "item_name": row.item_name,
				"delivered_qty": flt(row.delivered_qty), "billed_amount": flt(row.billed_amt),
				"amount": flt(row.amount), "pending_qty": max(pending, 0.0),
			})

	invoices = frappe.get_all(
		"Sales Invoice Item", filters={"sales_order": sales_order, "docstatus": ["<", 2]},
		fields=["parent"], distinct=True, pluck="parent",
	)
	invoice_rows = []
	for name in sorted(set(invoices)):
		inv = frappe.db.get_value(
			"Sales Invoice", name,
			["name", "docstatus", "grand_total", "outstanding_amount", "due_date", "status"],
			as_dict=True,
		)
		if inv:
			invoice_rows.append(inv)

	paid = sales_order_paid_amount(sales_order)
	return {
		"sales_order": sales_order, "customer": order.customer, "company": order.company,
		"currency": order.currency, "grand_total": flt(order.grand_total),
		"per_delivered": flt(order.per_delivered), "per_billed": flt(order.per_billed),
		"advance_paid": paid,
		"outstanding": max(flt(order.grand_total) - paid, 0.0),
		"delivered_not_invoiced": delivered_not_invoiced,
		"invoices": invoice_rows,
		"fully_invoiced": flt(order.per_billed) >= 100 - TOLERANCE,
	}


@frappe.whitelist(methods=["POST"])
def create_sales_invoice(delivery_note: str | None = None, sales_order: str | None = None,
                         submit: int = 0, allocate_advances: int = 1,
                         request_id: str | None = None):
	"""Create the final Sales Invoice from a Delivery Note (preferred) or Sales Order.

	Delivery-first is the approved flow: goods leave on a Delivery Note and the
	invoice bills what was actually delivered.
	"""
	_require_login()
	if not frappe.has_permission("Sales Invoice", "create"):
		frappe.throw(_("You cannot create invoices."), frappe.PermissionError)
	if not delivery_note and not sales_order:
		frappe.throw(_("A Delivery Note or Sales Order is required."), frappe.ValidationError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Sales Invoice", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Sales Invoice", existing, "docstatus")}

	sp = "wholesale_invoice"
	frappe.db.savepoint(sp)
	try:
		if delivery_note:
			invoice = _from_delivery_note(delivery_note)
		else:
			invoice = _from_sales_order(sales_order)
		invoice.set("items", [row for row in invoice.items if flt(row.qty) > TOLERANCE])
		if not invoice.get("items"):
			frappe.throw(_("There is nothing left to invoice."), frappe.ValidationError)
		if cint(allocate_advances):
			_attach_advances(invoice)
		idempotency.stamp(invoice, request_id)
		invoice.insert()
		if cint(submit):
			invoice.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Sales Invoice", request_id, invoice.name)
	return {
		"name": invoice.name, "docstatus": invoice.docstatus, "duplicate": False,
		"grand_total": flt(invoice.grand_total),
		"outstanding_amount": flt(invoice.get("outstanding_amount")),
	}


def _from_delivery_note(delivery_note: str):
	if not frappe.has_permission("Delivery Note", "read", doc=delivery_note):
		frappe.throw(_("You do not have permission to read this delivery."), frappe.PermissionError)
	note = frappe.get_doc("Delivery Note", delivery_note)
	if note.docstatus != 1:
		frappe.throw(_("Only a submitted Delivery Note can be invoiced."), frappe.ValidationError)
	if flt(note.per_billed) >= 100 - TOLERANCE:
		frappe.throw(_("This delivery is already fully invoiced."), frappe.ValidationError)
	from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice

	return make_sales_invoice(delivery_note)


def _from_sales_order(sales_order: str):
	if not frappe.has_permission("Sales Order", "read", doc=sales_order):
		frappe.throw(_("You do not have permission to read this order."), frappe.PermissionError)
	order = frappe.get_doc("Sales Order", sales_order)
	if order.docstatus != 1:
		frappe.throw(_("Only a submitted Sales Order can be invoiced."), frappe.ValidationError)
	if flt(order.per_billed) >= 100 - TOLERANCE:
		frappe.throw(_("This order is already fully invoiced."), frappe.ValidationError)
	from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

	return make_sales_invoice(sales_order)


def _attach_advances(invoice) -> None:
	"""Pull unallocated advances onto the invoice using the standard helper."""
	try:
		invoice.set_advances()
	except Exception:
		frappe.log_error(title="Advance allocation failed", message=frappe.get_traceback())
		return
	# set_advances() proposes every advance; never allocate more than the invoice.
	remaining = flt(invoice.grand_total)
	kept = []
	for row in invoice.get("advances") or []:
		if remaining <= TOLERANCE:
			break
		allocated = min(flt(row.advance_amount), remaining)
		if allocated <= TOLERANCE:
			continue
		row.allocated_amount = allocated
		remaining -= allocated
		kept.append(row)
	invoice.set("advances", kept)
