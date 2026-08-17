"""Build a role by picking the pages it can see.

Navigation visibility in this app is derived from ERPNext DocType permissions:
a link appears when you can read the data behind it. That is correct, but it is
not something a shop owner can drive -- it means opening the Role Permissions
Manager and reasoning about eleven checkboxes per DocType.

This module turns it around. You name a role, tick the pages it should see, and
the two things that have to be true are made true together:

  1. The choice is stored, and `frontend_routes` narrows both the header menu
     and route access to it.
  2. The role is granted read on the DocTypes those pages need, and loses it on
     the ones they no longer do -- because a page you can open but whose data
     you cannot read is an empty screen, not access control.

Granting is done through frappe.permissions.add_permission, which copies the
standard permission rows into Custom DocPerm first. Writing Custom DocPerm
directly would silently drop every other role's access to that DocType, since
Frappe stops consulting the standard rows as soon as one custom row exists.

Only a System Manager may use any of this, and a small set of roles is refused
outright: locking out System Manager or All would make the system unusable and
unrecoverable through the UI.
"""

from __future__ import annotations

import frappe
from frappe import _

from my_store_ui.services.frontend_routes import NAVIGATION

# Roles this tool refuses to touch. System Manager and Administrator are how the
# system is repaired; All and Guest are framework-level and shared by everyone.
PROTECTED_ROLES = frozenset({
	"System Manager", "Administrator", "All", "Guest", "Desk User", "Report Manager",
})

ACCESS_DOCTYPE = "Retail Role Page Access"


def _require_role_admin() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	if frappe.session.user == "Administrator":
		return
	if "System Manager" not in frappe.get_roles():
		frappe.throw(_("Only a System Manager can manage role access."), frappe.PermissionError)


def _assert_role_editable(role: str) -> str:
	role = (role or "").strip()
	if not role:
		frappe.throw(_("Pick a role."), frappe.ValidationError)
	if role in PROTECTED_ROLES:
		frappe.throw(
			_("{0} is a built-in role and cannot be limited here. Locking it would make the system unusable.").format(role),
			frappe.PermissionError,
		)
	if not frappe.db.exists("Role", role):
		frappe.throw(_("Role {0} does not exist.").format(role), frappe.DoesNotExistError)
	return role


def _link_doctypes(link: dict) -> list[str]:
	"""Every DocType a link needs read on before its page shows anything."""
	needed = []
	if link.get("doctype"):
		needed.append(link["doctype"])
	for doctype in link.get("any_read") or ():
		needed.append(doctype)
	return needed


@frappe.whitelist(methods=["GET"])
def get_page_catalogue() -> dict:
	"""The header menu as a pick-list: each section, its links, and what they need."""
	_require_role_admin()
	sections = []
	for item in NAVIGATION:
		links = []
		for link in item.get("links", ()):
			path = link.get("path")
			if not path:
				continue
			links.append({
				"label": link["label"],
				"path": path,
				"doctypes": sorted(set(_link_doctypes(link))),
				"admin_only": bool(link.get("roles")),
			})
		sections.append({
			"name": item["name"],
			"label": item["label"],
			"path": item["path"],
			"icon": item.get("icon"),
			"accent": item.get("accent"),
			"doctypes": sorted(set(item.get("any_read") or ())),
			"admin_only": bool(item.get("roles")),
			"links": links,
		})
	return {"sections": sections}


@frappe.whitelist(methods=["GET"])
def list_manageable_roles() -> dict:
	"""Roles this tool may configure, with whether each already has a selection."""
	_require_role_admin()
	configured = set(frappe.get_all(ACCESS_DOCTYPE, pluck="role"))
	roles = []
	for row in frappe.get_all(
		"Role", filters={"disabled": 0}, fields=["name", "desk_access"], order_by="name",
		limit_page_length=0,
	):
		if row["name"] in PROTECTED_ROLES:
			continue
		roles.append({
			"role": row["name"],
			"desk_access": bool(row["desk_access"]),
			"configured": row["name"] in configured,
			"user_count": frappe.db.count("Has Role", {"role": row["name"], "parenttype": "User"}),
		})
	return {"roles": roles, "protected": sorted(PROTECTED_ROLES)}


@frappe.whitelist(methods=["POST"])
def create_role(role_name: str) -> dict:
	"""Create an empty role, ready to have pages ticked for it."""
	_require_role_admin()
	role_name = (role_name or "").strip()
	if not role_name:
		frappe.throw(_("Give the role a name."), frappe.ValidationError)
	if len(role_name) > 140:
		frappe.throw(_("That role name is too long."), frappe.ValidationError)
	if role_name in PROTECTED_ROLES:
		frappe.throw(_("{0} already exists as a built-in role.").format(role_name), frappe.ValidationError)
	if frappe.db.exists("Role", role_name):
		frappe.throw(_("A role called {0} already exists.").format(role_name), frappe.DuplicateEntryError)

	doc = frappe.new_doc("Role")
	doc.role_name = role_name
	# Desk access off: these roles are for the Retail ERP screens, not the
	# ERPNext desk. It can still be turned on in ERPNext if it is ever needed.
	doc.desk_access = 0
	doc.insert()
	return {"role": doc.name, "created": True}


