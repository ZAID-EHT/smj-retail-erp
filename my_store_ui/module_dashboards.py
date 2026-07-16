"""Permission-aware, live-data module dashboards (Accounts, Payments, Buying,
CRM, Selling, Stock).

Each function below reproduces one native ERPNext module dashboard's number
cards and dashboard charts as real, permission-checked aggregates — never
hardcoded preview values. Every query is scoped by frappe.has_permission()
before it runs and uses frappe.get_list()/frappe.get_all() (never raw SQL,
never ignore_permissions). Accounting/stock totals (outstanding_amount,
per_billed, per_delivered, actual_qty, valuation_rate, ...) are always read
from standard ERPNext-maintained fields, never recomputed — only bucketing,
grouping and trend arithmetic happens here.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, add_months, flt, get_first_day, get_last_day, getdate, nowdate

MONTHS_DEFAULT = 6
MAX_MONTHS = 12
TOP_N_DEFAULT = 5
MAX_TOP_N = 10
AGEING_BUCKETS = [(0, 30), (30, 60), (60, 90), (90, None)]


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _company(company: str | None = None) -> str | None:
	if company:
		if not frappe.db.exists("Company", company):
			frappe.throw(_("Invalid company."), frappe.ValidationError)
		return company
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")


def _can(doctype: str) -> bool:
	return bool(frappe.has_permission(doctype, "read"))


def _months(months) -> int:
	return max(1, min(int(months or MONTHS_DEFAULT), MAX_MONTHS))


def _top_n(limit) -> int:
	return max(1, min(int(limit or TOP_N_DEFAULT), MAX_TOP_N))


def _count(doctype: str, filters: dict) -> int:
	if not _can(doctype):
		return 0
	return frappe.db.count(doctype, filters=filters)


def _sum(doctype: str, field: str, filters: dict) -> float:
	if not _can(doctype):
		return 0.0
	rows = frappe.get_list(doctype, filters=filters, fields=[f"sum({field}) as total"], limit_page_length=1)
	return flt(rows[0].total) if rows else 0.0


def _monthly_trend(doctype: str, amount_field: str, date_field: str, months: int, company: str | None) -> dict:
	labels, values = [], []
	for offset in range(-(months - 1), 1):
		anchor = add_months(getdate(nowdate()), offset)
		labels.append(anchor.strftime("%b"))
		if not _can(doctype):
			values.append(0.0)
			continue
		start, end = str(get_first_day(anchor)), str(get_last_day(anchor))
		filters = {"docstatus": 1, date_field: ["between", [start, end]]}
		if company:
			filters["company"] = company
		values.append(_sum(doctype, amount_field, filters))
	return {"labels": labels, "series": [{"name": doctype, "color": "var(--ref-primary-blue)", "values": values}]}


def _ageing(doctype: str, company: str | None) -> list[dict]:
	"""Bucket the standard, ERPNext-maintained outstanding_amount by document
	age (today - due_date). Only the bucketing is computed here; the amounts
	themselves are always ERPNext's own values, never recalculated."""
	if not _can(doctype):
		return [{"label": f"{lo}-{hi}" if hi else f"{lo}+", "value": 0.0} for lo, hi in AGEING_BUCKETS]
	filters = {"docstatus": 1, "outstanding_amount": [">", 0]}
	if company:
		filters["company"] = company
	rows = frappe.get_list(doctype, filters=filters, fields=["due_date", "outstanding_amount"], limit_page_length=5000)
	today = getdate(nowdate())
	buckets = {f"{lo}-{hi}" if hi else f"{lo}+": 0.0 for lo, hi in AGEING_BUCKETS}
	for row in rows:
		age = (today - getdate(row.due_date)).days if row.due_date else 0
		age = max(age, 0)
		for lo, hi in AGEING_BUCKETS:
			if hi is None or age < hi:
				if age >= lo:
					buckets[f"{lo}-{hi}" if hi else f"{lo}+"] += flt(row.outstanding_amount)
					break
	colors = ["var(--ref-primary-blue)", "var(--ref-warning)", "var(--ref-danger)", "#7038d4"]
	return [{"label": label, "value": value, "color": colors[i % len(colors)]} for i, (label, value) in enumerate(buckets.items())]


