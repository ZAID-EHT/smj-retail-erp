"""Phase 10 — guided data import/export over standard Frappe Data Import.

Only an allowlist of business DocTypes may be imported or exported; an arbitrary
DocType is never accepted. Every call re-checks the caller's DocType permission on
the server, and export goes through frappe.get_list so User Permissions and company
filters apply. Nothing writes GL/SLE directly; opening stock and balances use the
standard ERPNext mechanisms via Data Import.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

# DocTypes an authorised user may import/export through this surface. Deliberately
# an allowlist -- an arbitrary DocType must never be reachable here.
ALLOWED_DOCTYPES = {
	"Customer": "read",
	"Supplier": "read",
	"Item": "read",
	"Item Price": "read",
	"Warehouse": "read",
	"Contact": "read",
	"Address": "read",
}

# Fields never included in an export, regardless of DocType.
FORBIDDEN_EXPORT_FIELDS = {
	"password", "new_password", "api_key", "api_secret", "reset_password_key",
	"encryption_key", "salt", "session_data", "secret",
}

# What SMJ pays for its goods is not something plain Item read should reveal.
# The app gates this twice already -- entity_schemas restricts valuation_rate and
# standard_rate to stock/accounts roles, and quick_entry/product hides cost_price
# behind _require_manager_for_cost -- but the export built its field list from the
# whole DocType, so a salesperson could pull the entire margin structure in one
# call. These come out unless the caller holds a cost-bearing role.
# price_list_rate is deliberately absent: on Item Price it is the selling price a
# salesperson legitimately needs. Buying rates are withheld by filtering the rows
# to selling price lists instead, so the useful half of the export survives.
COST_EXPORT_FIELDS = {
	"valuation_rate", "last_purchase_rate", "standard_rate",
	"custom_purchase_price", "custom_cost_price",
}

COST_ROLES = {
	"Stock Manager", "Accounts User", "Accounts Manager", "Item Manager",
	"Purchase Master Manager", "Sales Master Manager", "System Manager",
}


def _may_see_cost() -> bool:
	return frappe.session.user == "Administrator" or bool(set(frappe.get_roles()) & COST_ROLES)


MAX_EXPORT_ROWS = 5000


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _check_doctype(doctype: str, permission: str) -> str:
	doctype = str(doctype or "").strip()
	if doctype not in ALLOWED_DOCTYPES:
		frappe.throw(_("{0} is not available for data management.").format(doctype), frappe.ValidationError)
	if not frappe.has_permission(doctype, permission):
		frappe.throw(_("You do not have {0} permission on {1}.").format(permission, doctype), frappe.PermissionError)
	return doctype


@frappe.whitelist(methods=["GET"])
def get_import_types() -> dict:
	"""Allowlisted import/export types the caller may actually use."""
	_require_login()
	available = []
	for doctype in ALLOWED_DOCTYPES:
		if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"):
			available.append({
				"doctype": doctype,
				"can_import": frappe.has_permission(doctype, "create"),
				"can_export": True,
			})
	return {"types": available}


@frappe.whitelist(methods=["GET"])
def get_import_template_fields(doctype: str) -> dict:
	"""Safe, importable field list for a template. No sensitive fields."""
	doctype = _check_doctype(doctype, "read")
	meta = frappe.get_meta(doctype)
	fields = []
	for field in meta.fields:
		if field.fieldtype in {"Section Break", "Column Break", "HTML", "Button", "Table", "Table MultiSelect"}:
			continue
		if field.fieldname in FORBIDDEN_EXPORT_FIELDS or field.get("is_virtual"):
			continue
		if field.get("hidden") and not field.get("reqd"):
			continue
		fields.append({"fieldname": field.fieldname, "label": field.label, "reqd": bool(field.reqd), "fieldtype": field.fieldtype})
	return {"doctype": doctype, "fields": fields}


@frappe.whitelist(methods=["GET"])
def export_records(doctype: str, limit: int = 1000) -> dict:
	"""Permission-filtered export. Respects User Permissions and company filters;
	never returns a credential, key or session field."""
	doctype = _check_doctype(doctype, "read")
	meta = frappe.get_meta(doctype)
	fields = [
		field.fieldname for field in meta.fields
		if field.fieldtype not in {"Section Break", "Column Break", "HTML", "Button", "Table", "Table MultiSelect", "Password"}
		and field.fieldname not in FORBIDDEN_EXPORT_FIELDS and not field.get("is_virtual")
	]
	if not _may_see_cost():
		fields = [f for f in fields if f not in COST_EXPORT_FIELDS]
	fields = ["name"] + [f for f in fields if f != "name"]
	limit = max(1, min(cint(limit) or 1000, MAX_EXPORT_ROWS))
	filters = {}
	if doctype == "Item Price" and not _may_see_cost():
		# Every row on a buying price list is a supplier cost. Selling rows are
		# ordinary sales reference and stay visible.
		filters["buying"] = 0
	# get_list applies role permissions AND User Permissions / company scoping.
	rows = frappe.get_list(
		doctype, filters=filters, fields=fields, limit_page_length=limit, order_by="modified desc"
	)
	return {"doctype": doctype, "row_count": len(rows), "fields": fields, "rows": rows, "capped_at": limit}


@frappe.whitelist(methods=["GET"])
def get_import_history(limit: int = 20) -> dict:
	"""Recent Data Import runs the caller may see."""
	_require_login()
	if not frappe.has_permission("Data Import", "read"):
		return {"imports": [], "note": _("You do not have access to import history.")}
	imports = frappe.get_list(
		"Data Import",
		filters={"reference_doctype": ["in", list(ALLOWED_DOCTYPES)]},
		fields=["name", "reference_doctype", "import_type", "status", "creation"],
		order_by="creation desc", limit_page_length=max(1, min(cint(limit) or 20, 100)),
	)
	return {"imports": imports}
