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
from frappe.utils import cint, flt, now_datetime, nowdate

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
		"company": doc.get("restrict_to_company") or "",
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
	doc.restrict_to_company = (data.get("company") or "").strip() or None
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
		"company": doc.get("restrict_to_company") or None,
		"is_active": bool(doc.is_active),
		"effective_from": str(doc.effective_from) if doc.effective_from else None,
		"effective_to": str(doc.effective_to) if doc.effective_to else None,
		"members": members,
		"total_share": round(sum(m["share_percentage"] for m in members), 2),
		"representatives": [m for m in members if m["role"] == REPRESENTATIVE_ROLE],
	}


def _apply_team_rows(doc, team: str | None) -> None:
	"""Project the team onto ERPNext's standard sales_team child table.

	The row's own `commission_rate` is deliberately left alone: it is read-only and
	`fetch_from: sales_person.commission_rate`, so it carries the sales person's own
	rate. Writing the team rate into it is silently overwritten on save.
	"""
	if not doc.meta.get_field("sales_team"):
		return
	doc.set("sales_team", [])
	payload = team_payload(team)
	if not payload:
		return
	for member, share in zip(payload["members"], _balanced_shares(payload["members"])):
		doc.append("sales_team", {
			"sales_person": member["sales_person"],
			"allocated_percentage": share,
		})


