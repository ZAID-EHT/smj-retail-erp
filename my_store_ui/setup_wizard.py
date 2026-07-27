"""Phase 7 — first-time empty-system company setup.

Detects a system with no Company and drives creation through the standard ERPNext
Company controller (which itself builds the Chart of Accounts, cost center, default
warehouses and default accounts). This module never hand-writes ledger rows; it only
orchestrates standard doctypes and ensures the wholesale/retail Price Lists exist.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.access_management import _require_user_manager

# Price Lists the wholesale workflow expects to exist after setup.
REQUIRED_PRICE_LISTS = (
	{"price_list_name": "Standard Selling", "selling": 1, "buying": 0},
	{"price_list_name": "Standard Buying", "selling": 0, "buying": 1},
	{"price_list_name": "Retail Price List", "selling": 1, "buying": 0},
	{"price_list_name": "Wholesale Price List", "selling": 1, "buying": 0},
)


@frappe.whitelist(methods=["GET"])
def get_setup_status() -> dict:
	"""Whether first-time setup is required, and the readiness checklist.

	Login is required; the detection itself is not secret. Actually creating a
	company is gated separately in create_company.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)

	company_count = frappe.db.count("Company")
	setup_required = company_count == 0
	default_company = frappe.defaults.get_global_default("company")

	checklist = _checklist(default_company) if default_company else _empty_checklist()
	return {
		"setup_required": setup_required,
		"company_count": company_count,
		"default_company": default_company,
		"can_create_company": _may_create_company(),
		"checklist": checklist,
		"ready_for_transactions": setup_required is False and all(item["done"] for item in checklist),
	}


def _may_create_company() -> bool:
	return frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()


def _empty_checklist() -> list[dict]:
	items = ["Company", "Chart of Accounts", "Fiscal Year", "Warehouses", "Price Lists",
	         "Taxes", "Opening Stock", "Opening Balances", "Users"]
	return [{"item": name, "done": False} for name in items]


def _checklist(company: str) -> list[dict]:
	fy = bool(frappe.get_all("Fiscal Year", limit_page_length=1))
	coa = bool(frappe.get_all("Account", filters={"company": company}, limit_page_length=1))
	warehouses = frappe.db.count("Warehouse", {"company": company, "is_group": 0})
	price_lists = frappe.db.count("Price List", {"enabled": 1})
	taxes = bool(frappe.get_all("Sales Taxes and Charges Template", filters={"company": company}, limit_page_length=1))
	opening_stock = bool(frappe.get_all("Bin", filters={"actual_qty": [">", 0]}, limit_page_length=1))
	users = frappe.db.count("User", {"enabled": 1, "user_type": "System User"})
	return [
		{"item": "Company", "done": bool(company)},
		{"item": "Chart of Accounts", "done": coa},
		{"item": "Fiscal Year", "done": fy},
		{"item": "Warehouses", "done": warehouses > 0, "count": warehouses},
		{"item": "Price Lists", "done": price_lists >= 2, "count": price_lists},
		{"item": "Taxes", "done": taxes},
		{"item": "Opening Stock", "done": opening_stock},
		{"item": "Users", "done": users > 0, "count": users},
	]


@frappe.whitelist(methods=["GET"])
def get_setup_options() -> dict:
	"""Reference data the company form needs."""
	_require_user_manager()
	return {
		"currencies": frappe.get_all("Currency", filters={"enabled": 1}, pluck="name", order_by="name")[:200],
		"countries": frappe.get_all("Country", pluck="name", order_by="name")[:300],
		"coa_templates": _coa_templates(),
	}


def _coa_templates() -> list[str]:
	try:
		from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_charts_for_country
		return get_charts_for_country("All") or ["Standard"]
	except Exception:
		return ["Standard"]


@frappe.whitelist(methods=["POST"])
def create_company(values: dict | str) -> dict:
	"""Create a Company via the standard controller, then ensure Price Lists.

	The standard Company controller creates the Chart of Accounts, root cost center
	and default accounts on insert; we do not hand-write any of those.
	"""
	_require_user_manager()
	if not frappe.has_permission("Company", "create"):
		frappe.throw(_("You do not have permission to create a company."), frappe.PermissionError)
	data = frappe.parse_json(values) if isinstance(values, str) else values
	if not isinstance(data, dict):
		frappe.throw(_("Invalid company details."), frappe.ValidationError)

	company_name = str(data.get("company_name") or "").strip()
	if not company_name:
		frappe.throw(_("Company name is required."), frappe.ValidationError)
	if frappe.db.exists("Company", company_name):
		frappe.throw(_("A company named {0} already exists.").format(company_name), frappe.ValidationError)

	company = frappe.get_doc({
		"doctype": "Company",
		"company_name": company_name,
		"abbr": (str(data.get("abbr") or "").strip() or None),
		"default_currency": str(data.get("default_currency") or "LKR").strip(),
		"country": str(data.get("country") or "Sri Lanka").strip(),
		"chart_of_accounts": str(data.get("chart_of_accounts") or "Standard").strip(),
		"create_chart_of_accounts_based_on": "Standard Template",
	})
	company.insert()  # standard controller builds CoA / cost center / default accounts
	_ensure_price_lists()
	# Make it the global default when it is the first company.
	if frappe.db.count("Company") == 1:
		frappe.db.set_default("company", company.name)
	# No explicit commit: Frappe commits a successful request. Omitting it keeps the
	# whole creation atomic and lets tests savepoint-rollback cleanly.
	return {
		"company": company.name,
		"checklist": _checklist(company.name),
	}


def _ensure_price_lists() -> None:
	for spec in REQUIRED_PRICE_LISTS:
		if not frappe.db.exists("Price List", spec["price_list_name"]):
			frappe.get_doc({
				"doctype": "Price List", "price_list_name": spec["price_list_name"],
				"enabled": 1, "selling": spec["selling"], "buying": spec["buying"], "currency": "LKR",
			}).insert(ignore_permissions=True)
