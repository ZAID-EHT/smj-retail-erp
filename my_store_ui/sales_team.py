"""Sales Teams, customer assignment and the commission snapshot.

A Retail Sales Team is the master: one Sales Manager plus their representatives,
and how the team's commission pool is split between them. A Customer is assigned to
a team; new transactions copy that team onto themselves as an immutable snapshot,
so reassigning a customer later never rewrites history.

The team is also projected onto ERPNext's own `sales_team` child table on the
Customer and Sales Order, so standard ERPNext sales-person reporting keeps working
rather than being replaced.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

from my_store_ui.my_store_ui.doctype.retail_sales_team.retail_sales_team import (
	MANAGER_ROLE,
	REPRESENTATIVE_ROLE,
	SHARE_TOLERANCE,
	TOTAL_SHARE,
)

DOCTYPE = "Retail Sales Team"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Roles allowed to create or change a team, or to reassign a customer.
ADMIN_ROLES = ("System Manager", "Sales Manager")

DEFAULT_SPLIT = (
	{"team_role": MANAGER_ROLE, "share_percentage": 50.0},
	{"team_role": REPRESENTATIVE_ROLE, "share_percentage": 25.0},
	{"team_role": REPRESENTATIVE_ROLE, "share_percentage": 25.0},
)


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_read() -> None:
	_require_login()
	if not frappe.has_permission(DOCTYPE, "read"):
		frappe.throw(_("You do not have access to sales teams."), frappe.PermissionError)


def can_manage() -> bool:
	roles = set(frappe.get_roles())
	return bool(roles & set(ADMIN_ROLES)) and frappe.has_permission(DOCTYPE, "write")


def _require_manage() -> None:
	_require_login()
	if not can_manage():
		frappe.throw(
			_("Only a Sales Manager or System Manager can change sales teams."),
			frappe.PermissionError,
		)


# --------------------------------------------------------------------------
# Master: list / read / save
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def list_sales_teams(search: str = "", is_active: str = "", sales_manager: str = "",
                     effective_on: str = "", page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                     sort_field: str = "team_name", sort_order: str = "asc"):
	"""Permission-aware, filtered, sorted, paginated list."""
	_require_read()
	if sort_field not in {"team_name", "sales_manager", "commission_rate", "effective_from", "modified"}:
		frappe.throw(_("Unsupported sort field."), frappe.ValidationError)
	if str(sort_order).lower() not in {"asc", "desc"}:
		frappe.throw(_("Unsupported sort order."), frappe.ValidationError)

	page = max(cint(page) or 1, 1)
	page_size = min(max(cint(page_size) or DEFAULT_PAGE_SIZE, 1), MAX_PAGE_SIZE)

	filters = {}
	if is_active in ("0", "1", 0, 1):
		filters["is_active"] = cint(is_active)
	if sales_manager:
		filters["sales_manager"] = sales_manager
	if effective_on:
		filters["effective_from"] = ["<=", effective_on]

	or_filters = None
	if search:
		like = f"%{search.strip()}%"
		or_filters = {"team_name": ["like", like], "name": ["like", like],
		              "sales_manager": ["like", like]}

	fields = ["name", "team_name", "sales_manager", "commission_rate", "effective_from",
	          "effective_to", "is_active", "modified"]
	# get_list applies User Permissions; get_all would bypass them.
	rows = frappe.get_list(
		DOCTYPE, filters=filters, or_filters=or_filters, fields=fields,
		order_by=f"{sort_field} {sort_order}",
		limit_start=(page - 1) * page_size, limit_page_length=page_size,
	)
	total = len(frappe.get_list(
		DOCTYPE, filters=filters, or_filters=or_filters, fields=["name"], limit_page_length=0
	))

	names = [r["name"] for r in rows]
	counts = {}
	if names:
		for row in frappe.get_all(
			"Retail Sales Team Member",
			filters={"parent": ["in", names], "parenttype": DOCTYPE, "is_active": 1},
			fields=["parent", "count(name) as total"], group_by="parent",
		):
			counts[row["parent"]] = cint(row["total"])

	for row in rows:
		row["member_count"] = counts.get(row["name"], 0)
		# The customer form previews the manager/representatives/split without a
		# second round trip per team.
		row["preview"] = team_payload(row["name"])
		if row.get("effective_to") and str(row["effective_to"]) < nowdate():
			row["status"] = "Expired"
		elif row.get("is_active"):
			row["status"] = "Active"
		else:
			row["status"] = "Inactive"

	return {
		"rows": rows,
		"pagination": {"page": page, "page_size": page_size, "total": total,
		               "pages": max((total + page_size - 1) // page_size, 1)},
		"can_manage": can_manage(),
		"managers": frappe.get_all(
			DOCTYPE, filters={"sales_manager": ["is", "set"]}, pluck="sales_manager", distinct=True
		),
	}


def _serialise(doc) -> dict:
	return {
		"name": doc.name,
		"team_name": doc.team_name,
		"team_code": doc.name,
		"sales_manager": doc.sales_manager,
		"commission_rate": flt(doc.commission_rate),
		"effective_from": str(doc.effective_from) if doc.effective_from else None,
		"effective_to": str(doc.effective_to) if doc.effective_to else None,
		"is_active": bool(doc.is_active),
		"notes": doc.notes or "",
		"members": [
			{
				"sales_person": row.sales_person,
				"team_role": row.team_role,
				"share_percentage": flt(row.share_percentage),
				"is_active": bool(row.is_active),
				"effective_from": str(row.effective_from) if row.effective_from else None,
				"effective_to": str(row.effective_to) if row.effective_to else None,
			}
			for row in doc.get("members") or []
		],
	}


@frappe.whitelist(methods=["GET"])
def get_sales_team(name: str = ""):
	# A blank name means "give me the shape of a new team". The client drops empty
	# query parameters, so this must default rather than be required.
	"""One team, or the default shape for a new one when name is blank."""
	_require_read()
	if not name:
		return {
			"team": {
				"name": None, "team_name": "", "team_code": "(generated on save)",
				"sales_manager": None, "commission_rate": 0.0,
				"effective_from": nowdate(), "effective_to": None, "is_active": True,
				"notes": "",
				# The requested starting structure; the user may change any of it.
				"members": [dict(row, sales_person="", is_active=True,
				                 effective_from=nowdate(), effective_to=None)
				            for row in DEFAULT_SPLIT],
			},
			"can_manage": can_manage(),
			"roles": [MANAGER_ROLE, REPRESENTATIVE_ROLE],
			"is_new": True,
		}
	if not frappe.has_permission(DOCTYPE, "read", doc=name):
		frappe.throw(_("You do not have access to this sales team."), frappe.PermissionError)
	doc = frappe.get_doc(DOCTYPE, name)
	return {
		"team": _serialise(doc),
		"can_manage": can_manage(),
		"roles": [MANAGER_ROLE, REPRESENTATIVE_ROLE],
		"is_new": False,
		"assigned_customers": frappe.get_list(
			"Customer", filters={"custom_sales_team": name}, fields=["name", "customer_name"],
			limit_page_length=25,
		),
	}


@frappe.whitelist(methods=["POST"])
def save_sales_team(payload, name: str | None = None):
	"""Create or update a team. Every rule is re-checked by the controller."""
	_require_manage()
	data = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(data, dict):
		frappe.throw(_("Invalid sales team details."), frappe.ValidationError)

	if name:
		if not frappe.has_permission(DOCTYPE, "write", doc=name):
			frappe.throw(_("You cannot edit this sales team."), frappe.PermissionError)
		doc = frappe.get_doc(DOCTYPE, name)
	else:
		doc = frappe.new_doc(DOCTYPE)

	doc.team_name = str(data.get("team_name") or "").strip()
	doc.commission_rate = flt(data.get("commission_rate"))
	doc.effective_from = data.get("effective_from") or nowdate()
	doc.effective_to = data.get("effective_to") or None
	doc.is_active = 1 if data.get("is_active", True) else 0
	doc.notes = data.get("notes") or ""

	doc.set("members", [])
	for row in data.get("members") or []:
		doc.append("members", {
			"sales_person": str((row or {}).get("sales_person") or "").strip(),
			"team_role": (row or {}).get("team_role") or REPRESENTATIVE_ROLE,
			"share_percentage": flt((row or {}).get("share_percentage")),
			"is_active": 1 if (row or {}).get("is_active", True) else 0,
			"effective_from": (row or {}).get("effective_from") or None,
			"effective_to": (row or {}).get("effective_to") or None,
		})

	doc.save()
	_sync_assigned_customers(doc.name)
	return {"name": doc.name, "team": _serialise(doc)}


def _sync_assigned_customers(team: str) -> None:
	"""Keep ERPNext's own Customer.sales_team rows aligned with the master."""
	for customer in frappe.get_all("Customer", filters={"custom_sales_team": team}, pluck="name"):
		try:
			doc = frappe.get_doc("Customer", customer)
			_apply_team_rows(doc, team)
			doc.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(title="Customer sales team sync failed", message=frappe.get_traceback())


