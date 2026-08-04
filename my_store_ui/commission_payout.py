"""Statements, payout preparation and the accounting boundary.

Everything here stops short of posting. A payout can be prepared, validated and
previewed down to the proposed debit and credit, and then it stops -- because the
decisions that make a posting correct (which expense account, which party type,
whether commission is earned on invoicing or collection, the payout cycle,
withholding and tax treatment, and the clawback rule) have not been made by anyone
qualified to make them.

`post_commission_payout` exists, is reachable, and always refuses. That is
deliberate: a missing endpoint invites someone to write a quick one, while an
endpoint that explains exactly which approvals are missing does not.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime

from my_store_ui.commission import can_see_everyone, sales_persons_for_user
from my_store_ui.commission_period import PERIOD, _has
from my_store_ui.my_store_ui.doctype.retail_commission_payout.retail_commission_payout import (
	STATUS_DRAFT,
	STATUS_READY,
	STATUS_VALIDATED,
)

PAYOUT = "Retail Commission Payout"
POLICY = "Retail Commission Policy"

PAYOUT_PREPARE_ROLES = ("System Manager", "Accounts Manager")
PAYOUT_POST_ROLES = ("System Manager", "Accounts Manager")
HISTORICAL_REVIEW_ROLES = ("System Manager", "Sales Manager", "Accounts Manager")


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require(roles, message) -> None:
	_require_login()
	if not _has(roles):
		frappe.throw(message, frappe.PermissionError)


# --------------------------------------------------------------------------
# Statements
# --------------------------------------------------------------------------

def _visible_people() -> list[str] | None:
	"""None means every member; a list restricts to the caller's own records."""
	if can_see_everyone():
		return None
	return sales_persons_for_user()


@frappe.whitelist(methods=["GET"])
def get_commission_statement(period: str, sales_person: str = ""):
	"""One member's statement for one period, filtered to who is asking."""
	_require_login()
	if not frappe.has_permission(PERIOD, "read", doc=period):
		frappe.throw(_("You do not have access to this period."), frappe.PermissionError)

	people = _visible_people()
	sales_person = (sales_person or "").strip()
	if people is not None:
		if not people:
			return {"period": period, "statements": [], "restricted": True}
		if sales_person and sales_person not in people:
			frappe.throw(
				_("You may only view your own commission statement."), frappe.PermissionError)
		if not sales_person:
			sales_person = people[0]

	doc = frappe.get_doc(PERIOD, period)
	wanted = [sales_person] if sales_person else None
	return {
		"period": _period_header(doc),
		"statements": _build_statements(doc, wanted, people),
		"restricted": people is not None,
	}


@frappe.whitelist(methods=["GET"])
def list_commission_statements(period: str):
	"""Every statement the caller may see for a period."""
	_require_login()
	if not frappe.has_permission(PERIOD, "read", doc=period):
		frappe.throw(_("You do not have access to this period."), frappe.PermissionError)
	people = _visible_people()
	if people is not None and not people:
		return {"period": period, "statements": [], "restricted": True}
	doc = frappe.get_doc(PERIOD, period)
	return {
		"period": _period_header(doc),
		"statements": _build_statements(doc, people, people),
		"restricted": people is not None,
	}


def _period_header(doc) -> dict:
	return {
		"name": doc.name, "company": doc.company, "policy": doc.policy,
		"currency": doc.currency, "status": doc.status,
		"from_date": str(doc.from_date), "to_date": str(doc.to_date),
	}


