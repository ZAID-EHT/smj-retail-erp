"""Commission periods: preparing, reviewing, adjusting and approving a closing.

The period is where a calculation becomes a claim. Every row it holds is derived
from the immutable snapshot frozen onto the invoice, never from the Sales Team
master, so nothing that happens to a team afterwards can move a figure a period has
already recorded.

Where the policy selects an option this system has no data source for -- a
customer-specific rate, a per-category rate, rule-based withholding -- the row
raises a **blocking exception** instead of quietly substituting a different number.
An unpayable period is a better outcome than a plausible wrong one.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime, nowdate

from my_store_ui.my_store_ui.doctype.retail_commission_period.retail_commission_period import (
	LOCKED_STATUSES,
	STATUS_APPROVED,
	STATUS_CANCELLED,
	STATUS_DRAFT,
	STATUS_PREPARED,
	STATUS_REOPENED,
	STATUS_UNDER_REVIEW,
)

PERIOD = "Retail Commission Period"
ADJUSTMENT = "Retail Commission Adjustment"
SNAPSHOT_ROWS = "Retail Sales Team Snapshot"

PREPARER_ROLES = ("System Manager", "Sales Manager", "Accounts Manager")
REVIEWER_ROLES = ("System Manager", "Sales Manager", "Accounts Manager")
APPROVER_ROLES = ("System Manager", "Accounts Manager")
ADJUSTMENT_REQUEST_ROLES = ("System Manager", "Sales Manager", "Accounts Manager")
ADJUSTMENT_APPROVE_ROLES = ("System Manager", "Accounts Manager")

BLOCKING = "Blocking"
WARNING = "Warning"

MAX_INVOICES = 2000


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _has(roles) -> bool:
	return bool(set(frappe.get_roles()) & set(roles))


def _require(roles, message) -> None:
	_require_login()
	if not _has(roles):
		frappe.throw(message, frappe.PermissionError)


def _require_read() -> None:
	_require_login()
	if not frappe.has_permission(PERIOD, "read"):
		frappe.throw(_("You do not have access to commission periods."), frappe.PermissionError)


# --------------------------------------------------------------------------
# Eligibility, basis, rate and withholding
# --------------------------------------------------------------------------

def _exception(kind, severity, source_doctype, source_name, description, owner, action):
	return {
		"exception_type": kind, "severity": severity, "source_doctype": source_doctype,
		"source_name": source_name, "description": description, "owner_role": owner,
		"recommended_action": action, "resolution_status": "Open",
	}


def _paid_fraction(invoice: dict) -> float:
	"""How much of this invoice has actually been collected, as a fraction."""
	total = flt(invoice.get("base_grand_total"))
	if total <= 0:
		return 0.0
	outstanding = flt(invoice.get("outstanding_amount"))
	return max(0.0, min(1.0, (total - outstanding) / total))


def _resolve_basis(invoice: dict, policy, exceptions: list) -> tuple[float, str]:
	"""The amount the commission is worked out on, per the policy's chosen basis."""
	basis = policy.commission_basis
	eligible = flt(invoice.get("amount_eligible_for_commission"))

	if basis == "Net Total":
		return flt(invoice.get("base_net_total")), "Net total before document discount."
	if basis == "Net Total After Discount":
		return eligible, "ERPNext's own eligible amount: item net amounts, after discount."
	if basis == "Grand Total Excluding Tax":
		return (flt(invoice.get("base_grand_total"))
		        - flt(invoice.get("base_total_taxes_and_charges"))), "Grand total less tax."
	if basis == "Collected Amount":
		return eligible * _paid_fraction(invoice), "The collected share of the eligible amount."
	if basis == "Gross Profit":
		profit = _gross_profit(invoice, exceptions)
		return profit, "Net amount less incoming cost."
	if basis == "Approved Custom Basis":
		exceptions.append(_exception(
			"Custom basis not implemented", BLOCKING, "Sales Invoice", invoice["name"],
			_("The policy uses an approved custom basis, which has no calculation here yet."),
			"Accounts Manager", _("Implement the approved basis, or choose a standard one.")))
		return 0.0, "Custom basis; not calculable."
	exceptions.append(_exception(
		"Commission basis not set", BLOCKING, "Sales Invoice", invoice["name"],
		_("The policy has no commission basis."), "Accounts Manager",
		_("Choose a commission basis on the policy.")))
	return 0.0, "No basis chosen."


