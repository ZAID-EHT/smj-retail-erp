"""Daily wholesale operations dashboard.

Answers "what needs doing today" across sales, inventory, purchasing and finance.
Every figure is counted from standard ERPNext documents through frappe.get_list, so
User Permissions, company and warehouse restrictions apply. Financial totals are
withheld from users without a finance role rather than silently shown.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, nowdate

FINANCIAL_ROLES = ("Accounts User", "Accounts Manager", "Sales Manager")
LOW_STOCK_LIMIT = 20


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _can_see_financials() -> bool:
	roles = set(frappe.get_roles(frappe.session.user))
	return "System Manager" in roles or bool(roles & set(FINANCIAL_ROLES))


def _count(doctype: str, filters: dict) -> int:
	"""Permission-aware count (get_list applies User Permissions; count() does not)."""
	if not frappe.has_permission(doctype, "read"):
		return 0
	return len(frappe.get_list(doctype, filters=filters, fields=["name"], limit_page_length=0))


def _sum(doctype: str, filters: dict, field: str) -> float:
	if not frappe.has_permission(doctype, "read"):
		return 0.0
	rows = frappe.get_list(doctype, filters=filters, fields=[field], limit_page_length=0)
	return flt(sum(flt(r.get(field)) for r in rows))


def _company_filter(company: str | None) -> dict:
	return {"company": company} if company else {}


@frappe.whitelist(methods=["GET"])
def get_operations_dashboard(company: str | None = None):
	"""Sales, inventory, purchasing and finance work queues for today."""
	_require_login()
	company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_default("company")
	base = _company_filter(company)
	today = nowdate()
	show_money = _can_see_financials()

	return {
		"company": company,
		"as_of": today,
		"shows_financials": show_money,
		"sales": _sales_section(base, today, show_money),
		"inventory": _inventory_section(company),
		"purchasing": _purchasing_section(base, today, show_money),
		"finance": _finance_section(base, today) if show_money else None,
	}


def _sales_section(base: dict, today: str, show_money: bool) -> dict:
	submitted = {**base, "docstatus": 1}
	open_states = ["not in", ("Closed", "Completed", "Cancelled")]

	orders_today = _count("Sales Order", {**base, "transaction_date": today, "docstatus": ["<", 2]})
	awaiting_delivery = _count(
		"Sales Order", {**submitted, "status": open_states, "per_delivered": ["<", 100]}
	)
	partially_delivered = _count(
		"Sales Order",
		{**submitted, "status": open_states, "per_delivered": [">", 0], "per_billed": ["<", 100]},
	)
	delivered_not_invoiced = _count(
		"Sales Order",
		{**submitted, "per_delivered": [">", 0], "per_billed": ["<", 100], "status": open_states},
	)
	invoices_outstanding = _count(
		"Sales Invoice", {**submitted, "outstanding_amount": [">", 0.01]}
	)
	overdue_invoices = _count(
		"Sales Invoice",
		{**submitted, "outstanding_amount": [">", 0.01], "due_date": ["<", today]},
	)

	out = {
		"orders_today": orders_today,
		"awaiting_delivery": awaiting_delivery,
		"partially_delivered": partially_delivered,
		"delivered_not_invoiced": delivered_not_invoiced,
		"invoices_outstanding": invoices_outstanding,
		"overdue_invoices": overdue_invoices,
		"overdue_customers": _overdue_customers(base, today),
	}
	if show_money:
		out["overdue_amount"] = _sum(
			"Sales Invoice",
			{**base, "docstatus": 1, "outstanding_amount": [">", 0.01], "due_date": ["<", today]},
			"outstanding_amount",
		)
		out["receivable_total"] = _sum(
			"Sales Invoice", {**base, "docstatus": 1, "outstanding_amount": [">", 0.01]},
			"outstanding_amount",
		)
	return out


def _overdue_customers(base: dict, today: str) -> int:
	if not frappe.has_permission("Sales Invoice", "read"):
		return 0
	rows = frappe.get_list(
		"Sales Invoice",
		filters={**base, "docstatus": 1, "outstanding_amount": [">", 0.01], "due_date": ["<", today]},
		fields=["customer"], limit_page_length=0,
	)
	return len({r.get("customer") for r in rows if r.get("customer")})


def _inventory_section(company: str | None) -> dict:
	if not frappe.has_permission("Bin", "read"):
		return {"out_of_stock": 0, "low_stock": 0, "reserved_qty": 0.0, "available_to_sell": 0.0,
		        "low_stock_items": []}
	warehouses = frappe.get_all(
		"Warehouse", filters={"company": company, "is_group": 0} if company else {"is_group": 0},
		pluck="name",
	)
	if not warehouses:
		return {"out_of_stock": 0, "low_stock": 0, "reserved_qty": 0.0, "available_to_sell": 0.0,
		        "low_stock_items": []}
	rows = frappe.get_all(
		"Bin", filters={"warehouse": ["in", warehouses]},
		fields=["item_code", "warehouse", "actual_qty", "reserved_stock"], limit_page_length=0,
	)
	reserved = flt(sum(flt(r.reserved_stock) for r in rows))
	actual = flt(sum(flt(r.actual_qty) for r in rows))
	out_of_stock = [r for r in rows if flt(r.actual_qty) <= 0]
	low = [r for r in rows if 0 < flt(r.actual_qty) - flt(r.reserved_stock) <= LOW_STOCK_LIMIT]
	return {
		"out_of_stock": len(out_of_stock),
		"low_stock": len(low),
		"reserved_qty": reserved,
		"available_to_sell": actual - reserved,
		"low_stock_items": [
			{"item_code": r.item_code, "warehouse": r.warehouse,
			 "available": flt(r.actual_qty) - flt(r.reserved_stock)}
			for r in low[:10]
		],
	}


def _purchasing_section(base: dict, today: str, show_money: bool) -> dict:
	submitted = {**base, "docstatus": 1}
	open_states = ["not in", ("Closed", "Completed", "Cancelled")]
	out = {
		"open_orders": _count("Purchase Order", {**submitted, "status": open_states}),
		"overdue_orders": _count(
			"Purchase Order",
			{**submitted, "status": open_states, "schedule_date": ["<", today],
			 "per_received": ["<", 100]},
		),
		"awaiting_receipt": _count(
			"Purchase Order", {**submitted, "status": open_states, "per_received": ["<", 100]}
		),
		"received_not_invoiced": _count(
			"Purchase Receipt", {**submitted, "per_billed": ["<", 100]}
		),
		"supplier_invoices_outstanding": _count(
			"Purchase Invoice", {**submitted, "outstanding_amount": [">", 0.01]}
		),
	}
	if show_money:
		out["payable_total"] = _sum(
			"Purchase Invoice", {**submitted, "outstanding_amount": [">", 0.01]}, "outstanding_amount"
		)
	return out


def _finance_section(base: dict, today: str) -> dict:
	received_today = _sum(
		"Payment Entry",
		{**base, "docstatus": 1, "payment_type": "Receive", "posting_date": today},
		"paid_amount",
	)
	paid_today = _sum(
		"Payment Entry",
		{**base, "docstatus": 1, "payment_type": "Pay", "posting_date": today},
		"paid_amount",
	)
	return {
		"payments_received_today": received_today,
		"payments_made_today": paid_today,
		"customer_outstanding": _sum(
			"Sales Invoice", {**base, "docstatus": 1, "outstanding_amount": [">", 0.01]},
			"outstanding_amount",
		),
		"supplier_outstanding": _sum(
			"Purchase Invoice", {**base, "docstatus": 1, "outstanding_amount": [">", 0.01]},
			"outstanding_amount",
		),
		"credit_exposure": _credit_exposure(base),
	}


def _credit_exposure(base: dict) -> float:
	"""Outstanding owed by customers classified as Credit customers."""
	if not frappe.has_permission("Sales Invoice", "read"):
		return 0.0
	if not frappe.get_meta("Customer").get_field("custom_credit_type"):
		return 0.0
	credit_customers = frappe.get_all(
		"Customer", filters={"custom_credit_type": "Credit Customer"}, pluck="name"
	)
	if not credit_customers:
		return 0.0
	return _sum(
		"Sales Invoice",
		{**base, "docstatus": 1, "outstanding_amount": [">", 0.01],
		 "customer": ["in", credit_customers]},
		"outstanding_amount",
	)
