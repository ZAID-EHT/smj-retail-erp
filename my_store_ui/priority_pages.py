"""Permission-aware data adapters for priority Retail ERP pages."""

from __future__ import annotations

import shutil
from urllib.parse import quote, urlsplit

import frappe
from frappe import _
from frappe.utils import add_months, cint, getdate, nowdate

from my_store_ui.services.frontend_routes import (
	get_permitted_navigation,
	resolve_frontend_route,
	route_is_permitted,
)
from my_store_ui.services.priority_registry import MODULES, REPORT_FILTERS, REPORT_GROUPS


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _authorise(path: str):
	definition, params = resolve_frontend_route(path)
	if not definition or not route_is_permitted(definition):
		frappe.throw(_("Page is not available."), frappe.PermissionError)
	return definition, params


def _safe_count(doctype: str) -> int:
	if not frappe.has_permission(doctype, "read"):
		return 0
	rows = frappe.get_list(doctype, fields=["count(name) as total"], limit_page_length=1)
	return cint(rows[0].total) if rows else 0


def _detail_path(path: str, name: str) -> str:
	return f"{path}/{quote(name, safe='')}"


@frappe.whitelist(methods=["GET"])
def get_priority_route_definition(path: str):
	_require_login()
	definition, params = _authorise(path)
	component = definition.get("component")
	# The Wholesale Transaction Register is a dedicated Retail ERP register page.
	if definition.get("classification") == "register":
		component = "register"
	# Payment Reconciliation is a dedicated 3-step adapter (see
	# my_store_ui.wholesale.payment_reconciliation_api), not the generic
	# read-only "specialised interface" placeholder.
	if path == "/finance/payment-reconciliation":
		component = "payment_reconciliation"
	# Bank Reconciliation Tool is a dedicated adapter (see
	# my_store_ui.wholesale.bank_reconciliation_api) reproducing ERPNext's
	# own Bank Reconciliation Tool controller functions, not the generic
	# read-only "specialised interface" placeholder.
	if path == "/finance/bank-reconciliation":
		component = "bank_reconciliation"
	# Bank Clearance and Pegged Currencies are Single DocTypes (frappe.get_meta
	# .issingle) — always exactly one record, no list/new mode. Dedicated
	# pages instead of forcing them through the generic list-oriented engine.
	# Pegged Currencies uses universal/api.py's permission-aware Single
	# load/save branch; Bank Clearance uses its controller-specific adapter.
	if path == "/finance/bank-clearance":
		component = "bank_clearance"
	if path == "/finance/pegged-currencies":
		component = "pegged_currencies"
	if path == "/admin/print-settings":
		component = "single"
	if path == "/sales/funnel":
		component = "sales_funnel"
	if path == "/inventory/warehouse-capacity":
		component = "warehouse_capacity"
	if component not in {
		"entity", "tree", "special", "report", "report_hub", "register",
		"payment_reconciliation", "bank_reconciliation", "bank_clearance", "pegged_currencies", "single",
		"sales_funnel", "warehouse_capacity",
	}:
		frappe.throw(_("This route uses a dedicated Retail ERP page."), frappe.ValidationError)
	result = {
		"component": component, "mode": definition.get("mode"), "module": definition.get("module"),
		"feature_id": definition.get("feature_id"), "base_path": definition.get("base_path"),
		"classification": definition.get("classification"), "defaults": definition.get("defaults") or {},
		"params": params,
	}
	if definition.get("doctype"):
		result["doctype"] = definition["doctype"]
		result["feature"] = frappe.scrub(definition["doctype"]).replace("_", "-")
		result["permissions"] = {
			"can_read": frappe.has_permission(definition["doctype"], "read"),
			"can_create": frappe.has_permission(definition["doctype"], "create"),
		}
	if definition.get("report"):
		result["report"] = definition["report"]
	if definition.get("group"):
		result["group"] = definition["group"]
	if definition.get("alias"):
		result["redirect"] = definition["alias"]
	return result


