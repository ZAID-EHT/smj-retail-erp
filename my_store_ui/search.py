"""Permission-aware global search for the Retail ERP shell."""

from __future__ import annotations

from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, strip_html_tags


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


def _require_login():
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _approved_fields(definition: dict) -> list[str]:
	meta = frappe.get_meta(definition["doctype"])
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
	"""Search only allowlisted DocTypes and return only permission-filtered fields."""
	_require_login()
	text = str(text or "").strip()[:80].replace("%", "").replace("_", "").strip()
	if len(text) < 2:
		return {"results": [], "minimum_length": 2}
	limit = max(1, min(cint(limit) or 20, 30))
	results = []
	for definition in SEARCH_REGISTRY:
		if len(results) >= limit or not frappe.has_permission(definition["doctype"], "read"):
			continue
		fields = _approved_fields(definition)
		meta = frappe.get_meta(definition["doctype"])
		search_fields = ["name"] + [
			field for field in fields[1:]
			if meta.get_field(field) and meta.get_field(field).fieldtype in {"Data", "Link", "Dynamic Link", "Select", "Text", "Small Text", "Read Only"}
		]
		or_filters = [[definition["doctype"], field, "like", f"%{text}%"] for field in search_fields]
		or_filters.extend([[doctype, field, "like", f"%{text}%"] for doctype, field in definition.get("child_search", ())])
		rows = frappe.get_list(
			definition["doctype"],
			fields=fields,
			or_filters=or_filters,
			order_by=f"`tab{definition['doctype']}`.`modified` desc",
			limit_page_length=min(4, limit - len(results)),
		)
		for row in rows:
			subtitle_values = []
			for fieldname in fields[1:]:
				value = row.get(fieldname)
				if value not in (None, "", 0):
					subtitle_values.append(strip_html_tags(str(value)).strip())
			results.append({
				"doctype": definition["doctype"],
				"group": definition["label"],
				"name": row.name,
				"title": str(row.get(fields[1]) or row.name) if len(fields) > 1 else row.name,
				"subtitle": " · ".join(subtitle_values[:3]),
				"route": _result_route(definition, row.name),
			})
	return {"results": results, "minimum_length": 2}