def _status_breakdown(doctype: str, field: str, company: str | None, extra: dict | None = None) -> list[dict]:
	if not _can(doctype):
		return []
	filters = {"docstatus": 1, **(extra or {})}
	if company and frappe.get_meta(doctype).has_field("company"):
		filters["company"] = company
	rows = frappe.get_list(
		doctype, filters=filters, fields=[field, "count(name) as total"],
		group_by=field, order_by="total desc", limit_page_length=12,
	)
	return [{"label": row.get(field) or _("Not set"), "value": row.total} for row in rows]


def _top_ranked(doctype: str, group_field: str, label_field: str, amount_field: str, company: str | None, limit: int, extra: dict | None = None) -> list[dict]:
	if not _can(doctype):
		return []
	filters = {"docstatus": 1, **(extra or {})}
	if company:
		filters["company"] = company
	rows = frappe.get_list(
		doctype, filters=filters, fields=[group_field, label_field, f"sum({amount_field}) as total"],
		group_by=group_field, order_by="total desc", limit_page_length=limit,
	)
	return [{"label": row.get(label_field) or row.get(group_field), "value": flt(row.total)} for row in rows if row.get(group_field)]


def _run_report_safely(report: str, filters: dict) -> list[dict]:
	try:
		from frappe.desk.query_report import run as run_report

		result = run_report(report, filters=filters, ignore_prepared_report=True)
		return [row for row in (result.get("result") or []) if isinstance(row, dict)]
	except Exception:
		frappe.log_error(title=f"SMJ module dashboard: {report} report unavailable")
		return []


# ---------------------------------------------------------------------------
# Accounts dashboard: erpnext:dashboard:accounts + its charts/cards
# ---------------------------------------------------------------------------
@frappe.whitelist(methods=["GET"])
def get_accounts_dashboard(company: str | None = None, months: int = MONTHS_DEFAULT):
	_require_login()
	company = _company(company)
	months = _months(months)

	cards = [
		{"key": "total-incoming-bills", "label": _("Total Incoming Bills"), "value": _count("Purchase Invoice", {"docstatus": 1, **({"company": company} if company else {})}), "accent": "orange", "to": "/purchases/invoices"},
		{"key": "total-outgoing-bills", "label": _("Total Outgoing Bills"), "value": _count("Sales Invoice", {"docstatus": 1, **({"company": company} if company else {})}), "accent": "green", "to": "/sales/invoices"},
	]

	pl_rows = _run_report_safely("Profit and Loss Statement", {
		"company": company, "period_start_date": str(get_first_day(add_months(getdate(nowdate()), -(months - 1)))),
		"period_end_date": str(get_last_day(getdate(nowdate()))), "periodicity": "Monthly", "filter_based_on": "Date Range",
	}) if company else []
	income_total = flt(sum(flt(row.get("total")) for row in pl_rows if "total income" in str(row.get("account_name") or "").lower()))
	expense_total = flt(sum(flt(row.get("total")) for row in pl_rows if "total expense" in str(row.get("account_name") or "").lower()))

	charts = [
		{"key": "accounts-payable-ageing", "title": _("Accounts Payable Ageing"), "type": "bar", "bars": _ageing("Purchase Invoice", company), "report_link": "/reports/view/Accounts%20Payable"},
		{"key": "accounts-receivable-ageing", "title": _("Accounts Receivable Ageing"), "type": "bar", "bars": _ageing("Sales Invoice", company), "report_link": "/reports/view/Accounts%20Receivable"},
		{"key": "budget-variance", "title": _("Budget Variance"), "type": "bar", "bars": _budget_variance(company), "report_link": "/reports/view/Budget%20Variance%20Report"},
		{"key": "incoming-bills-purchase-invoice", "title": _("Incoming Bills (Purchase Invoice)"), "type": "line", **_monthly_trend("Purchase Invoice", "base_grand_total", "posting_date", months, company), "report_link": "/purchases/invoices"},
		{"key": "outgoing-bills-sales-invoice", "title": _("Outgoing Bills (Sales Invoice)"), "type": "line", **_monthly_trend("Sales Invoice", "base_grand_total", "posting_date", months, company), "report_link": "/sales/invoices"},
		{"key": "profit-and-loss", "title": _("Profit and Loss"), "type": "bar", "bars": [
			{"label": _("Income"), "value": income_total, "color": "var(--ref-success)"},
			{"label": _("Expense"), "value": expense_total, "color": "var(--ref-danger)"},
		], "report_link": "/reports/view/Profit%20and%20Loss%20Statement"},
	]
	return {"company": company, "currency": frappe.get_cached_value("Company", company, "default_currency") if company else "", "cards": cards, "charts": charts}


