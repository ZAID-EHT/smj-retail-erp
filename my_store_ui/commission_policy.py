"""Commission policy: configuration, validation and simulation.

A policy states the decisions that turn a calculated figure into money owed --
when commission is earned, on what, at what rate, into which accounts, on what
cycle, with what withholding, and what happens when a sale comes back.

None of those has a business default here. The controller keeps a policy
`Incomplete` until each is chosen, and refuses to let an incomplete policy prepare
a payout. See docs/sales/SMJ_COMMISSION_POLICY.md.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime, nowdate

from my_store_ui.my_store_ui.doctype.retail_commission_policy.retail_commission_policy import (
	CALCULATION_FIELDS,
	POSTING_FIELDS,
	STATUS_ACTIVE,
	STATUS_SUSPENDED,
)

DOCTYPE = "Retail Commission Policy"

# Who may write a policy at all.
POLICY_ADMIN_ROLES = ("System Manager", "Accounts Manager")
# Who may approve one. Deliberately narrower than "can edit".
POLICY_APPROVER_ROLES = ("System Manager", "Accounts Manager")

SIMULATION_LIMIT = 50


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_read() -> None:
	_require_login()
	if not frappe.has_permission(DOCTYPE, "read"):
		frappe.throw(_("You do not have access to commission policy."), frappe.PermissionError)


def can_manage_policy() -> bool:
	return bool(set(frappe.get_roles()) & set(POLICY_ADMIN_ROLES)) and frappe.has_permission(
		DOCTYPE, "write")


def can_approve_policy() -> bool:
	return bool(set(frappe.get_roles()) & set(POLICY_APPROVER_ROLES)) and frappe.has_permission(
		DOCTYPE, "write")


def _require_manage() -> None:
	_require_login()
	if not can_manage_policy():
		frappe.throw(
			_("Only an Accounts Manager or System Manager can change commission policy."),
			frappe.PermissionError,
		)


def active_policy(company: str) -> str | None:
	"""The one policy in force for a company today, if any."""
	rows = frappe.get_all(
		DOCTYPE,
		filters={"company": company, "status": STATUS_ACTIVE, "enabled": 1,
		         "effective_from": ["<=", nowdate()]},
		fields=["name", "effective_to"], order_by="effective_from desc", limit_page_length=0,
	)
	for row in rows:
		if not row["effective_to"] or str(row["effective_to"]) >= nowdate():
			return row["name"]
	return None


# --------------------------------------------------------------------------
# Read
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def list_commission_policies(company: str = "", status: str = "", search: str = "",
                             limit: int = 50):
	"""Every policy the caller may see, with its completeness stated plainly."""
	_require_read()
	filters = {}
	if company:
		filters["company"] = company
	if status:
		filters["status"] = status
	or_filters = {"policy_name": ["like", f"%{search}%"], "name": ["like", f"%{search}%"]} \
		if search else None
	rows = frappe.get_list(
		DOCTYPE, filters=filters, or_filters=or_filters,
		fields=["name", "policy_name", "company", "status", "enabled", "effective_from",
		        "effective_to", "earning_trigger", "commission_basis", "rate_source"],
		order_by="modified desc", limit_page_length=min(max(cint(limit) or 50, 1), 200),
	)
	for row in rows:
		doc = frappe.get_cached_doc(DOCTYPE, row["name"])
		row["complete_for_calculation"] = doc.is_complete_for_calculation()
		row["complete_for_posting"] = doc.is_complete_for_posting()
		row["may_post"] = doc.may_post()
	return {
		"rows": rows,
		"can_manage": can_manage_policy(),
		"can_approve": can_approve_policy(),
		"companies": frappe.get_list("Company", pluck="name", limit_page_length=0),
	}


@frappe.whitelist(methods=["GET"])
def get_commission_policy(name: str = ""):
	"""One policy, or the shape of a new one when the name is blank."""
	_require_read()
	if not name:
		return {
			"policy": {
				"name": None, "policy_name": "", "company": "", "currency": "",
				"status": "Draft", "enabled": False, "effective_from": nowdate(),
				"effective_to": None,
				# Every decision starts unset. There is no safe default for any of them.
				"earning_trigger": "", "commission_basis": "", "rate_source": "",
				"fixed_rate": 0.0, "payout_cycle": "", "withholding_mode": "",
				"withholding_percentage": 0.0, "returns_rule": "",
				"minimum_payout_amount": 0.0, "carry_forward_small_balance": True,
				"maximum_negative_carry_forward": 0.0, "manual_approval_threshold": 0.0,
				"accounting_document_type": "", "commission_expense_account": "",
				"commission_payable_account": "", "payee_party_type": "",
				"mode_of_payment": "", "cost_center": "",
				"accountant_approval_reference": "", "notes": "",
				"missing_for_calculation": [label for _f, label in CALCULATION_FIELDS],
				"missing_for_posting": [label for _f, label in CALCULATION_FIELDS + POSTING_FIELDS],
				"complete_for_calculation": False, "complete_for_posting": False,
				"may_post": False,
			},
			"is_new": True,
			"can_manage": can_manage_policy(),
			"can_approve": can_approve_policy(),
			"options": _options(),
		}
	if not frappe.has_permission(DOCTYPE, "read", doc=name):
		frappe.throw(_("You do not have access to this policy."), frappe.PermissionError)
	doc = frappe.get_doc(DOCTYPE, name)
	return {
		"policy": doc.summary(),
		"is_new": False,
		"can_manage": can_manage_policy(),
		"can_approve": can_approve_policy(),
		"options": _options(),
	}


def _options() -> dict:
	"""The choices, read from the doctype so the screen can never drift from it."""
	meta = frappe.get_meta(DOCTYPE)

	def select(fieldname):
		field = meta.get_field(fieldname)
		return [o for o in (field.options or "").split("\n") if o] if field else []

	return {
		"earning_trigger": select("earning_trigger"),
		"commission_basis": select("commission_basis"),
		"rate_source": select("rate_source"),
		"payout_cycle": select("payout_cycle"),
		"withholding_mode": select("withholding_mode"),
		"returns_rule": select("returns_rule"),
		"payee_party_type": select("payee_party_type"),
		"accounting_document_type": select("accounting_document_type"),
		"companies": frappe.get_list("Company", pluck="name", limit_page_length=0),
		"currencies": frappe.get_list("Currency", pluck="name", limit_page_length=0),
	}


WRITABLE = (
	"policy_name", "company", "currency", "enabled", "effective_from", "effective_to",
	"earning_trigger", "custom_rule_note", "commission_basis", "custom_basis_note",
	"rate_source", "fixed_rate", "rate_priority_note", "commission_expense_account",
	"commission_payable_account", "payee_party_type", "mode_of_payment", "cost_center",
	"accounting_document_type", "payout_cycle", "withholding_mode", "withholding_percentage",
	"returns_rule", "minimum_payout_amount", "carry_forward_small_balance",
	"maximum_negative_carry_forward", "manual_approval_threshold",
	"accountant_approval_reference", "notes",
)
# Deliberately absent from WRITABLE: status, approved_by, approved_on. They are
# derived or set by the approval endpoint, never by a client payload.


@frappe.whitelist(methods=["POST"])
def save_commission_policy(payload, name: str | None = None):
	"""Create or update a policy. Approval fields are never accepted from a payload."""
	_require_manage()
	data = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(data, dict):
		frappe.throw(_("Invalid policy details."), frappe.ValidationError)

	if name:
		if not frappe.has_permission(DOCTYPE, "write", doc=name):
			frappe.throw(_("You cannot edit this policy."), frappe.PermissionError)
		doc = frappe.get_doc(DOCTYPE, name)
	else:
		doc = frappe.new_doc(DOCTYPE)

	# Captured before anything is changed. `get_doc_before_save()` is not usable
	# here: Frappe only populates it inside save(), which is after the point the
	# comparison has to be made.
	before = {field: doc.get(field) for field in TERM_FIELDS}

	for fieldname in WRITABLE:
		if fieldname not in data:
			continue
		value = data.get(fieldname)
		if isinstance(value, str):
			value = value.strip()
		doc.set(fieldname, value)

	# Changing the terms of an approved policy withdraws the approval. Otherwise a
	# rate could be edited under a signature that was given for something else.
	if doc.get("approved_by") and _terms_changed(doc, before):
		doc.approved_by = None
		doc.approved_on = None

	doc.save()
	return {"name": doc.name, "policy": doc.summary()}


TERM_FIELDS = (
	tuple(f for f, _label in CALCULATION_FIELDS)
	+ tuple(f for f, _label in POSTING_FIELDS)
	+ ("fixed_rate", "withholding_percentage", "effective_from", "effective_to")
)


def _terms_changed(doc, before: dict) -> bool:
	return any(str(doc.get(f) or "") != str(before.get(f) or "") for f in TERM_FIELDS)


@frappe.whitelist(methods=["POST"])
def approve_commission_policy(name: str, note: str = ""):
	"""Record that a policy's terms have been signed off."""
	_require_login()
	if not can_approve_policy():
		frappe.throw(
			_("Only an Accounts Manager or System Manager can approve a commission policy."),
			frappe.PermissionError,
		)
	doc = frappe.get_doc(DOCTYPE, name)
	missing = doc.missing_for_calculation()
	if missing:
		frappe.throw(
			_("This policy is still missing: {0}.").format(", ".join(missing)),
			frappe.ValidationError,
		)
	doc.approved_by = frappe.session.user
	doc.approved_on = now_datetime()
	if note:
		doc.notes = f"{doc.notes or ''}\n[{nowdate()}] approved: {note}".strip()
	doc.save()
	return {"name": doc.name, "policy": doc.summary()}


