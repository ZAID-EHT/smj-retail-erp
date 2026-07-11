from __future__ import annotations

import frappe


def get_doctype_permissions(doctype: str) -> dict[str, bool]:
	is_submittable = bool(frappe.get_meta(doctype).is_submittable)
	return {
		"can_read": bool(frappe.has_permission(doctype, "read")),
		"can_create": bool(frappe.has_permission(doctype, "create")),
		"can_write": bool(frappe.has_permission(doctype, "write")),
		"can_submit": is_submittable and bool(frappe.has_permission(doctype, "submit")),
		"can_cancel": is_submittable and bool(frappe.has_permission(doctype, "cancel")),
		"can_print": bool(frappe.has_permission(doctype, "print")),
	}


def can_open_standard_desk() -> bool:
	return frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()
