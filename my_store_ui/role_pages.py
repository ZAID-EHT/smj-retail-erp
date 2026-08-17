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

Before granting, the standard permission rows are copied into Custom DocPerm.
That ordering matters: Frappe stops consulting the standard rows as soon as one
custom row exists, so inserting only the new role first would silently drop
every other role's access to that DocType.

Only a System Manager may use any of this, and a small set of roles is refused
outright: locking out System Manager or All would make the system unusable and
unrecoverable through the UI.
"""

from __future__ import annotations

from urllib.parse import unquote, urlsplit

import frappe
from frappe import _

from my_store_ui.services.frontend_routes import NAVIGATION
from my_store_ui.services.priority_registry import REPORT_GROUPS

# Roles this tool refuses to touch. System Manager and Administrator are how the
# system is repaired; All and Guest are framework-level and shared by everyone.
PROTECTED_ROLES = frozenset({
	"System Manager", "Administrator", "All", "Guest", "Desk User", "Report Manager",
})

ACCESS_DOCTYPE = "Retail Role Page Access"
ACCESS_LEVEL_PERMISSIONS = {
	"view": ("read",),
	"edit": ("read", "write", "create"),
	"submit": ("read", "write", "create", "submit"),
}


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


def _page_catalogue_by_path() -> dict[str, dict]:
	"""Flatten the navigation tree to the exact paths this tool may store."""
	catalogue = {}
	for section in get_page_catalogue()["sections"]:
		catalogue[section["path"]] = {
			"label": section["label"], "doctypes": section["doctypes"],
			"admin_only": section["admin_only"],
		}
		for link in section["links"]:
			catalogue.setdefault(link["path"], {
				"label": link["label"], "doctypes": link["doctypes"],
				"admin_only": section["admin_only"] or link["admin_only"],
			})
	return catalogue


def _normalise_paths(paths, *, reject_admin_only: bool = False) -> tuple[list[str], dict[str, dict]]:
	selected = frappe.parse_json(paths) if isinstance(paths, str) else (paths or [])
	if not isinstance(selected, list):
		frappe.throw(_("Page selection has an invalid format."), frappe.ValidationError)

	catalogue = _page_catalogue_by_path()
	clean, unknown, admin_only = [], [], []
	for path in selected:
		path = str(path).strip()
		if path not in catalogue:
			if path:
				unknown.append(path)
			continue
		if reject_admin_only and catalogue[path]["admin_only"]:
			admin_only.append(path)
			continue
		if path not in clean:
			clean.append(path)
	if unknown:
		frappe.throw(_("Unknown page: {0}").format(", ".join(sorted(set(unknown))[:5])), frappe.ValidationError)
	if admin_only:
		frappe.throw(
			_("System Manager-only pages cannot be assigned to another role: {0}").format(
				", ".join(sorted(set(admin_only))[:5])
			),
			frappe.PermissionError,
		)
	return clean, catalogue


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
	doc = _insert_role(role_name, desk_access=0)
	return {"role": doc.name, "created": True}


def _insert_role(role_name: str, *, disabled: int = 0, desk_access: int = 0, is_custom: int = 0):
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
	doc.disabled = 1 if frappe.utils.cint(disabled) else 0
	doc.desk_access = 1 if frappe.utils.cint(desk_access) else 0
	doc.is_custom = 1 if frappe.utils.cint(is_custom) else 0
	doc.insert()
	return doc


def _grant_access_permissions(doctype: str, role: str, access_level: str) -> list[str]:
	"""Add the requested access without replacing any other role's rows."""
	from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
	from frappe.permissions import setup_custom_perms

	if not frappe.db.exists("DocType", doctype):
		return []
	permissions = list(ACCESS_LEVEL_PERMISSIONS[access_level])
	if not frappe.get_meta(doctype).is_submittable and "submit" in permissions:
		permissions.remove("submit")

	# Frappe switches an entire DocType to Custom DocPerm as soon as one custom
	# row exists. Materialise the standard rows first so granting this new role
	# cannot silently erase access belonging to every existing role.
	setup_custom_perms(doctype)
	name = frappe.db.get_value(
		"Custom DocPerm",
		{"parent": doctype, "role": role, "permlevel": 0, "if_owner": 0},
	)
	if name:
		row = frappe.get_doc("Custom DocPerm", name)
	else:
		row = frappe.get_doc({
			"doctype": "Custom DocPerm", "parent": doctype,
			"parenttype": "DocType", "parentfield": "permissions",
			"role": role, "permlevel": 0, "if_owner": 0,
		})
	granted = []
	for permission in permissions:
		if not frappe.utils.cint(row.get(permission)):
			row.set(permission, 1)
			granted.append(permission)
	row.save()
	validate_permissions_for_doctype(doctype)
	return granted