@frappe.whitelist(methods=["GET"])
def get_role_page_access(role: str) -> dict:
	"""What this role can currently see, and what it can actually read."""
	_require_role_admin()
	role = _assert_role_editable(role)
	paths, labels = [], {}
	if frappe.db.exists(ACCESS_DOCTYPE, role):
		doc = frappe.get_doc(ACCESS_DOCTYPE, role)
		for row in doc.pages:
			paths.append(row.path)
			labels[row.path] = row.label
	readable = _role_readable_doctypes(role)
	return {
		"role": role,
		"configured": bool(frappe.db.exists(ACCESS_DOCTYPE, role)),
		"paths": paths,
		"labels": labels,
		"readable_doctypes": sorted(readable),
	}


def _role_readable_doctypes(role: str) -> set[str]:
	custom = frappe.get_all(
		"Custom DocPerm", filters={"role": role, "read": 1, "permlevel": 0}, pluck="parent",
	)
	standard = frappe.get_all(
		"DocPerm", filters={"role": role, "read": 1, "permlevel": 0}, pluck="parent",
	)
	# Custom rows replace standard rows for a DocType once any exist for it.
	overridden = set(frappe.get_all("Custom DocPerm", pluck="parent"))
	return set(custom) | {name for name in standard if name not in overridden}


def _grant_read(doctype: str, role: str) -> bool:
	from frappe.permissions import add_permission

	if not frappe.db.exists("DocType", doctype):
		return False
	add_permission(doctype, role, 0, "read")
	return True


def _revoke_read(doctype: str, role: str) -> bool:
	"""Drop this role's read row, leaving every other role's access alone."""
	from frappe.permissions import setup_custom_perms

	if not frappe.db.exists("DocType", doctype):
		return False
	# Materialise the standard rows as custom ones first, or deleting here would
	# do nothing while the standard row keeps granting access.
	setup_custom_perms(doctype)
	rows = frappe.get_all(
		"Custom DocPerm", filters={"parent": doctype, "role": role, "permlevel": 0}, pluck="name",
	)
	for name in rows:
		frappe.delete_doc("Custom DocPerm", name, ignore_permissions=True, force=True)
	return bool(rows)


@frappe.whitelist(methods=["POST"])
def save_role_page_access(role: str, paths=None, grant_permissions: int = 1) -> dict:
	"""Store the page selection and align the role's read permissions with it."""
	_require_role_admin()
	role = _assert_role_editable(role)

	selected = frappe.parse_json(paths) if isinstance(paths, str) else (paths or [])
	if not isinstance(selected, list):
		frappe.throw(_("Page selection has an invalid format."), frappe.ValidationError)

	# Only paths that exist in the catalogue are accepted, so a crafted request
	# cannot invent a page or smuggle in something that is not a nav entry.
	catalogue = {}
	for section in get_page_catalogue()["sections"]:
		catalogue[section["path"]] = {"label": section["label"], "doctypes": section["doctypes"]}
		for link in section["links"]:
			catalogue.setdefault(link["path"], {"label": link["label"], "doctypes": link["doctypes"]})

	clean, unknown = [], []
	for path in selected:
		path = str(path).strip()
		if path in catalogue:
			if path not in clean:
				clean.append(path)
		elif path:
			unknown.append(path)
	if unknown:
		frappe.throw(_("Unknown page: {0}").format(", ".join(sorted(set(unknown))[:5])), frappe.ValidationError)

	if frappe.db.exists(ACCESS_DOCTYPE, role):
		doc = frappe.get_doc(ACCESS_DOCTYPE, role)
		doc.set("pages", [])
	else:
		doc = frappe.new_doc(ACCESS_DOCTYPE)
		doc.role = role
	for path in clean:
		doc.append("pages", {"path": path, "label": catalogue[path]["label"]})
	doc.save()

	granted, revoked = [], []
	if frappe.utils.cint(grant_permissions):
		wanted = set()
		for path in clean:
			wanted.update(catalogue[path]["doctypes"])
		# Everything this catalogue could ever ask for. Only these are revoked,
		# so a permission granted for some other reason is never taken away.
		managed = set()
		for entry in catalogue.values():
			managed.update(entry["doctypes"])

		current = _role_readable_doctypes(role)
		for doctype in sorted(wanted - current):
			if _grant_read(doctype, role):
				granted.append(doctype)
		for doctype in sorted((current & managed) - wanted):
			if _revoke_read(doctype, role):
				revoked.append(doctype)

	frappe.clear_cache()
	return {
		"role": role, "paths": clean, "saved": True,
		"granted": granted, "revoked": revoked,
	}


@frappe.whitelist(methods=["POST"])
def clear_role_page_access(role: str) -> dict:
	"""Remove the restriction, returning the role to plain permission-driven nav."""
	_require_role_admin()
	role = _assert_role_editable(role)
	if frappe.db.exists(ACCESS_DOCTYPE, role):
		frappe.delete_doc(ACCESS_DOCTYPE, role, ignore_permissions=True)
	frappe.clear_cache()
	return {"role": role, "cleared": True}


def allowed_paths_for_user() -> set[str] | None:
	"""Paths the current user may see, or None when no role limits them.

	Only roles that carry a selection restrict anything; a role with no
	selection contributes nothing rather than silently opening everything.
	"""
	if frappe.session.user in ("Administrator",):
		return None
	roles = set(frappe.get_roles())
	if "System Manager" in roles:
		return None
	configured = frappe.get_all(
		ACCESS_DOCTYPE, filters={"role": ["in", list(roles)]}, pluck="name",
	) if roles else []
	if not configured:
		return None
	allowed: set[str] = set()
	for name in configured:
		allowed.update(frappe.get_all(
			"Retail Role Page", filters={"parent": name, "parenttype": ACCESS_DOCTYPE}, pluck="path",
		))
	return allowed