@frappe.whitelist(methods=["GET"])
def get_module_dashboard(module: str):
	_require_login()
	module = str(module or "").lower()
	if module not in MODULES:
		frappe.throw(_("Module is not available."), frappe.DoesNotExistError)
	_authorise(f"/{module}")
	permitted_navigation = get_permitted_navigation()
	navigation = next((item for item in permitted_navigation if item["name"] == module), None)
	links = navigation.get("links", []) if navigation else []
	if module == "home":
		links = [link for item in permitted_navigation if item["name"] != "home" for link in item.get("links", [])[:2]]
	metrics, recent, quick_actions, reports = [], [], [], []
	seen = set()
	for link in links:
		path = link.get("path")
		definition, _params = resolve_frontend_route(path or "")
		if not definition or not route_is_permitted(definition):
			continue
		doctype = definition.get("doctype")
		if doctype and doctype not in seen:
			seen.add(doctype)
			meta = frappe.get_meta(doctype)
			# Single settings records are represented by their controlled special
			# page; they are not list metrics and cannot be queried with get_list.
			if meta.issingle:
				continue
			metrics.append({"label": link["label"], "value": _safe_count(doctype), "path": path})
			if frappe.has_permission(doctype, "create"):
				quick_actions.append({"label": f"New {meta.get('label') or doctype}", "path": f"{definition.get('base_path') or path}/new"})
			fields = ["name", "modified"]
			if meta.title_field and meta.has_field(meta.title_field):
				fields.append(meta.title_field)
			for row in frappe.get_list(doctype, fields=fields, order_by="modified desc", limit_page_length=3) or []:
				recent.append({"doctype": doctype, "name": row.name, "title": row.get(meta.title_field) or row.name, "modified": row.modified, "path": _detail_path(definition.get("base_path") or path, row.name)})
		if definition.get("report") or "/reports/" in (path or ""):
			reports.append({"label": link["label"], "path": path})
	return {
		"module": module, **MODULES[module], "metrics": metrics[:8], "quick_actions": quick_actions[:8],
		"recent": sorted(recent, key=lambda row: str(row["modified"]), reverse=True)[:8],
		"alerts": [], "reports": reports[:8], "links": links,
	}


def _report_permitted(name: str) -> bool:
	return bool(
		frappe.db.exists("Report", {"name": name, "disabled": 0})
		and frappe.has_permission("Report", "read", doc=name)
	)


def _report_route(name: str) -> str:
	return f"/reports/view/{quote(name, safe='')}"


@frappe.whitelist(methods=["GET"])
def get_report_hub(group: str | None = None):
	_require_login()
	if group and group not in REPORT_GROUPS:
		frappe.throw(_("Report group is not available."), frappe.DoesNotExistError)
	groups = [group] if group else list(REPORT_GROUPS)
	result = []
	for key in groups:
		reports = []
		for name in REPORT_GROUPS[key]:
			if not _report_permitted(name):
				continue
			doc = frappe.get_cached_doc("Report", name)
			reports.append({"name": name, "report_type": doc.report_type, "reference_doctype": doc.ref_doctype, "prepared_report": bool(doc.prepared_report), "path": _report_route(name)})
		if reports:
			result.append({"key": key, "label": MODULES.get(key, {"label": key.title()})["label"], "reports": reports})
	return {"groups": result, "selected_group": group}


