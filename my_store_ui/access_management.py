"""Phase 8 — user, role and access administration.

Every endpoint here is a user-management surface, so each one re-checks
`System Manager` **and** the relevant DocType permission on the server. Nothing
trusts a role list supplied by the browser, and no endpoint uses
`ignore_permissions`.

Effective access is always evaluated by the backend for the *target* user
(`frappe.has_permission(..., user=user)`, `frappe.get_roles(user)`,
`get_user_permissions(user)`) — never inferred from frontend state.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

# DocTypes that may be used to restrict a user via standard User Permission
# records. Deliberately an allowlist -- an arbitrary DocType must never be
# accepted from a request.
RESTRICTION_DOCTYPES = (
	"Company", "Warehouse", "Customer", "Supplier",
	"Territory", "Project", "Cost Center", "Sales Person",
)

# Permission types reported on the effective-access view.
PERMISSION_TYPES = (
	"read", "create", "write", "submit", "cancel", "amend", "print", "export", "delete",
)

# The business DocTypes whose effective access is worth showing an administrator.
EFFECTIVE_ACCESS_DOCTYPES = (
	"Customer", "Supplier", "Item", "Quotation", "Sales Order", "Delivery Note",
	"Sales Invoice", "Material Request", "Purchase Order", "Purchase Receipt",
	"Purchase Invoice", "Payment Entry", "Journal Entry", "Stock Entry",
	"Stock Reconciliation", "User", "Role",
)

# Accounts that must never be disabled, deleted or have sessions revoked through
# this surface. Frappe's own User.validate also guards Administrator and the last
# System Manager; this is an additional explicit boundary.
PROTECTED_USERS = ("Administrator", "Guest")

# Roles whose membership changes are high risk and must be flagged in the UI.
HIGH_RISK_ROLES = ("System Manager", "Administrator", "Accounts Manager", "Stock Manager")

# Frappe-owned roles that are not meaningful to assign or edit.
PROTECTED_ROLES = ("All", "Guest", "Administrator", "Desk User")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_user_manager() -> None:
	"""Server-side gate for every endpoint in this module."""
	_require_login()
	if frappe.session.user == "Administrator":
		return
	if "System Manager" not in frappe.get_roles():
		frappe.throw(_("Only a System Manager can manage users and access."), frappe.PermissionError)


def _permitted_user(user: str, permission: str = "read") -> str:
	"""Validate a user name from a request and confirm access to that User doc."""
	user = str(user or "").strip()
	if not user or len(user) > 140:
		frappe.throw(_("A user is required."), frappe.ValidationError)
	if not frappe.has_permission("User", permission):
		frappe.throw(_("You do not have permission to manage users."), frappe.PermissionError)
	# get_list applies User Permissions and does not leak inaccessible names.
	if not frappe.get_list("User", filters={"name": user}, pluck="name", limit_page_length=1):
		frappe.throw(_("User not found or unavailable."), frappe.DoesNotExistError)
	return user


def _assert_not_protected(user: str, action: str) -> None:
	if user in PROTECTED_USERS:
		frappe.throw(
			_("{0} is a protected system account and cannot be {1}.").format(user, action),
			frappe.PermissionError,
		)


# ---------------------------------------------------------------------------
# User directory
# ---------------------------------------------------------------------------

# Safe to show an administrator. Deliberately excludes every credential and
# session field (api_key, api_secret, password hashes, reset keys).
USER_DIRECTORY_FIELDS = (
	"name", "full_name", "enabled", "user_type", "role_profile_name", "last_login",
	"last_active", "creation",
)


@frappe.whitelist(methods=["GET"])
def search_users(
	search: str = "",
	status: str = "",
	role: str = "",
	role_profile: str = "",
	user_type: str = "",
	never_logged_in: int | str = 0,
	limit: int = 50,
) -> dict:
	"""Permission-filtered user directory for the access surfaces.

	Uses `frappe.get_list`, so User Permissions apply and a manager never sees an
	account they are not entitled to.
	"""
	_require_user_manager()
	if not frappe.has_permission("User", "read"):
		frappe.throw(_("You do not have permission to view users."), frappe.PermissionError)

	filters: dict = {}
	if status == "enabled":
		filters["enabled"] = 1
	elif status == "disabled":
		filters["enabled"] = 0
	if user_type in {"System User", "Website User"}:
		filters["user_type"] = user_type
	if role_profile:
		filters["role_profile_name"] = role_profile
	if cint(never_logged_in):
		filters["last_login"] = ["is", "not set"]
	if role:
		holders = frappe.get_all(
			"Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent", limit_page_length=0
		)
		if not holders:
			return {"users": [], "total": 0}
		filters["name"] = ["in", holders]

	or_filters = None
	if search:
		term = f"%{str(search)[:60]}%"
		or_filters = {"name": ["like", term], "full_name": ["like", term]}

	rows = frappe.get_list(
		"User", filters=filters, or_filters=or_filters, fields=list(USER_DIRECTORY_FIELDS),
		order_by="enabled desc, full_name asc", limit_page_length=max(1, min(cint(limit) or 50, 200)),
	)
	for row in rows:
		row["effective_role_count"] = len(frappe.get_roles(row["name"]))
		row["protected"] = row["name"] in PROTECTED_USERS
	return {"users": rows, "total": len(rows)}


# ---------------------------------------------------------------------------
# Effective access
# ---------------------------------------------------------------------------

def _effective_permissions(user: str) -> list[dict]:
	rows = []
	for doctype in EFFECTIVE_ACCESS_DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			continue
		meta = frappe.get_meta(doctype)
		entry = {"doctype": doctype, "is_submittable": bool(meta.is_submittable)}
		for permission in PERMISSION_TYPES:
			if permission in {"submit", "cancel", "amend"} and not meta.is_submittable:
				entry[permission] = False
				continue
			# Real backend evaluation for the target user, not a role guess.
			entry[permission] = bool(frappe.has_permission(doctype, permission, user=user))
		rows.append(entry)
	return rows


def _restrictions(user: str) -> list[dict]:
	from frappe.permissions import get_user_permissions

	permissions = get_user_permissions(user) or {}
	rows = []
	for doctype in RESTRICTION_DOCTYPES:
		values = [entry.get("doc") for entry in permissions.get(doctype, []) if entry.get("doc")]
		rows.append({
			"doctype": doctype,
			"restricted": bool(values),
			"values": sorted(values),
		})
	return rows


def _allowed_modules(user: str) -> list[str]:
	blocked = {
		row.module for row in frappe.get_all(
			"Block Module", filters={"parent": user, "parenttype": "User"}, fields=["module"]
		)
	}
	modules = frappe.get_all("Module Def", pluck="name", order_by="name asc")
	return [module for module in modules if module not in blocked]


@frappe.whitelist(methods=["GET"])
def get_user_access_overview(user: str) -> dict:
	"""Backend-evaluated effective access for one user."""
	_require_user_manager()
	user = _permitted_user(user)
	doc = frappe.get_doc("User", user)
	roles = sorted(frappe.get_roles(user))
	return {
		"user": user,
		"full_name": doc.full_name,
		"account": {
			"enabled": bool(doc.enabled),
			"status": _("Active") if doc.enabled else _("Disabled"),
			"user_type": doc.user_type,
			"last_login": doc.last_login,
			"last_active": doc.last_active,
			"login_after": doc.login_after,
			"protected": user in PROTECTED_USERS,
			"active_sessions": count_user_sessions(user),
		},
		"role_profile": doc.role_profile_name,
		"effective_roles": roles,
		"direct_roles": sorted({row.role for row in doc.get("roles", []) if row.role}),
		"allowed_modules": _allowed_modules(user),
		"permissions": _effective_permissions(user),
		"restrictions": _restrictions(user),
		"email": _email_configuration_status(),
	}


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def count_user_sessions(user: str) -> int:
	return cint(frappe.db.count("Sessions", {"user": user}))


@frappe.whitelist(methods=["POST"])
def revoke_user_sessions(user: str) -> dict:
	"""Sign a user out of every device without changing their password."""
	_require_user_manager()
	user = _permitted_user(user, "write")
	_assert_not_protected(user, _("signed out"))
	if not frappe.has_permission("User", "write", doc=user):
		frappe.throw(_("You do not have permission to manage this user."), frappe.PermissionError)
	revoked = count_user_sessions(user)
	# Frappe's own helper clears the Sessions rows and the session cache together.
	from frappe.sessions import clear_sessions

	clear_sessions(user=user, force=True)
	# No explicit commit: Frappe commits a successful request, and committing here
	# would make a later failure impossible to roll back.
	return {"user": user, "revoked_sessions": revoked, "active_sessions": count_user_sessions(user)}


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def get_role_overview() -> dict:
	"""Every role with its real assignment counts and risk flag."""
	_require_user_manager()
	if not frappe.has_permission("Role", "read"):
		frappe.throw(_("You do not have permission to view roles."), frappe.PermissionError)

	user_counts: dict[str, int] = {}
	for row in frappe.get_all("Has Role", filters={"parenttype": "User"}, fields=["role"]):
		user_counts[row.role] = user_counts.get(row.role, 0) + 1
	profile_counts: dict[str, int] = {}
	for row in frappe.get_all("Has Role", filters={"parenttype": "Role Profile"}, fields=["role"]):
		profile_counts[row.role] = profile_counts.get(row.role, 0) + 1

	roles = []
	for role in frappe.get_all(
		"Role", fields=["name", "disabled", "is_custom", "desk_access"], order_by="name asc"
	):
		roles.append({
			"role": role.name,
			"disabled": bool(role.disabled),
			"is_custom": bool(role.is_custom),
			"desk_access": bool(role.desk_access),
			"assigned_users": user_counts.get(role.name, 0),
			"role_profiles": profile_counts.get(role.name, 0),
			"high_risk": role.name in HIGH_RISK_ROLES,
			"protected": role.name in PROTECTED_ROLES,
		})
	return {"roles": roles, "high_risk_roles": list(HIGH_RISK_ROLES), "protected_roles": list(PROTECTED_ROLES)}


@frappe.whitelist(methods=["GET"])
def get_role_permission_summary(role: str) -> dict:
	"""What a single role actually grants, read from DocPerm metadata."""
	_require_user_manager()
	role = str(role or "").strip()
	if not role or not frappe.db.exists("Role", role):
		frappe.throw(_("Role not found."), frappe.DoesNotExistError)
	if not frappe.has_permission("Role", "read"):
		frappe.throw(_("You do not have permission to view roles."), frappe.PermissionError)

	rows = []
	for perm in frappe.get_all(
		"DocPerm", filters={"role": role}, order_by="parent asc",
		fields=["parent", "permlevel", *PERMISSION_TYPES],
	):
		if cint(perm.permlevel) != 0:
			continue
		granted = [permission for permission in PERMISSION_TYPES if cint(perm.get(permission))]
		if granted:
			rows.append({"doctype": perm.parent, "granted": granted})
	return {
		"role": role,
		"high_risk": role in HIGH_RISK_ROLES,
		"protected": role in PROTECTED_ROLES,
		"assigned_users": cint(frappe.db.count("Has Role", {"role": role, "parenttype": "User"})),
		"role_profiles": cint(frappe.db.count("Has Role", {"role": role, "parenttype": "Role Profile"})),
		"doctype_permissions": rows,
	}


# ---------------------------------------------------------------------------
# Role Profiles
# ---------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def get_role_profile_overview() -> dict:
	_require_user_manager()
	if not frappe.has_permission("Role Profile", "read"):
		frappe.throw(_("You do not have permission to view role profiles."), frappe.PermissionError)

	assigned: dict[str, int] = {}
	for row in frappe.get_all("User", fields=["role_profile_name"]):
		if row.role_profile_name:
			assigned[row.role_profile_name] = assigned.get(row.role_profile_name, 0) + 1

	profiles = []
	for name in frappe.get_list("Role Profile", pluck="name", order_by="name asc", limit_page_length=0):
		roles = sorted(
			row.role for row in frappe.get_all(
				"Has Role", filters={"parent": name, "parenttype": "Role Profile"}, fields=["role"]
			) if row.role
		)
		profiles.append({
			"role_profile": name,
			"roles": roles,
			"role_count": len(roles),
			"assigned_users": assigned.get(name, 0),
			"high_risk_roles": [role for role in roles if role in HIGH_RISK_ROLES],
		})
	return {"profiles": profiles}


@frappe.whitelist(methods=["GET"])
def compare_role_profiles(first: str, second: str) -> dict:
	"""Side-by-side role difference between two profiles."""
	_require_user_manager()
	if not frappe.has_permission("Role Profile", "read"):
		frappe.throw(_("You do not have permission to view role profiles."), frappe.PermissionError)

	def roles_of(profile: str) -> set[str]:
		profile = str(profile or "").strip()
		if not profile or not frappe.db.exists("Role Profile", profile):
			frappe.throw(_("Role Profile {0} not found.").format(profile), frappe.DoesNotExistError)
		return {
			row.role for row in frappe.get_all(
				"Has Role", filters={"parent": profile, "parenttype": "Role Profile"}, fields=["role"]
			) if row.role
		}

	left, right = roles_of(first), roles_of(second)
	return {
		"first": first, "second": second,
		"shared": sorted(left & right),
		"only_in_first": sorted(left - right),
		"only_in_second": sorted(right - left),
		"high_risk_difference": sorted((left ^ right) & set(HIGH_RISK_ROLES)),
	}


@frappe.whitelist(methods=["GET"])
def get_role_profile_change_impact(role_profile: str) -> dict:
	"""Who is affected before a profile's roles are changed."""
	_require_user_manager()
	role_profile = str(role_profile or "").strip()
	if not role_profile or not frappe.db.exists("Role Profile", role_profile):
		frappe.throw(_("Role Profile not found."), frappe.DoesNotExistError)
	users = frappe.get_list(
		"User", filters={"role_profile_name": role_profile},
		fields=["name", "full_name", "enabled"], limit_page_length=0,
	)
	roles = sorted(
		row.role for row in frappe.get_all(
			"Has Role", filters={"parent": role_profile, "parenttype": "Role Profile"}, fields=["role"]
		) if row.role
	)
	return {
		"role_profile": role_profile,
		"roles": roles,
		"affected_user_count": len(users),
		"affected_users": users,
		"high_risk_roles": [role for role in roles if role in HIGH_RISK_ROLES],
		"warning": _(
			"Changing this profile immediately changes access for {0} user(s)."
		).format(len(users)) if users else None,
	}