@frappe.whitelist(methods=["POST"])
def suspend_commission_policy(name: str, reason: str = ""):
	"""Take a policy out of force without deleting the history behind it."""
	_require_manage()
	if not (reason or "").strip():
		frappe.throw(_("Give a reason for suspending the policy."), frappe.ValidationError)
	doc = frappe.get_doc(DOCTYPE, name)
	doc.enabled = 0
	doc.status = STATUS_SUSPENDED
	doc.notes = f"{doc.notes or ''}\n[{nowdate()}] suspended: {reason}".strip()
	doc.save()
	return {"name": doc.name, "policy": doc.summary()}


# --------------------------------------------------------------------------
# Inspection, validation and simulation
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["GET"])
def get_commission_policy_status(company: str = ""):
	"""Is there a policy in force, and can it do anything yet?"""
	_require_read()
	company = (company or "").strip() or frappe.defaults.get_user_default("Company")
	if not company:
		companies = frappe.get_list("Company", pluck="name", limit_page_length=1)
		company = companies[0] if companies else None
	if not company:
		return {"company": None, "has_active_policy": False, "policy": None,
		        "may_calculate": False, "may_post": False,
		        "blocked_because": [_("No company is configured.")]}

	name = active_policy(company)
	if not name:
		return {
			"company": company, "has_active_policy": False, "policy": None,
			"may_calculate": False, "may_post": False,
			"blocked_because": [_("No approved, enabled commission policy is in force "
			                      "for {0}.").format(company)],
		}
	doc = frappe.get_cached_doc(DOCTYPE, name)
	blocked = []
	if not doc.is_complete_for_posting():
		blocked.append(_("Accounting configuration is incomplete: {0}.").format(
			", ".join(doc.missing_for_posting())))
	return {
		"company": company, "has_active_policy": True, "policy": doc.summary(),
		"may_calculate": doc.is_complete_for_calculation(),
		"may_post": doc.may_post(),
		"blocked_because": blocked,
	}


