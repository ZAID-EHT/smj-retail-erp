"""Permission-aware adapters for ERPNext's native analytical Desk pages."""

from __future__ import annotations

from collections import defaultdict
from html import unescape

import frappe
from frappe import _
from frappe.utils import add_months, cint, flt, getdate, nowdate


PAGE_RULES = {
	"sales-funnel": {"doctypes": ("Lead", "Opportunity", "Quotation", "Customer")},
	"warehouse-capacity-summary": {"doctypes": ("Putaway Rule", "Warehouse", "Item")},
}
LINK_FIELDS = {
	"sales-funnel": {"company": ("Company", {})},
	"warehouse-capacity-summary": {
		"company": ("Company", {}),
		"warehouse": ("Warehouse", {"is_group": 0}),
		"parent_warehouse": ("Warehouse", {"is_group": 1}),
		"item_code": ("Item", {"disabled": 0}),
	},
}
MAX_LINK_RESULTS = 30
MAX_ANALYTICS_ROWS = 5000


def _require_page(page: str) -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	if page not in PAGE_RULES or not frappe.db.exists("Page", page):
		frappe.throw(_("Analytics page is not available."), frappe.DoesNotExistError)
	if not frappe.has_permission("Page", "read", doc=page):
		frappe.throw(_("Analytics page is not available."), frappe.PermissionError)


def _require_doctypes(*doctypes: str) -> None:
	if not all(frappe.has_permission(doctype, "read") for doctype in doctypes):
		frappe.throw(_("You do not have access to the required records."), frappe.PermissionError)


def _visible_link(doctype: str, name: str, filters: dict | None = None) -> bool:
	if not name or not frappe.has_permission(doctype, "read"):
		return False
	return bool(frappe.get_list(
		doctype,
		filters={"name": name, **(filters or {})},
		pluck="name",
		limit_page_length=1,
	))


def _count(doctype: str, filters=None, or_filters=None) -> int:
	rows = frappe.get_list(
		doctype,
		filters=filters or {},
		or_filters=or_filters or [],
		fields=["count(name) as total"],
		limit_page_length=1,
	)
	return cint(rows[0].total) if rows else 0


@frappe.whitelist(methods=["GET"])
def search_link(page: str, fieldname: str, txt: str = ""):
	_require_page(page)
	if fieldname not in LINK_FIELDS.get(page, {}):
		frappe.throw(_("Unsupported analytics filter."), frappe.ValidationError)
	doctype, filters = LINK_FIELDS[page][fieldname]
	_require_doctypes(doctype)
	txt = str(txt or "").strip()[:140]
	or_filters = [["name", "like", f"%{txt}%"]] if txt else []
	if doctype == "Item" and txt:
		or_filters.append(["item_name", "like", f"%{txt}%"])
	rows = frappe.get_list(
		doctype,
		filters=filters,
		or_filters=or_filters,
		fields=["name"],
		order_by="name asc",
		limit_page_length=MAX_LINK_RESULTS,
	)
	return [{"value": row.name, "label": row.name} for row in rows]


def _sales_filters(from_date: str | None, to_date: str | None, company: str | None):
	from_date = getdate(from_date or add_months(nowdate(), -1))
	to_date = getdate(to_date or nowdate())
	if from_date >= to_date:
		frappe.throw(_("To Date must be greater than From Date."), frappe.ValidationError)
	if not _visible_link("Company", company):
		frappe.throw(_("A permitted Company is required."), frappe.PermissionError)
	return str(from_date), str(to_date), company


def _converted_customer_count(from_date: str, to_date: str, company: str) -> int:
	customers = frappe.get_list(
		"Customer",
		filters={"creation": ["between", [from_date, to_date]], "lead_name": ["!=", ""]},
		fields=["lead_name"],
		limit_page_length=MAX_ANALYTICS_ROWS,
	)
	leads = {row.lead_name for row in customers if row.lead_name}
	if not leads:
		return 0
	return len(frappe.get_list(
		"Lead",
		filters={"name": ["in", sorted(leads)], "company": company},
		pluck="name",
		limit_page_length=MAX_ANALYTICS_ROWS,
	))