def _build_statements(doc, wanted, allowed) -> list[dict]:
	rows = doc.get("details") or []
	adjustments = frappe.get_all(
		"Retail Commission Adjustment",
		filters={"period": doc.name, "status": "Approved"},
		fields=["sales_person", "adjustment_type", "amount", "reason"], limit_page_length=0)

	by_person: dict[str, dict] = {}
	for row in rows:
		person = row.sales_person
		if wanted is not None and person not in wanted:
			continue
		if allowed is not None and person not in allowed:
			continue
		entry = by_person.setdefault(person, {
			"sales_person": person,
			"sales_person_name": row.sales_person_name or person,
			"team_role": row.team_role, "sales_team": row.sales_team,
			"opening_carry_forward": _carry_forward_in(doc, person),
			"transactions": [], "adjustment_lines": [],
			"gross_commission": 0.0, "return_reversal": 0.0, "withholding": 0.0,
			"adjustments": 0.0, "net_payable": 0.0, "paid_amount": 0.0,
		})
		entry["gross_commission"] += flt(row.gross_commission)
		entry["return_reversal"] += flt(row.return_reversal)
		entry["withholding"] += flt(row.withholding)
		entry["adjustments"] += flt(row.adjustment)
		entry["net_payable"] += flt(row.net_commission)
		entry["transactions"].append({
			"date": str(row.eligibility_date) if row.eligibility_date else None,
			"customer": row.customer, "sales_order": row.sales_order,
			"sales_invoice": row.sales_invoice, "payment_entry": row.payment_entry,
			"eligible_basis": flt(row.eligible_basis), "commission_rate": flt(row.commission_rate),
			"allocation_percentage": flt(row.allocation_percentage),
			"gross_commission": flt(row.gross_commission),
			"return_reversal": flt(row.return_reversal),
			"net_commission": flt(row.net_commission),
			"is_return": bool(row.is_return),
		})

	for adjustment in adjustments:
		entry = by_person.get(adjustment["sales_person"])
		if entry:
			entry["adjustment_lines"].append(adjustment)

	statements = []
	for entry in by_person.values():
		for key in ("gross_commission", "return_reversal", "withholding", "adjustments",
		            "net_payable"):
			entry[key] = round(entry[key], 2)
		entry["outstanding"] = round(entry["net_payable"] - entry["paid_amount"], 2)
		entry["closing_carry_forward"] = _carry_forward_out(doc, entry)
		statements.append(entry)
	return sorted(statements, key=lambda s: s["sales_person_name"])


def _carry_forward_in(doc, sales_person: str) -> float:
	"""What was held back last time because it was below the minimum payout."""
	previous = frappe.get_all(
		PERIOD,
		filters={"company": doc.company, "policy": doc.policy,
		         "to_date": ["<", doc.from_date], "status": ["!=", "Cancelled"]},
		fields=["name"], order_by="to_date desc", limit_page_length=1)
	if not previous:
		return 0.0
	rows = frappe.get_all(
		"Retail Commission Payout Line",
		filters={"parenttype": PAYOUT, "sales_person": sales_person},
		fields=["parent", "carry_forward_out"], limit_page_length=0)
	for row in rows:
		if frappe.db.get_value(PAYOUT, row["parent"], "period") == previous[0]["name"]:
			return flt(row["carry_forward_out"])
	return 0.0


def _carry_forward_out(doc, entry: dict) -> float:
	"""A balance too small to pay is carried, not lost -- when the policy says so."""
	policy = frappe.get_cached_doc(POLICY, doc.policy)
	total = flt(entry["net_payable"]) + flt(entry["opening_carry_forward"])
	minimum = flt(policy.minimum_payout_amount)
	if minimum and total < minimum and cint(policy.carry_forward_small_balance):
		return round(total, 2)
	return 0.0


