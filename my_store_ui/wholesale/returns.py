"""Sales returns (Return Delivery Note + Credit Note) and supplier returns.

Returns are produced by ERPNext's own ``make_sales_return`` / ``make_purchase_return``
mappings, which create the negative-quantity return document against the original.
Stock goes back in and the receivable/payable is reduced by standard controllers --
no ledger entry is ever reversed by hand here.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.wholesale import idempotency

TOLERANCE = 0.001

RETURN_REASONS = (
	"Damaged", "Wrong Item", "Excess Delivery", "Quality Issue",
	"Customer Cancelled", "Expired", "Other",
)


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def returned_qty(doctype: str, source_name: str) -> dict[str, float]:
	"""Quantity already returned per source line (positive numbers)."""
	child = f"{doctype} Item"
	# Return documents carry `return_against` on the parent; sum their lines.
	returns = frappe.get_all(
		doctype, filters={"return_against": source_name, "docstatus": 1}, pluck="name"
	)
	out: dict[str, float] = {}
	for name in returns:
		for row in frappe.get_all(child, filters={"parent": name}, fields=["item_code", "qty"]):
			out[row.item_code] = out.get(row.item_code, 0.0) + abs(flt(row.qty))
	return out


@frappe.whitelist(methods=["GET"])
def get_return_position(delivery_note: str):
	"""What can still be returned against a Delivery Note."""
	_require_login()
	if not frappe.has_permission("Delivery Note", "read", doc=delivery_note):
		frappe.throw(_("You do not have permission to read this delivery."), frappe.PermissionError)
	note = frappe.get_doc("Delivery Note", delivery_note)
	if note.docstatus != 1:
		frappe.throw(_("Only a submitted Delivery Note can be returned."), frappe.ValidationError)
	if note.get("is_return"):
		frappe.throw(_("A return document cannot itself be returned."), frappe.ValidationError)

	already = returned_qty("Delivery Note", delivery_note)
	lines = []
	for row in note.items:
		done = already.get(row.item_code, 0.0)
		lines.append({
			"idx": row.idx, "item_code": row.item_code, "item_name": row.item_name,
			"warehouse": row.warehouse, "uom": row.uom, "conversion_factor": flt(row.conversion_factor),
			"delivered_qty": flt(row.qty), "returned_qty": done,
			"returnable_qty": max(flt(row.qty) - done, 0.0),
			"batch_no": row.get("batch_no"), "rate": flt(row.rate),
		})
	return {
		"delivery_note": delivery_note, "customer": note.customer, "company": note.company,
		"posting_date": str(note.posting_date), "currency": note.currency,
		"lines": lines, "reasons": list(RETURN_REASONS),
		"fully_returned": all(line["returnable_qty"] <= TOLERANCE for line in lines),
	}


@frappe.whitelist(methods=["POST"])
def create_sales_return(delivery_note: str, lines=None, reason: str | None = None,
                        condition: str | None = None, warehouse: str | None = None,
                        submit: int = 0, request_id: str | None = None):
	"""Return Delivery Note against an original delivery.

	``lines`` is [{idx, qty}] in the original line's UOM; omit it to return
	everything still returnable.
	"""
	_require_login()
	if not frappe.has_permission("Delivery Note", "create"):
		frappe.throw(_("You cannot create returns."), frappe.PermissionError)

	reason = (reason or "").strip()
	if not reason:
		frappe.throw(_("A return reason is required."), frappe.ValidationError)
	if reason not in RETURN_REASONS:
		frappe.throw(
			_("Invalid return reason. Allowed: {0}.").format(", ".join(RETURN_REASONS)),
			frappe.ValidationError,
		)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Delivery Note", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Delivery Note", existing, "docstatus")}

	position = get_return_position(delivery_note)
	if position["fully_returned"]:
		frappe.throw(_("Everything on this delivery has already been returned."), frappe.ValidationError)
	returnable = {line["idx"]: line for line in position["lines"]}
	requested = _requested_map(lines)

	if warehouse:
		company = position["company"]
		if not frappe.db.exists("Warehouse", {"name": warehouse, "company": company, "is_group": 0,
		                                      "disabled": 0}):
			frappe.throw(
				_("{0} is not a valid warehouse for {1}.").format(warehouse, company),
				frappe.ValidationError,
			)

	sp = "wholesale_sales_return"
	frappe.db.savepoint(sp)
	try:
		from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_return

		ret = make_sales_return(delivery_note)
		kept = []
		for row in ret.items:
			source = returnable.get(row.idx)
			if not source:
				continue
			allowed = source["returnable_qty"]
			if allowed <= TOLERANCE:
				continue
			qty = allowed if requested is None else flt(requested.get(row.idx, 0.0))
			if qty <= TOLERANCE:
				continue
			if qty > allowed + TOLERANCE:
				frappe.throw(
					_("Line {0}: cannot return {1} when only {2} was delivered and not yet returned.").format(
						row.idx, qty, allowed),
					frappe.ValidationError,
				)
			# Return documents carry negative quantities.
			row.qty = -abs(qty)
			if warehouse:
				row.warehouse = warehouse
			kept.append(row)
		ret.set("items", kept)
		if not ret.get("items"):
			frappe.throw(_("Select at least one line to return."), frappe.ValidationError)
		_set_return_reason(ret, reason, condition)
		idempotency.stamp(ret, request_id)
		ret.insert()
		if cint(submit):
			ret.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Delivery Note", request_id, ret.name)
	return {"name": ret.name, "docstatus": ret.docstatus, "duplicate": False,
	        "return_against": delivery_note, "reason": reason}


@frappe.whitelist(methods=["POST"])
def create_credit_note(sales_invoice: str, return_delivery_note: str | None = None,
                       submit: int = 0, request_id: str | None = None):
	"""Credit Note (return Sales Invoice) reducing the receivable."""
	_require_login()
	if not frappe.has_permission("Sales Invoice", "create"):
		frappe.throw(_("You cannot create credit notes."), frappe.PermissionError)
	if not frappe.has_permission("Sales Invoice", "read", doc=sales_invoice):
		frappe.throw(_("You do not have permission to read this invoice."), frappe.PermissionError)

	invoice = frappe.get_doc("Sales Invoice", sales_invoice)
	if invoice.docstatus != 1:
		frappe.throw(_("Only a submitted invoice can be credited."), frappe.ValidationError)
	if invoice.get("is_return"):
		frappe.throw(_("This document is already a credit note."), frappe.ValidationError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Sales Invoice", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Sales Invoice", existing, "docstatus")}

	sp = "wholesale_credit_note"
	frappe.db.savepoint(sp)
	try:
		from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return

		note = make_sales_return(sales_invoice)
		# The mapping copies the original invoice's advance allocations, which do not
		# apply to a credit note and fail validation. Let ERPNext resolve them afresh.
		note.set("advances", [])
		idempotency.stamp(note, request_id)
		note.insert()
		if cint(submit):
			note.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Sales Invoice", request_id, note.name)
	return {"name": note.name, "docstatus": note.docstatus, "duplicate": False,
	        "return_against": sales_invoice, "grand_total": flt(note.grand_total)}


@frappe.whitelist(methods=["POST"])
def create_purchase_return(purchase_receipt: str, lines=None, reason: str | None = None,
                           submit: int = 0, request_id: str | None = None):
	"""Return Purchase Receipt against a supplier."""
	_require_login()
	if not frappe.has_permission("Purchase Receipt", "create"):
		frappe.throw(_("You cannot create supplier returns."), frappe.PermissionError)

	reason = (reason or "").strip()
	if reason and reason not in RETURN_REASONS:
		frappe.throw(
			_("Invalid return reason. Allowed: {0}.").format(", ".join(RETURN_REASONS)),
			frappe.ValidationError,
		)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Purchase Receipt", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Purchase Receipt", existing, "docstatus")}

	receipt = frappe.get_doc("Purchase Receipt", purchase_receipt)
	if receipt.docstatus != 1:
		frappe.throw(_("Only a submitted Purchase Receipt can be returned."), frappe.ValidationError)
	if receipt.get("is_return"):
		frappe.throw(_("A return document cannot itself be returned."), frappe.ValidationError)

	already = returned_qty("Purchase Receipt", purchase_receipt)
	requested = _requested_map(lines)

	sp = "wholesale_purchase_return"
	frappe.db.savepoint(sp)
	try:
		from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return

		ret = make_purchase_return(purchase_receipt)
		source_by_idx = {row.idx: row for row in receipt.items}
		kept = []
		for row in ret.items:
			source = source_by_idx.get(row.idx)
			if not source:
				continue
			allowed = flt(source.qty) - already.get(source.item_code, 0.0)
			if allowed <= TOLERANCE:
				continue
			qty = allowed if requested is None else flt(requested.get(row.idx, 0.0))
			if qty <= TOLERANCE:
				continue
			if qty > allowed + TOLERANCE:
				frappe.throw(
					_("Line {0}: cannot return {1} when only {2} was received and not yet returned.").format(
						row.idx, qty, allowed),
					frappe.ValidationError,
				)
			# A Purchase Receipt line must keep received = accepted + rejected, and a
			# return may not carry a rejected quantity at all.
			row.qty = -abs(qty)
			row.rejected_qty = 0
			row.received_qty = row.qty
			kept.append(row)
		ret.set("items", kept)
		if not ret.get("items"):
			frappe.throw(_("Select at least one line to return."), frappe.ValidationError)
		_set_return_reason(ret, reason, None)
		idempotency.stamp(ret, request_id)
		ret.insert()
		if cint(submit):
			ret.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Purchase Receipt", request_id, ret.name)
	return {"name": ret.name, "docstatus": ret.docstatus, "duplicate": False,
	        "return_against": purchase_receipt}


@frappe.whitelist(methods=["POST"])
def create_debit_note(purchase_invoice: str, submit: int = 0, request_id: str | None = None):
	"""Debit Note (return Purchase Invoice) reducing the payable."""
	_require_login()
	if not frappe.has_permission("Purchase Invoice", "create"):
		frappe.throw(_("You cannot create debit notes."), frappe.PermissionError)

	invoice = frappe.get_doc("Purchase Invoice", purchase_invoice)
	if invoice.docstatus != 1:
		frappe.throw(_("Only a submitted invoice can be debited."), frappe.ValidationError)
	if invoice.get("is_return"):
		frappe.throw(_("This document is already a debit note."), frappe.ValidationError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Purchase Invoice", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Purchase Invoice", existing, "docstatus")}

	sp = "wholesale_debit_note"
	frappe.db.savepoint(sp)
	try:
		from erpnext.controllers.sales_and_purchase_return import make_return_doc

		note = make_return_doc("Purchase Invoice", purchase_invoice)
		idempotency.stamp(note, request_id)
		note.insert()
		if cint(submit):
			note.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Purchase Invoice", request_id, note.name)
	return {"name": note.name, "docstatus": note.docstatus, "duplicate": False,
	        "return_against": purchase_invoice, "grand_total": flt(note.grand_total)}


def _requested_map(lines) -> dict[int, float] | None:
	if lines in (None, "", []):
		return None
	rows = json.loads(lines) if isinstance(lines, str) else lines
	if not isinstance(rows, list):
		frappe.throw(_("Invalid return lines."), frappe.ValidationError)
	out: dict[int, float] = {}
	for row in rows:
		idx = cint((row or {}).get("idx"))
		qty = flt((row or {}).get("qty"))
		if idx <= 0:
			frappe.throw(_("Each return line needs the original line number."), frappe.ValidationError)
		if qty < 0:
			frappe.throw(_("A return quantity cannot be negative."), frappe.ValidationError)
		out[idx] = out.get(idx, 0.0) + qty
	return out


# The narrative field differs by doctype: Delivery Note has `instructions` but no
# `remarks`, Purchase Receipt has both. Resolve against the meta rather than assume.
NARRATIVE_FIELDS = ("remarks", "instructions")


def _narrative_field(doctype: str) -> str | None:
	meta = frappe.get_meta(doctype)
	for fieldname in NARRATIVE_FIELDS:
		if meta.get_field(fieldname):
			return fieldname
	return None


def _set_return_reason(doc, reason: str | None, condition: str | None) -> None:
	"""Record why the goods came back, in the document's own narrative field."""
	parts = [p for p in (reason and _("Reason: {0}").format(reason),
	                     condition and _("Condition: {0}").format(condition)) if p]
	if not parts:
		return
	fieldname = _narrative_field(doc.doctype)
	if not fieldname:
		return
	text = " | ".join(parts)
	existing = (doc.get(fieldname) or "").strip()
	doc.set(fieldname, f"{existing}\n{text}".strip() if existing else text)
