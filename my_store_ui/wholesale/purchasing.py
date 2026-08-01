"""Purchasing: Purchase Order -> Purchase Receipt -> Purchase Invoice -> payment.

Receipts and invoices are produced by ERPNext's own mappings so stock, batch
creation, valuation and the payable are all handled by standard controllers.
Quantities are entered in Unit or Carton and converted through the Item's real UOM
conversion, exactly as on the selling side.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

from my_store_ui.wholesale import idempotency
from my_store_ui.wholesale.uom import conversion_factor

TOLERANCE = 0.001


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _validate_link(doctype: str, name: str | None, filters: dict | None = None) -> None:
	if not name:
		frappe.throw(_("{0} is required.").format(doctype), frappe.ValidationError)
	if not frappe.db.exists(doctype, {"name": name, **(filters or {})}):
		frappe.throw(_("Invalid {0}: {1}").format(doctype, name), frappe.ValidationError)
	if not frappe.has_permission(doctype, "read", doc=name):
		frappe.throw(_("You do not have permission to use {0} {1}.").format(doctype, name),
		             frappe.PermissionError)


@frappe.whitelist(methods=["POST"])
def create_purchase_order(supplier: str, items, company: str | None = None,
                          warehouse: str | None = None, schedule_date: str | None = None,
                          submit: int = 0, request_id: str | None = None):
	"""Draft (optionally submitted) Purchase Order.

	``items`` is [{item_code, qty, rate, uom}]. Rates are supplier prices and are
	accepted from the caller; quantities convert through the Item's UOM table.
	"""
	_require_login()
	if not frappe.has_permission("Purchase Order", "create"):
		frappe.throw(_("You cannot create purchase orders."), frappe.PermissionError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Purchase Order", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Purchase Order", existing, "docstatus")}

	company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_default("company")
	_validate_link("Supplier", supplier, {"disabled": 0})
	_validate_link("Company", company)
	if warehouse:
		_validate_link("Warehouse", warehouse, {"company": company, "is_group": 0, "disabled": 0})

	rows = json.loads(items) if isinstance(items, str) else items
	if not isinstance(rows, list) or not rows:
		frappe.throw(_("Add at least one product to the purchase order."), frappe.ValidationError)

	schedule_date = schedule_date or frappe.utils.add_days(nowdate(), 7)

	sp = "wholesale_purchase_order"
	frappe.db.savepoint(sp)
	try:
		order = frappe.new_doc("Purchase Order")
		order.supplier = supplier
		order.company = company
		order.transaction_date = nowdate()
		order.schedule_date = schedule_date
		if warehouse:
			order.set_warehouse = warehouse

		seen: set[str] = set()
		for row in rows:
			item_code = str((row or {}).get("item_code") or "").strip()
			qty = flt((row or {}).get("qty"))
			if not item_code or item_code in seen:
				frappe.throw(_("Each product must appear once on the order."), frappe.ValidationError)
			if qty <= 0:
				frappe.throw(_("Quantity for {0} must be greater than zero.").format(item_code),
				             frappe.ValidationError)
			_validate_link("Item", item_code, {"disabled": 0, "is_purchase_item": 1})
			seen.add(item_code)
			uom = str((row or {}).get("uom") or "").strip() or frappe.db.get_value(
				"Item", item_code, "stock_uom")
			factor = conversion_factor(item_code, uom)
			line = {
				"item_code": item_code, "qty": qty, "uom": uom, "conversion_factor": factor,
				"schedule_date": schedule_date,
			}
			if warehouse:
				line["warehouse"] = warehouse
			if (row or {}).get("rate") is not None:
				line["rate"] = flt(row.get("rate"))
			order.append("items", line)

		idempotency.stamp(order, request_id)
		order.insert()
		if cint(submit):
			order.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Purchase Order", request_id, order.name)
	return {"name": order.name, "docstatus": order.docstatus, "duplicate": False,
	        "grand_total": flt(order.grand_total)}


@frappe.whitelist(methods=["GET"])
def get_purchase_position(purchase_order: str):
	"""Received and billed progress for a Purchase Order."""
	_require_login()
	if not frappe.has_permission("Purchase Order", "read", doc=purchase_order):
		frappe.throw(_("You do not have permission to read this order."), frappe.PermissionError)
	order = frappe.get_doc("Purchase Order", purchase_order)
	lines = []
	for row in order.items:
		lines.append({
			"idx": row.idx, "item_code": row.item_code, "item_name": row.item_name,
			"uom": row.uom, "conversion_factor": flt(row.conversion_factor),
			"ordered_qty": flt(row.qty), "received_qty": flt(row.received_qty),
			"pending_qty": max(flt(row.qty) - flt(row.received_qty), 0.0),
			"billed_amount": flt(row.billed_amt), "amount": flt(row.amount),
			"warehouse": row.warehouse,
		})
	return {
		"purchase_order": purchase_order, "supplier": order.supplier, "company": order.company,
		"status": order.status, "per_received": flt(order.per_received),
		"per_billed": flt(order.per_billed), "grand_total": flt(order.grand_total),
		"currency": order.currency, "lines": lines,
		"fully_received": flt(order.per_received) >= 100 - TOLERANCE,
		"fully_billed": flt(order.per_billed) >= 100 - TOLERANCE,
	}


@frappe.whitelist(methods=["POST"])
def create_purchase_receipt(purchase_order: str, lines=None, submit: int = 0,
                            request_id: str | None = None):
	"""Receive goods against a Purchase Order (full or partial)."""
	_require_login()
	if not frappe.has_permission("Purchase Receipt", "create"):
		frappe.throw(_("You cannot receive goods."), frappe.PermissionError)
	if not frappe.has_permission("Purchase Order", "read", doc=purchase_order):
		frappe.throw(_("You do not have permission to read this order."), frappe.PermissionError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Purchase Receipt", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Purchase Receipt", existing, "docstatus")}

	order = frappe.get_doc("Purchase Order", purchase_order)
	if order.docstatus != 1:
		frappe.throw(_("Only a submitted Purchase Order can be received."), frappe.ValidationError)
	if flt(order.per_received) >= 100 - TOLERANCE:
		frappe.throw(_("This order is already fully received."), frappe.ValidationError)

	requested = _requested_map(lines)

	sp = "wholesale_purchase_receipt"
	frappe.db.savepoint(sp)
	try:
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

		receipt = make_purchase_receipt(purchase_order)
		source_by_idx = {row.idx: row for row in order.items}
		kept = []
		for row in receipt.items:
			source = source_by_idx.get(row.idx)
			if not source:
				kept.append(row)
				continue
			outstanding = flt(source.qty) - flt(source.received_qty)
			if outstanding <= TOLERANCE:
				continue
			qty = outstanding if requested is None else flt(requested.get(source.idx, 0.0))
			if qty <= TOLERANCE:
				continue
			if qty > outstanding + TOLERANCE:
				frappe.throw(
					_("Line {0}: cannot receive {1} when only {2} is outstanding.").format(
						source.idx, qty, outstanding),
					frappe.ValidationError,
				)
			# On a Purchase Receipt `qty` is the accepted quantity and ERPNext requires
			# received = accepted + rejected, so both must move together.
			row.qty = qty
			row.received_qty = qty + flt(row.get("rejected_qty"))
			kept.append(row)
		receipt.set("items", kept)
		if not receipt.get("items"):
			frappe.throw(_("Nothing is left to receive on this order."), frappe.ValidationError)
		idempotency.stamp(receipt, request_id)
		receipt.insert()
		if cint(submit):
			receipt.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Purchase Receipt", request_id, receipt.name)
	return {"name": receipt.name, "docstatus": receipt.docstatus, "duplicate": False}


@frappe.whitelist(methods=["POST"])
def create_purchase_invoice(purchase_receipt: str | None = None, purchase_order: str | None = None,
                            submit: int = 0, request_id: str | None = None):
	"""Bill a Purchase Receipt (preferred) or a Purchase Order."""
	_require_login()
	if not frappe.has_permission("Purchase Invoice", "create"):
		frappe.throw(_("You cannot create purchase invoices."), frappe.PermissionError)
	if not purchase_receipt and not purchase_order:
		frappe.throw(_("A Purchase Receipt or Purchase Order is required."), frappe.ValidationError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Purchase Invoice", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Purchase Invoice", existing, "docstatus")}

	sp = "wholesale_purchase_invoice"
	frappe.db.savepoint(sp)
	try:
		if purchase_receipt:
			receipt = frappe.get_doc("Purchase Receipt", purchase_receipt)
			if receipt.docstatus != 1:
				frappe.throw(_("Only a submitted Purchase Receipt can be billed."),
				             frappe.ValidationError)
			if flt(receipt.per_billed) >= 100 - TOLERANCE:
				frappe.throw(_("This receipt is already fully billed."), frappe.ValidationError)
			from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

			invoice = make_purchase_invoice(purchase_receipt)
		else:
			order = frappe.get_doc("Purchase Order", purchase_order)
			if order.docstatus != 1:
				frappe.throw(_("Only a submitted Purchase Order can be billed."), frappe.ValidationError)
			if flt(order.per_billed) >= 100 - TOLERANCE:
				frappe.throw(_("This order is already fully billed."), frappe.ValidationError)
			from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_invoice

			invoice = make_purchase_invoice(purchase_order)

		invoice.set("items", [row for row in invoice.items if flt(row.qty) > TOLERANCE])
		if not invoice.get("items"):
			frappe.throw(_("There is nothing left to bill."), frappe.ValidationError)
		if not invoice.get("bill_no"):
			invoice.bill_no = f"AUTO-{frappe.generate_hash(length=8).upper()}"
		invoice.bill_date = invoice.get("bill_date") or nowdate()
		idempotency.stamp(invoice, request_id)
		invoice.insert()
		if cint(submit):
			invoice.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Purchase Invoice", request_id, invoice.name)
	return {"name": invoice.name, "docstatus": invoice.docstatus, "duplicate": False,
	        "grand_total": flt(invoice.grand_total),
	        "outstanding_amount": flt(invoice.get("outstanding_amount"))}


@frappe.whitelist(methods=["POST"])
def create_supplier_payment(supplier: str, amount: float, company: str | None = None,
                            mode_of_payment: str | None = None, paid_from: str | None = None,
                            reference_no: str | None = None, reference_date: str | None = None,
                            allocations=None, submit: int = 0, request_id: str | None = None):
	"""Pay a supplier through a standard Payment Entry."""
	_require_login()
	if not frappe.has_permission("Payment Entry", "create"):
		frappe.throw(_("You cannot record payments."), frappe.PermissionError)
	_validate_link("Supplier", supplier)

	amount = flt(amount)
	if amount <= 0:
		frappe.throw(_("The payment amount must be greater than zero."), frappe.ValidationError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Payment Entry", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Payment Entry", existing, "docstatus")}

	company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_default("company")
	account = paid_from or _default_payment_account(company, mode_of_payment)
	if frappe.db.get_value("Account", account, "account_type") == "Bank" and not (reference_no or "").strip():
		frappe.throw(_("Reference Number is required for a bank payment."), frappe.ValidationError)

	rows = _supplier_allocations(supplier, amount, allocations)

	sp = "wholesale_supplier_payment"
	frappe.db.savepoint(sp)
	try:
		entry = frappe.new_doc("Payment Entry")
		entry.payment_type = "Pay"
		entry.company = company
		entry.party_type = "Supplier"
		entry.party = supplier
		entry.posting_date = nowdate()
		entry.mode_of_payment = mode_of_payment
		entry.paid_amount = amount
		entry.received_amount = amount
		entry.paid_from = account
		entry.reference_no = reference_no or None
		entry.reference_date = reference_date or nowdate()
		for row in rows:
			entry.append("references", row)
		entry.setup_party_account_field()
		entry.set_missing_values()
		idempotency.stamp(entry, request_id)
		entry.insert()
		if cint(submit):
			entry.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Payment Entry", request_id, entry.name)
	return {"name": entry.name, "docstatus": entry.docstatus, "duplicate": False,
	        "paid_amount": flt(entry.paid_amount)}


def _default_payment_account(company: str, mode_of_payment: str | None) -> str:
	if mode_of_payment:
		account = frappe.db.get_value(
			"Mode of Payment Account", {"parent": mode_of_payment, "company": company}, "default_account"
		)
		if account:
			return account
	account = frappe.db.get_value("Company", company, "default_bank_account")
	if account:
		return account
	rows = frappe.get_all(
		"Account", filters={"company": company, "account_type": ["in", ("Bank", "Cash")], "is_group": 0},
		pluck="name", limit=1,
	)
	if not rows:
		frappe.throw(_("No Bank or Cash account is configured for {0}.").format(company),
		             frappe.ValidationError)
	return rows[0]


def _supplier_allocations(supplier: str, amount: float, allocations) -> list[dict]:
	if allocations in (None, "", []):
		return []
	rows = json.loads(allocations) if isinstance(allocations, str) else allocations
	if not isinstance(rows, list):
		frappe.throw(_("Invalid allocation."), frappe.ValidationError)
	out: list[dict] = []
	total = 0.0
	for row in rows:
		doctype = str((row or {}).get("reference_doctype") or "").strip()
		name = str((row or {}).get("reference_name") or "").strip()
		allocated = flt((row or {}).get("allocated_amount"))
		if doctype not in ("Purchase Order", "Purchase Invoice"):
			frappe.throw(
				_("A supplier payment can only be allocated to Purchase Order or Purchase Invoice."),
				frappe.ValidationError,
			)
		if not frappe.db.exists(doctype, {"name": name, "docstatus": 1, "supplier": supplier}):
			frappe.throw(_("{0} {1} does not belong to this supplier.").format(doctype, name),
			             frappe.ValidationError)
		if allocated <= 0:
			frappe.throw(_("Each allocation must be greater than zero."), frappe.ValidationError)
		total += allocated
		out.append({"reference_doctype": doctype, "reference_name": name,
		            "allocated_amount": allocated})
	if total > amount + 0.01:
		frappe.throw(_("Allocated {0} exceeds the payment of {1}.").format(total, amount),
		             frappe.ValidationError)
	return out


def _requested_map(lines) -> dict[int, float] | None:
	if lines in (None, "", []):
		return None
	rows = json.loads(lines) if isinstance(lines, str) else lines
	if not isinstance(rows, list):
		frappe.throw(_("Invalid receipt lines."), frappe.ValidationError)
	out: dict[int, float] = {}
	for row in rows:
		idx = cint((row or {}).get("idx"))
		qty = flt((row or {}).get("qty"))
		if idx <= 0:
			frappe.throw(_("Each receipt line needs the order line number."), frappe.ValidationError)
		if qty < 0:
			frappe.throw(_("A receipt quantity cannot be negative."), frappe.ValidationError)
		out[idx] = out.get(idx, 0.0) + qty
	return out