@frappe.whitelist(methods=["GET"])
def get_customer_sales_assignment(customer: str):
	"""The team assigned to a customer, ready for display."""
	_require_login()
	if not frappe.has_permission("Customer", "read", doc=customer):
		frappe.throw(_("You do not have access to this customer."), frappe.PermissionError)
	team = frappe.db.get_value("Customer", customer, "custom_sales_team")
	payload = team_payload(team)
	warnings = []
	if not payload:
		warnings.append(_("No sales team is assigned to this customer. "
		                  "The order will carry no commission split."))
	elif not payload["is_active"]:
		warnings.append(_("{0} is no longer active. Choose another team before "
		                  "raising a new order.").format(payload["team_name"] or team))
	return {
		"customer": customer,
		"assigned": bool(payload),
		"assignment": payload,
		"can_manage": can_manage(),
		"can_override": can_override(),
		"warnings": warnings,
		"source": SOURCE_CUSTOMER,
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
def search_sales_teams(query: str = "", company: str = "", active_only: str = "1", limit: int = 20):
	"""Type-ahead for the team pickers. Only teams usable for the given company."""
	_require_read()
	limit = min(max(cint(limit) or 20, 1), 50)
	filters = {}
	if cint(active_only or 0):
		filters["is_active"] = 1
	or_filters = None
	if query:
		like = f"%{query.strip()}%"
		or_filters = {"team_name": ["like", like], "name": ["like", like]}
	rows = frappe.get_list(
		DOCTYPE, filters=filters, or_filters=or_filters,
		fields=["name", "team_name", "sales_manager", "commission_rate", "restrict_to_company",
		        "is_active"],
		order_by="team_name asc", limit_page_length=limit,
	)
	company = (company or "").strip()
	results = []
	for row in rows:
		# A team pinned to another company must not even be offered.
		if company and row.get("restrict_to_company") and row["restrict_to_company"] != company:
			continue
		payload = team_payload(row["name"]) or {}
		results.append({
			"value": row["name"],
			"label": row.get("team_name") or row["name"],
			"team_code": row["name"],
			"sales_manager": row.get("sales_manager"),
			"commission_rate": flt(row.get("commission_rate")),
			"company": row.get("restrict_to_company") or None,
			"is_active": bool(row.get("is_active")),
			"member_count": len(payload.get("members") or []),
			"members": payload.get("members") or [],
			"total_share": payload.get("total_share", 0),
		})
	return results


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

SNAPSHOT_DOCTYPES = ("Sales Order", "Delivery Note", "Sales Invoice")
SOURCE_CUSTOMER = "Customer Default"
SOURCE_OVERRIDE = "Overridden"

# Overriding the customer's team for one transaction is a supervisor action.
OVERRIDE_ROLES = ("System Manager", "Sales Manager")


def can_override() -> bool:
	"""May the current user use a team other than the customer's default?"""
	return bool(set(frappe.get_roles()) & set(OVERRIDE_ROLES))


def _balanced_shares(members: list[dict]) -> list[float]:
	"""Percentages that total exactly 100.

	The master validator accepts 100 +/- 0.01, but ERPNext's own
	`calculate_contribution` compares the standard sales_team rows against 100.0
	exactly and throws otherwise. Three equal thirds stored as 33.33 would pass our
	check and then block the order. The residue is put on the largest share, so the
	adjustment is at most 0.01 and no money is created or lost when the pool is
	divided.
	"""
	shares = [flt(m.get("share_percentage")) for m in members]
	if not shares:
		return []
	rounded = [flt(s, 6) for s in shares]
	residue = flt(TOTAL_SHARE - sum(rounded), 6)
	if residue:
		largest = max(range(len(rounded)), key=lambda i: rounded[i])
		rounded[largest] = flt(rounded[largest] + residue, 6)
	return rounded


def _assert_team_usable(team: str, company: str | None) -> dict:
	"""A team may only be put on a *new* document when it is active and in company."""
	payload = team_payload(team)
	if not payload:
		frappe.throw(_("Invalid sales team: {0}").format(team), frappe.ValidationError)
	if not payload["is_active"]:
		frappe.throw(
			_("{0} is no longer active and cannot be used on a new document.").format(
				payload["team_name"] or team),
			frappe.ValidationError,
		)
	team_company = payload.get("company")
	if team_company and company and team_company != company:
		frappe.throw(
			_("{0} belongs to {1} and cannot be used on a {2} document.").format(
				payload["team_name"] or team, team_company, company),
			frappe.PermissionError,
		)
	return payload


def build_snapshot(customer: str, team: str | None = None) -> dict | None:
	"""The values to freeze onto a document raised for this customer now."""
	resolved = team or frappe.db.get_value("Customer", customer, "custom_sales_team")
	payload = team_payload(resolved)
	if not payload:
		return None
	return {**payload, "source_customer": customer, "captured_on": nowdate()}


def _resolve_document_team(doc) -> tuple[str | None, str | None, str, str]:
	"""Which team this document should freeze, where it came from, and why.

	Returns (team, customer_team, source, reason). The override is re-authorised
	here rather than trusted from whoever built the document, so posting straight at
	the REST API is refused exactly like the Smart Sales route is.
	"""
	customer = doc.get("customer")
	customer_team = frappe.db.get_value("Customer", customer, "custom_sales_team") if customer else None
	requested = (doc.get("custom_sales_team") or "").strip() or None
	reason = (doc.get("custom_sales_team_override_reason") or "").strip()

	if not requested or requested == customer_team:
		return customer_team, customer_team, SOURCE_CUSTOMER, ""

	# A team other than the customer's default is an override.
	if not can_override():
		frappe.throw(
			_("Only a Sales Manager can use a team other than the customer's own."),
			frappe.PermissionError,
		)
	if not reason:
		frappe.throw(
			_("Give a reason for using a team other than the customer's own."),
			frappe.ValidationError,
		)
	return requested, customer_team, SOURCE_OVERRIDE, reason


def freeze_team(doc, method=None):
	"""`before_validate`: settle the team and the split, once, and never again.

	This runs *before* the document's own validate so ERPNext's
	`calculate_commission` / `calculate_contribution` see the rate and the
	percentages and derive the eligible amount, the pool and each person's
	contribution themselves. Running it as a plain `validate` hook would be too
	late -- Frappe runs the document's own method first and the hooks after it.
	"""
	if not doc.meta.get_field("custom_sales_team_snapshot"):
		return

	if doc.get("custom_sales_team_captured_on"):
		# Already frozen. The team never moves again; only the money below follows
		# the document while it is still a draft.
		return

	inherited = _snapshot_from_source(doc)
	if inherited:
		snapshot = inherited
		source = inherited.get("source") or SOURCE_CUSTOMER
		reason = inherited.get("override_reason") or ""
		customer_team = inherited.get("customer_team")
	else:
		team, customer_team, source, reason = _resolve_document_team(doc)
		if not team:
			return
		_assert_team_usable(team, doc.get("company"))
		snapshot = build_snapshot(doc.get("customer"), team)
		if not snapshot:
			return

	members = snapshot.get("members") or []
	shares = _balanced_shares(members)

	doc.custom_sales_team = snapshot["team"]
	doc.custom_sales_team_name = snapshot["team_name"]
	doc.custom_sales_manager = snapshot["sales_manager"]
	doc.custom_team_commission_rate = flt(snapshot["commission_rate"])
	doc.custom_customer_sales_team = customer_team
	doc.custom_sales_team_source = source
	doc.custom_sales_team_override_reason = reason
	doc.custom_sales_team_captured_on = now_datetime()
	doc.custom_sales_team_captured_by = frappe.session.user

	doc.set("custom_sales_team_members", [])
	for member, share in zip(members, shares):
		doc.append("custom_sales_team_members", {
			"sales_person": member["sales_person"],
			"sales_person_name": frappe.db.get_value(
				"Sales Person", member["sales_person"], "sales_person_name") or member["sales_person"],
			"team_role": member["role"],
			"allocation_percentage": share,
		})

	# Standard ERPNext rows, so ordinary sales-person reporting keeps working. The
	# row's own commission_rate is read-only and fetched from the Sales Person, so
	# it is deliberately not written here.
	if doc.meta.get_field("sales_team"):
		doc.set("sales_team", [])
		for member, share in zip(members, shares):
			doc.append("sales_team", {
				"sales_person": member["sales_person"],
				"allocated_percentage": share,
			})
	if doc.meta.get_field("commission_rate"):
		doc.commission_rate = flt(snapshot["commission_rate"])

	snapshot = {
		**snapshot,
		"source": source,
		"override_reason": reason,
		"customer_team": customer_team,
		"balanced_shares": shares,
		"captured_by": frappe.session.user,
	}
	doc.custom_sales_team_snapshot = json.dumps(snapshot, sort_keys=True, default=str)


def price_commission(doc, method=None):
	"""`validate`, after ERPNext has worked out the pool: split it between members.

	The team and the percentages are frozen. The money is not -- while the document
	is a draft its value can still change, and the estimate has to follow it. Once
	submitted, nothing can change either.
	"""
	if not doc.meta.get_field("custom_sales_team_members"):
		return
	rows = doc.get("custom_sales_team_members") or []
	if not rows:
		return
	pool = flt(doc.get("total_commission"))
	precision = doc.precision("total_commission") or 2
	for row in rows:
		row.commission_amount = flt(pool * flt(row.allocation_percentage) / 100.0, precision)


def stamp_sales_document(doc, method=None):
	"""Kept for the existing hook name; freezing now happens in `before_validate`."""
	freeze_team(doc, method)


def guard_snapshot_after_submit(doc, method=None):
	"""A submitted document's team may not be edited in place."""
	if not doc.meta.get_field("custom_sales_team_snapshot"):
		return
	before = doc.get_doc_before_save()
	if not before:
		return
	frozen = ("custom_sales_team", "custom_sales_team_name", "custom_sales_manager",
	          "custom_team_commission_rate", "custom_sales_team_source",
	          "custom_sales_team_captured_on", "custom_sales_team_snapshot")
	for fieldname in frozen:
		if (doc.get(fieldname) or "") != (before.get(fieldname) or ""):
			frappe.throw(
				_("The sales team on a submitted document cannot be changed. "
				  "Cancel and amend it instead."),
				frappe.ValidationError,
			)


def _snapshot_from_source(doc) -> dict | None:
	"""Inherit the snapshot from whatever this document was made from.

	Delivery Notes and Invoices follow their Sales Order; a Credit Note follows the
	invoice it reverses. None of them re-read the customer or the master, so one
	frozen team runs the whole chain.
	"""
	candidates: list[tuple[str, str]] = []
	if doc.get("return_against"):
		candidates.append((doc.doctype, doc.get("return_against")))
	for row in doc.get("items") or []:
		for fieldname in ("against_sales_order", "sales_order"):
			value = row.get(fieldname)
			if value:
				candidates.append(("Sales Order", value))
		for fieldname in ("against_sales_invoice", "sales_invoice"):
			value = row.get(fieldname)
			if value:
				candidates.append(("Sales Invoice", value))
		if row.get("delivery_note"):
			candidates.append(("Delivery Note", row["delivery_note"]))

	seen = set()
	for doctype, name in candidates:
		if (doctype, name) in seen or doctype not in SNAPSHOT_DOCTYPES:
			continue
		seen.add((doctype, name))
		if not frappe.get_meta(doctype).get_field("custom_sales_team_snapshot"):
			continue
		raw = frappe.db.get_value(doctype, name, "custom_sales_team_snapshot")
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
	if doctype not in SNAPSHOT_DOCTYPES:
		frappe.throw(_("Unsupported document type."), frappe.ValidationError)
	if not frappe.db.exists(doctype, name):
		frappe.throw(_("That document does not exist."), frappe.DoesNotExistError)
	if not frappe.has_permission(doctype, "read", doc=name):
		frappe.throw(_("You do not have access to this document."), frappe.PermissionError)

	empty = {"doctype": doctype, "name": name, "assigned": False, "assignment": None,
	         "members": [], "commission": None}
	head = frappe.db.get_value(
		doctype, name,
		["custom_sales_team", "custom_sales_team_name", "custom_sales_manager",
		 "custom_team_commission_rate", "custom_customer_sales_team",
		 "custom_sales_team_source", "custom_sales_team_override_reason",
		 "custom_sales_team_captured_on", "custom_sales_team_captured_by",
		 "amount_eligible_for_commission", "total_commission", "currency", "docstatus"],
		as_dict=True,
	)
	if not head or not head.get("custom_sales_team"):
		return empty

	members = frappe.get_all(
		"Retail Sales Team Snapshot",
		filters={"parent": name, "parenttype": doctype,
		         "parentfield": "custom_sales_team_members"},
		fields=["sales_person", "sales_person_name", "team_role", "allocation_percentage",
		        "commission_amount"],
		order_by="idx asc",
	)
	return {
		"doctype": doctype,
		"name": name,
		"assigned": True,
		"is_snapshot": True,
		"assignment": {
			"team": head["custom_sales_team"],
			"team_name": head.get("custom_sales_team_name"),
			"sales_manager": head.get("custom_sales_manager"),
			"commission_rate": flt(head.get("custom_team_commission_rate")),
			"customer_team": head.get("custom_customer_sales_team"),
			"source": head.get("custom_sales_team_source") or SOURCE_CUSTOMER,
			"override_reason": head.get("custom_sales_team_override_reason") or "",
			"captured_on": str(head["custom_sales_team_captured_on"])
			if head.get("custom_sales_team_captured_on") else None,
			"captured_by": head.get("custom_sales_team_captured_by"),
			"members": members,
			"total_share": round(sum(flt(m["allocation_percentage"]) for m in members), 2),
		},
		"members": members,
		"commission": {
			"base": flt(head.get("amount_eligible_for_commission")),
			"rate": flt(head.get("custom_team_commission_rate")),
			"pool": flt(head.get("total_commission")),
			"currency": head.get("currency"),
			"status": _commission_status(doctype, head.get("docstatus")),
		},
	}


def _commission_status(doctype: str, docstatus) -> str:
	"""What the figure on this document actually means."""
	if cint(docstatus) == 2:
		return "Cancelled"
	if doctype == "Sales Invoice" and cint(docstatus) == 1:
		return "Earned"
	if cint(docstatus) == 1:
		return "Estimated"
	return "Draft"


@frappe.whitelist(methods=["GET"])
def get_sales_team_snapshot(sales_team: str = "", customer: str = ""):
	"""What *would* be frozen right now, for a preview before anything is raised."""
	_require_read()
	team = (sales_team or "").strip()
	if not team and customer:
		if not frappe.has_permission("Customer", "read", doc=customer):
			frappe.throw(_("You do not have access to this customer."), frappe.PermissionError)
		team = frappe.db.get_value("Customer", customer, "custom_sales_team")
	payload = team_payload(team) if team else None
	if not payload:
		return {"assigned": False, "assignment": None}
	shares = _balanced_shares(payload["members"])
	return {
		"assigned": True,
		"assignment": {
			**payload,
			"members": [
				{**member, "allocation_percentage": share}
				for member, share in zip(payload["members"], shares)
			],
		},
	}