def _filter_definition(fieldname: str) -> dict:
	links = {
		"company": "Company", "customer": "Customer", "supplier": "Supplier", "warehouse": "Warehouse",
		"item_code": "Item", "item_group": "Item Group", "account": "Account", "bank_account": "Bank Account",
		"fiscal_year": "Fiscal Year", "from_fiscal_year": "Fiscal Year", "to_fiscal_year": "Fiscal Year",
		"party": None,
		# Financial-statement / ledger drill-down filters (General Ledger, Trial
		# Balance, P&L, Balance Sheet, Cash Flow, AR/AP, Customer/Supplier Ledger).
		"cost_center": "Cost Center", "project": "Project", "finance_book": "Finance Book",
		"presentation_currency": "Currency", "party_account": "Account",
		"customer_group": "Customer Group", "supplier_group": "Supplier Group", "territory": "Territory",
		"sales_partner": "Sales Partner", "sales_person": "Sales Person",
		"payment_terms_template": "Payment Terms Template",
		# Stock ledger drill-down filters (Warehouse/Batch/Serial No navigation).
		"batch_no": "Batch", "serial_no": "Serial No",
		"request_for_quotation": "Request for Quotation", "supplier_quotation": "Supplier Quotation",
	}
	if fieldname in {"from_date", "to_date", "posting_date", "period_start_date", "period_end_date", "report_date"}:
		fieldtype, options = "Date", None
	elif fieldname in {"periodicity", "ageing_based_on", "party_type", "filter_based_on", "group_by"}:
		fieldtype, options = "Select", {
			"periodicity": ["Yearly", "Half-Yearly", "Quarterly", "Monthly"],
			"ageing_based_on": ["Due Date", "Posting Date"], "party_type": ["Customer", "Supplier"],
			"filter_based_on": ["Fiscal Year", "Date Range"],
			# Gross Profit's Group By is reqd-with-a-default in erpnext's own
			# .js; its execute() indexes group_wise_columns by this value and
			# raises TypeError on None, so it must always carry a default.
			"group_by": [
				"Invoice", "Item Code", "Item Group", "Brand", "Warehouse", "Customer",
				"Customer Group", "Territory", "Sales Person", "Project", "Cost Center",
				"Monthly", "Payment Term",
			],
		}[fieldname]
	else:
		fieldtype, options = ("Link", links.get(fieldname)) if fieldname in links else ("Data", None)
	return {"fieldname": fieldname, "label": fieldname.replace("_", " ").title(), "fieldtype": fieldtype, "options": options, "required": fieldname == "company"}


REPORT_LINK_DOCTYPES = {
	"company": "Company", "customer": "Customer", "supplier": "Supplier", "warehouse": "Warehouse",
	"item_code": "Item", "item_group": "Item Group", "account": "Account", "bank_account": "Bank Account",
	"fiscal_year": "Fiscal Year", "from_fiscal_year": "Fiscal Year", "to_fiscal_year": "Fiscal Year",
	"cost_center": "Cost Center", "project": "Project", "finance_book": "Finance Book",
	"presentation_currency": "Currency", "party_account": "Account",
	"customer_group": "Customer Group", "supplier_group": "Supplier Group", "territory": "Territory",
	"sales_partner": "Sales Partner", "sales_person": "Sales Person",
	"payment_terms_template": "Payment Terms Template",
	"batch_no": "Batch", "serial_no": "Serial No",
	"request_for_quotation": "Request for Quotation", "supplier_quotation": "Supplier Quotation",
}

# Reports whose party filter has an implicit, fixed party type (the report
# itself only ever deals with one side of the ledger) rather than a
# browser-suppliable party_type filter.
REPORT_IMPLICIT_PARTY_TYPE = {
	"Accounts Receivable": "Customer", "Accounts Payable": "Supplier",
	"Customer Ledger Summary": "Customer", "Supplier Ledger Summary": "Supplier",
}

# Filter fieldnames that the report's own Python `execute()` expects as a
# frappe.parse_json()-decoded list (its Desk filter widget is
# "MultiSelectList", not a plain Link) — confirmed by reading each report's
# .js filter definition and its execute()/validate_filters() source. Retail
# ERP's filter form only offers single-value selection (no MultiSelectList
# widget), so a single chosen value is wrapped into a one-item JSON array
# before being passed to frappe.desk.query_report.run — never passed as a
# bare string, which erpnext's own parse_json() call would reject.
#
# Membership here is NOT guessable from the fieldname: the same fieldname is
# list-parsed in one report and a plain equality match in another (e.g.
# `cost_center` is `parse_json`-ed by Gross Profit but compared with `==` by
# Fixed Asset Register, which would BREAK if wrapped in a list). Each entry
# below is verified against that specific report's own .py source.
MULTISELECT_REPORT_FILTER_FIELDS = {
	"General Ledger": {"party", "account", "cost_center", "project"},
	"Gross Profit": {"cost_center", "project"},
	"Trial Balance": {"cost_center", "project"},
	"Profit and Loss Statement": {"cost_center", "project"},
	"Balance Sheet": {"cost_center", "project"},
	"Cash Flow": {"cost_center", "project"},
	"Accounts Receivable": {"party", "cost_center", "project"},
	"Accounts Payable": {"party", "cost_center", "project"},
}


