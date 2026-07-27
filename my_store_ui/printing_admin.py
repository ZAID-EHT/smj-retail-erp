"""Phase 8 — printing and branding, over ERPNext's own print system.

Lists Letter Heads and Print Formats and renders previews using Frappe's standard
`get_print` (which honours field-level permissions, so a Sales user never sees a
purchase-cost field). No separate PDF engine, no arbitrary template execution here.
Advanced HTML/Jinja Print Format authoring stays in the generated Print Format CRUD,
which is System Manager gated.
"""

from __future__ import annotations

import frappe
from frappe import _

from my_store_ui.access_management import _require_user_manager

# Documents whose printing matters for the wholesale workflow.
PRINTABLE_DOCTYPES = (
	"Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
	"Purchase Order", "Purchase Receipt", "Purchase Invoice",
)


@frappe.whitelist(methods=["GET"])
def get_printing_overview() -> dict:
	"""Letter heads, print settings status, and print formats per DocType."""
	_require_user_manager()
	letter_heads = frappe.get_list(
		"Letter Head", fields=["name", "is_default", "disabled"], order_by="is_default desc, name asc",
		limit_page_length=100,
	) if frappe.has_permission("Letter Head", "read") else []

	formats_by_doctype = []
	if frappe.has_permission("Print Format", "read"):
		for doctype in PRINTABLE_DOCTYPES:
			if not frappe.db.exists("DocType", doctype):
				continue
			formats = frappe.get_all(
				"Print Format",
				filters={"doc_type": doctype, "disabled": 0},
				fields=["name", "standard", "print_format_type"],
				order_by="standard asc, name asc",
			)
			default = frappe.db.get_value("Property Setter", {
				"doc_type": doctype, "property": "default_print_format",
			}, "value")
			formats_by_doctype.append({
				"doctype": doctype,
				"formats": formats,
				"default_format": default,
				"format_count": len(formats),
			})

	return {
		"letter_heads": letter_heads,
		"formats_by_doctype": formats_by_doctype,
		"print_settings": _print_settings_summary(),
	}


def _print_settings_summary() -> dict:
	try:
		settings = frappe.get_single("Print Settings")
		return {
			"with_letterhead": bool(settings.with_letterhead),
			"pdf_page_size": settings.pdf_page_size,
			"font_size": settings.font_size,
		}
	except Exception:
		return {}


@frappe.whitelist(methods=["GET"])
def preview_document(doctype: str, name: str, print_format: str | None = None) -> dict:
	"""Render a print preview of one document the caller may read.

	Uses Frappe's standard get_print, which enforces field-level permissions -- a
	user without permission on cost fields does not see them in the output.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	doctype = str(doctype or "").strip()
	if doctype not in PRINTABLE_DOCTYPES:
		frappe.throw(_("{0} is not available for preview.").format(doctype), frappe.ValidationError)
	name = str(name or "").strip()
	if not name or not frappe.db.exists(doctype, name):
		frappe.throw(_("Document not found."), frappe.DoesNotExistError)
	# Real permission check on the specific document.
	if not frappe.has_permission(doctype, "print", doc=name) and not frappe.has_permission(doctype, "read", doc=name):
		frappe.throw(_("You do not have permission to print this document."), frappe.PermissionError)

	if print_format:
		if not frappe.db.exists("Print Format", {"name": print_format, "doc_type": doctype}):
			frappe.throw(_("That print format does not apply to this document."), frappe.ValidationError)

	html = frappe.get_print(doctype, name, print_format=print_format or None, no_letterhead=0)
	return {"doctype": doctype, "name": name, "print_format": print_format, "html": html}


@frappe.whitelist(methods=["GET"])
def get_preview_candidates(doctype: str) -> dict:
	"""A few documents the caller may read, to drive the preview picker."""
	_require_user_manager()
	doctype = str(doctype or "").strip()
	if doctype not in PRINTABLE_DOCTYPES:
		frappe.throw(_("{0} is not printable here.").format(doctype), frappe.ValidationError)
	rows = frappe.get_list(doctype, fields=["name"], order_by="modified desc", limit_page_length=10)
	return {"doctype": doctype, "candidates": [r["name"] for r in rows]}