@frappe.whitelist(methods=["POST"])
def create_role_with_page_access(
	role_name: str,
	paths=None,
	disabled: int = 0,
	desk_access: int = 1,
	is_custom: int = 0,
	access_level: str = "submit",
) -> dict:
	"""Atomically create a Role, store its visible pages, and grant their data access."""
	_require_role_admin()
	access_level = (access_level or "").strip().lower()
	if access_level not in ACCESS_LEVEL_PERMISSIONS:
		frappe.throw(_("Choose View, Add & edit, or Submit access."), frappe.ValidationError)
	clean, catalogue = _normalise_paths(paths, reject_admin_only=True)
	if not clean:
		frappe.throw(_("Tick at least one page for this role."), frappe.ValidationError)

	doc = _insert_role(
		role_name, disabled=disabled, desk_access=desk_access, is_custom=is_custom,
	)
	# Store the menu restriction without invoking the legacy read-only grant. The
	# access level below supplies the complete permission row in one operation.
	save_role_page_access(doc.name, clean, grant_permissions=0)
	wanted = set()
	for path in clean:
		wanted.update(catalogue[path]["doctypes"])
	granted = {}
	for doctype in sorted(wanted):
		permissions = _grant_access_permissions(doctype, doc.name, access_level)
		if permissions:
			granted[doctype] = permissions
	frappe.clear_cache()
	return {
		"role": doc.name,
		"created": True,
		"paths": clean,
		"access_level": access_level,
		"granted": granted,
	}


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
	return bool(_grant_access_permissions(doctype, role, "view"))


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

	# Only paths that exist in the catalogue are accepted, so a crafted request
	# cannot invent a page. Existing saved Admin selections remain editable; the
	# route guard still requires System Manager for those pages.
	clean, catalogue = _normalise_paths(paths)

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


def path_is_allowed_for_user(path: str) -> bool:
	"""Apply configured role page access to routes outside the visible menu too."""
	allowed = allowed_paths_for_user()
	if allowed is None:
		return True
	relative = urlsplit(str(path or "")).path.rstrip("/") or "/"
	if relative == "/retail-erp":
		relative = "/home"
	elif relative.startswith("/retail-erp/"):
		relative = relative[len("/retail-erp"):]
	# These internal destinations must remain reachable so a refusal can render
	# instead of recursively refusing its own error page.
	if relative in {"/permission-denied", "/not-found", "/feature-unavailable"}:
		return True
	for selected in allowed:
		selected = str(selected or "").rstrip("/") or "/"
		if relative == selected or relative.startswith(f"{selected}/"):
			return True
	# A report result opens /reports/view/<name>, while role setup selects the
	# corresponding report group. Preserve that explicit relationship.
	if relative.startswith("/reports/view/"):
		report_name = unquote(relative[len("/reports/view/"):])
		for group, names in REPORT_GROUPS.items():
			if report_name in names and ("/reports" in allowed or f"/reports/{group}" in allowed):
				return True
	return False