def _report_defaults() -> dict:
	today = getdate(nowdate())
	return {
		"company": frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company"),
		"from_date": str(add_months(today, -1)), "to_date": str(today), "posting_date": str(today),
		"period_start_date": str(add_months(today, -12)), "period_end_date": str(today),
		"periodicity": "Monthly", "ageing_based_on": "Due Date", "group_by": "Invoice",
		"fiscal_year": frappe.defaults.get_user_default("fiscal_year") or frappe.defaults.get_global_default("fiscal_year"),
	}


@frappe.whitelist(methods=["GET"])
def get_priority_report_definition(report: str):
	_require_login()
	if report not in {name for names in REPORT_GROUPS.values() for name in names} or not _report_permitted(report):
		frappe.throw(_("Report is not available."), frappe.PermissionError)
	doc = frappe.get_cached_doc("Report", report)
	filters = [_filter_definition(fieldname) for fieldname in REPORT_FILTERS.get(report, ("company", "from_date", "to_date"))]
	defaults = _report_defaults()
	for field in filters:
		field["default"] = defaults.get(field["fieldname"])
	return {
		"name": report, "report_type": doc.report_type, "reference_doctype": doc.ref_doctype,
		"prepared_report": bool(doc.prepared_report), "filters": filters,
		"permissions": {
			"can_export": bool(doc.ref_doctype and frappe.has_permission(doc.ref_doctype, "export")),
			"can_print": bool(doc.ref_doctype and frappe.has_permission(doc.ref_doctype, "print")),
		},
		"pdf_environment": {"available": bool(shutil.which("wkhtmltopdf")), "generator": "wkhtmltopdf"},
	}


@frappe.whitelist(methods=["POST"])
def run_priority_report(report: str, filters=None):
	_require_login()
	get_priority_report_definition(report)
	filters = frappe.parse_json(filters or {})
	if not isinstance(filters, dict):
		frappe.throw(_("Filters have an invalid format."), frappe.ValidationError)
	allowed = set(REPORT_FILTERS.get(report, ("company", "from_date", "to_date")))
	if set(filters) - allowed:
		frappe.throw(_("Unsupported report filter."), frappe.ValidationError)
	for fieldname, doctype in REPORT_LINK_DOCTYPES.items():
		value = filters.get(fieldname)
		if value and (not frappe.has_permission(doctype, "read") or not frappe.get_list(doctype, filters={"name": value}, pluck="name", limit_page_length=1)):
			frappe.throw(_("A report filter is invalid or unavailable."), frappe.PermissionError)
	if filters.get("party"):
		party_type = filters.get("party_type") or REPORT_IMPLICIT_PARTY_TYPE.get(report)
		if party_type not in {"Customer", "Supplier"} or not frappe.has_permission(party_type, "read") or not frappe.get_list(party_type, filters={"name": filters["party"]}, pluck="name", limit_page_length=1):
			frappe.throw(_("A report filter is invalid or unavailable."), frappe.PermissionError)
	for fieldname in MULTISELECT_REPORT_FILTER_FIELDS.get(report, ()):
		# These reports read this filter as a real Python list (the Desk
		# client's MultiSelectList value survives outer JSON decoding as a
		# native list) — some call frappe.parse_json() on it defensively
		# (a no-op on an already-a-list value), others check
		# isinstance(x, list) directly (erpnext...get_cost_centers_with_children).
		# A JSON-encoded *string* here breaks the isinstance check and is
		# mis-parsed as a comma-separated value instead.
		if filters.get(fieldname) and not isinstance(filters[fieldname], list):
			filters[fieldname] = [filters[fieldname]]
	from frappe.desk.query_report import run
	result = run(report, filters=filters, ignore_prepared_report=False)
	result["retail_links"] = _permission_filtered_report_links(result)
	result["pdf_environment"] = {"available": bool(shutil.which("wkhtmltopdf")), "generator": "wkhtmltopdf"}
	return result