# --------------------------------------------------------------------------
# Payout preparation
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def prepare_commission_payout(period: str):
	"""Group an approved period into per-member payable lines. Posts nothing."""
	_require(PAYOUT_PREPARE_ROLES, _("You cannot prepare a commission payout."))
	doc = frappe.get_doc(PERIOD, period)
	if doc.status not in ("Approved", "Payment Prepared"):
		frappe.throw(
			_("Only an approved period can be paid. {0} is {1}.").format(doc.name, doc.status),
			frappe.ValidationError,
		)

	existing = frappe.get_all(
		PAYOUT, filters={"period": period, "status": ["!=", "Cancelled"]}, pluck="name")
	if existing:
		# Idempotent: the same period never produces a second live payout.
		payout = frappe.get_doc(PAYOUT, existing[0])
	else:
		payout = frappe.new_doc(PAYOUT)
		payout.period = period

	policy = frappe.get_cached_doc(POLICY, doc.policy)
	statements = _build_statements(doc, None, None)

	payout.set("lines", [])
	for statement in statements:
		party_type, party, note = _resolve_payee(statement["sales_person"], policy)
		carry_in = flt(statement["opening_carry_forward"])
		net = flt(statement["net_payable"]) + carry_in
		carry_out = 0.0
		minimum = flt(policy.minimum_payout_amount)
		if minimum and net < minimum and cint(policy.carry_forward_small_balance):
			carry_out, net = net, 0.0
			note = (note + " " if note else "") + _(
				"Below the minimum payout; carried to the next period.")
		valid, validation_note = _validate_line(policy, party_type, party, net, note)
		payout.append("lines", {
			"sales_person": statement["sales_person"],
			"sales_person_name": statement["sales_person_name"],
			"payee_party_type": party_type or "", "party": party or "",
			"gross_commission": statement["gross_commission"],
			"reversals": statement["return_reversal"],
			"withholding": statement["withholding"],
			"adjustments": statement["adjustments"],
			"carry_forward_in": carry_in,
			"net_payable": round(net, 2),
			"carry_forward_out": round(carry_out, 2),
			"validation_status": "Valid" if valid else "Blocked",
			"validation_note": validation_note,
		})

	payout.status = STATUS_DRAFT
	payout.posting_blocked_reason = "\n".join(posting_blockers(policy))
	payout.accounting_preview = json.dumps(
		_preview_entries(payout, policy), indent=1, default=str)
	payout.save()

	if doc.status == "Approved":
		doc.db_set("status", "Payment Prepared", update_modified=False)
	return {"name": payout.name, "payout": _serialise_payout(payout)}


def _resolve_payee(sales_person: str, policy) -> tuple[str | None, str | None, str]:
	"""Who actually gets paid, per the policy's party type."""
	party_type = policy.payee_party_type
	if not party_type:
		return None, None, _("The policy has no payee party type.")
	employee = frappe.db.get_value("Sales Person", sales_person, "employee")
	if party_type == "Employee":
		if not employee:
			return party_type, None, _("{0} is not linked to an Employee.").format(sales_person)
		return party_type, employee, ""
	if party_type == "Supplier":
		supplier = frappe.db.get_value("Supplier", {"supplier_name": sales_person}, "name")
		if not supplier:
			return party_type, None, _("No Supplier matches {0}.").format(sales_person)
		return party_type, supplier, ""
	return party_type, None, _("Party resolution for {0} has not been approved.").format(party_type)


def _validate_line(policy, party_type, party, net, note) -> tuple[bool, str]:
	problems = []
	if note:
		problems.append(note)
	if not party_type:
		problems.append(_("No payee party type."))
	if not party:
		problems.append(_("No payee could be resolved."))
	if not policy.commission_expense_account:
		problems.append(_("No commission expense account."))
	if not policy.commission_payable_account:
		problems.append(_("No commission payable account."))
	if not policy.cost_center:
		problems.append(_("No cost centre."))
	if flt(net) < 0:
		problems.append(_("The net payable is negative; it needs a clawback decision."))
	return (not problems), " ".join(problems)


def posting_blockers(policy) -> list[str]:
	"""Every reason real money cannot move yet. Never empty in this build."""
	blockers = []
	missing = policy.missing_for_posting()
	if missing:
		blockers.append(_("Policy configuration is incomplete: {0}.").format(", ".join(missing)))
	if not policy.is_active():
		blockers.append(_("The policy is {0}, not Active.").format(policy.status))
	blockers.append(_(
		"Commission posting is disabled in this build. An accountant must first approve "
		"the expense account, the payable account or payment method, the payee party type, "
		"whether commission is earned on invoicing or on collection, the payout cycle, "
		"withholding, tax treatment, and the cancellation and clawback rules."))
	return blockers