def _gross_profit(invoice: dict, exceptions: list) -> float:
	"""Net amount less incoming cost, read from the invoice's own item rows.

	Cost stays permission-gated: this runs server-side and only the resulting
	commission figure ever reaches a member, never the cost itself.
	"""
	rows = frappe.get_all(
		"Sales Invoice Item", filters={"parent": invoice["name"]},
		fields=["base_net_amount", "incoming_rate", "stock_qty"], limit_page_length=0)
	if not rows:
		return 0.0
	if not any(flt(r.get("incoming_rate")) for r in rows):
		exceptions.append(_exception(
			"No cost recorded", WARNING, "Sales Invoice", invoice["name"],
			_("No incoming rate is recorded, so gross profit equals the net amount."),
			"Accounts Manager", _("Confirm valuation is posted for these items.")))
	return flt(sum(
		flt(r.get("base_net_amount")) - flt(r.get("incoming_rate")) * flt(r.get("stock_qty"))
		for r in rows), 2)


def _resolve_rate(invoice: dict, policy, exceptions: list) -> float:
	"""The team commission rate to apply, per the policy's chosen source."""
	source = policy.rate_source
	frozen = flt(invoice.get("custom_team_commission_rate"))

	if source == "Sales Team Rate":
		if not frozen:
			exceptions.append(_exception(
				"Missing commission rate", BLOCKING, "Sales Invoice", invoice["name"],
				_("The team had no commission rate when this invoice was raised."),
				"Sales Manager", _("Set a rate on the team; future invoices will carry it. "
				                   "This one needs an adjustment or exclusion.")))
		return frozen
	if source == "Fixed Policy Rate":
		return flt(policy.fixed_rate)
	if source == "Approved Priority Order":
		return frozen or flt(policy.fixed_rate)
	if source in ("Customer Rate", "Product Category Rate"):
		# Deliberately not substituted with the team rate: that would pay a number
		# nobody configured, under a policy that says something else.
		exceptions.append(_exception(
			f"{source} has no data source", BLOCKING, "Sales Invoice", invoice["name"],
			_("The policy selects {0}, which is not configured anywhere in this system."
			  ).format(source),
			"Accounts Manager",
			_("Configure the rate source, or change the policy to Sales Team Rate.")))
		return 0.0
	exceptions.append(_exception(
		"Rate source not set", BLOCKING, "Sales Invoice", invoice["name"],
		_("The policy has no rate source."), "Accounts Manager",
		_("Choose a rate source on the policy.")))
	return 0.0


def _withholding(gross: float, policy, exceptions: list, source_name: str) -> float:
	"""What is held back, per the policy. Never defaulted to a percentage."""
	mode = policy.withholding_mode
	if mode in ("No Withholding", "External Payroll", ""):
		return 0.0
	if mode == "Fixed Percentage":
		return flt(gross * flt(policy.withholding_percentage) / 100.0, 2)
	if mode == "Rule Based":
		exceptions.append(_exception(
			"Withholding rules not configured", BLOCKING, "Sales Invoice", source_name,
			_("The policy uses rule-based withholding, and no rules exist."),
			"Accountant", _("Define the rules, or choose a fixed percentage.")))
		return 0.0
	return 0.0


