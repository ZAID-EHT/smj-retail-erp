"""Permission-aware command and record search for the Retail ERP shell.

The browser supplies only text.  Searchable pages, reports and DocTypes are
owned by server registries, and every result is permission checked before it
is returned.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, strip_html_tags

from my_store_ui.services.frontend_routes import (
	get_permitted_navigation,
	resolve_frontend_route,
	route_is_permitted,
)
from my_store_ui.services.priority_registry import ENTITY_ROUTES, REPORT_GROUPS

if TYPE_CHECKING:
	from frappe.model.meta import Meta


SEARCH_REGISTRY = (
	{"doctype": "Customer", "label": "Customers", "fields": ("customer_name", "mobile_no"), "route": "/sales/customers/{name}"},
	{"doctype": "Supplier", "label": "Suppliers", "fields": ("supplier_name", "supplier_group"), "route": "/purchases/suppliers/{name}"},
	{"doctype": "Item", "label": "Products", "fields": ("item_name", "item_code", "item_group", "brand"), "child_search": (("Item Barcode", "barcode"),), "route": "/inventory/products/{name}"},
	{"doctype": "Quotation", "label": "Quotations", "fields": ("party_name", "status", "transaction_date"), "route": "/sales/quotations/{name}"},
	{"doctype": "Sales Order", "label": "Sales Orders", "fields": ("customer_name", "status", "transaction_date", "grand_total"), "route": "/sales/orders/{name}"},
	{"doctype": "Delivery Note", "label": "Delivery Notes", "fields": ("customer_name", "status", "posting_date", "grand_total"), "route": "/sales/delivery-notes/{name}"},
	{"doctype": "Sales Invoice", "label": "Sales Invoices", "fields": ("customer_name", "status", "posting_date", "grand_total", "outstanding_amount"), "route": "/sales/invoices/{name}"},
	{"doctype": "Material Request", "label": "Material Requests", "fields": ("status", "transaction_date", "company"), "route": "/purchases/material-requests/{name}"},
	{"doctype": "Request for Quotation", "label": "Requests for Quotation", "fields": ("transaction_date", "status", "company"), "route": "/purchases/requests-for-quotation/{name}"},
	{"doctype": "Supplier Quotation", "label": "Supplier Quotations", "fields": ("supplier_name", "status", "transaction_date", "grand_total"), "route": "/purchases/supplier-quotations/{name}"},
	{"doctype": "Purchase Order", "label": "Purchase Orders", "fields": ("supplier_name", "status", "transaction_date", "grand_total"), "route": "/purchases/orders/{name}"},
	{"doctype": "Purchase Receipt", "label": "Purchase Receipts", "fields": ("supplier_name", "status", "posting_date", "grand_total"), "route": "/purchases/receipts/{name}"},
	{"doctype": "Purchase Invoice", "label": "Purchase Invoices", "fields": ("supplier_name", "status", "posting_date", "grand_total", "outstanding_amount"), "route": "/purchases/invoices/{name}"},
	{"doctype": "Payment Entry", "label": "Payment Entries", "fields": ("party", "payment_type", "posting_date", "paid_amount"), "route": "/finance/payments/{name}"},
	{"doctype": "Journal Entry", "label": "Journal Entries", "fields": ("voucher_type", "posting_date", "total_debit"), "route": "/finance/journal-entries/{name}"},
	{"doctype": "Stock Entry", "label": "Stock Entries", "fields": ("stock_entry_type", "purpose", "posting_date", "company"), "route": "/inventory/stock-entries/{name}"},
	{"doctype": "Stock Reconciliation", "label": "Stock Reconciliations", "fields": ("purpose", "posting_date", "company"), "route": "/inventory/reconciliations/{name}"},
	{"doctype": "Serial No", "label": "Serial Numbers", "fields": ("item_code", "warehouse", "status"), "route": "/inventory/serial-numbers/{name}"},
	{"doctype": "Batch", "label": "Batches", "fields": ("item", "batch_qty", "expiry_date"), "route": "/inventory/batches/{name}"},
	{"doctype": "Lead", "label": "Leads", "fields": ("lead_name", "company_name", "status"), "route": "/crm/leads/{name}"},
	{"doctype": "Opportunity", "label": "Opportunities", "fields": ("party_name", "opportunity_from", "status"), "route": "/crm/opportunities/{name}"},
	{"doctype": "Contact", "label": "Contacts", "fields": ("full_name", "email_id", "mobile_no"), "route": "/crm/contacts/{name}"},
	{"doctype": "Address", "label": "Addresses", "fields": ("address_title", "address_type", "city"), "route": "/crm/addresses/{name}"},
	{"doctype": "Project", "label": "Projects", "fields": ("project_name", "status", "customer"), "route": "/operations/projects/{name}"},
	{"doctype": "Task", "label": "Tasks", "fields": ("subject", "status", "project"), "route": "/operations/tasks/{name}"},
	{"doctype": "Asset", "label": "Assets", "fields": ("asset_name", "item_code", "status"), "route": "/operations/assets/{name}"},
	{"doctype": "Issue", "label": "Support Issues", "fields": ("subject", "status", "customer"), "route": "/operations/support/issues/{name}"},
	{"doctype": "Work Order", "label": "Work Orders", "fields": ("production_item", "status", "qty"), "route": "/operations/manufacturing/work-orders/{name}"},
	{"doctype": "User", "label": "Users", "fields": ("full_name", "email", "enabled"), "route": "/admin/users/{name}"},
)


# Friendly vocabulary for tasks people search for rather than ERPNext's exact
# page label.  Values only enhance matching; routes still come exclusively
# from the server-owned navigation/route registries below.
PAGE_SEARCH_ALIASES = {
	"/smart-sales": "smart sale wholesale catalogue catalog cart checkout order taking pos",
	"/sales/orders": "sales order customer order reserve order booking",
	"/sales/delivery-notes": "delivery receipt dispatch shipment goods delivery",
	"/sales/invoices": "sales invoice customer bill billing",
	"/purchases/orders": "purchase order supplier order procurement",
	"/purchases/receipts": "purchase receipt goods receipt grn received goods",
	"/purchases/invoices": "purchase invoice supplier bill payable",
	"/inventory/receipts/new": "stock receipt material receipt receive stock goods in",
	"/inventory/issues/new": "stock issue material issue goods out",
	"/inventory/transfers/new": "stock transfer material transfer warehouse transfer",
	"/finance/payments": "payment receipt cash receipt receive payment pay supplier collect customer",
	"/finance/journal-entries": "petty cash cash expense cash book journal general journal",
	"/finance/chart-of-accounts": "accounts ledger chart account cash bank",
	"/reports": "reports analytics statements insights",
}


def _normalise(value: str) -> str:
	return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


def _match_score(text: str, *values: str) -> int:
	query = _normalise(text)
	haystack = " ".join(_normalise(value) for value in values if value)
	if not query or not haystack:
		return 0
	if query == haystack:
		return 100
	if haystack.startswith(query):
		return 90
	if query in haystack:
		return 80
	tokens = query.split()
	if tokens and all(token in haystack for token in tokens):
		return 65
	matched = sum(1 for token in tokens if len(token) >= 4 and token in haystack)
	if len(tokens) >= 3 and matched >= 2:
		return 25 + round(20 * matched / len(tokens))
	return 0


def _page_results(text: str, limit: int) -> list[dict]:
	"""Return permitted navigation and generated entity launchers."""
	candidates: dict[str, dict] = {}
	for module in get_permitted_navigation():
		module_label = module.get("label") or module.get("name", "").title()
		if module.get("path"):
			candidates[module["path"]] = {
				"title": module_label,
				"module": module_label,
				"route": module["path"],
				"keywords": PAGE_SEARCH_ALIASES.get(module["path"], ""),
			}
		for link in module.get("links", ()):
			path = link.get("path")
			if not path:
				continue
			if path == module.get("path"):
				continue
			candidates[path] = {
				"title": link.get("label") or module_label,
				"module": module_label,
				"route": path,
				"keywords": PAGE_SEARCH_ALIASES.get(path, ""),
			}

	# ENTITY_ROUTES contains the larger allowlisted generated surface.  Text is
	# matched before any permission call so a search does not enumerate or load
	# the entire metadata inventory.
	for path, definition in ENTITY_ROUTES.items():
		doctype = definition.get("doctype")
		if path in candidates or not doctype:
			continue
		score = _match_score(text, doctype, path, PAGE_SEARCH_ALIASES.get(path, ""))
		if not score or not frappe.has_permission(doctype, "read"):
			continue
		candidates[path] = {
			"title": doctype,
			"module": str(definition.get("module") or "ERPNext").title(),
			"route": path,
			"keywords": PAGE_SEARCH_ALIASES.get(path, ""),
			"score": score,
		}

	results = []
	for candidate in candidates.values():
		score = candidate.get("score") or _match_score(
			text, candidate["title"], candidate["module"], candidate["route"], candidate["keywords"]
		)
		if not score:
			continue
		definition, _params = resolve_frontend_route(candidate["route"])
		if not definition or not route_is_permitted(definition):
			continue
		results.append({
			"kind": "page",
			"type_label": "Page",
			"doctype": "Retail ERP Page",
			"group": "Pages & Functions",
			"name": candidate["route"],
			"title": candidate["title"],
			"subtitle": f"{candidate['module']} · Open page",
			"route": candidate["route"],
			"score": score,
		})
	return sorted(results, key=lambda row: (-row["score"], row["title"]))[:limit]


def _report_results(text: str, limit: int) -> list[dict]:
	results = []
	for group, report_names in REPORT_GROUPS.items():
		for name in report_names:
			score = _match_score(text, name, group, "report analytics statement")
			if not score:
				continue
			if not frappe.db.exists("Report", {"name": name, "disabled": 0}):
				continue
			if not frappe.has_permission("Report", "read", doc=name):
				continue
			results.append({
				"kind": "report",
				"type_label": "Report",
				"doctype": "Report",
				"group": "Reports",
				"name": name,
				"title": name,
				"subtitle": f"{group.title()} reports · Run report",
				"route": f"/reports/view/{quote(name, safe='')}",
				"score": score,
			})
	return sorted(results, key=lambda row: (-row["score"], row["title"]))[:limit]


def _searchable_meta(doctype) -> Meta | None:
	"""Meta for a registered search entry, or ``None`` when the entry is unusable.

	A registry entry can go stale — the DocType is renamed, removed, or owned by
	an app that is no longer installed — and ``frappe.get_meta`` raises
	``DoesNotExistError`` for those (including the ``None``/empty case).  One bad
	entry must never take global search down for every other entry, so the entry
	is skipped and reported as unavailable.

	Nothing is widened here: the DocType is never substituted, and callers still
	permission-check whatever this returns.  Anything other than a missing
	DocType is left to propagate — a genuinely broken install should be loud.
	"""
	if not doctype or not isinstance(doctype, str):
		frappe.logger("my_store_ui").warning(
			f"global search: registry entry has no usable doctype ({doctype!r}); skipped"
		)
		return None
	try:
		return frappe.get_meta(doctype)
	except frappe.DoesNotExistError:
		# get_meta throws, which also queues a user-facing message; drop it so a
		# stale registry entry cannot leak into an unrelated search response.
		frappe.clear_last_message()
		frappe.logger("my_store_ui").warning(
			f"global search: registry doctype {doctype!r} is unavailable; entry skipped"
		)
		return None


def _document_results(text: str, limit: int) -> list[dict]:
	results = []
	for definition in SEARCH_REGISTRY:
		if len(results) >= limit:
			break
		doctype = definition.get("doctype")
		meta = _searchable_meta(doctype)
		if meta is None or not frappe.has_permission(doctype, "read"):
			continue
		fields = _approved_fields(definition, meta=meta)
		search_fields = ["name"] + [
			field for field in fields[1:]
			if meta.get_field(field) and meta.get_field(field).fieldtype in {"Data", "Link", "Dynamic Link", "Select", "Text", "Small Text", "Read Only"}
		]
		or_filters = [[definition["doctype"], field, "like", f"%{text}%"] for field in search_fields]
		or_filters.extend([[doctype, field, "like", f"%{text}%"] for doctype, field in definition.get("child_search", ())])
		rows = frappe.get_list(
			definition["doctype"], fields=fields, or_filters=or_filters,
			order_by=f"`tab{definition['doctype']}`.`modified` desc",
			limit_page_length=min(4, limit - len(results)),
		)
		for row in rows:
			# get_list already applies permission query conditions and User
			# Permissions.  The explicit document check also covers shares,
			# ownership rules and controller-level has_permission hooks.
			if not frappe.has_permission(definition["doctype"], "read", doc=row.name):
				continue
			subtitle_values = []
			for fieldname in fields[1:]:
				value = row.get(fieldname)
				if value not in (None, "", 0):
					subtitle_values.append(strip_html_tags(str(value)).strip())
			results.append({
				"kind": "document",
				"type_label": definition["doctype"],
				"doctype": definition["doctype"],
				"group": "Documents",
				"name": row.name,
				"title": str(row.get(fields[1]) or row.name) if len(fields) > 1 else row.name,
				"subtitle": " · ".join(subtitle_values[:3]),
				"route": _result_route(definition, row.name),
			})
	return results[:limit]


def _require_login():
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _approved_fields(definition: dict, meta=None) -> list[str]:
	meta = meta if meta is not None else _searchable_meta(definition.get("doctype"))
	if meta is None:
		return ["name"]
	approved = ["name"]
	for fieldname in definition["fields"]:
		field = meta.get_field(fieldname)
		if field and cint(field.permlevel) == 0:
			approved.append(fieldname)
	return approved


def _result_route(definition: dict, name: str) -> str:
	if definition.get("route"):
		return definition["route"].format(name=quote(name, safe=""))
	feature = quote(definition["label"], safe="")
	return f"/feature-unavailable?feature={feature}"


@frappe.whitelist(methods=["GET"])
def global_search(text: str, limit: int = 20):
	"""Search permitted pages/functions, reports and allowlisted records."""
	_require_login()
	text = str(text or "").strip()[:80].replace("%", "").replace("_", "").strip()
	if len(text) < 2:
		return {"results": [], "minimum_length": 2}
	limit = max(1, min(cint(limit) or 20, 30))
	pages = _page_results(text, min(8, limit))
	reports = _report_results(text, min(5, max(0, limit - len(pages))))
	remaining = max(0, limit - len(pages) - len(reports))
	documents = _document_results(text, remaining)
	results = pages + reports + documents
	for result in results:
		result.pop("score", None)
	return {"results": results, "minimum_length": 2}