def _preview_entries(payout, policy) -> dict:
	"""The accounting that *would* be produced. Nothing is created."""
	lines = [row for row in payout.get("lines") or [] if flt(row.net_payable) > 0]
	total = round(sum(flt(row.net_payable) for row in lines), 2)
	entries = []
	for row in lines:
		entries.append({
			"party_type": row.payee_party_type or None,
			"party": row.party or None,
			"debit_account": policy.commission_expense_account or None,
			"credit_account": policy.commission_payable_account or None,
			"amount": flt(row.net_payable),
			"cost_center": policy.cost_center or None,
			"reference_doctype": PERIOD,
			"reference_name": payout.period,
			"remark": f"Commission for {row.sales_person_name or row.sales_person}",
		})
	return {
		"proposed_document_type": policy.accounting_document_type or None,
		"company": payout.company,
		"currency": payout.currency,
		"total": total,
		"entry_count": len(entries),
		"entries": entries,
		"would_post": False,
		"blocked_because": posting_blockers(policy),
	}


@frappe.whitelist(methods=["GET"])
def get_commission_payout(name: str):
	_require_login()
	if not frappe.has_permission(PAYOUT, "read", doc=name):
		frappe.throw(_("You do not have access to this payout."), frappe.PermissionError)
	return {"payout": _serialise_payout(frappe.get_doc(PAYOUT, name)),
	        "can_prepare": _has(PAYOUT_PREPARE_ROLES)}


@frappe.whitelist(methods=["GET"])
def list_commission_payouts(period: str = "", company: str = "", limit: int = 50):
	_require_login()
	if not frappe.has_permission(PAYOUT, "read"):
		frappe.throw(_("You do not have access to commission payouts."), frappe.PermissionError)
	filters = {}
	if period:
		filters["period"] = period
	if company:
		filters["company"] = company
	return {
		"rows": frappe.get_list(
			PAYOUT, filters=filters,
			fields=["name", "period", "company", "currency", "status", "total_net_payable",
			        "modified"],
			order_by="modified desc",
			limit_page_length=min(max(cint(limit) or 50, 1), 200)),
		"can_prepare": _has(PAYOUT_PREPARE_ROLES),
	}


def _serialise_payout(doc) -> dict:
	try:
		preview = json.loads(doc.accounting_preview or "{}")
	except ValueError:
		preview = {}
	return {
		"name": doc.name, "period": doc.period, "company": doc.company,
		"currency": doc.currency, "status": doc.status,
		"total_net_payable": flt(doc.total_net_payable),
		"posting_blocked_reason": doc.posting_blocked_reason,
		"accounting_preview": preview,
		"lines": [
			{
				"sales_person": r.sales_person, "sales_person_name": r.sales_person_name,
				"payee_party_type": r.payee_party_type, "party": r.party,
				"gross_commission": flt(r.gross_commission), "reversals": flt(r.reversals),
				"withholding": flt(r.withholding), "adjustments": flt(r.adjustments),
				"carry_forward_in": flt(r.carry_forward_in),
				"net_payable": flt(r.net_payable),
				"carry_forward_out": flt(r.carry_forward_out),
				"validation_status": r.validation_status,
				"validation_note": r.validation_note,
			}
			for r in doc.get("lines") or []
		],
	}


@frappe.whitelist(methods=["POST"])
def validate_commission_payout(name: str):
	"""Re-check every line and move the payout to Validated when they all pass."""
	_require(PAYOUT_PREPARE_ROLES, _("You cannot validate a commission payout."))
	doc = frappe.get_doc(PAYOUT, name)
	policy = frappe.get_cached_doc(
		POLICY, frappe.db.get_value(PERIOD, doc.period, "policy"))
	blocked = [r for r in doc.get("lines") or [] if r.validation_status != "Valid"]
	payable = [r for r in doc.get("lines") or [] if flt(r.net_payable) > 0]
	doc.posting_blocked_reason = "\n".join(posting_blockers(policy))
	doc.accounting_preview = json.dumps(_preview_entries(doc, policy), indent=1, default=str)
	# Ready for Posting is only ever reachable when the policy itself permits posting,
	# which it cannot in this build.
	if not blocked and payable and policy.may_post():
		doc.status = STATUS_READY
	elif not blocked and payable:
		doc.status = STATUS_VALIDATED
	else:
		doc.status = STATUS_DRAFT
	doc.save()
	return {
		"name": doc.name, "payout": _serialise_payout(doc),
		"blocked_lines": len(blocked), "payable_lines": len(payable),
	}