# --------------------------------------------------------------------------
# Customer assignment
# --------------------------------------------------------------------------

def team_payload(team: str | None) -> dict | None:
	"""The team as the UI and the snapshot need it: members, roles, shares, rate."""
	if not team or not frappe.db.exists(DOCTYPE, team):
		return None
	doc = frappe.get_cached_doc(DOCTYPE, team)
	members = [
		{
			"sales_person": row.sales_person,
			"role": row.team_role,
			"share_percentage": flt(row.share_percentage),
		}
		for row in doc.get("members") or [] if row.is_active
	]
	return {
		"team": doc.name,
		"team_name": doc.team_name,
		"sales_manager": doc.sales_manager,
		"commission_rate": flt(doc.commission_rate),
		"is_active": bool(doc.is_active),
		"effective_from": str(doc.effective_from) if doc.effective_from else None,
		"effective_to": str(doc.effective_to) if doc.effective_to else None,
		"members": members,
		"total_share": round(sum(m["share_percentage"] for m in members), 2),
		"representatives": [m for m in members if m["role"] == REPRESENTATIVE_ROLE],
	}


def _apply_team_rows(doc, team: str | None) -> None:
	"""Project the team onto ERPNext's standard sales_team child table."""
	if not doc.meta.get_field("sales_team"):
		return
	doc.set("sales_team", [])
	payload = team_payload(team)
	if not payload:
		return
	for member in payload["members"]:
		doc.append("sales_team", {
			"sales_person": member["sales_person"],
			"allocated_percentage": member["share_percentage"],
			"commission_rate": payload["commission_rate"],
		})