# ---------------------------------------------------------------------------
# User Permissions (restrictions)
# ---------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def get_restriction_options(doctype: str, search: str = "") -> dict:
	"""Permitted values for one restriction DocType."""
	_require_user_manager()
	doctype = str(doctype or "").strip()
	if doctype not in RESTRICTION_DOCTYPES:
		frappe.throw(_("{0} cannot be used as a restriction.").format(doctype), frappe.ValidationError)
	if not frappe.db.exists("DocType", doctype) or not frappe.has_permission(doctype, "read"):
		frappe.throw(_("You do not have permission to read {0}.").format(doctype), frappe.PermissionError)
	filters = {}
	if search:
		filters["name"] = ["like", f"%{str(search)[:60]}%"]
	return {
		"doctype": doctype,
		"options": frappe.get_list(doctype, filters=filters, pluck="name", order_by="name asc", limit_page_length=50),
	}


@frappe.whitelist(methods=["POST"])
def set_user_restrictions(user: str, doctype: str, values: list | str | None = None) -> dict:
	"""Replace a user's User Permission rows for one restriction DocType.

	Uses standard `User Permission` documents so ERPNext's own permission query
	conditions apply everywhere -- no parallel restriction mechanism.
	"""
	_require_user_manager()
	user = _permitted_user(user, "write")
	doctype = str(doctype or "").strip()
	if doctype not in RESTRICTION_DOCTYPES:
		frappe.throw(_("{0} cannot be used as a restriction.").format(doctype), frappe.ValidationError)
	if not frappe.has_permission("User Permission", "create") or not frappe.has_permission("User Permission", "delete"):
		frappe.throw(_("You do not have permission to manage user permissions."), frappe.PermissionError)

	if isinstance(values, str):
		values = frappe.parse_json(values)
	values = [str(value).strip() for value in (values or []) if str(value or "").strip()]
	for value in values:
		if not frappe.db.exists(doctype, value):
			frappe.throw(_("{0} {1} does not exist.").format(doctype, value), frappe.ValidationError)
		# Never let an administrator grant a restriction to a record they cannot read.
		if not frappe.get_list(doctype, filters={"name": value}, pluck="name", limit_page_length=1):
			frappe.throw(_("{0} {1} is not available to you.").format(doctype, value), frappe.PermissionError)

	existing = frappe.get_all(
		"User Permission", filters={"user": user, "allow": doctype}, fields=["name", "for_value"]
	)
	keep = {row.for_value for row in existing if row.for_value in values}
	for row in existing:
		if row.for_value not in values:
			frappe.delete_doc("User Permission", row.name)
	for value in values:
		if value in keep:
			continue
		frappe.get_doc({
			"doctype": "User Permission", "user": user, "allow": doctype, "for_value": value,
		}).insert()
	# Deletes and inserts must land together, so the request's own commit is the
	# only commit -- a partial restriction set is a security bug, not a cosmetic one.
	return {"user": user, "doctype": doctype, "values": sorted(values), "restrictions": _restrictions(user)}