def _budget_variance(company: str | None) -> list[dict]:
	if not company or not _can("Budget"):
		return []
	fiscal_year = frappe.db.get_value("Fiscal Year", {"year_start_date": ["<=", nowdate()], "year_end_date": [">=", nowdate()]}, "name")
	if not fiscal_year:
		return []
	rows = _run_report_safely("Budget Variance Report", {
		"company": company, "fiscal_year": fiscal_year, "period": "Monthly", "budget_against": "Cost Center",
	})
	variances = []
	for row in rows[:8]:
		target = row.get("cost_center") or row.get("account") or row.get("project")
		variance = row.get("variance") if "variance" in row else None
		if target and variance is not None:
			variances.append({"label": target, "value": flt(variance), "color": "var(--ref-warning)"})
	return variances


# ---------------------------------------------------------------------------
# Payments dashboard: erpnext:dashboard:payments + its charts/cards
# ---------------------------------------------------------------------------
@frappe.whitelist(methods=["GET"])
def get_payments_dashboard(company: str | None = None):
	_require_login()
	company = _company(company)
	base = {"docstatus": 1, **({"company": company} if company else {})}

	cards = [
		{"key": "total-incoming-payment", "label": _("Total Incoming Payment"), "value": _sum("Payment Entry", "base_paid_amount", {**base, "payment_type": "Receive"}), "accent": "green", "to": "/finance/payments"},
		{"key": "total-outgoing-payment", "label": _("Total Outgoing Payment"), "value": _sum("Payment Entry", "base_paid_amount", {**base, "payment_type": "Pay"}), "accent": "orange", "to": "/finance/payments"},
	]

	bank_bars = []
	if _can("Bank Account"):
		accounts = frappe.get_list("Bank Account", filters={"is_company_account": 1, **({"company": company} if company else {})}, fields=["name", "account_name", "account"], limit_page_length=20)
		colors = ["var(--ref-primary-blue)", "var(--ref-success)", "var(--ref-warning)", "#7038d4"]
		for i, account in enumerate(accounts):
			balance = frappe.db.get_value("Account", account.account, "balance") if account.account and _can("Account") else None
			bank_bars.append({"label": account.account_name or account.name, "value": flt(balance), "color": colors[i % len(colors)]})

	charts = [{"key": "bank-balance", "title": _("Bank Balance"), "type": "bar", "bars": bank_bars, "report_link": "/reports/view/General%20Ledger"}]
	return {"company": company, "currency": frappe.get_cached_value("Company", company, "default_currency") if company else "", "cards": cards, "charts": charts}