@frappe.whitelist(methods=["GET"])
def get_customer_sales_assignment(customer: str):
	"""The team assigned to a customer, ready for display."""
	_require_login()
	if not frappe.has_permission("Customer", "read", doc=customer):
		frappe.throw(_("You do not have access to this customer."), frappe.PermissionError)
	team = frappe.db.get_value("Customer", customer, "custom_sales_team")
	payload = team_payload(team)
	return {
		"customer": customer,
		"assigned": bool(payload),
		"assignment": payload,
		"can_manage": can_manage(),
	}


@frappe.whitelist(methods=["POST"])
def assign_customer_sales_team(customer: str, team: str | None = None):
	"""Assign (or clear) a customer's sales team. Only new documents are affected."""
	_require_manage()
	if not frappe.has_permission("Customer", "write", doc=customer):
		frappe.throw(_("You cannot edit this customer."), frappe.PermissionError)
	team = (team or "").strip()
	if team and not frappe.db.exists(DOCTYPE, team):
		frappe.throw(_("Invalid sales team: {0}").format(team), frappe.ValidationError)
	if team and not frappe.db.get_value(DOCTYPE, team, "is_active"):
		frappe.throw(_("{0} is not active.").format(team), frappe.ValidationError)

	doc = frappe.get_doc("Customer", customer)
	doc.custom_sales_team = team or None
	_apply_team_rows(doc, team or None)
	doc.save()
	return {
		"customer": customer,
		"assignment": team_payload(team or None),
		# Stated plainly so the UI can warn the user.
		"note": _("Existing submitted documents keep the team they were raised with."),
	}


