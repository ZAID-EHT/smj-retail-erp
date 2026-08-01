"""Landed Cost Voucher: freight, customs and clearing charges onto valuation.

Uses the standard ERPNext Landed Cost Voucher, which distributes the charges across
the receipt lines and re-posts valuation itself. Valuation rates are never edited
directly.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

from my_store_ui.wholesale import idempotency

# The charge types a wholesale import typically carries. Free text is still allowed
# in `description`; this list drives the UI.
CHARGE_TYPES = ("Freight", "Customs Duty", "Clearing Charges", "Insurance", "Handling", "Other")

DISTRIBUTION_METHODS = ("Qty", "Amount", "Distribute Manually")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


@frappe.whitelist(methods=["POST"])
def create_landed_cost_voucher(purchase_receipts, charges, company: str | None = None,
                               distribute_on: str = "Amount", submit: int = 0,
                               request_id: str | None = None):
	"""Apply landed costs to one or more Purchase Receipts.

	``purchase_receipts`` is a list of Purchase Receipt names.
	``charges`` is [{description, amount, expense_account}].
	"""
	_require_login()
	if not frappe.has_permission("Landed Cost Voucher", "create"):
		frappe.throw(_("You cannot create landed cost vouchers."), frappe.PermissionError)

	if distribute_on not in DISTRIBUTION_METHODS:
		frappe.throw(
			_("Distribution must be one of: {0}.").format(", ".join(DISTRIBUTION_METHODS)),
			frappe.ValidationError,
		)

	request_id = idempotency.normalise(request_id)
	existing = idempotency.find_existing("Landed Cost Voucher", request_id)
	if existing:
		return {"name": existing, "duplicate": True,
		        "docstatus": frappe.db.get_value("Landed Cost Voucher", existing, "docstatus")}

	receipts = json.loads(purchase_receipts) if isinstance(purchase_receipts, str) else purchase_receipts
	if isinstance(receipts, str):
		receipts = [receipts]
	if not isinstance(receipts, list) or not receipts:
		frappe.throw(_("At least one Purchase Receipt is required."), frappe.ValidationError)

	rows = json.loads(charges) if isinstance(charges, str) else charges
	if not isinstance(rows, list) or not rows:
		frappe.throw(_("At least one charge is required."), frappe.ValidationError)

	company = company or frappe.db.get_value("Purchase Receipt", receipts[0], "company")

	sp = "wholesale_landed_cost"
	frappe.db.savepoint(sp)
	try:
		voucher = frappe.new_doc("Landed Cost Voucher")
		voucher.company = company
		voucher.posting_date = nowdate()
		voucher.distribute_charges_based_on = distribute_on

		for name in receipts:
			if not frappe.db.exists("Purchase Receipt", {"name": name, "docstatus": 1,
			                                             "company": company}):
				frappe.throw(
					_("{0} is not a submitted Purchase Receipt for {1}.").format(name, company),
					frappe.ValidationError,
				)
			if not frappe.has_permission("Purchase Receipt", "read", doc=name):
				frappe.throw(_("You do not have permission to use {0}.").format(name),
				             frappe.PermissionError)
			voucher.append("purchase_receipts", {
				"receipt_document_type": "Purchase Receipt", "receipt_document": name,
				"supplier": frappe.db.get_value("Purchase Receipt", name, "supplier"),
			})

		total = 0.0
		for row in rows:
			description = str((row or {}).get("description") or "").strip()
			amount = flt((row or {}).get("amount"))
			if not description:
				frappe.throw(_("Each charge needs a description."), frappe.ValidationError)
			if amount <= 0:
				frappe.throw(_("Each charge must be greater than zero."), frappe.ValidationError)
			account = (row or {}).get("expense_account") or _default_expense_account(company)
			voucher.append("taxes", {
				"description": description, "amount": amount, "expense_account": account,
			})
			total += amount

		# Standard helper pulls the receipt lines the charges are spread over.
		voucher.get_items_from_purchase_receipts()
		voucher.total_taxes_and_charges = total
		idempotency.stamp(voucher, request_id)
		voucher.insert()
		if cint(submit):
			voucher.submit()
	except Exception:
		frappe.db.rollback(save_point=sp)
		raise

	idempotency.remember("Landed Cost Voucher", request_id, voucher.name)
	return {
		"name": voucher.name, "docstatus": voucher.docstatus, "duplicate": False,
		"total_taxes_and_charges": flt(voucher.total_taxes_and_charges),
		"receipts": receipts,
	}


def _default_expense_account(company: str) -> str:
	"""An expense account to book the charge against."""
	for fieldname in ("default_expense_account", "stock_adjustment_account"):
		account = frappe.db.get_value("Company", company, fieldname)
		if account:
			return account
	rows = frappe.get_all(
		"Account",
		filters={"company": company, "root_type": "Expense", "is_group": 0},
		pluck="name", limit=1,
	)
	if not rows:
		frappe.throw(_("No expense account is configured for {0}.").format(company),
		             frappe.ValidationError)
	return rows[0]


@frappe.whitelist(methods=["GET"])
def get_landed_costs(purchase_receipt: str):
	"""Landed cost vouchers already applied to a receipt."""
	_require_login()
	if not frappe.has_permission("Purchase Receipt", "read", doc=purchase_receipt):
		frappe.throw(_("You do not have permission to read this receipt."), frappe.PermissionError)
	names = frappe.get_all(
		"Landed Cost Purchase Receipt",
		filters={"receipt_document": purchase_receipt, "receipt_document_type": "Purchase Receipt"},
		pluck="parent",
	)
	out = []
	for name in sorted(set(names)):
		row = frappe.db.get_value(
			"Landed Cost Voucher", name,
			["name", "docstatus", "posting_date", "total_taxes_and_charges",
			 "distribute_charges_based_on"],
			as_dict=True,
		)
		if row and row.docstatus != 2:
			out.append(row)
	return {"purchase_receipt": purchase_receipt, "vouchers": out,
	        "total_applied": sum(flt(r.total_taxes_and_charges) for r in out if r.docstatus == 1),
	        "charge_types": list(CHARGE_TYPES)}