@frappe.whitelist(methods=["GET"])
def inspect_commission_policy(name: str = "", company: str = ""):
	"""Everything about one policy's readiness, without changing it."""
	_require_read()
	name = (name or "").strip()
	if not name:
		company = (company or "").strip()
		name = active_policy(company) if company else None
	if not name:
		return {"found": False, "policy": None, "issues": [
			{"severity": "Blocking", "message": _("No policy to inspect.")}]}
	doc = frappe.get_cached_doc(DOCTYPE, name)
	return {"found": True, "policy": doc.summary(), "issues": _policy_issues(doc)}


@frappe.whitelist(methods=["GET"])
def validate_commission_policy(name: str):
	"""The same checks the controller applies, reported rather than thrown."""
	_require_read()
	doc = frappe.get_cached_doc(DOCTYPE, name)
	issues = _policy_issues(doc)
	return {
		"policy": doc.summary(),
		"issues": issues,
		"blocking": [i for i in issues if i["severity"] == "Blocking"],
		"valid_for_calculation": doc.is_complete_for_calculation(),
		"valid_for_posting": doc.is_complete_for_posting(),
	}


def _policy_issues(doc) -> list[dict]:
	issues = []
	for label in doc.missing_for_calculation():
		issues.append({
			"severity": "Blocking", "field": label,
			"message": _("{0} has not been chosen. There is no safe default.").format(label),
			"owner": "Accounts Manager",
		})
	posting_only = [m for m in doc.missing_for_posting() if m not in doc.missing_for_calculation()]
	for label in posting_only:
		issues.append({
			"severity": "Blocking for posting", "field": label,
			"message": _("{0} is required before any commission can be posted.").format(label),
			"owner": "Accountant",
		})
	if doc.commission_basis == "Gross Profit":
		issues.append({
			"severity": "Warning", "field": "Commission Basis",
			"message": _("Gross Profit uses purchase cost. Cost stays permission-gated, so "
			             "members without cost access cannot see how their own figure was "
			             "reached."),
			"owner": "Accounts Manager",
		})
	if doc.earning_trigger in ("Customer Payment Collection", "Full Payment Collection"):
		issues.append({
			"severity": "Warning", "field": "Commission Is Earned On",
			"message": _("Commission follows collection, so a period only includes invoices "
			             "that were actually paid within it."),
			"owner": "Accounts Manager",
		})
	if doc.withholding_mode == "External Payroll":
		issues.append({
			"severity": "Warning", "field": "Withholding",
			"message": _("Withholding is handled outside this system; the statement shows "
			             "the gross figure."),
			"owner": "Accountant",
		})
	if not doc.enabled and doc.is_complete_for_calculation():
		issues.append({
			"severity": "Warning", "field": "Enabled",
			"message": _("The policy is complete but not enabled, so it is not in force."),
			"owner": "Accounts Manager",
		})
	return issues


