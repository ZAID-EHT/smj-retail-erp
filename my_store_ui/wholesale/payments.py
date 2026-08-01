"""Customer receipts and allocation against orders and invoices.

Every entry is a standard ERPNext Payment Entry; the Payment Ledger and GL are
written by ERPNext's controllers. Outstanding figures are always read from
ERPNext, never recomputed or patched here.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

from my_store_ui.wholesale import idempotency

TOLERANCE = 0.01
ALLOCATABLE = ("Sales Order", "Sales Invoice")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


@frappe.whitelist(methods=["GET"])
def get_outstanding_documents(customer: str, company: str | None = None):
	"""Submitted orders and invoices with money still due from this customer."""
	_require_login()
	if not frappe.has_permission("Customer", "read", doc=customer):
		frappe.throw(_("You do not have permission to read this customer."), frappe.PermissionError)
	company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_default("company")

	invoices = []
	if frappe.has_permission("Sales Invoice", "read"):
		invoices = frappe.get_all(
			"Sales Invoice",
			filters={"customer": customer, "company": company, "docstatus": 1,
			         "outstanding_amount": [">", TOLERANCE]},
			fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"],
			order_by="due_date asc, posting_date asc",
		)
	orders = []
	if frappe.has_permission("Sales Order", "read"):
		for row in frappe.get_all(
			"Sales Order",
			filters={"customer": customer, "company": company, "docstatus": 1,
			         "status": ["not in", ("Closed", "Completed")]},
			fields=["name", "transaction_date", "grand_total", "advance_paid", "per_billed", "status"],
			order_by="transaction_date asc",
		):
			pending = flt(row.grand_total) - flt(row.advance_paid)
			if pending > TOLERANCE and flt(row.per_billed) < 100:
				row["pending_amount"] = pending
				orders.append(row)

	total_outstanding = sum(flt(r.outstanding_amount) for r in invoices)
	return {
		"customer": customer, "company": company,
		"invoices": invoices, "orders": orders,
		"total_invoice_outstanding": total_outstanding,
		"total_order_pending": sum(flt(r["pending_amount"]) for r in orders),
	}


def _default_bank_account(company: str, mode_of_payment: str | None) -> str:
	"""Resolve the receiving account, preferring the Mode of Payment default."""
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
		frappe.throw(_("No Bank or Cash account is configured for {0}.").format(company), frappe.ValidationError)
	return rows[0]


@frappe.whitelist(methods=["POST"])
def create_customer_payment(customer: str, amount: float, company: str | None = None,
                            mode_of_payment: str | None = None, paid_to: str | None = None,
                            reference_no: str | None = None, reference_date: str | None = None,
                            allocations=None, remarks: str | None = None,
                            submit: int = 0, request_id: str | None = None):
	"""Record a customer receipt and allocate it across orders/invoices.

	``allocations`` is a list of {reference_doctype, reference_name, allocated_amount}.
	When omitted the receipt is allocated oldest-first against outstanding invoices,
	then against unbilled orders as an advance.
	"""
	_require_login()
	if not frappe.has_permission("Payment Entry", "create"):
		frappe.throw(_("You cannot record payments."), frappe.PermissionError)
	if not frappe.has_permission("Customer", "read", doc=customer):
		frappe.throw(_("You do not have permission to read this customer."), frappe.PermissionError)

	amount = flt(amount)
	if amount <= 0:
		frappe.throw(_("The payment amount must be greater than zero."), frappe.ValidationError)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Payment Entry", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Payment Entry", existing, "docstatus")}

	company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_default("company")
	account = paid_to or _default_bank_account(company, mode_of_payment)
	# ERPNext requires a reference for bank movements; fail early with a field-level
	# message instead of surfacing the controller's generic error.
	if frappe.db.get_value("Account", account, "account_type") == "Bank" and not (reference_no or "").strip():
		frappe.throw(
			_("Reference Number is required for a bank payment."), frappe.ValidationError
		)
	rows = _resolve_allocations(customer, company, amount, allocations)

	sp = "wholesale_payment"
	frappe.db.savepoint(sp)
	try:
		entry = frappe.new_doc("Payment Entry")
		entry.payment_type = "Receive"
		entry.company = company
		entry.party_type = "Customer"
		entry.party = customer
		entry.posting_date = nowdate()
		entry.mode_of_payment = mode_of_payment
		entry.paid_amount = amount
		entry.received_amount = amount
		entry.paid_to = account
		entry.reference_no = reference_no or None
		entry.reference_date = reference_date or nowdate()
		entry.remarks = remarks or None
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
	return {
		"name": entry.name, "docstatus": entry.docstatus, "duplicate": False,
		"paid_amount": flt(entry.paid_amount),
		"allocated": sum(flt(r.allocated_amount) for r in entry.get("references") or []),
		"unallocated_amount": flt(entry.get("unallocated_amount")),
	}


def _resolve_allocations(customer: str, company: str, amount: float, allocations) -> list[dict]:
	if allocations in (None, "", []):
		return _auto_allocate(customer, company, amount)
	rows = json.loads(allocations) if isinstance(allocations, str) else allocations
	if not isinstance(rows, list):
		frappe.throw(_("Invalid allocation."), frappe.ValidationError)
	out: list[dict] = []
	total = 0.0
	for row in rows:
		doctype = str((row or {}).get("reference_doctype") or "").strip()
		name = str((row or {}).get("reference_name") or "").strip()
		allocated = flt((row or {}).get("allocated_amount"))
		if doctype not in ALLOCATABLE:
			frappe.throw(_("A payment can only be allocated to {0}.").format(", ".join(ALLOCATABLE)),
			             frappe.ValidationError)
		if not frappe.db.exists(doctype, {"name": name, "docstatus": 1, "customer": customer}):
			frappe.throw(_("{0} {1} does not belong to this customer.").format(doctype, name),
			             frappe.ValidationError)
		if allocated <= 0:
			frappe.throw(_("Each allocation must be greater than zero."), frappe.ValidationError)
		outstanding = _outstanding_of(doctype, name)
		if allocated > outstanding + TOLERANCE:
			frappe.throw(
				_("Cannot allocate {0} to {1} {2}; only {3} is outstanding.").format(
					allocated, doctype, name, outstanding),
				frappe.ValidationError,
			)
		total += allocated
		out.append({"reference_doctype": doctype, "reference_name": name, "allocated_amount": allocated})
	if total > amount + TOLERANCE:
		frappe.throw(
			_("Allocated {0} exceeds the payment of {1}.").format(total, amount), frappe.ValidationError
		)
	return out


def _outstanding_of(doctype: str, name: str) -> float:
	if doctype == "Sales Invoice":
		return flt(frappe.db.get_value("Sales Invoice", name, "outstanding_amount"))
	row = frappe.db.get_value("Sales Order", name, ["grand_total", "advance_paid"], as_dict=True)
	return max(flt(row.grand_total) - flt(row.advance_paid), 0.0)


def _auto_allocate(customer: str, company: str, amount: float) -> list[dict]:
	"""Oldest-first: settle invoices, then hold the rest against unbilled orders."""
	position = get_outstanding_documents(customer, company)
	remaining = amount
	out: list[dict] = []
	for invoice in position["invoices"]:
		if remaining <= TOLERANCE:
			break
		allocated = min(flt(invoice.outstanding_amount), remaining)
		out.append({"reference_doctype": "Sales Invoice", "reference_name": invoice.name,
		            "allocated_amount": allocated})
		remaining -= allocated
	for order in position["orders"]:
		if remaining <= TOLERANCE:
			break
		allocated = min(flt(order["pending_amount"]), remaining)
		out.append({"reference_doctype": "Sales Order", "reference_name": order["name"],
		            "allocated_amount": allocated})
		remaining -= allocated
	return out