def _eligible_invoices(company: str, policy, from_date: str, to_date: str, limit: int):
	"""The invoices in scope, according to the policy's earning trigger."""
	filters = {"docstatus": 1, "company": company, "custom_sales_team": ["is", "set"]}
	if from_date and to_date:
		filters["posting_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["posting_date"] = [">=", from_date]
	elif to_date:
		filters["posting_date"] = ["<=", to_date]

	invoices = frappe.get_list(
		"Sales Invoice", filters=filters,
		fields=["name", "posting_date", "customer", "customer_name", "company", "currency",
		        "custom_sales_team", "custom_sales_team_name", "custom_team_commission_rate",
		        "amount_eligible_for_commission", "base_net_total", "base_grand_total",
		        "base_total_taxes_and_charges", "total_commission", "outstanding_amount",
		        "is_return", "return_against"],
		order_by="posting_date asc, name asc",
		limit_page_length=min(max(cint(limit) or MAX_INVOICES, 1), MAX_INVOICES),
	)

	trigger = policy.earning_trigger
	if trigger in ("Sales Invoice Submission", "", None):
		return invoices
	kept = []
	for invoice in invoices:
		fraction = _paid_fraction(invoice)
		if trigger == "Full Payment Collection" and fraction < 1.0:
			continue
		if trigger == "Customer Payment Collection" and fraction <= 0:
			continue
		invoice["_paid_fraction"] = fraction
		kept.append(invoice)
	return kept


def collect_eligible_rows(company: str, policy, from_date: str = "", to_date: str = "",
                          limit: int = MAX_INVOICES) -> dict:
	"""Every member row a period would hold, plus everything that is wrong.

	Pure computation: reads frozen snapshots and returns dicts. It writes nothing, so
	the same function backs both the simulation and the real preparation, and the two
	cannot drift apart.
	"""
	exceptions: list[dict] = []
	invoices = _eligible_invoices(company, policy, from_date, to_date, limit)
	if not invoices:
		return {"rows": [], "exceptions": exceptions}

	names = [i["name"] for i in invoices]
	members: dict[str, list] = {}
	for row in frappe.get_all(
		SNAPSHOT_ROWS,
		filters={"parent": ["in", names], "parenttype": "Sales Invoice",
		         "parentfield": "custom_sales_team_members"},
		fields=["parent", "sales_person", "sales_person_name", "team_role",
		        "allocation_percentage", "commission_amount"],
		order_by="parent, idx", limit_page_length=0,
	):
		members.setdefault(row["parent"], []).append(row)

	orders: dict[str, str] = {}
	for row in frappe.get_all(
		"Sales Invoice Item", filters={"parent": ["in", names], "sales_order": ["is", "set"]},
		fields=["parent", "sales_order"], order_by="parent, idx", limit_page_length=0,
	):
		orders.setdefault(row["parent"], row["sales_order"])

	rows: list[dict] = []
	for invoice in invoices:
		people = members.get(invoice["name"])
		if not people:
			exceptions.append(_exception(
				"Missing team snapshot", BLOCKING, "Sales Invoice", invoice["name"],
				_("The invoice records a team but has no member rows."), "Sales Manager",
				_("Investigate the document; it cannot be paid on as it stands.")))
			continue

		share_total = round(sum(flt(p["allocation_percentage"]) for p in people), 2)
		if abs(share_total - 100.0) > 0.01:
			exceptions.append(_exception(
				"Allocation does not total 100%", BLOCKING, "Sales Invoice", invoice["name"],
				_("The frozen allocation totals {0}%.").format(share_total), "Sales Manager",
				_("Exclude the row, or correct it with an approved adjustment.")))

		basis, basis_note = _resolve_basis(invoice, policy, exceptions)
		rate = _resolve_rate(invoice, policy, exceptions)
		pool = flt(basis * rate / 100.0, 2)
		is_return = bool(cint(invoice.get("is_return")))

		for person in people:
			if not person.get("sales_person"):
				exceptions.append(_exception(
					"Missing team member", BLOCKING, "Sales Invoice", invoice["name"],
					_("A snapshot row has no sales person."), "Sales Manager",
					_("Investigate the document.")))
				continue
			allocation = flt(person["allocation_percentage"])
			gross = flt(pool * allocation / 100.0, 2)
			reversal = gross if is_return else 0.0
			gross_positive = 0.0 if is_return else gross
			withheld = _withholding(gross_positive, policy, exceptions, invoice["name"])
			net = flt(gross - withheld, 2)
			rows.append({
				"sales_person": person["sales_person"],
				"sales_person_name": person.get("sales_person_name") or person["sales_person"],
				"team_role": person.get("team_role"),
				"sales_team": invoice["custom_sales_team"],
				"customer": invoice["customer"],
				"customer_name": invoice.get("customer_name"),
				"sales_invoice": invoice["name"],
				"sales_order": orders.get(invoice["name"], ""),
				"payment_entry": "",
				"eligibility_date": str(invoice["posting_date"]),
				"is_return": is_return,
				"eligible_basis": flt(basis, 2),
				"commission_rate": rate,
				"gross_pool": pool,
				"allocation_percentage": allocation,
				"gross_commission": gross_positive,
				"return_reversal": reversal,
				"withholding": withheld,
				"adjustment": 0.0,
				"net_commission": net,
				"row_status": "Reversed" if is_return else "Eligible",
				"source_key": f"{invoice['name']}::{person['sales_person']}",
				"basis_note": basis_note,
				"frozen_commission_amount": flt(person.get("commission_amount")),
			})
	return {"rows": rows, "exceptions": exceptions}


# --------------------------------------------------------------------------
# Period lifecycle
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def list_commission_periods(company: str = "", status: str = "", limit: int = 50):
	"""Every period the caller may see."""
	_require_read()
	filters = {}
	if company:
		filters["company"] = company
	if status:
		filters["status"] = status
	rows = frappe.get_list(
		PERIOD, filters=filters,
		fields=["name", "company", "policy", "from_date", "to_date", "status", "currency",
		        "gross_commission", "reversals", "withholding", "adjustments",
		        "net_payable", "paid_amount", "outstanding", "modified"],
		order_by="from_date desc, name desc",
		limit_page_length=min(max(cint(limit) or 50, 1), 200),
	)
	return {
		"rows": rows,
		"can_prepare": _has(PREPARER_ROLES),
		"can_review": _has(REVIEWER_ROLES),
		"can_approve": _has(APPROVER_ROLES),
		"companies": frappe.get_list("Company", pluck="name", limit_page_length=0),
	}


@frappe.whitelist(methods=["GET"])
def get_commission_period(name: str):
	"""One period with its rows, exceptions, adjustments and audit trail."""
	_require_read()
	if not frappe.db.exists(PERIOD, name):
		frappe.throw(_("That commission period does not exist."), frappe.DoesNotExistError)
	if not frappe.has_permission(PERIOD, "read", doc=name):
		frappe.throw(_("You do not have access to this period."), frappe.PermissionError)
	doc = frappe.get_doc(PERIOD, name)
	policy = frappe.get_cached_doc("Retail Commission Policy", doc.policy) if doc.policy else None
	return {
		"period": _serialise_period(doc),
		"policy": policy.summary() if policy else None,
		"adjustments": _period_adjustments(name),
		"can_prepare": _has(PREPARER_ROLES) and not doc.is_locked(),
		"can_review": _has(REVIEWER_ROLES),
		"can_approve": _has(APPROVER_ROLES),
		"can_request_adjustment": _has(ADJUSTMENT_REQUEST_ROLES),
		"can_approve_adjustment": _has(ADJUSTMENT_APPROVE_ROLES),
		"blocking_exceptions": len(doc.blocking_exceptions()),
	}


def _serialise_period(doc) -> dict:
	return {
		"name": doc.name, "company": doc.company, "policy": doc.policy,
		"currency": doc.currency, "status": doc.status,
		"from_date": str(doc.from_date), "to_date": str(doc.to_date),
		"gross_commission": flt(doc.gross_commission), "reversals": flt(doc.reversals),
		"withholding": flt(doc.withholding), "adjustments": flt(doc.adjustments),
		"net_payable": flt(doc.net_payable), "paid_amount": flt(doc.paid_amount),
		"outstanding": flt(doc.outstanding),
		"prepared_by": doc.prepared_by,
		"prepared_on": str(doc.prepared_on) if doc.prepared_on else None,
		"reviewed_by": doc.reviewed_by,
		"reviewed_on": str(doc.reviewed_on) if doc.reviewed_on else None,
		"approved_by": doc.approved_by,
		"approved_on": str(doc.approved_on) if doc.approved_on else None,
		"decision_log": _decisions(doc),
		"details": [
			{
				"sales_person": r.sales_person, "sales_person_name": r.sales_person_name,
				"team_role": r.team_role, "sales_team": r.sales_team, "customer": r.customer,
				"sales_invoice": r.sales_invoice, "sales_order": r.sales_order,
				"payment_entry": r.payment_entry,
				"eligibility_date": str(r.eligibility_date) if r.eligibility_date else None,
				"is_return": bool(r.is_return), "eligible_basis": flt(r.eligible_basis),
				"commission_rate": flt(r.commission_rate), "gross_pool": flt(r.gross_pool),
				"allocation_percentage": flt(r.allocation_percentage),
				"gross_commission": flt(r.gross_commission),
				"return_reversal": flt(r.return_reversal), "withholding": flt(r.withholding),
				"adjustment": flt(r.adjustment), "net_commission": flt(r.net_commission),
				"row_status": r.row_status,
			}
			for r in doc.get("details") or []
		],
		"exceptions": [
			{
				"exception_type": r.exception_type, "severity": r.severity,
				"source_doctype": r.source_doctype, "source_name": r.source_name,
				"description": r.description, "owner_role": r.owner_role,
				"recommended_action": r.recommended_action,
				"resolution_status": r.resolution_status, "resolution_note": r.resolution_note,
				"resolved_by": r.resolved_by,
				"resolved_on": str(r.resolved_on) if r.resolved_on else None,
				"idx": r.idx,
			}
			for r in doc.get("exceptions") or []
		],
	}


def _decisions(doc) -> list:
	try:
		return json.loads(doc.decision_log or "[]")
	except ValueError:
		return []


def _record_decision(doc, decision: str, comment: str, previous: str, new: str) -> None:
	log = _decisions(doc)
	log.append({
		"decision": decision, "comment": comment or "", "by": frappe.session.user,
		"on": str(now_datetime()), "from_status": previous, "to_status": new,
	})
	doc.decision_log = json.dumps(log, indent=1)


@frappe.whitelist(methods=["POST"])
def create_commission_period(company: str, policy: str, from_date: str, to_date: str):
	"""Open a new closing cycle. Overlap and policy checks live in the controller."""
	_require(PREPARER_ROLES, _("You cannot open a commission period."))
	if not frappe.has_permission(PERIOD, "create"):
		frappe.throw(_("You cannot create commission periods."), frappe.PermissionError)
	policy_doc = frappe.get_cached_doc("Retail Commission Policy", policy)
	if not policy_doc.is_active():
		frappe.throw(
			_("{0} is {1}. Only an active, approved policy can open a period.").format(
				policy, policy_doc.status),
			frappe.ValidationError,
		)
	doc = frappe.new_doc(PERIOD)
	doc.company = company
	doc.policy = policy
	doc.from_date = from_date
	doc.to_date = to_date
	doc.status = STATUS_DRAFT
	doc.insert()
	return {"name": doc.name, "period": _serialise_period(doc)}


@frappe.whitelist(methods=["POST"])
def prepare_commission_period(name: str):
	"""Fill the period from the frozen snapshots. Idempotent while it is unlocked.

	Rows are rebuilt from scratch every time rather than appended to, so preparing
	twice produces exactly the same period -- and the `source_key` on each row makes
	a duplicate detectable rather than merely unlikely.
	"""
	_require(PREPARER_ROLES, _("You cannot prepare a commission period."))
	doc = frappe.get_doc(PERIOD, name)
	if not frappe.has_permission(PERIOD, "write", doc=name):
		frappe.throw(_("You cannot change this period."), frappe.PermissionError)
	doc.assert_editable()

	policy = frappe.get_cached_doc("Retail Commission Policy", doc.policy)
	if not policy.is_active():
		frappe.throw(
			_("{0} is {1}; a period can only be prepared under an active policy.").format(
				doc.policy, policy.status),
			frappe.ValidationError,
		)

	result = collect_eligible_rows(
		company=doc.company, policy=policy, from_date=doc.from_date, to_date=doc.to_date)
	rows, exceptions = result["rows"], list(result["exceptions"])

	rows = _drop_duplicates(rows, exceptions)
	rows = _exclude_paid_elsewhere(doc, rows, exceptions)
	_apply_approved_adjustments(doc, rows)

	doc.set("details", [])
	for row in rows:
		doc.append("details", {
			k: v for k, v in row.items()
			if k not in ("basis_note", "frozen_commission_amount", "customer_name")
		})
	_merge_exceptions(doc, exceptions)

	doc.prepared_by = frappe.session.user
	doc.prepared_on = now_datetime()
	previous = doc.status
	doc.status = STATUS_PREPARED
	_record_decision(doc, "Prepared", f"{len(rows)} rows", previous, doc.status)
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc),
	        "prepared_rows": len(rows), "exceptions": len(doc.get("exceptions") or [])}


