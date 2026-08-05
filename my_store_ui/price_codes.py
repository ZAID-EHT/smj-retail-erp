"""Category-wise price codes: the preset prices and the SKU series behind them.

A price code (CCA, CCB, AAC …) belongs to one product category, carries the
Wholesale / Department / Retail prices a product of that code starts from, and
owns the running number that makes the SKU -- CCA 1, then CCA 2.

Reading is open to any authenticated user because the Product form needs the
codes; creating, editing and deleting a code or a category is administrator-only,
which is what "that button should only be accessible to the admin" means.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt

from my_store_ui.my_store_ui.doctype.retail_price_code.retail_price_code import peek_next_sku

DOCTYPE = "Retail Price Code"
ADMIN_ROLES = ("System Manager", "Item Manager")
MAX_CODES = 1000

PRICE_FIELDS = ("wholesale_price", "department_price", "retail_price")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def can_manage() -> bool:
	"""Whether this user may create or change price codes and categories."""
	if frappe.session.user == "Guest":
		return False
	if frappe.session.user == "Administrator":
		return True
	return bool(set(frappe.get_roles()) & set(ADMIN_ROLES)) and frappe.has_permission(DOCTYPE, "write")


def _require_manage() -> None:
	_require_login()
	if not can_manage():
		frappe.throw(_("Only an administrator can change price codes."), frappe.PermissionError)


def _serialise(row: dict) -> dict:
	return {
		"name": row["name"],
		"price_code": row["name"],
		"category": row.get("category"),
		"description": row.get("description") or "",
		"wholesale_price": flt(row.get("wholesale_price")),
		"department_price": flt(row.get("department_price")),
		"retail_price": flt(row.get("retail_price")),
		"current_sequence": cint(row.get("current_sequence")),
		"next_sku": f"{row['name']} {cint(row.get('current_sequence')) + 1}",
		"is_active": bool(row.get("is_active")),
	}


@frappe.whitelist(methods=["GET"])
def list_price_codes(query: str = "", category: str = "", include_inactive: str = "0") -> dict:
	"""Every usable price code, grouped by category, for the Product form picker."""
	_require_login()
	filters = {}
	if not cint(include_inactive):
		filters["is_active"] = 1
	if str(category or "").strip():
		filters["category"] = category.strip()
	or_filters = None
	text = str(query or "").strip()[:60]
	if text:
		or_filters = {"name": ["like", f"%{text}%"], "description": ["like", f"%{text}%"],
		              "category": ["like", f"%{text}%"]}
	rows = frappe.get_all(
		DOCTYPE, filters=filters, or_filters=or_filters,
		fields=["name", "category", "description", "wholesale_price", "department_price",
		        "retail_price", "current_sequence", "is_active"],
		order_by="category asc, name asc", limit_page_length=MAX_CODES,
	)
	codes = [_serialise(row) for row in rows]
	groups: dict[str, list] = {}
	for code in codes:
		groups.setdefault(code["category"] or _("Uncategorised"), []).append(code)
	return {
		"codes": codes,
		# Ordered list of {category, codes} so the picker can render optgroups
		# without re-sorting a dict on the client.
		"groups": [{"category": key, "codes": groups[key]} for key in sorted(groups)],
		"can_manage": can_manage(),
	}


@frappe.whitelist(methods=["GET"])
def get_price_code(name: str) -> dict:
	"""One code, including the SKU the next product carrying it would receive."""
	_require_login()
	if not frappe.db.exists(DOCTYPE, name):
		frappe.throw(_("Price Code not found."), frappe.DoesNotExistError)
	doc = frappe.get_doc(DOCTYPE, name)
	return {
		**_serialise(doc.as_dict()),
		"next_sku": peek_next_sku(doc.name),
		"can_manage": can_manage(),
	}


@frappe.whitelist(methods=["POST"])
def save_price_code(values: dict | str, name: str | None = None) -> dict:
	"""Create or edit a price code. Administrator only.

	The code and its category are set once: an existing code is already embedded in
	the SKU of every product carrying it, so renaming it would orphan those SKUs.
	"""
	_require_manage()
	data = frappe.parse_json(values) if isinstance(values, str) else values
	if not isinstance(data, dict):
		frappe.throw(_("Invalid price code details."), frappe.ValidationError)
	allowed = {"price_code", "category", "description", "is_active", *PRICE_FIELDS}
	unknown = set(data) - allowed
	if unknown:
		frappe.throw(_("Unsupported field: {0}").format(", ".join(sorted(unknown))), frappe.ValidationError)

	if name:
		if not frappe.db.exists(DOCTYPE, name):
			frappe.throw(_("Price Code not found."), frappe.DoesNotExistError)
		doc = frappe.get_doc(DOCTYPE, name)
	else:
		doc = frappe.new_doc(DOCTYPE)
		doc.price_code = str(data.get("price_code") or "").strip().upper()
		doc.category = str(data.get("category") or "").strip()

	doc.description = str(data.get("description") or "").strip() or None
	for field in PRICE_FIELDS:
		if field in data:
			doc.set(field, flt(data.get(field)))
	if "is_active" in data:
		doc.is_active = 1 if cint(data.get("is_active")) else 0

	doc.save() if name else doc.insert()
	return _serialise(doc.as_dict())


@frappe.whitelist(methods=["POST"])
def delete_price_code(name: str) -> dict:
	"""Delete a code. Refused by the DocType when products already carry it."""
	_require_manage()
	if not frappe.db.exists(DOCTYPE, name):
		frappe.throw(_("Price Code not found."), frappe.DoesNotExistError)
	frappe.delete_doc(DOCTYPE, name, ignore_permissions=False)
	return {"deleted": name}


# --------------------------------------------------------------------------
# Product categories (standard ERPNext Item Groups)
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def list_categories(query: str = "") -> dict:
	"""Selectable product categories -- the leaf Item Groups."""
	_require_login()
	or_filters = None
	text = str(query or "").strip()[:60]
	if text:
		or_filters = {"name": ["like", f"%{text}%"]}
	rows = frappe.get_all(
		"Item Group", filters={"is_group": 0}, or_filters=or_filters, pluck="name",
		order_by="name asc", limit_page_length=500,
	)
	return {"categories": rows, "can_manage": can_manage()}


@frappe.whitelist(methods=["POST"])
def add_category(category: str, parent: str = "") -> dict:
	"""Create a product category. Administrator only.

	A leaf Item Group under the site's root group, so it behaves exactly like a
	category created through ERPNext itself.
	"""
	_require_manage()
	name = str(category or "").strip()
	if not name:
		frappe.throw(_("Give the category a name."), frappe.ValidationError)
	if frappe.db.exists("Item Group", name):
		frappe.throw(_("{0} already exists.").format(name), frappe.DuplicateEntryError)
	root = str(parent or "").strip() or frappe.db.get_value(
		"Item Group", {"is_group": 1, "parent_item_group": ["in", ("", None)]}, "name") or "All Item Groups"
	doc = frappe.new_doc("Item Group")
	doc.item_group_name = name
	doc.parent_item_group = root
	doc.is_group = 0
	doc.insert()
	return {"category": doc.name, "parent": root}