@frappe.whitelist(methods=["POST"])
def post_commission_payout(name: str, confirmation: str = ""):
	"""Always refuses, and says exactly what is missing.

	Kept reachable on purpose. An absent endpoint invites someone to write a quick
	one against the ledger; an endpoint that refuses with the list of unapproved
	decisions does not.
	"""
	_require(PAYOUT_POST_ROLES, _("You cannot post a commission payout."))
	doc = frappe.get_doc(PAYOUT, name)
	policy = frappe.get_cached_doc(
		POLICY, frappe.db.get_value(PERIOD, doc.period, "policy"))
	frappe.throw(
		_("Commission posting is not enabled. {0}").format(" ".join(posting_blockers(policy))),
		frappe.ValidationError,
	)


# --------------------------------------------------------------------------
# Historical review
# --------------------------------------------------------------------------

HISTORICAL_STATUSES = ("Unreviewed", "Evidence Found", "Assigned", "No Reliable Evidence",
                       "Excluded", "Escalated")


@frappe.whitelist(methods=["GET"])
def list_historical_commission_review(status: str = "", doctype_filter: str = "",
                                      limit: int = 200):
	"""Documents raised before the feature existed, with no team evidence.

	A customer's *current* team is shown for context and is never treated as proof
	of what the team was at the time. Suggesting one would fabricate commission
	history, so the suggestion column stays empty unless real evidence exists on the
	document itself.
	"""
	_require(HISTORICAL_REVIEW_ROLES, _("You cannot review historical commission."))
	limit = min(max(cint(limit) or 200, 1), 500)

	rows = []
	for source in ("Sales Order", "Sales Invoice"):
		if doctype_filter and doctype_filter != source:
			continue
		if not frappe.has_permission(source, "read"):
			continue
		for doc in frappe.get_list(
			source,
			filters={"docstatus": 1, "custom_sales_team": ["is", "not set"]},
			fields=["name", "customer", "customer_name", "company", "grand_total",
			        "posting_date" if source == "Sales Invoice" else "transaction_date"],
			order_by="creation desc", limit_page_length=limit,
		):
			date = doc.get("posting_date") or doc.get("transaction_date")
			evidence = _historical_evidence(source, doc["name"])
			decision = _historical_decision(source, doc["name"])
			row_status = decision.get("status") or (
				"Evidence Found" if evidence["sales_persons"] else "No Reliable Evidence")
			if status and row_status != status:
				continue
			rows.append({
				"source_doctype": source,
				"source_name": doc["name"],
				"date": str(date) if date else None,
				"customer": doc["customer"],
				"customer_name": doc.get("customer_name") or doc["customer"],
				"company": doc["company"],
				"grand_total": flt(doc.get("grand_total")),
				"sales_order": evidence["sales_order"],
				"existing_sales_persons": evidence["sales_persons"],
				# Context only. Never a suggestion, and never applied automatically.
				"customer_current_team": frappe.db.get_value(
					"Customer", doc["customer"], "custom_sales_team"),
				"has_reliable_evidence": bool(evidence["sales_persons"]),
				"suggested_team": evidence["suggested_team"],
				"status": row_status,
				"reviewer": decision.get("reviewer"),
				"reviewed_on": decision.get("reviewed_on"),
				"reason": decision.get("reason"),
				"confidence": decision.get("confidence"),
			})
	return {
		"rows": rows[:limit],
		"statuses": list(HISTORICAL_STATUSES),
		"can_review": True,
		"note": _("A customer's current team is not evidence of the team a historical "
		          "document was raised with. Nothing here is assigned automatically."),
	}