@frappe.whitelist(methods=["GET"])
def simulate_commission_policy(name: str, from_date: str = "", to_date: str = "",
                               limit: int = SIMULATION_LIMIT):
	"""Run a policy over real historical invoices without changing anything.

	Read-only by construction: it reads the frozen snapshots and computes in memory.
	No document is written, and no accounting entry is produced.
	"""
	_require_read()
	if not frappe.has_permission("Sales Invoice", "read"):
		frappe.throw(_("You do not have access to invoice data."), frappe.PermissionError)
	doc = frappe.get_cached_doc(DOCTYPE, name)
	limit = min(max(cint(limit) or SIMULATION_LIMIT, 1), 200)

	from my_store_ui.commission_period import collect_eligible_rows

	result = collect_eligible_rows(
		company=doc.company, policy=doc, from_date=from_date, to_date=to_date, limit=limit)
	rows = result["rows"]
	compared = _compare_with_current(rows)
	return {
		"policy": doc.summary(),
		"from_date": from_date or None,
		"to_date": to_date or None,
		"rows": rows,
		"exceptions": result["exceptions"],
		"totals": {
			"lines": len(rows),
			"gross_commission": round(sum(flt(r["gross_commission"]) for r in rows), 2),
			"return_reversal": round(sum(flt(r["return_reversal"]) for r in rows), 2),
			"withholding": round(sum(flt(r["withholding"]) for r in rows), 2),
			"net_commission": round(sum(flt(r["net_commission"]) for r in rows), 2),
		},
		"matches_current_calculation": compared["matches"],
		"differences": compared["differences"],
		"persisted": False,
	}


def _compare_with_current(rows: list[dict]) -> dict:
	"""Does the policy reproduce what the register already reports?

	A difference is not necessarily wrong -- withholding and a non-invoice earning
	trigger legitimately change the figure -- but it must be visible, not silent.
	"""
	differences = []
	for row in rows:
		gross = flt(row["gross_commission"])
		frozen = flt(row.get("frozen_commission_amount"))
		if abs(gross - frozen) > 0.01:
			differences.append({
				"sales_invoice": row["sales_invoice"],
				"sales_person": row["sales_person"],
				"frozen_on_document": frozen,
				"policy_result": gross,
				"reason": row.get("basis_note") or _("The policy basis differs from the "
				                                     "amount frozen on the document."),
			})
	return {"matches": not differences, "differences": differences[:50]}
