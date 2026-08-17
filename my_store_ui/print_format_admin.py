"""Retail ERP print-format administration.

Manages which ERPNext Print Format Retail ERP uses per document type, and lets an
administrator create, duplicate, disable and preview *custom* formats.

ERPNext Standard formats are protected: they are never edited, renamed, disabled or
overwritten. A "customise" action always produces a new custom Print Format and
leaves the standard one untouched.

The chosen defaults live in the `Retail ERP Print Setting` single DocType, so the
selection is reproducible through migrate rather than hand-edited in one database.
"""

from __future__ import annotations

import frappe
from frappe import _

SETTINGS = "Retail ERP Print Setting"

# Stock Transfer is ERPNext's Stock Entry.
MANAGED_DOCTYPES = (
	("Quotation", "Quotation"),
	("Sales Order", "Sales Order"),
	("Delivery Note", "Delivery Note"),
	("Sales Invoice", "Sales Invoice"),
	("Payment Entry", "Payment Entry"),
	("Purchase Order", "Purchase Order"),
	("Purchase Receipt", "Purchase Receipt"),
	("Purchase Invoice", "Purchase Invoice"),
	("Stock Entry", "Stock Transfer"),
)

MANAGED = {name for name, _label in MANAGED_DOCTYPES}


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_admin() -> None:
	"""Managing print formats is an administrative action."""
	_require_login()
	roles = set(frappe.get_roles())
	if "System Manager" not in roles:
		frappe.throw(
			_("Only a System Manager can manage Retail ERP print formats."), frappe.PermissionError
		)


def _validate_doctype(doctype: str) -> str:
	doctype = (doctype or "").strip()
	if doctype not in MANAGED:
		frappe.throw(
			_("{0} is not a Retail ERP printable document.").format(doctype or "(blank)"),
			frappe.ValidationError,
		)
	return doctype


def _is_standard(print_format: str) -> bool:
	return (frappe.db.get_value("Print Format", print_format, "standard") or "No") == "Yes"


def get_default_map() -> dict[str, dict]:
	settings = frappe.get_cached_doc(SETTINGS)
	return {
		row.document_type: {"print_format": row.print_format, "language": row.language}
		for row in settings.get("defaults") or []
	}


def resolve_print_format(doctype: str) -> str | None:
	"""The Retail ERP default for a document type, if one is configured and usable."""
	entry = get_default_map().get(doctype)
	name = (entry or {}).get("print_format")
	if name and frappe.db.exists("Print Format", {"name": name, "disabled": 0}):
		return name
	return None


@frappe.whitelist(methods=["GET"])
def get_print_format_admin():
	"""Every managed document type with its formats and the Retail ERP default."""
	_require_admin()
	defaults = get_default_map()
	languages = frappe.get_all("Language", filters={"enabled": 1}, pluck="name", limit_page_length=0)

	documents = []
	for doctype, label in MANAGED_DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			continue
		formats = frappe.get_all(
			"Print Format",
			filters={"doc_type": doctype, "disabled": 0},
			fields=["name", "standard", "print_format_type", "disabled", "module"],
			order_by="standard desc, name asc",
			limit_page_length=0,
		)
		entry = defaults.get(doctype) or {}
		documents.append({
			"doctype": doctype,
			"label": label,
			"formats": [
				{
					"name": f["name"],
					"is_standard": (f["standard"] or "No") == "Yes",
					"type": f["print_format_type"],
					"module": f["module"],
				}
				for f in formats
			],
			"default_print_format": entry.get("print_format"),
			"default_language": entry.get("language"),
			"sample": _sample_document(doctype),
		})
	return {"documents": documents, "languages": languages, "can_edit": True}


def _sample_document(doctype: str) -> str | None:
	"""A real submitted document to preview against, if the user may read one."""
	rows = frappe.get_list(
		doctype, filters={"docstatus": 1}, fields=["name"], order_by="modified desc", limit=1
	)
	if not rows:
		rows = frappe.get_list(doctype, fields=["name"], order_by="modified desc", limit=1)
	return rows[0]["name"] if rows else None


@frappe.whitelist(methods=["POST"])
def set_default_print_format(doctype: str, print_format: str | None = None,
                             language: str | None = None):
	"""Choose (or clear) the Retail ERP default format for a document type."""
	_require_admin()
	doctype = _validate_doctype(doctype)
	print_format = (print_format or "").strip()
	language = (language or "").strip()

	if print_format:
		row = frappe.db.get_value(
			"Print Format", print_format, ["doc_type", "disabled"], as_dict=True
		)
		if not row:
			frappe.throw(_("Invalid Print Format: {0}").format(print_format), frappe.ValidationError)
		if row.doc_type != doctype:
			frappe.throw(
				_("{0} belongs to {1}, not {2}.").format(print_format, row.doc_type, doctype),
				frappe.ValidationError,
			)
		if row.disabled:
			frappe.throw(_("{0} is disabled.").format(print_format), frappe.ValidationError)
	if language and not frappe.db.exists("Language", language):
		frappe.throw(_("Invalid Language: {0}").format(language), frappe.ValidationError)

	settings = frappe.get_doc(SETTINGS)
	rows = [r for r in (settings.get("defaults") or []) if r.document_type != doctype]
	settings.set("defaults", [])
	for row in rows:
		settings.append("defaults", {
			"document_type": row.document_type, "print_format": row.print_format,
			"language": row.language,
		})
	if print_format:
		settings.append("defaults", {
			"document_type": doctype, "print_format": print_format, "language": language or None,
		})
	settings.save()
	return {"doctype": doctype, "default_print_format": print_format or None,
	        "default_language": language or None}


