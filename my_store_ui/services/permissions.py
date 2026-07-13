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


def get_document_permissions(doc) -> dict[str, bool]:
	is_submittable = bool(doc.meta.is_submittable)
	return {
		"can_read": bool(frappe.has_permission(doc.doctype, "read", doc=doc)),
		"can_create": bool(frappe.has_permission(doc.doctype, "create")),
		"can_write": bool(frappe.has_permission(doc.doctype, "write", doc=doc)),
		"can_submit": is_submittable and bool(frappe.has_permission(doc.doctype, "submit", doc=doc)),
		"can_cancel": is_submittable and bool(frappe.has_permission(doc.doctype, "cancel", doc=doc)),
		"can_print": bool(frappe.has_permission(doc.doctype, "print", doc=doc)),
	}


def can_open_standard_desk() -> bool:
	# Emergency Desk is intentionally never advertised by business APIs or the
	# normal navigation. A separately approved direct Administrator bypass is
	# enforced only by route_guard when site configuration explicitly enables it.
	return False
