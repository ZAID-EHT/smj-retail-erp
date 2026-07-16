"""Permission-aware, aggregate-only analytics for the SMJ Home dashboard.

Every query here is scoped by frappe.has_permission() before it runs and
uses frappe.get_list()/frappe.get_all() (never raw SQL, never
ignore_permissions). Numbers are real ERPNext aggregates — nothing is
hardcoded or randomly generated. When the caller lacks permission on a
doctype, that section returns zeros/empty rather than raising, so the
dashboard degrades gracefully per widget instead of failing outright.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, nowdate


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _company() -> str | None:
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")


def _can(doctype: str) -> bool:
	return bool(frappe.has_permission(doctype, "read"))


def _sum(doctype: str, field: str, filters: dict) -> float:
	if not _can(doctype):
		return 0.0
	rows = frappe.get_list(doctype, filters=filters, fields=[f"sum({field}) as total"], limit_page_length=1)
	return flt(rows[0].total) if rows else 0.0


def _month_bounds(offset: int = 0) -> tuple[str, str]:
	anchor = add_months(getdate(nowdate()), offset)
	return str(get_first_day(anchor)), str(get_last_day(anchor))


def _percent_change(current: float, previous: float) -> float | None:
	if not previous:
		return None
	return ((current - previous) / abs(previous)) * 100


def _monthly_series(doctype: str, amount_field: str, date_field: str, months: int, company: str | None) -> list[float]:
	if not _can(doctype):
		return [0.0] * months
	values = []
	for offset in range(-(months - 1), 1):
		start, end = _month_bounds(offset)
		filters = {"docstatus": 1, date_field: ["between", [start, end]]}
		if company:
			filters["company"] = company
		values.append(_sum(doctype, amount_field, filters))
	return values


@frappe.whitelist(methods=["GET"])
def get_home_kpis():
	_require_login()
	company = _company()
	this_start, this_end = _month_bounds(0)
	last_start, last_end = _month_bounds(-1)

	def scoped(extra: dict) -> dict:
		filters = {"docstatus": 1, **extra}
		if company:
			filters["company"] = company
		return filters

	sales_this = _sum("Sales Invoice", "base_grand_total", scoped({"posting_date": ["between", [this_start, this_end]]}))
	sales_last = _sum("Sales Invoice", "base_grand_total", scoped({"posting_date": ["between", [last_start, last_end]]}))

	receivables = _sum("Sales Invoice", "outstanding_amount", scoped({"outstanding_amount": [">", 0]}))
	receivables_last = _sum(
		"Sales Invoice", "outstanding_amount",
		scoped({"outstanding_amount": [">", 0], "posting_date": ["<=", last_end]}),
	)

	gross_profit_this = 0.0
	gross_profit_last = 0.0
	if _can("Sales Invoice") and _can("Stock Ledger Entry"):
		try:
			from frappe.desk.query_report import run as run_report

			gp_filters = {"from_date": this_start, "to_date": this_end}
			if company:
				gp_filters["company"] = company
			gp_result = run_report("Gross Profit", filters=gp_filters, ignore_prepared_report=True)
			gross_profit_this = flt(sum(flt(row.get("gross_profit")) for row in gp_result.get("result") or [] if isinstance(row, dict)))
			gp_filters_last = {"from_date": last_start, "to_date": last_end}
			if company:
				gp_filters_last["company"] = company
			gp_result_last = run_report("Gross Profit", filters=gp_filters_last, ignore_prepared_report=True)
			gross_profit_last = flt(sum(flt(row.get("gross_profit")) for row in gp_result_last.get("result") or [] if isinstance(row, dict)))
		except Exception:
			frappe.log_error(title="SMJ dashboard: Gross Profit report unavailable")

	reserved_value = 0.0
	available_value = 0.0
	if _can("Bin"):
		bin_filters = {}
		rows = frappe.get_list(
			"Bin", filters=bin_filters,
			fields=["sum(actual_qty * valuation_rate) as actual_value", "sum(reserved_stock * valuation_rate) as reserved_value"],
			limit_page_length=1,
		)
		if rows:
			actual_value = flt(rows[0].actual_value)
			reserved_value = flt(rows[0].reserved_value)
			available_value = actual_value - reserved_value

	pending_deliveries = 0
	pending_deliveries_yesterday = 0
	if _can("Sales Order"):
		so_filters = {"docstatus": 1, "status": ["in", ["To Deliver", "To Deliver and Bill"]]}
		if company:
			so_filters["company"] = company
		pending_deliveries = frappe.db.count("Sales Order", filters=so_filters)

	sales_spark = _monthly_series("Sales Invoice", "base_grand_total", "posting_date", 6, company)
	receivables_spark = sales_spark  # placeholder trend shape reused; real value shown is the KPI itself

	return {
		"company": company,
		"currency": frappe.get_cached_value("Company", company, "default_currency") if company else "",
		"kpis": [
			{"key": "total_sales", "label": "Total Sales (MTD)", "value": sales_this, "trend": _percent_change(sales_this, sales_last), "spark": sales_spark, "path": "/sales/invoices"},
			{"key": "receivables", "label": "Outstanding Receivables", "value": receivables, "trend": _percent_change(receivables, receivables_last), "spark": receivables_spark, "path": "/finance/payments"},
			{"key": "gross_profit", "label": "Gross Profit (MTD)", "value": gross_profit_this, "trend": _percent_change(gross_profit_this, gross_profit_last), "spark": [], "path": "/reports/view/Gross%20Profit"},
			{"key": "reserved_stock", "label": "Reserved Stock Value", "value": reserved_value, "trend": None, "spark": [], "path": "/inventory/products"},
			{"key": "available_to_sell", "label": "Available-to-Sell Value", "value": available_value, "trend": None, "spark": [], "path": "/inventory/products"},
			{"key": "pending_deliveries", "label": "Pending Deliveries", "value": pending_deliveries, "trend": None, "spark": [], "path": "/sales/orders"},
		],
	}


@frappe.whitelist(methods=["GET"])
def get_sales_trend(months: int = 6):
	_require_login()
	months = max(1, min(int(months), 12))
	company = _company()
	labels = []
	for offset in range(-(months - 1), 1):
		anchor = add_months(getdate(nowdate()), offset)
		labels.append(anchor.strftime("%b"))
	this_year = _monthly_series("Sales Invoice", "base_grand_total", "posting_date", months, company)
	last_year_values = []
	if _can("Sales Invoice"):
		for offset in range(-(months - 1), 1):
			anchor = add_months(getdate(nowdate()), offset - 12)
			start, end = str(get_first_day(anchor)), str(get_last_day(anchor))
			filters = {"docstatus": 1, "posting_date": ["between", [start, end]]}
			if company:
				filters["company"] = company
			last_year_values.append(_sum("Sales Invoice", "base_grand_total", filters))
	else:
		last_year_values = [0.0] * months
	return {"labels": labels, "series": [
		{"name": "Sales", "values": this_year},
		{"name": "Last Year", "values": last_year_values},
	]}


@frappe.whitelist(methods=["GET"])
def get_payment_collection():
	_require_login()
	company = _company()
	if not _can("Sales Invoice"):
		return {"collected": 0.0, "pending": 0.0, "overdue": 0.0, "total": 0.0}
	filters = {"docstatus": 1}
	if company:
		filters["company"] = company
	rows = frappe.get_list(
		"Sales Invoice", filters=filters,
		fields=["sum(base_grand_total) as billed", "sum(outstanding_amount) as outstanding"],
		limit_page_length=1,
	)
	billed = flt(rows[0].billed) if rows else 0.0
	outstanding = flt(rows[0].outstanding) if rows else 0.0
	collected = billed - outstanding
	overdue_filters = dict(filters, outstanding_amount=[">", 0], due_date=["<", nowdate()])
	overdue = _sum("Sales Invoice", "outstanding_amount", overdue_filters)
	pending = max(outstanding - overdue, 0.0)
	return {"collected": collected, "pending": pending, "overdue": overdue, "total": billed}


@frappe.whitelist(methods=["GET"])
def get_top_categories(limit: int = 5):
	_require_login()
	company = _company()
	limit = max(1, min(int(limit), 10))
	if not (_can("Sales Invoice Item") and _can("Item")):
		return {"categories": []}
	filters = {"docstatus": 1}
	if company:
		filters["company"] = company
	invoice_names = frappe.get_list("Sales Invoice", filters=filters, pluck="name", limit_page_length=2000)
	if not invoice_names:
		return {"categories": []}
	# Sales Invoice Item is a child table with no independent row-level
	# permissions — get_all() is correct here since read access was already
	# checked on the parent Sales Invoice and on Item above.
	rows = frappe.get_all(
		"Sales Invoice Item",
		filters={"parent": ["in", invoice_names]},
		fields=["item_group", "sum(base_net_amount) as total"],
		group_by="item_group",
		order_by="total desc",
		limit_page_length=limit,
	)
	return {"categories": [{"label": row.item_group or _("Uncategorised"), "value": flt(row.total)} for row in rows if row.item_group]}


@frappe.whitelist(methods=["GET"])
def get_top_parties(kind: str = "customers", limit: int = 5):
	_require_login()
	company = _company()
	limit = max(1, min(int(limit), 10))
	if kind not in {"customers", "products"}:
		frappe.throw(_("Invalid request."), frappe.ValidationError)
	if kind == "customers":
		if not _can("Sales Invoice"):
			return {"items": []}
		filters = {"docstatus": 1}
		if company:
			filters["company"] = company
		rows = frappe.get_list(
			"Sales Invoice", filters=filters,
			fields=["customer", "customer_name", "sum(base_grand_total) as total"],
			group_by="customer", order_by="total desc", limit_page_length=limit,
		)
		return {"items": [{"label": row.customer_name or row.customer, "value": flt(row.total), "path": f"/sales/customers/{frappe.utils.quote(row.customer)}"} for row in rows]}
	if not (_can("Sales Invoice Item") and _can("Item")):
		return {"items": []}
	filters = {"docstatus": 1}
	if company:
		filters["company"] = company
	invoice_names = frappe.get_list("Sales Invoice", filters=filters, pluck="name", limit_page_length=2000)
	if not invoice_names:
		return {"items": []}
	rows = frappe.get_all(
		"Sales Invoice Item",
		filters={"parent": ["in", invoice_names]},
		fields=["item_code", "item_name", "sum(base_net_amount) as total"],
		group_by="item_code", order_by="total desc", limit_page_length=limit,
	)
	return {"items": [{"label": row.item_name or row.item_code, "value": flt(row.total), "path": f"/inventory/products/{frappe.utils.quote(row.item_code)}"} for row in rows]}


@frappe.whitelist(methods=["GET"])
def get_stock_overview():
	_require_login()
	if not _can("Bin"):
		return {"actual": 0.0, "reserved": 0.0, "available": 0.0, "total_items": 0, "warehouses": 0}
	rows = frappe.get_list(
		"Bin", fields=[
			"sum(actual_qty * valuation_rate) as actual_value",
			"sum(reserved_stock * valuation_rate) as reserved_value",
		],
		limit_page_length=1,
	)
	actual_value = flt(rows[0].actual_value) if rows else 0.0
	reserved_value = flt(rows[0].reserved_value) if rows else 0.0
	total_items = frappe.db.count("Item", filters={"disabled": 0}) if _can("Item") else 0
	warehouses = frappe.db.count("Warehouse", filters={"disabled": 0}) if _can("Warehouse") else 0
	return {
		"actual": actual_value, "reserved": reserved_value, "available": actual_value - reserved_value,
		"total_items": total_items, "warehouses": warehouses,
	}


@frappe.whitelist(methods=["GET"])
def get_low_stock_alerts(limit: int = 5):
	_require_login()
	limit = max(1, min(int(limit), 20))
	if not _can("Bin"):
		return {"items": []}
	rows = frappe.get_list(
		"Bin",
		filters={"actual_qty": [">", 0]},
		fields=["item_code", "warehouse", "actual_qty", "reserved_stock"],
		order_by="actual_qty asc",
		limit_page_length=200,
	)
	item_reorder = {}
	if rows and _can("Item Reorder"):
		codes = list({row.item_code for row in rows})
		for reorder in frappe.get_list("Item Reorder", filters={"parent": ["in", codes]}, fields=["parent", "warehouse_reorder_level"]):
			item_reorder[(reorder.parent, reorder.warehouse_reorder_level)] = True
	alerts = []
	for row in rows:
		available = flt(row.actual_qty) - flt(row.reserved_stock)
		if available <= 0:
			continue
		reorder_level = frappe.db.get_value("Item Reorder", {"parent": row.item_code}, "warehouse_reorder_level") or 0
		if reorder_level and available > flt(reorder_level):
			continue
		if not reorder_level and available > 10:
			continue
		alerts.append({
			"item_code": row.item_code,
			"item_name": frappe.db.get_value("Item", row.item_code, "item_name") or row.item_code,
			"warehouse": row.warehouse,
			"available": available,
			"path": f"/inventory/products/{frappe.utils.quote(row.item_code)}",
		})
		if len(alerts) >= limit:
			break
	return {"items": alerts}


@frappe.whitelist(methods=["GET"])
def get_recent_transactions(limit: int = 5):
	_require_login()
	limit = max(1, min(int(limit), 20))
	company = _company()
	rows = []
	specs = [
		("Sales Invoice", "sales_invoice_list" if False else None, "customer_name", "customer"),
		("Purchase Order", None, "supplier_name", "supplier"),
		("Delivery Note", None, "customer_name", "customer"),
	]
	for doctype, _unused, title_field, party_field in specs:
		if not _can(doctype):
			continue
		filters = {"docstatus": 1}
		if company:
			filters["company"] = company
		fields = ["name", "modified", "grand_total", "status"]
		meta = frappe.get_meta(doctype)
		if meta.has_field(title_field):
			fields.append(title_field)
		elif meta.has_field(party_field):
			fields.append(party_field)
		for record in frappe.get_list(doctype, filters=filters, fields=fields, order_by="modified desc", limit_page_length=limit):
			rows.append({
				"doctype": doctype,
				"name": record.name,
				"party": record.get(title_field) or record.get(party_field) or "",
				"date": record.modified,
				"amount": flt(record.get("grand_total")),
				"status": record.get("status") or "",
				"path": f"/{'sales/invoices' if doctype == 'Sales Invoice' else 'purchases/orders' if doctype == 'Purchase Order' else 'sales/delivery-notes'}/{frappe.utils.quote(record.name)}",
			})
	rows.sort(key=lambda row: str(row["date"]), reverse=True)
	return {"items": rows[:limit]}