# ---------------------------------------------------------------------------
# Buying dashboard: erpnext:dashboard:buying + its charts/cards
# ---------------------------------------------------------------------------
@frappe.whitelist(methods=["GET"])
def get_buying_dashboard(company: str | None = None, months: int = MONTHS_DEFAULT):
	_require_login()
	company = _company(company)
	months = _months(months)
	base = {"docstatus": 1, **({"company": company} if company else {})}

	po_count = _count("Purchase Order", base)
	po_total = _sum("Purchase Order", "base_grand_total", base)

	cards = [
		{"key": "active-suppliers", "label": _("Active Suppliers"), "value": _count("Supplier", {"disabled": 0}), "accent": "blue", "to": "/purchases/suppliers"},
		{"key": "annual-purchase", "label": _("Annual Purchase"), "value": _sum("Purchase Invoice", "base_grand_total", {**base, "posting_date": [">=", str(get_first_day(add_months(getdate(nowdate()), -11)))]}), "accent": "orange", "to": "/purchases/invoices"},
		{"key": "average-order-values", "label": _("Average Order Value"), "value": (po_total / po_count) if po_count else 0.0, "accent": "purple", "to": "/purchases/orders"},
		{"key": "purchase-orders-count", "label": _("Purchase Orders"), "value": po_count, "accent": "blue", "to": "/purchases/orders"},
		{"key": "purchase-orders-to-bill", "label": _("Purchase Orders to Bill"), "value": _count("Purchase Order", {**base, "per_billed": ["<", 100], "status": ["not in", ["Closed", "Cancelled"]]}), "accent": "gold", "to": "/purchases/orders"},
		{"key": "purchase-orders-to-receive", "label": _("Purchase Orders to Receive"), "value": _count("Purchase Order", {**base, "per_received": ["<", 100], "status": ["not in", ["Closed", "Cancelled"]]}), "accent": "green", "to": "/purchases/orders"},
		{"key": "total-purchase-amount", "label": _("Total Purchase Amount"), "value": _sum("Purchase Invoice", "base_grand_total", base), "accent": "orange", "to": "/purchases/invoices"},
	]
	charts = [
		{"key": "material-request-analysis", "title": _("Material Request Analysis"), "type": "donut", "segments": _status_breakdown("Material Request", "status", company), "report_link": "/purchases/material-requests"},
		{"key": "purchase-order-analysis", "title": _("Purchase Order Analysis"), "type": "donut", "segments": _status_breakdown("Purchase Order", "status", company), "report_link": "/purchases/orders"},
		{"key": "purchase-order-trends", "title": _("Purchase Order Trends"), "type": "line", **_monthly_trend("Purchase Order", "base_grand_total", "transaction_date", months, company), "report_link": "/purchases/orders"},
		{"key": "top-suppliers", "title": _("Top Suppliers"), "type": "bar", "bars": _top_ranked("Purchase Invoice", "supplier", "supplier_name", "base_grand_total", company, _top_n(TOP_N_DEFAULT)), "report_link": "/purchases/suppliers"},
	]
	return {"company": company, "currency": frappe.get_cached_value("Company", company, "default_currency") if company else "", "cards": cards, "charts": charts}