def _drop_duplicates(rows: list[dict], exceptions: list) -> list[dict]:
	"""One row per invoice per member. A repeat is reported, never silently kept."""
	seen: dict[str, dict] = {}
	for row in rows:
		key = row["source_key"]
		if key in seen:
			exceptions.append(_exception(
				"Duplicate source", BLOCKING, "Sales Invoice", row["sales_invoice"],
				_("{0} appears more than once for {1}.").format(
					row["sales_invoice"], row["sales_person"]),
				"Accounts Manager", _("Investigate before approving.")))
			continue
		seen[key] = row
	return list(seen.values())


def _exclude_paid_elsewhere(doc, rows: list[dict], exceptions: list) -> list[dict]:
	"""A row already recorded in another live period is not claimed twice."""
	if not rows:
		return rows
	keys = [r["source_key"] for r in rows]
	taken = {}
	for row in frappe.get_all(
		"Retail Commission Period Detail",
		filters={"source_key": ["in", keys], "parenttype": PERIOD,
		         "parent": ["!=", doc.name]},
		fields=["parent", "source_key"], limit_page_length=0,
	):
		status = frappe.db.get_value(PERIOD, row["parent"], "status")
		if status and status != STATUS_CANCELLED:
			taken[row["source_key"]] = row["parent"]
	if not taken:
		return rows
	kept = []
	for row in rows:
		other = taken.get(row["source_key"])
		if other:
			exceptions.append(_exception(
				"Already in another period", WARNING, "Sales Invoice", row["sales_invoice"],
				_("{0} for {1} is already included in {2}.").format(
					row["sales_invoice"], row["sales_person"], other),
				"Accounts Manager", _("Excluded here to avoid paying it twice.")))
			continue
		kept.append(row)
	return kept