# ---------------------------------------------------------------------------
# Email / onboarding status
# ---------------------------------------------------------------------------

def _email_configuration_status() -> dict:
	"""Whether a welcome/reset email can actually be delivered.

	Credentials are never read or returned -- only whether a usable outgoing
	account exists, so an administrator knows to set a temporary password instead.

	`Email Account` has no `disabled` field; outgoing delivery is driven by
	`enable_outgoing`, and `awaiting_password` means the account exists but has no
	working credentials, so it cannot actually send.
	"""
	accounts = frappe.get_all(
		"Email Account",
		filters={"enable_outgoing": 1},
		fields=["name", "email_id", "default_outgoing", "awaiting_password"],
		order_by="default_outgoing desc, name asc",
	)
	usable = [row for row in accounts if not row.awaiting_password]
	default_outgoing = next((row for row in usable if row.default_outgoing), None)
	# Frappe also falls back to a site-config SMTP server when no account is defined.
	site_fallback = bool(frappe.conf.get("mail_server") or frappe.conf.get("mail_login"))
	can_send = bool(default_outgoing or usable or site_fallback)
	return {
		"outgoing_configured": bool(accounts) or site_fallback,
		"outgoing_enabled": bool(usable) or site_fallback,
		"default_outgoing_account": default_outgoing.name if default_outgoing else None,
		"accounts": [
			{
				"name": row.name,
				"email_id": row.email_id,
				"default_outgoing": bool(row.default_outgoing),
				# Surfaced so "configured but silently dead" is distinguishable.
				"awaiting_password": bool(row.awaiting_password),
			}
			for row in accounts
		],
		"site_config_fallback": site_fallback,
		"can_send_welcome_email": can_send,
		"message": None if can_send else _(
			"Email delivery is not configured. Use an administrator-set temporary password."
		),
	}


@frappe.whitelist(methods=["GET"])
def get_email_configuration_status() -> dict:
	_require_user_manager()
	return _email_configuration_status()