def _historical_evidence(doctype: str, name: str) -> dict:
	"""The only admissible evidence: sales-person rows the document already carries."""
	people = frappe.get_all(
		"Sales Team", filters={"parent": name, "parenttype": doctype},
		fields=["sales_person", "allocated_percentage"], limit_page_length=0)
	sales_order = ""
	if doctype == "Sales Invoice":
		row = frappe.get_all(
			"Sales Invoice Item", filters={"parent": name, "sales_order": ["is", "set"]},
			fields=["sales_order"], limit_page_length=1)
		sales_order = row[0]["sales_order"] if row else ""

	suggested = ""
	if people:
		# A team is only suggested when one team's active membership exactly matches
		# the sales people already recorded on the document.
		names = {p["sales_person"] for p in people}
		for team in frappe.get_all("Retail Sales Team", pluck="name", limit_page_length=0):
			members = {
				m["sales_person"] for m in frappe.get_all(
					"Retail Sales Team Member",
					filters={"parent": team, "parenttype": "Retail Sales Team", "is_active": 1},
					fields=["sales_person"], limit_page_length=0)
			}
			if members and members == names:
				suggested = team
				break
	return {"sales_persons": people, "sales_order": sales_order, "suggested_team": suggested}


def _historical_decision(doctype: str, name: str) -> dict:
	"""A reviewer's recorded decision, stored as a Comment against the document.

	Frappe's Comment trail is the existing audit record; a second one is not
	invented, and nothing about the submitted document is edited.
	"""
	rows = frappe.get_all(
		"Comment",
		filters={"reference_doctype": doctype, "reference_name": name,
		         "comment_type": "Comment", "content": ["like", "%[commission-review]%"]},
		fields=["content", "owner", "creation"], order_by="creation desc", limit_page_length=1)
	if not rows:
		return {}
	try:
		payload = json.loads(rows[0]["content"].split("[commission-review]", 1)[1])
	except (ValueError, IndexError):
		return {}
	return {
		"status": payload.get("status"), "reason": payload.get("reason"),
		"confidence": payload.get("confidence"), "team": payload.get("team"),
		"reviewer": rows[0]["owner"], "reviewed_on": str(rows[0]["creation"]),
	}


@frappe.whitelist(methods=["POST"])
def record_historical_commission_decision(source_doctype: str, source_name: str,
                                          status: str, reason: str, team: str = "",
                                          confidence: str = ""):
	"""Record a reviewer's decision without touching the submitted document.

	Assigning a team requires evidence on the document itself. The customer's
	current team is never sufficient -- that is the whole point of the review.
	"""
	_require(HISTORICAL_REVIEW_ROLES, _("You cannot review historical commission."))
	if source_doctype not in ("Sales Order", "Sales Invoice"):
		frappe.throw(_("Unsupported document type."), frappe.ValidationError)
	if status not in HISTORICAL_STATUSES:
		frappe.throw(_("Unsupported review status."), frappe.ValidationError)
	if not (reason or "").strip():
		frappe.throw(_("Record why you reached this decision."), frappe.ValidationError)
	if not frappe.has_permission(source_doctype, "read", doc=source_name):
		frappe.throw(_("You do not have access to that document."), frappe.PermissionError)

	if status == "Assigned":
		if not team:
			frappe.throw(_("Choose the team you are assigning."), frappe.ValidationError)
		evidence = _historical_evidence(source_doctype, source_name)
		if not evidence["sales_persons"]:
			frappe.throw(
				_("{0} carries no sales-person evidence, so a team cannot be assigned to "
				  "it. The customer's current team is not evidence of what it was."
				  ).format(source_name),
				frappe.ValidationError,
			)

	payload = {"status": status, "reason": reason.strip(), "team": team or None,
	           "confidence": confidence or None}
	comment = frappe.new_doc("Comment")
	comment.comment_type = "Comment"
	comment.reference_doctype = source_doctype
	comment.reference_name = source_name
	comment.content = f"[commission-review]{json.dumps(payload)}"
	comment.insert(ignore_permissions=True)
	return {"source_name": source_name, "decision": _historical_decision(
		source_doctype, source_name)}