def _apply_approved_adjustments(doc, rows: list[dict]) -> None:
	"""Approved adjustments land on the member's first row for the period."""
	totals: dict[str, float] = {}
	for row in frappe.get_all(
		ADJUSTMENT, filters={"period": doc.name, "status": "Approved"},
		fields=["sales_person", "amount"], limit_page_length=0,
	):
		totals[row["sales_person"]] = totals.get(row["sales_person"], 0.0) + flt(row["amount"])
	if not totals:
		return
	for row in rows:
		amount = totals.pop(row["sales_person"], None)
		if amount is None:
			continue
		row["adjustment"] = flt(amount, 2)
		row["net_commission"] = flt(flt(row["net_commission"]) + flt(amount), 2)


def _merge_exceptions(doc, exceptions: list[dict]) -> None:
	"""Keep resolutions a human already recorded; add whatever is newly wrong."""
	resolved = {
		(r.exception_type, r.source_name): r
		for r in doc.get("exceptions") or []
		if r.resolution_status in ("Resolved", "Waived")
	}
	doc.set("exceptions", [])
	for exception in exceptions:
		previous = resolved.get((exception["exception_type"], exception["source_name"]))
		if previous:
			exception = {
				**exception,
				"resolution_status": previous.resolution_status,
				"resolution_note": previous.resolution_note,
				"resolved_by": previous.resolved_by,
				"resolved_on": previous.resolved_on,
			}
		doc.append("exceptions", exception)