def _permission_filtered_report_links(result: dict) -> dict:
	"""Resolve report Link cells in batches without leaking inaccessible names."""
	columns = result.get("columns") or []
	rows = result.get("result") or []
	link_columns = []
	for index, column in enumerate(columns):
		if isinstance(column, dict) and column.get("fieldtype") == "Link" and column.get("options"):
			link_columns.append((index, column.get("fieldname"), column["options"], None))
		elif isinstance(column, dict) and column.get("fieldtype") == "Dynamic Link" and column.get("options"):
			link_columns.append((index, column.get("fieldname"), None, column["options"]))
	candidates = {}
	for index, fieldname, fixed_doctype, dynamic_field in link_columns:
		for row in rows[:500]:
			value = row.get(fieldname) if isinstance(row, dict) else row[index] if index < len(row) else None
			doctype = fixed_doctype or (row.get(dynamic_field) if isinstance(row, dict) else None)
			if value and doctype and frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"):
				candidates.setdefault(doctype, set()).add(str(value))
	links = {}
	from my_store_ui.universal.registry import get_feature
	for doctype, names in candidates.items():
		try:
			record = get_feature(frappe.scrub(doctype).replace("_", "-"))
		except Exception:
			continue
		if record.get("implementation_type") not in {"custom", "generated", "generated_provisional"}:
			continue
		base = record.get("route") or record.get("list_route")
		if not base:
			continue
		visible = frappe.get_list(doctype, filters={"name": ["in", list(names)[:200]]}, pluck="name", limit_page_length=200)
		for name in visible:
			links[f"{doctype}:{name}"] = _detail_path(base, name)
	return links


TREE_CONFIG = {
	"Account": {"parent": "parent_account", "title": "account_name", "group": "is_group", "company": True},
	"Warehouse": {"parent": "parent_warehouse", "title": "warehouse_name", "group": "is_group", "company": True},
	"Item Group": {"parent": "parent_item_group", "title": "item_group_name", "group": "is_group"},
	"Cost Center": {"parent": "parent_cost_center", "title": "cost_center_name", "group": "is_group", "company": True},
	"Territory": {"parent": "parent_territory", "title": "territory_name", "group": "is_group"},
	"Customer Group": {"parent": "parent_customer_group", "title": "customer_group_name", "group": "is_group"},
	"Supplier Group": {"parent": "parent_supplier_group", "title": "supplier_group_name", "group": "is_group"},
	"Sales Person": {"parent": "parent_sales_person", "title": "sales_person_name", "group": "is_group"},
	"Department": {"parent": "parent_department", "title": "department_name", "group": "is_group", "company": True},
}


@frappe.whitelist(methods=["GET"])
def get_tree_nodes(path: str, parent: str | None = None, company: str | None = None):
	_require_login()
	definition, _params = _authorise(path)
	doctype = definition.get("doctype")
	config = TREE_CONFIG.get(doctype)
	if not config:
		frappe.throw(_("Tree view is not available."), frappe.ValidationError)
	filters = {config["parent"]: parent or ["is", "not set"]}
	if config.get("company"):
		company = company or frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")
		if company:
			filters["company"] = company
	fields = ["name", config["title"], config["group"]]
	rows = frappe.get_list(doctype, filters=filters, fields=fields, order_by=f"`{config['title']}` asc", limit_page_length=500)
	return {"doctype": doctype, "company": company, "nodes": [{"name": row.name, "label": row.get(config["title"]) or row.name, "expandable": bool(row.get(config["group"]))} for row in rows]}


