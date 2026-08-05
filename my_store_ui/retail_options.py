"""Admin-managed dropdown options for the Retail ERP forms.

Every "add / delete the choices in this dropdown" button on the Customer and
Product forms lands here. Reading is open to any authenticated user (the forms
need the choices); creating, renaming and deleting is System Manager only, which
is what the requirement means by "only the admin".
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.my_store_ui.doctype.retail_option_list.retail_option_list import (
	OPTION_TYPES,
	USAGE,
)

DOCTYPE = "Retail Option List"
ADMIN_ROLES = ("System Manager",)
MAX_OPTIONS = 2000


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def can_manage() -> bool:
	"""Whether this user may add or remove options."""
	if frappe.session.user == "Guest":
		return False
	if frappe.session.user == "Administrator":
		return True
	return bool(set(frappe.get_roles()) & set(ADMIN_ROLES)) and frappe.has_permission(DOCTYPE, "write")


def _require_manage() -> None:
	_require_login()
	if not can_manage():
		frappe.throw(_("Only an administrator can change these options."), frappe.PermissionError)


def _validate_type(option_type: str) -> str:
	option_type = str(option_type or "").strip()
	if option_type not in OPTION_TYPES:
		frappe.throw(_("Unsupported option type."), frappe.ValidationError)
	return option_type


def option_values(option_type: str, include_inactive: bool = False) -> list[str]:
	"""Active values for one type, in the admin's chosen order. Server-side helper."""
	filters = {"option_type": option_type}
	if not include_inactive:
		filters["is_active"] = 1
	rows = frappe.get_all(
		DOCTYPE, filters=filters, fields=["option_value", "sort_order"],
		order_by="sort_order asc, option_value asc", limit_page_length=MAX_OPTIONS,
	)
	return [row["option_value"] for row in rows]


@frappe.whitelist(methods=["GET"])
def list_options(option_type: str = "", query: str = "", include_inactive: str = "0") -> dict:
	"""The choices one dropdown should offer, optionally type-ahead filtered."""
	_require_login()
	option_type = _validate_type(option_type)
	filters = {"option_type": option_type}
	if not cint(include_inactive):
		filters["is_active"] = 1
	or_filters = None
	text = str(query or "").strip()[:60]
	if text:
		or_filters = {"option_value": ["like", f"%{text}%"]}
	rows = frappe.get_all(
		DOCTYPE, filters=filters, or_filters=or_filters,
		fields=["name", "option_value", "is_active", "sort_order"],
		order_by="sort_order asc, option_value asc", limit_page_length=MAX_OPTIONS,
	)
	return {
		"option_type": option_type,
		"options": [row["option_value"] for row in rows],
		"rows": rows,
		"can_manage": can_manage(),
	}


@frappe.whitelist(methods=["GET"])
def list_all_options() -> dict:
	"""Every type and its choices -- one request for the admin page and the forms."""
	_require_login()
	return {
		"types": list(OPTION_TYPES),
		"can_manage": can_manage(),
		"options": {
			option_type: frappe.get_all(
				DOCTYPE, filters={"option_type": option_type},
				fields=["name", "option_value", "is_active", "sort_order"],
				order_by="sort_order asc, option_value asc", limit_page_length=MAX_OPTIONS,
			)
			for option_type in OPTION_TYPES
		},
		# Shown on the admin page so "why can't I delete this?" is answered before
		# the attempt rather than after it.
		"usage": {key: value[0] for key, value in USAGE.items()},
	}


@frappe.whitelist(methods=["POST"])
def add_option(option_type: str, option_value: str, sort_order: int = 0) -> dict:
	"""Create one option. Admin only."""
	_require_manage()
	option_type = _validate_type(option_type)
	value = str(option_value or "").strip()
	if not value:
		frappe.throw(_("Give the option a value."), frappe.ValidationError)
	if len(value) > 140:
		frappe.throw(_("The option is too long."), frappe.ValidationError)
	if frappe.db.exists(DOCTYPE, {"option_type": option_type, "option_value": value}):
		frappe.throw(_("{0} already offers {1}.").format(option_type, value), frappe.DuplicateEntryError)
	doc = frappe.new_doc(DOCTYPE)
	doc.option_type = option_type
	doc.option_value = value
	doc.sort_order = cint(sort_order)
	doc.is_active = 1
	doc.insert()
	return {"name": doc.name, "option_type": option_type, "option_value": value}


@frappe.whitelist(methods=["POST"])
def set_option_active(name: str, is_active: int = 1) -> dict:
	"""Hide or restore an option without touching records that already use it."""
	_require_manage()
	if not frappe.db.exists(DOCTYPE, name):
		frappe.throw(_("Option not found."), frappe.DoesNotExistError)
	doc = frappe.get_doc(DOCTYPE, name)
	doc.is_active = 1 if cint(is_active) else 0
	doc.save()
	return {"name": doc.name, "is_active": bool(doc.is_active)}


@frappe.whitelist(methods=["POST"])
def delete_option(name: str) -> dict:
	"""Delete an option. Refused by the DocType when records already carry it."""
	_require_manage()
	if not frappe.db.exists(DOCTYPE, name):
		frappe.throw(_("Option not found."), frappe.DoesNotExistError)
	option_type = frappe.db.get_value(DOCTYPE, name, "option_type")
	frappe.delete_doc(DOCTYPE, name, ignore_permissions=False)
	return {"deleted": name, "option_type": option_type}