@frappe.whitelist(methods=["GET"])
def get_sales_funnel(from_date: str | None = None, to_date: str | None = None, company: str | None = None):
	_require_page("sales-funnel")
	_require_doctypes("Lead", "Opportunity", "Quotation", "Customer")
	from_date, to_date, company = _sales_filters(from_date, to_date, company)
	created = ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59.999999"]]
	funnel = [
		{"label": _("Active Leads"), "value": _count("Lead", {"creation": created, "company": company}), "color": "#B03B46"},
		{"label": _("Opportunities"), "value": _count("Opportunity", {"creation": created, "company": company, "opportunity_from": "Lead"}), "color": "#F09C00"},
		{
			"label": _("Quotations"),
			"value": _count(
				"Quotation",
				{"docstatus": 1, "creation": created, "company": company},
				[["opportunity", "!=", ""], ["quotation_to", "=", "Lead"]],
			),
			"color": "#006685",
		},
		{"label": _("Converted"), "value": _converted_customer_count(from_date, to_date, company), "color": "#00AD65"},
	]
	opportunities = frappe.get_list(
		"Opportunity",
		filters={
			"status": ["in", ["Open", "Quotation", "Replied"]],
			"company": company,
			"transaction_date": ["between", [from_date, to_date]],
		},
		fields=["currency", "sales_stage", "opportunity_amount", "probability", "source"],
		limit_page_length=MAX_ANALYTICS_ROWS,
	)
	from erpnext.accounts.report.utils import convert
	default_currency = frappe.get_cached_value("Global Defaults", "None", "default_currency")
	pipeline = defaultdict(float)
	by_source = defaultdict(float)
	for row in opportunities:
		amount = flt(convert(row.opportunity_amount, row.currency, default_currency, to_date)) * flt(row.probability) / 100
		pipeline[row.sales_stage or _("Unspecified")] += amount
		by_source[row.source or _("Unspecified")] += amount
	return {
		"filters": {"from_date": from_date, "to_date": to_date, "company": company},
		"currency": default_currency,
		"funnel": funnel,
		"pipeline": [{"label": label, "value": value} for label, value in pipeline.items()],
		"by_source": [{"label": label, "value": value} for label, value in by_source.items()],
		"truncated": len(opportunities) >= MAX_ANALYTICS_ROWS,
	}


@frappe.whitelist(methods=["GET"])
def get_warehouse_capacity(
	company: str | None = None,
	warehouse: str | None = None,
	parent_warehouse: str | None = None,
	item_code: str | None = None,
	start: int = 0,
	sort_by: str = "stock_capacity",
	sort_order: str = "desc",
):
	_require_page("warehouse-capacity-summary")
	_require_doctypes("Putaway Rule", "Warehouse", "Item")
	if not company or not _visible_link("Company", company):
		frappe.throw(_("Company is not available."), frappe.PermissionError)
	if warehouse and not _visible_link("Warehouse", warehouse, {"is_group": 0}):
		frappe.throw(_("Warehouse is not available."), frappe.PermissionError)
	if parent_warehouse and not _visible_link("Warehouse", parent_warehouse, {"is_group": 1}):
		frappe.throw(_("Parent Warehouse is not available."), frappe.PermissionError)
	if item_code and not _visible_link("Item", item_code, {"disabled": 0}):
		frappe.throw(_("Item is not available."), frappe.PermissionError)
	if sort_by not in {"stock_capacity", "percent_occupied", "actual_qty"}:
		frappe.throw(_("Unsupported capacity sort field."), frappe.ValidationError)
	if sort_order not in {"asc", "desc"}:
		frappe.throw(_("Unsupported capacity sort order."), frappe.ValidationError)
	start = max(cint(start), 0)
	from erpnext.stock.dashboard.warehouse_capacity_dashboard import get_data
	rows = get_data(
		item_code=item_code,
		warehouse=warehouse,
		parent_warehouse=parent_warehouse,
		company=company,
		start=start,
		sort_by=sort_by,
		sort_order=sort_order,
	)
	visible = []
	for row in rows:
		item = unescape(row.item_code)
		row_warehouse = unescape(row.warehouse)
		if _visible_link("Item", item) and _visible_link("Warehouse", row_warehouse):
			visible.append({
				"item_code": item,
				"warehouse": row_warehouse,
				"company": unescape(row.company),
				"stock_capacity": flt(row.stock_capacity),
				"actual_qty": flt(row.actual_qty),
				"percent_occupied": flt(row.percent_occupied),
			})
	return {"records": visible[:10], "start": start, "has_more": len(visible) > 10}
