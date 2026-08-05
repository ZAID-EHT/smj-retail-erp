"""Allowlisted link-option search for the quick-entry forms.

Only a fixed set of link kinds is searchable; each is permission-filtered via
frappe.get_list (so warehouses respect company/User Permissions). No arbitrary
DocType access.
"""

from __future__ import annotations

import frappe
from frappe import _

# kind -> (doctype, base filters)
KINDS = {
	"warehouse": ("Warehouse", {"is_group": 0, "disabled": 0}),
	"item_group": ("Item Group", {"is_group": 0}),
	"price_list": ("Price List", {"enabled": 1, "selling": 1}),
	"transport_method": None,  # served from the Select options
}


@frappe.whitelist(methods=["GET"])
def search(kind: str, query: str = "", company: str | None = None) -> dict:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	kind = str(kind or "").strip()
	if kind not in KINDS:
		frappe.throw(_("Unsupported option kind."), frappe.ValidationError)

	spec = KINDS[kind]
	if spec is None:
		return {"kind": kind, "options": []}
	doctype, filters = spec
	filters = dict(filters)
	if kind == "warehouse":
		company = company or frappe.defaults.get_global_default("company")
		if company:
			filters["company"] = company
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	q = str(query or "").strip()[:60]
	or_filters = {"name": ["like", f"%{q}%"]} if q else None
	# The form narrows these inside its own dropdown, so the whole list has to
	# arrive rather than just the first page of it.
	rows = frappe.get_list(doctype, filters=filters, or_filters=or_filters, pluck="name",
	                       order_by="name asc", limit_page_length=500)
	return {"kind": kind, "options": rows}