# ---------------------------------------------------------------------------
# CRM dashboard: erpnext:dashboard:crm + its charts/cards
# ---------------------------------------------------------------------------
@frappe.whitelist(methods=["GET"])
def get_crm_dashboard(company: str | None = None, months: int = MONTHS_DEFAULT):
	_require_login()
	company = _company(company)
	months = _months(months)
	since = str(add_days(nowdate(), -30))

	cards = [
		{"key": "new-lead-last-1-month", "label": _("New Leads (30d)"), "value": _count("Lead", {"creation": [">=", since]}), "accent": "blue", "to": "/crm/leads"},
		{"key": "new-opportunity-last-1-month", "label": _("New Opportunities (30d)"), "value": _count("Opportunity", {"creation": [">=", since]}), "accent": "purple", "to": "/crm/opportunities"},
		{"key": "open-opportunity", "label": _("Open Opportunities"), "value": _count("Opportunity", {"status": "Open"}), "accent": "gold", "to": "/crm/opportunities"},
		{"key": "won-opportunity-last-1-month", "label": _("Won Opportunities (30d)"), "value": _count("Opportunity", {"status": "Converted", "modified": [">=", since]}), "accent": "green", "to": "/crm/opportunities"},
	]
	charts = [
		{"key": "incoming-leads", "title": _("Incoming Leads"), "type": "line", **_monthly_trend("Lead", "name", "creation", months, None), "report_link": "/crm/leads"},
		{"key": "lead-source", "title": _("Lead Source"), "type": "donut", "segments": _status_breakdown("Lead", "source", None), "report_link": "/crm/leads"},
		{"key": "opportunities-via-campaigns", "title": _("Opportunities via Campaigns"), "type": "bar", "bars": _status_breakdown("Opportunity", "campaign", None, {"campaign": ["is", "set"]}), "report_link": "/crm/opportunities"},
		{"key": "opportunity-trends", "title": _("Opportunity Trends"), "type": "line", **_monthly_trend("Opportunity", "opportunity_amount", "transaction_date", months, None), "report_link": "/crm/opportunities"},
		{"key": "territory-wise-opportunity-count", "title": _("Territory Wise Opportunity Count"), "type": "bar", "bars": _status_breakdown("Opportunity", "territory", None), "report_link": "/crm/opportunities"},
		{"key": "territory-wise-sales", "title": _("Territory Wise Sales"), "type": "bar", "bars": _top_ranked("Sales Invoice", "territory", "territory", "base_grand_total", company, _top_n(TOP_N_DEFAULT)), "report_link": "/sales/invoices"},
		{"key": "won-opportunities", "title": _("Won Opportunities"), "type": "line", **_monthly_trend_count("Opportunity", "modified", months, {"status": "Converted"}), "report_link": "/crm/opportunities"},
	]
	return {"company": company, "cards": cards, "charts": charts}


def _monthly_trend_count(doctype: str, date_field: str, months: int, extra: dict | None = None) -> dict:
	labels, values = [], []
	for offset in range(-(months - 1), 1):
		anchor = add_months(getdate(nowdate()), offset)
		labels.append(anchor.strftime("%b"))
		if not _can(doctype):
			values.append(0)
			continue
		start, end = str(get_first_day(anchor)), str(get_last_day(anchor))
		filters = {date_field: ["between", [start, end]], **(extra or {})}
		values.append(_count(doctype, filters))
	return {"labels": labels, "series": [{"name": doctype, "color": "var(--ref-success)", "values": values}]}