@frappe.whitelist(methods=["GET"])
def get_special_page(path: str):
	_require_login()
	definition, _params = _authorise(path)
	if definition.get("component") != "special":
		frappe.throw(_("Special page is not available."), frappe.ValidationError)
	if definition.get("alias"):
		return {"redirect": definition["alias"]}
	relative_path = urlsplit(path).path
	if relative_path.startswith("/retail-erp"):
		relative_path = relative_path[len("/retail-erp"):] or "/home"
	if relative_path == "/pos":
		return _get_pos_context()
	if relative_path in {"/admin/system-health", "/admin/background-jobs"}:
		facts = [{"label": "Server time", "value": str(frappe.utils.now_datetime())}]
		if frappe.has_permission("RQ Job", "read"):
			facts.append({"label": "Background jobs", "value": _safe_count("RQ Job")})
		if frappe.has_permission("Error Log", "read"):
			facts.append({"label": "Error log entries", "value": _safe_count("Error Log")})
		facts.append({"label": "Installed applications", "value": len(frappe.get_installed_apps())})
		return {
			"label": definition.get("label"), "module": "Admin", "classification": "read_only",
			"records": [], "facts": facts,
			"limitations": _("This is a safe read-only operational summary. Job payloads, logs and site secrets are not exposed."),
		}
	if relative_path == "/admin/permissions":
		return _get_role_permission_matrix(definition)
	records = []
	for doctype in tuple(definition.get("doctypes") or ()) + ((definition["doctype"],) if definition.get("doctype") else ()):
		if not frappe.db.exists("DocType", doctype) or not frappe.has_permission(doctype, "read"):
			continue
		if frappe.get_meta(doctype).issingle:
			records.append({"doctype": doctype, "name": doctype, "modified": None})
			continue
		try:
			from my_store_ui.universal.registry import get_feature
			feature = get_feature(frappe.scrub(doctype).replace("_", "-"))
			base = feature.get("route") or feature.get("list_route")
		except Exception:
			base = None
		for row in frappe.get_list(doctype, fields=["name", "modified"], order_by="modified desc", limit_page_length=5):
			record = {"doctype": doctype, "name": row.name, "modified": row.modified}
			if base:
				record["route"] = _detail_path(base, row.name)
			records.append(record)
	return {
		"label": definition.get("label"), "module": definition.get("module"),
		"classification": definition.get("classification", "specialised_provisional"),
		"records": records, "page_installed": bool(definition.get("page") and frappe.db.exists("Page", definition["page"])),
		"limitations": _("This installed feature needs a dedicated interaction adapter. Readable context is shown without opening ERPNext Desk."),
	}


def _get_role_permission_matrix(definition: dict) -> dict:
	"""Return a bounded, metadata-derived permission matrix for administrators.

	This adapter intentionally reads DocPerm metadata only. Role mutation remains
	available through the permission-checked Role and User generated forms; no
	permission rule can be altered through this read-only summary.
	"""
	from my_store_ui.services.priority_registry import ALL_PRIORITY_DOCTYPES

	rows = []
	for doctype in sorted(ALL_PRIORITY_DOCTYPES):
		if not frappe.db.exists("DocType", doctype):
			continue
		meta = frappe.get_meta(doctype)
		for permission in meta.permissions:
			rows.append({
				"doctype": doctype,
				"role": permission.role,
				"read": bool(permission.read),
				"create": bool(permission.create),
				"write": bool(permission.write),
				"delete": bool(permission.delete),
				"submit": bool(permission.submit),
				"cancel": bool(permission.cancel),
				"print": bool(permission.print),
				"email": bool(permission.email),
				"import": bool(permission.get("import")),
				"export": bool(permission.get("export")),
			})
	return {
		"label": definition.get("label"), "module": "Admin", "classification": "read_only",
		"records": [], "permission_matrix": rows,
		"limitations": _("This matrix is read-only and derived from installed DocPerm metadata. Use controlled User and Role forms for permitted account maintenance."),
	}


def _get_pos_context() -> dict:
	if not frappe.has_permission("POS Profile", "read"):
		frappe.throw(_("Point of Sale is not available."), frappe.PermissionError)
	profile = None
	try:
		from posawesome.posawesome.api.utils import get_active_pos_profile
		profile = get_active_pos_profile(frappe.session.user)
	except Exception:
		profile = None
	profiles = []
	if profile and frappe.has_permission("POS Profile", "read", doc=profile.get("name")):
		profiles.append({key: profile.get(key) for key in ("name", "company", "warehouse", "currency", "selling_price_list")})
	return {
		"label": "Point of Sale", "module": "Sales", "classification": "safe_integration",
		"profiles": profiles, "records": [], "launch_url": "/app/posapp" if profiles else None,
		"limitations": _("POS Awesome remains the specialised transaction interface. Retail ERP validates the assigned profile before showing its launch action."),
	}