@frappe.whitelist(methods=["GET"])
def search_sales_persons(txt: str = "", limit: int = 20):
	"""Sales Person options for the team form."""
	_require_read()
	limit = min(max(cint(limit) or 20, 1), 50)
	filters = {"enabled": 1} if frappe.get_meta("Sales Person").get_field("enabled") else {}
	or_filters = {"name": ["like", f"%{txt}%"], "sales_person_name": ["like", f"%{txt}%"]} if txt else None
	rows = frappe.get_list(
		"Sales Person", filters=filters, or_filters=or_filters,
		fields=["name", "sales_person_name"], limit_page_length=limit, order_by="name asc",
	)
	return [{"value": r["name"], "label": r.get("sales_person_name") or r["name"]} for r in rows]


# --------------------------------------------------------------------------
# Transaction snapshot
# --------------------------------------------------------------------------

def build_snapshot(customer: str) -> dict | None:
	"""The values to freeze onto a document raised for this customer now."""
	team = frappe.db.get_value("Customer", customer, "custom_sales_team")
	payload = team_payload(team)
	if not payload:
		return None
	return {
		**payload,
		"source_customer": customer,
		"captured_on": nowdate(),
	}


def apply_snapshot(doc, customer: str | None = None) -> None:
	"""Freeze the customer's current team onto a document. Called once, at creation."""
	if not doc.meta.get_field("custom_sales_team_snapshot"):
		return
	if doc.get("custom_sales_team_snapshot"):
		return   # already frozen; never re-read the master
	snapshot = build_snapshot(customer or doc.get("customer"))
	if not snapshot:
		return
	doc.custom_sales_team = snapshot["team"]
	doc.custom_sales_team_name = snapshot["team_name"]
	doc.custom_sales_manager = snapshot["sales_manager"]
	doc.custom_team_commission_rate = snapshot["commission_rate"]
	doc.custom_sales_team_snapshot = json.dumps(snapshot, sort_keys=True)


def stamp_sales_document(doc, method=None):
	"""Document hook: snapshot on first save, and carry forward on mapped documents."""
	if not doc.meta.get_field("custom_sales_team_snapshot"):
		return
	if doc.get("custom_sales_team_snapshot"):
		return
	# Delivery Notes and Invoices inherit from their Sales Order rather than
	# re-reading the customer, so the whole chain shares one snapshot.
	inherited = _snapshot_from_source(doc)
	if inherited:
		doc.custom_sales_team = inherited.get("team")
		doc.custom_sales_team_name = inherited.get("team_name")
		doc.custom_sales_manager = inherited.get("sales_manager")
		doc.custom_team_commission_rate = flt(inherited.get("commission_rate"))
		doc.custom_sales_team_snapshot = json.dumps(inherited, sort_keys=True)
		return
	apply_snapshot(doc)


def _snapshot_from_source(doc) -> dict | None:
	orders = set()
	for row in doc.get("items") or []:
		for fieldname in ("against_sales_order", "sales_order"):
			value = row.get(fieldname)
			if value:
				orders.add(value)
	for order in sorted(orders):
		raw = frappe.db.get_value("Sales Order", order, "custom_sales_team_snapshot")
		if raw:
			try:
				return json.loads(raw)
			except ValueError:
				continue
	return None


@frappe.whitelist(methods=["GET"])
def get_document_sales_team(doctype: str, name: str):
	"""The frozen team for a transaction, for the detail pages."""
	_require_login()
	if doctype not in ("Sales Order", "Delivery Note", "Sales Invoice"):
		frappe.throw(_("Unsupported document type."), frappe.ValidationError)
	if not frappe.has_permission(doctype, "read", doc=name):
		frappe.throw(_("You do not have access to this document."), frappe.PermissionError)
	raw = frappe.db.get_value(doctype, name, "custom_sales_team_snapshot")
	if not raw:
		return {"doctype": doctype, "name": name, "assigned": False, "assignment": None}
	try:
		snapshot = json.loads(raw)
	except ValueError:
		return {"doctype": doctype, "name": name, "assigned": False, "assignment": None}
	return {"doctype": doctype, "name": name, "assigned": True, "assignment": snapshot,
	        "is_snapshot": True}