# --------------------------------------------------------------------------
# Dashboards
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def get_commission_dashboard(company: str = ""):
	"""One dashboard, three audiences, each shown only what they may see."""
	_require_login()
	company = (company or "").strip()
	roles = set(frappe.get_roles())
	is_manager = bool(roles & {"System Manager", "Sales Manager", "Accounts Manager"})
	is_accounts = bool(roles & {"System Manager", "Accounts Manager", "Accounts User"})

	filters = {"company": company} if company else {}
	periods = frappe.get_list(
		PERIOD, filters=filters,
		fields=["name", "status", "from_date", "to_date", "net_payable", "outstanding",
		        "gross_commission", "reversals"],
		order_by="from_date desc", limit_page_length=50) \
		if frappe.has_permission(PERIOD, "read") else []

	def total(status_list, field="net_payable"):
		return round(sum(flt(p[field]) for p in periods if p["status"] in status_list), 2)

	dashboard = {
		"company": company or None,
		"is_manager": is_manager,
		"is_accounts": is_accounts,
		"periods": {
			"awaiting_review": len([p for p in periods if p["status"] == "Under Review"]),
			"awaiting_approval": len([p for p in periods if p["status"] == "Under Review"]),
			"draft": len([p for p in periods if p["status"] in ("Draft", "Prepared")]),
			"approved": len([p for p in periods if p["status"] == "Approved"]),
			"recent": periods[:10],
		},
		"accounts": None,
		"sales": None,
		"own": None,
	}

	if is_accounts:
		payouts = frappe.get_list(
			PAYOUT, filters=filters,
			fields=["name", "status", "total_net_payable"], limit_page_length=50) \
			if frappe.has_permission(PAYOUT, "read") else []
		missing_payees = 0
		for payout in payouts:
			missing_payees += len(frappe.get_all(
				"Retail Commission Payout Line",
				filters={"parent": payout["name"], "validation_status": "Blocked"},
				limit_page_length=0))
		dashboard["accounts"] = {
			"net_payable": total(("Approved", "Payment Prepared")),
			"withholding": round(sum(flt(p.get("reversals")) for p in periods), 2),
			"payouts_prepared": len(payouts),
			"payouts_blocked": len([p for p in payouts if p["status"] != "Ready for Posting"]),
			"blocked_payout_lines": missing_payees,
			"posting_enabled": False,
		}

	if is_manager:
		unresolved = frappe.db.count(
			"Retail Commission Exception", {"severity": "Blocking",
			                                "resolution_status": ["in", ("Open", "Acknowledged")]})
		dashboard["sales"] = {
			"gross_commission": round(sum(flt(p["gross_commission"]) for p in periods), 2),
			"reversals": round(sum(flt(p["reversals"]) for p in periods), 2),
			"net_commission": round(sum(flt(p["net_payable"]) for p in periods), 2),
			"unresolved_exceptions": unresolved,
		}

	people = _visible_people()
	if people:
		rows = frappe.get_all(
			"Retail Commission Period Detail",
			filters={"sales_person": ["in", people], "parenttype": PERIOD},
			fields=["gross_commission", "return_reversal", "adjustment", "net_commission"],
			limit_page_length=0)
		dashboard["own"] = {
			"gross_commission": round(sum(flt(r["gross_commission"]) for r in rows), 2),
			"reversals": round(sum(flt(r["return_reversal"]) for r in rows), 2),
			"adjustments": round(sum(flt(r["adjustment"]) for r in rows), 2),
			"net_commission": round(sum(flt(r["net_commission"]) for r in rows), 2),
			"paid": 0.0,
			"lines": len(rows),
		}
	return dashboard
