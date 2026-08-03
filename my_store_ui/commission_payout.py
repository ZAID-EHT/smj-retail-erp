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