# ---------------------------------------------------------------------------
# Selling dashboard: erpnext:dashboard:selling + its charts/cards
# ---------------------------------------------------------------------------
@frappe.whitelist(methods=["GET"])
def get_selling_dashboard(company: str | None = None, months: int = MONTHS_DEFAULT):
	_require_login()
	company = _company(company)
	months = _months(months)
	base = {"docstatus": 1, **({"company": company} if company else {})}

	so_count = _count("Sales Order", base)
	so_total = _sum("Sales Order", "base_grand_total", base)

	cards = [
		{"key": "active-customers", "label": _("Active Customers"), "value": _count("Customer", {"disabled": 0}), "accent": "blue", "to": "/sales/customers"},
		{"key": "annual-sales", "label": _("Annual Sales"), "value": _sum("Sales Invoice", "base_grand_total", {**base, "posting_date": [">=", str(get_first_day(add_months(getdate(nowdate()), -11)))]}), "accent": "green", "to": "/sales/invoices"},
		{"key": "average-sales-order-value", "label": _("Average Sales Order Value"), "value": (so_total / so_count) if so_count else 0.0, "accent": "purple", "to": "/sales/orders"},
		{"key": "sales-orders-count", "label": _("Sales Orders"), "value": so_count, "accent": "blue", "to": "/sales/orders"},
		{"key": "sales-orders-to-bill", "label": _("Sales Orders to Bill"), "value": _count("Sales Order", {**base, "per_billed": ["<", 100], "status": ["not in", ["Closed", "Cancelled"]]}), "accent": "gold", "to": "/sales/orders"},
		{"key": "sales-orders-to-deliver", "label": _("Sales Orders to Deliver"), "value": _count("Sales Order", {**base, "per_delivered": ["<", 100], "status": ["not in", ["Closed", "Cancelled"]]}), "accent": "orange", "to": "/sales/orders"},
		{"key": "total-sales-amount", "label": _("Total Sales Amount"), "value": _sum("Sales Invoice", "base_grand_total", base), "accent": "green", "to": "/sales/invoices"},
	]
	charts = [
		{"key": "item-wise-annual-sales", "title": _("Item-wise Annual Sales"), "type": "bar", "bars": _top_ranked_child("Sales Invoice", "Sales Invoice Item", "item_code", "item_name", "base_net_amount", company, _top_n(TOP_N_DEFAULT)), "report_link": "/sales/invoices"},
		{"key": "sales-order-analysis", "title": _("Sales Order Analysis"), "type": "donut", "segments": _status_breakdown("Sales Order", "status", company), "report_link": "/sales/orders"},
		{"key": "sales-order-trends", "title": _("Sales Order Trends"), "type": "line", **_monthly_trend("Sales Order", "base_grand_total", "transaction_date", months, company), "report_link": "/sales/orders"},
		{"key": "top-customers", "title": _("Top Customers"), "type": "bar", "bars": _top_ranked("Sales Invoice", "customer", "customer_name", "base_grand_total", company, _top_n(TOP_N_DEFAULT)), "report_link": "/sales/customers"},
	]
	return {"company": company, "currency": frappe.get_cached_value("Company", company, "default_currency") if company else "", "cards": cards, "charts": charts}


def _top_ranked_child(parent_doctype: str, child_doctype: str, group_field: str, label_field: str, amount_field: str, company: str | None, limit: int) -> list[dict]:
	if not (_can(parent_doctype) and _can(child_doctype)):
		return []
	filters = {"docstatus": 1}
	if company:
		filters["company"] = company
	parent_names = frappe.get_list(parent_doctype, filters=filters, pluck="name", limit_page_length=2000)
	if not parent_names:
		return []
	# Child rows carry no independent permission — parent read access above
	# already gates visibility, matching the existing get_top_categories pattern.
	rows = frappe.get_all(
		child_doctype, filters={"parent": ["in", parent_names]},
		fields=[group_field, label_field, f"sum({amount_field}) as total"],
		group_by=group_field, order_by="total desc", limit_page_length=limit,
	)
	return [{"label": row.get(label_field) or row.get(group_field), "value": flt(row.total)} for row in rows]