# --------------------------------------------------------------------------
# Exceptions, review and approval
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def resolve_commission_exception(name: str, idx: int, resolution: str, note: str = ""):
	"""Record a human decision on one exception. Never silently ignored."""
	_require(REVIEWER_ROLES, _("You cannot resolve commission exceptions."))
	if resolution not in ("Acknowledged", "Resolved", "Waived"):
		frappe.throw(_("Unsupported resolution."), frappe.ValidationError)
	if resolution == "Waived" and not (note or "").strip():
		frappe.throw(_("Waiving an exception needs a reason."), frappe.ValidationError)
	doc = frappe.get_doc(PERIOD, name)
	doc.assert_editable()
	row = next((r for r in doc.get("exceptions") or [] if cint(r.idx) == cint(idx)), None)
	if not row:
		frappe.throw(_("That exception is not on this period."), frappe.DoesNotExistError)
	row.resolution_status = resolution
	row.resolution_note = note
	row.resolved_by = frappe.session.user
	row.resolved_on = now_datetime()
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc)}


@frappe.whitelist(methods=["POST"])
def submit_period_for_review(name: str, comment: str = ""):
	_require(PREPARER_ROLES, _("You cannot send a period for review."))
	doc = frappe.get_doc(PERIOD, name)
	doc.assert_editable()
	if doc.status not in (STATUS_PREPARED, STATUS_REOPENED):
		frappe.throw(
			_("Only a prepared period can go for review. This one is {0}.").format(doc.status),
			frappe.ValidationError,
		)
	previous = doc.status
	doc.status = STATUS_UNDER_REVIEW
	doc.reviewed_by = None
	doc.reviewed_on = None
	_record_decision(doc, "Sent for review", comment, previous, doc.status)
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc)}


@frappe.whitelist(methods=["POST"])
def review_commission_period(name: str, comment: str = ""):
	"""Record that a reviewer has been through the period."""
	_require(REVIEWER_ROLES, _("You cannot review a commission period."))
	doc = frappe.get_doc(PERIOD, name)
	doc.assert_editable()
	if doc.status != STATUS_UNDER_REVIEW:
		frappe.throw(
			_("Only a period under review can be reviewed. This one is {0}.").format(doc.status),
			frappe.ValidationError,
		)
	if doc.prepared_by == frappe.session.user and not _has(("System Manager",)):
		frappe.throw(
			_("The person who prepared a period cannot also review it."),
			frappe.PermissionError,
		)
	doc.reviewed_by = frappe.session.user
	doc.reviewed_on = now_datetime()
	_record_decision(doc, "Reviewed", comment, doc.status, doc.status)
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc)}


