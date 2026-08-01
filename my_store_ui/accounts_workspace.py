"""Accounts workspace: a permission-aware finance landing page.

Every section, figure and link is filtered by what the signed-in user may actually
read. A Sales or Warehouse user without accounting permission receives no totals at
all -- the numbers are withheld on the server rather than hidden in the browser.

All figures come from standard ERPNext documents through frappe.get_list, so User
Permissions and company restrictions apply.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, nowdate

FINANCIAL_ROLES = ("Accounts User", "Accounts Manager")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _can_see_financials() -> bool:
	roles = set(frappe.get_roles())
	return "System Manager" in roles or bool(roles & set(FINANCIAL_ROLES))


def _sum(doctype: str, filters: dict, field: str) -> float:
	if not frappe.has_permission(doctype, "read"):
		return 0.0
	rows = frappe.get_list(doctype, filters=filters, fields=[field], limit_page_length=0)
	return flt(sum(flt(r.get(field)) for r in rows))


def _count(doctype: str, filters: dict) -> int:
	if not frappe.has_permission(doctype, "read"):
		return 0
	return len(frappe.get_list(doctype, filters=filters, fields=["name"], limit_page_length=0))


@frappe.whitelist(methods=["GET"])
def get_accounts_workspace(company: str | None = None):
	"""Sections, totals and links the signed-in user is allowed to see."""
	_require_login()
	company = (company or "").strip() or frappe.defaults.get_user_default("Company") \
		or frappe.db.get_default("company")
	base = {"company": company} if company else {}
	today = nowdate()
	show_money = _can_see_financials()

	sections = []

	# --- Ledgers and masters -------------------------------------------------
	ledger_links = []
	if frappe.has_permission("Account", "read"):
		ledger_links.append({"label": _("Chart of Accounts"), "path": "/finance/chart-of-accounts"})
	if frappe.has_permission("Journal Entry", "read"):
		ledger_links.append({"label": _("Journal Entries"), "path": "/finance/journal-entries"})
	if ledger_links:
		sections.append({"key": "ledgers", "title": _("Ledgers"), "links": ledger_links})

	# --- Receivables ---------------------------------------------------------
	if frappe.has_permission("Sales Invoice", "read"):
		unpaid = {**base, "docstatus": 1, "outstanding_amount": [">", 0.01]}
		overdue = {**unpaid, "due_date": ["<", today]}
		cards = [
			{"label": _("Unpaid invoices"), "value": _count("Sales Invoice", unpaid),
			 "kind": "count"},
			{"label": _("Overdue invoices"), "value": _count("Sales Invoice", overdue),
			 "kind": "count", "tone": "danger"},
		]
		if show_money:
			cards.append({"label": _("Receivable total"),
			              "value": _sum("Sales Invoice", unpaid, "outstanding_amount"),
			              "kind": "currency"})
			cards.append({"label": _("Overdue amount"),
			              "value": _sum("Sales Invoice", overdue, "outstanding_amount"),
			              "kind": "currency", "tone": "danger"})
		sections.append({
			"key": "receivables", "title": _("Receivables"), "cards": cards,
			"links": [
				{"label": _("Sales Invoices"), "path": "/sales/invoices"},
				{"label": _("Customer Balances"), "path": "/reports/view/Accounts%20Receivable"},
			],
		})

	# --- Payables ------------------------------------------------------------
	if frappe.has_permission("Purchase Invoice", "read"):
		unpaid = {**base, "docstatus": 1, "outstanding_amount": [">", 0.01]}
		cards = [{"label": _("Unpaid supplier invoices"),
		          "value": _count("Purchase Invoice", unpaid), "kind": "count"}]
		if show_money:
			cards.append({"label": _("Payable total"),
			              "value": _sum("Purchase Invoice", unpaid, "outstanding_amount"),
			              "kind": "currency"})
		sections.append({
			"key": "payables", "title": _("Payables"), "cards": cards,
			"links": [
				{"label": _("Purchase Invoices"), "path": "/purchases/invoices"},
				{"label": _("Supplier Balances"), "path": "/reports/view/Accounts%20Payable"},
			],
		})

	# --- Cash and bank -------------------------------------------------------
	if frappe.has_permission("Payment Entry", "read"):
		received = {**base, "docstatus": 1, "payment_type": "Receive", "posting_date": today}
		paid = {**base, "docstatus": 1, "payment_type": "Pay", "posting_date": today}
		cards = [
			{"label": _("Receipts today"), "value": _count("Payment Entry", received),
			 "kind": "count"},
			{"label": _("Payments today"), "value": _count("Payment Entry", paid), "kind": "count"},
		]
		if show_money:
			cards.append({"label": _("Received today"),
			              "value": _sum("Payment Entry", received, "paid_amount"),
			              "kind": "currency"})
			cards.append({"label": _("Paid today"),
			              "value": _sum("Payment Entry", paid, "paid_amount"),
			              "kind": "currency"})
		sections.append({
			"key": "cash_bank", "title": _("Cash and Bank"), "cards": cards,
			"links": [{"label": _("Payment Entries"), "path": "/finance/payments"}],
		})

	# --- Reconciliation tools ------------------------------------------------
	tools = []
	if frappe.has_permission("Payment Entry", "read"):
		tools.append({"label": _("Payment Reconciliation"),
		              "path": "/finance/payment-reconciliation"})
	if frappe.has_permission("Bank Transaction", "read"):
		tools.append({"label": _("Bank Reconciliation"), "path": "/finance/bank-reconciliation"})
		tools.append({"label": _("Bank Clearance"), "path": "/finance/bank-clearance"})
	if tools:
		sections.append({"key": "reconciliation", "title": _("Reconciliation"), "links": tools})

	# --- Reports -------------------------------------------------------------
	reports = []
	if frappe.has_permission("GL Entry", "read"):
		reports.append({"label": _("General Ledger"), "path": "/reports/view/General%20Ledger"})
	if frappe.has_permission("Sales Invoice", "read"):
		reports.append({"label": _("Accounts Receivable"),
		                "path": "/reports/view/Accounts%20Receivable"})
	if frappe.has_permission("Purchase Invoice", "read"):
		reports.append({"label": _("Accounts Payable"), "path": "/reports/view/Accounts%20Payable"})
	if reports:
		sections.append({"key": "reports", "title": _("Reports"), "links": reports})

	currency = frappe.db.get_value("Company", company, "default_currency") if company else None
	return {
		"company": company,
		"currency": currency,
		"shows_financials": show_money,
		"sections": sections,
		"has_access": bool(sections),
	}