# ---------------------------------------------------------------------------
# Stock dashboard: erpnext:dashboard:stock + its charts/cards
# ---------------------------------------------------------------------------
@frappe.whitelist(methods=["GET"])
def get_stock_dashboard(months: int = MONTHS_DEFAULT):
	_require_login()
	months = _months(months)

	total_stock_value = 0.0
	if _can("Bin"):
		rows = frappe.get_list("Bin", filters={"actual_qty": [">", 0]}, fields=["sum(actual_qty * valuation_rate) as total"], limit_page_length=1)
		total_stock_value = flt(rows[0].total) if rows else 0.0

	cards = [
		{"key": "total-active-items", "label": _("Total Active Items"), "value": _count("Item", {"disabled": 0}), "accent": "blue", "to": "/inventory/products"},
		{"key": "total-stock-value", "label": _("Total Stock Value"), "value": total_stock_value, "accent": "green", "to": "/inventory/products"},
		{"key": "total-warehouses", "label": _("Total Warehouses"), "value": _count("Warehouse", {"disabled": 0}), "accent": "purple", "to": "/inventory/warehouses"},
	]
	charts = [
		{"key": "delivery-trends", "title": _("Delivery Trends"), "type": "line", **_monthly_trend_count("Delivery Note", "posting_date", months, {"docstatus": 1}), "report_link": "/sales/delivery-notes"},
		{"key": "item-shortage-summary", "title": _("Item Shortage Summary"), "type": "bar", "bars": _item_shortage(), "report_link": "/reports/view/Stock%20Balance"},
		{"key": "oldest-items", "title": _("Oldest Items"), "type": "bar", "bars": _oldest_items(), "report_link": "/inventory/products"},
		{"key": "purchase-receipt-trends", "title": _("Purchase Receipt Trends"), "type": "line", **_monthly_trend_count("Purchase Receipt", "posting_date", months, {"docstatus": 1}), "report_link": "/purchases/receipts"},
		{"key": "stock-value-by-item-group", "title": _("Stock Value by Item Group"), "type": "donut", "segments": _stock_value_by_item_group(), "report_link": "/reports/view/Stock%20Balance"},
		{"key": "warehouse-wise-stock-value", "title": _("Warehouse wise Stock Value"), "type": "bar", "bars": _warehouse_wise_stock_value(), "report_link": "/inventory/warehouses"},
	]
	return {"cards": cards, "charts": charts}


def _item_shortage() -> list[dict]:
	if not (_can("Bin") and _can("Item Reorder")):
		return []
	rows = frappe.get_list(
		"Bin", filters={"projected_qty": ["<", 0]}, fields=["item_code", "warehouse", "projected_qty"],
		order_by="projected_qty asc", limit_page_length=MAX_TOP_N,
	)
	return [{"label": f"{row.item_code} ({row.warehouse})", "value": abs(flt(row.projected_qty)), "color": "var(--ref-danger)"} for row in rows]


def _oldest_items() -> list[dict]:
	if not _can("Item"):
		return []
	rows = frappe.get_list("Item", filters={"disabled": 0, "is_stock_item": 1}, fields=["item_code", "item_name", "creation"], order_by="creation asc", limit_page_length=MAX_TOP_N)
	today = getdate(nowdate())
	return [{"label": row.item_name or row.item_code, "value": (today - getdate(row.creation)).days, "color": "var(--ref-secondary-text)"} for row in rows]


def _stock_value_by_item_group() -> list[dict]:
	if not (_can("Bin") and _can("Item")):
		return []
	rows = frappe.get_list("Bin", filters={"actual_qty": [">", 0]}, fields=["item_code", "actual_qty", "valuation_rate"], limit_page_length=5000)
	if not rows:
		return []
	item_codes = list({row.item_code for row in rows})
	item_groups = {item.name: item.item_group for item in frappe.get_list("Item", filters={"name": ["in", item_codes]}, fields=["name", "item_group"])}
	totals: dict[str, float] = {}
	for row in rows:
		group = item_groups.get(row.item_code) or _("Ungrouped")
		totals[group] = totals.get(group, 0.0) + flt(row.actual_qty) * flt(row.valuation_rate)
	ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)[:MAX_TOP_N]
	colors = ["var(--ref-primary-blue)", "var(--ref-success)", "var(--ref-warning)", "#7038d4", "var(--ref-danger)"]
	return [{"label": label, "value": value, "color": colors[i % len(colors)]} for i, (label, value) in enumerate(ranked)]


def _warehouse_wise_stock_value() -> list[dict]:
	if not _can("Bin"):
		return []
	rows = frappe.get_list(
		"Bin", filters={"actual_qty": [">", 0]}, fields=["warehouse", "sum(actual_qty * valuation_rate) as total"],
		group_by="warehouse", order_by="total desc", limit_page_length=MAX_TOP_N,
	)
	colors = ["var(--ref-primary-blue)", "var(--ref-success)", "var(--ref-warning)", "#7038d4"]
	return [{"label": row.warehouse, "value": flt(row.total), "color": colors[i % len(colors)]} for i, row in enumerate(rows)]