def approval_checks(doc, policy) -> list[dict]:
	"""Everything that must be true before a period may be approved."""
	checks = []

	def add(label, ok, detail=""):
		checks.append({"check": label, "passed": bool(ok), "detail": detail})

	add(_("Policy is active and approved"), policy.is_active(), policy.status)
	add(_("Policy is complete for calculation"), policy.is_complete_for_calculation(),
	    ", ".join(policy.missing_for_calculation()))
	blocking = doc.blocking_exceptions()
	add(_("No unresolved blocking exceptions"), not blocking,
	    _("{0} unresolved").format(len(blocking)) if blocking else "")
	rows = doc.get("details") or []
	add(_("The period has rows"), bool(rows), _("{0} rows").format(len(rows)))

	expected = flt(sum(
		flt(r.gross_commission) - flt(r.withholding) + flt(r.adjustment) for r in rows), 2)
	add(_("Totals balance against the rows"), abs(expected - flt(doc.net_payable)) < 0.01,
	    f"rows={expected} period={flt(doc.net_payable)}")

	keys = [r.source_key for r in rows]
	add(_("No duplicate source rows"), len(keys) == len(set(keys)))
	add(_("Every row is traceable to an invoice"), all(r.sales_invoice for r in rows))

	per_invoice: dict[str, float] = {}
	for row in rows:
		per_invoice[row.sales_invoice] = per_invoice.get(row.sales_invoice, 0.0) + flt(
			row.allocation_percentage)
	unbalanced = [k for k, v in per_invoice.items() if abs(v - 100.0) > 0.01]
	add(_("Allocations total 100% on every invoice"), not unbalanced,
	    ", ".join(unbalanced[:3]))

	pending = frappe.get_all(
		ADJUSTMENT, filters={"period": doc.name, "status": "Requested"}, pluck="name")
	add(_("No adjustment is still awaiting approval"), not pending, ", ".join(pending[:3]))
	add(_("Withholding treatment is defined"), bool(policy.withholding_mode),
	    policy.withholding_mode or _("not set"))
	add(_("Returns rule is defined"), bool(policy.returns_rule),
	    policy.returns_rule or _("not set"))
	return checks


@frappe.whitelist(methods=["GET"])
def get_period_approval_checks(name: str):
	"""What stands between this period and approval, without approving it."""
	_require_read()
	doc = frappe.get_doc(PERIOD, name)
	policy = frappe.get_cached_doc("Retail Commission Policy", doc.policy)
	checks = approval_checks(doc, policy)
	return {
		"period": doc.name, "status": doc.status, "checks": checks,
		"failed": [c for c in checks if not c["passed"]],
		"can_approve": _has(APPROVER_ROLES) and not [c for c in checks if not c["passed"]],
	}


@frappe.whitelist(methods=["POST"])
def approve_commission_period(name: str, comment: str = ""):
	"""Approve the period. Every check must pass; none of them can be waived here."""
	_require(APPROVER_ROLES, _("Only an Accounts Manager can approve a commission period."))
	doc = frappe.get_doc(PERIOD, name)
	if doc.status != STATUS_UNDER_REVIEW:
		frappe.throw(
			_("Only a reviewed period can be approved. This one is {0}.").format(doc.status),
			frappe.ValidationError,
		)
	if doc.prepared_by == frappe.session.user and not _has(("System Manager",)):
		frappe.throw(
			_("The person who prepared a period cannot also approve it."),
			frappe.PermissionError,
		)
	policy = frappe.get_cached_doc("Retail Commission Policy", doc.policy)
	failed = [c for c in approval_checks(doc, policy) if not c["passed"]]
	if failed:
		frappe.throw(
			_("This period cannot be approved yet: {0}").format(
				"; ".join(f"{c['check']} ({c['detail']})" if c["detail"] else c["check"]
				          for c in failed)),
			frappe.ValidationError,
		)
	previous = doc.status
	doc.approved_by = frappe.session.user
	doc.approved_on = now_datetime()
	doc.status = STATUS_APPROVED
	_record_decision(doc, "Approved", comment, previous, doc.status)
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc)}


@frappe.whitelist(methods=["POST"])
def reopen_commission_period(name: str, reason: str):
	"""Unlock an approved period deliberately, with the reason on the record.

	Reopening is how a late credit note is dealt with when the policy says to reverse
	before payout. It never rewrites what the period said -- the decision log keeps
	the previous approval.
	"""
	_require(APPROVER_ROLES, _("Only an Accounts Manager can reopen a commission period."))
	if not (reason or "").strip():
		frappe.throw(_("Give a reason for reopening the period."), frappe.ValidationError)
	doc = frappe.get_doc(PERIOD, name)
	if doc.status not in (STATUS_APPROVED,):
		frappe.throw(
			_("Only an approved period can be reopened. This one is {0}.").format(doc.status),
			frappe.ValidationError,
		)
	if flt(doc.paid_amount):
		frappe.throw(
			_("{0} has already been paid in part; reopening it would contradict the "
			  "accounting. Raise an adjustment instead.").format(doc.name),
			frappe.ValidationError,
		)
	previous = doc.status
	doc.status = STATUS_REOPENED
	doc.approved_by = None
	doc.approved_on = None
	_record_decision(doc, "Reopened", reason, previous, doc.status)
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc)}