@frappe.whitelist(methods=["POST"])
def create_custom_print_format(doctype: str, format_name: str, based_on: str | None = None):
	"""Create a custom format, optionally copying an existing one.

	A Standard format is never modified: copying one produces a new custom record.
	"""
	_require_admin()
	doctype = _validate_doctype(doctype)
	format_name = (format_name or "").strip()
	if not format_name:
		frappe.throw(_("A format name is required."), frappe.ValidationError)
	if frappe.db.exists("Print Format", format_name):
		frappe.throw(
			_("A Print Format named {0} already exists.").format(format_name), frappe.ValidationError
		)

	source = None
	if based_on:
		source = frappe.db.get_value(
			"Print Format", based_on,
			["name", "doc_type", "print_format_type", "html", "font_size", "margin_top",
			 "margin_bottom", "margin_left", "margin_right", "css"],
			as_dict=True,
		)
		if not source:
			frappe.throw(_("Invalid source format: {0}").format(based_on), frappe.ValidationError)
		if source.doc_type != doctype:
			frappe.throw(
				_("{0} belongs to {1}, not {2}.").format(based_on, source.doc_type, doctype),
				frappe.ValidationError,
			)

	doc = frappe.new_doc("Print Format")
	doc.name = format_name
	doc.doc_type = doctype
	doc.module = "My Store UI"
	# Always custom: `standard = No` is what keeps ERPNext's own formats protected.
	doc.standard = "No"
	doc.print_format_type = (source or {}).get("print_format_type") or "Jinja"
	doc.html = (source or {}).get("html") or _starter_html(doctype)
	for field in ("font_size", "margin_top", "margin_bottom", "margin_left", "margin_right", "css"):
		if source and source.get(field):
			doc.set(field, source.get(field))
	doc.insert()
	return {"name": doc.name, "doctype": doctype, "based_on": based_on, "is_standard": False}


def _starter_html(doctype: str) -> str:
	return (
		"<div class=\"print-heading\">\n"
		f"  <h2>{doctype}</h2>\n"
		"  <h4>{{ doc.name }}</h4>\n"
		"</div>\n"
		"{{ doc.get_formatted('company') if doc.get('company') else '' }}\n"
	)


@frappe.whitelist(methods=["POST"])
def set_print_format_disabled(print_format: str, disabled: int = 1):
	"""Disable or re-enable a custom format. Standard formats are protected."""
	_require_admin()
	print_format = (print_format or "").strip()
	row = frappe.db.get_value("Print Format", print_format, ["name", "doc_type"], as_dict=True)
	if not row:
		frappe.throw(_("Invalid Print Format: {0}").format(print_format), frappe.ValidationError)
	if _is_standard(print_format):
		frappe.throw(
			_("{0} is an ERPNext Standard format and cannot be disabled. Duplicate it instead.")
			.format(print_format),
			frappe.ValidationError,
		)

	disabled = 1 if int(disabled or 0) else 0
	doc = frappe.get_doc("Print Format", print_format)
	doc.disabled = disabled
	doc.save()

	# A disabled format must not remain the Retail ERP default.
	if disabled and get_default_map().get(row.doc_type, {}).get("print_format") == print_format:
		set_default_print_format(row.doc_type, None, None)
	return {"name": print_format, "disabled": disabled}


@frappe.whitelist(methods=["GET"])
def preview_print_format(doctype: str, print_format: str | None = None,
                         name: str | None = None, language: str | None = None):
	"""Render a document through ERPNext's own print engine."""
	_require_login()
	doctype = _validate_doctype(doctype)
	if not frappe.has_permission(doctype, "print"):
		frappe.throw(_("You do not have print permission for {0}.").format(doctype),
		             frappe.PermissionError)

	name = (name or "").strip() or _sample_document(doctype)
	if not name:
		frappe.throw(_("There is no {0} to preview yet.").format(doctype), frappe.ValidationError)
	if not frappe.has_permission(doctype, "print", doc=name):
		frappe.throw(_("You cannot print this document."), frappe.PermissionError)

	print_format = (print_format or "").strip() or resolve_print_format(doctype)
	# Its three siblings -- printing_admin.preview_document, .download_pdf and
	# collaboration.email_document -- all check that the format belongs to the
	# DocType being rendered. Without it a permitted document renders through a
	# mismatched template.
	if print_format and not frappe.db.exists(
		"Print Format", {"name": print_format, "doc_type": doctype}
	):
		frappe.throw(_("That print format is not available for {0}.").format(doctype),
		             frappe.ValidationError)
	entry = get_default_map().get(doctype) or {}
	language = (language or "").strip() or entry.get("language") or None

	# frappe.get_print honours field-level permissions, so a restricted user never
	# sees a field they cannot read.
	html = frappe.get_print(doctype, name, print_format=print_format or None, no_letterhead=0)
	return {
		"doctype": doctype, "name": name, "print_format": print_format,
		"language": language, "html": html,
	}