@frappe.whitelist(methods=["POST"])
def cancel_commission_period(name: str, reason: str):
	_require(APPROVER_ROLES, _("Only an Accounts Manager can cancel a commission period."))
	if not (reason or "").strip():
		frappe.throw(_("Give a reason for cancelling the period."), frappe.ValidationError)
	doc = frappe.get_doc(PERIOD, name)
	if flt(doc.paid_amount):
		frappe.throw(
			_("{0} has been paid in part and cannot be cancelled.").format(doc.name),
			frappe.ValidationError,
		)
	previous = doc.status
	doc.status = STATUS_CANCELLED
	_record_decision(doc, "Cancelled", reason, previous, doc.status)
	doc.save()
	return {"name": doc.name, "period": _serialise_period(doc)}


# --------------------------------------------------------------------------
# Adjustments
# --------------------------------------------------------------------------

def _period_adjustments(period: str) -> list[dict]:
	return frappe.get_all(
		ADJUSTMENT, filters={"period": period},
		fields=["name", "sales_person", "adjustment_type", "amount", "status", "reason",
		        "supporting_reference", "requested_by", "requested_on", "approved_by",
		        "approved_on", "decision_note"],
		order_by="creation desc", limit_page_length=0,
	)


@frappe.whitelist(methods=["POST"])
def request_commission_adjustment(period: str, sales_person: str, adjustment_type: str,
                                  amount, reason: str, supporting_reference: str = ""):
	"""Ask for a change to what a member is owed. Requesting is not approving."""
	_require(ADJUSTMENT_REQUEST_ROLES, _("You cannot request a commission adjustment."))
	doc = frappe.get_doc(PERIOD, period)
	if doc.status in (STATUS_CANCELLED,):
		frappe.throw(_("That period is cancelled."), frappe.ValidationError)
	adjustment = frappe.new_doc(ADJUSTMENT)
	adjustment.period = period
	adjustment.sales_person = sales_person
	adjustment.adjustment_type = adjustment_type
	adjustment.amount = flt(amount)
	adjustment.reason = reason
	adjustment.supporting_reference = supporting_reference
	adjustment.status = "Requested"
	adjustment.insert()
	return {"name": adjustment.name, "adjustments": _period_adjustments(period)}


@frappe.whitelist(methods=["POST"])
def approve_commission_adjustment(name: str, note: str = ""):
	"""Approve someone else's request, and recalculate the period from it."""
	_require(ADJUSTMENT_APPROVE_ROLES, _("You cannot approve a commission adjustment."))
	doc = frappe.get_doc(ADJUSTMENT, name)
	if doc.status != "Requested":
		frappe.throw(_("Only a requested adjustment can be approved."), frappe.ValidationError)
	if doc.requested_by == frappe.session.user and not _has(("System Manager",)):
		frappe.throw(
			_("You cannot approve your own adjustment request."), frappe.PermissionError)

	period = frappe.get_doc(PERIOD, doc.period)
	policy = frappe.get_cached_doc("Retail Commission Policy", period.policy)
	limit = flt(policy.manual_approval_threshold)
	if limit and abs(flt(doc.amount)) > limit and not _has(("System Manager",)):
		frappe.throw(
			_("{0} exceeds the manual approval threshold of {1} and needs higher authority."
			  ).format(abs(flt(doc.amount)), limit),
			frappe.PermissionError,
		)
	negative_limit = flt(policy.maximum_negative_carry_forward)
	if negative_limit and flt(doc.amount) < 0 and abs(flt(doc.amount)) > negative_limit \
			and not _has(("System Manager",)):
		frappe.throw(
			_("A deduction of {0} exceeds the configured guardrail of {1}.").format(
				abs(flt(doc.amount)), negative_limit),
			frappe.PermissionError,
		)

	doc.status = "Approved"
	doc.approved_by = frappe.session.user
	doc.approved_on = now_datetime()
	doc.decision_note = note
	doc.save()

	# An approved adjustment changes what is owed, so an unlocked period is rebuilt
	# from source. A locked one is left alone: history is not rewritten.
	if not period.is_locked():
		prepare_commission_period(period.name)
	return {"name": doc.name, "adjustments": _period_adjustments(doc.period),
	        "period_recalculated": not period.is_locked()}


@frappe.whitelist(methods=["POST"])
def reject_commission_adjustment(name: str, note: str):
	_require(ADJUSTMENT_APPROVE_ROLES, _("You cannot decide on a commission adjustment."))
	if not (note or "").strip():
		frappe.throw(_("Give a reason for rejecting the adjustment."), frappe.ValidationError)
	doc = frappe.get_doc(ADJUSTMENT, name)
	if doc.status != "Requested":
		frappe.throw(_("Only a requested adjustment can be rejected."), frappe.ValidationError)
	doc.status = "Rejected"
	doc.approved_by = frappe.session.user
	doc.approved_on = now_datetime()
	doc.decision_note = note
	doc.save()
	return {"name": doc.name, "adjustments": _period_adjustments(doc.period)}
