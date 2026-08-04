"""The Accountant Decision Centre: every unresolved accountant-controlled question.

Two things in this product cannot be decided by software — how the opening-stock
overstatement is corrected, and how commission becomes money. Both were previously
recorded across several documents; this module gathers them into one permission-gated
place with a single vocabulary, so an accountant sees one list rather than a hunt.

The rules that make the list trustworthy:

- **Filling fields in is not approval.** `Approved` needs evidence and a named
  accountant, checked in the DocType controller, not here.
- **Segregation is real.** The user who prepared a proposal cannot record the decision
  on it, and a System Manager cannot stand in for the accountant.
- **History is immutable.** A changed answer supersedes the old record; it never
  overwrites it.
- **Nothing here posts anything.** The Centre records answers. Posting stays behind the
  guarded preparation service and the accountant's own authorisation.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate

from my_store_ui.my_store_ui.doctype.retail_accountant_decision.retail_accountant_decision import (
	DECIDED_STATUSES,
	OPEN_STATUSES,
	POSITIVE_STATUSES,
	STATUS_APPROVED,
	STATUS_APPROVED_WITH_CHANGES,
	STATUS_IMPLEMENTED,
	STATUS_INFORMATION_REQUIRED,
	STATUS_NOT_REVIEWED,
	STATUS_REJECTED,
	STATUS_UNDER_REVIEW,
	STATUS_VERIFIED,
)

DECISION = "Retail Accountant Decision"

AREA_OPENING_STOCK = "Opening Stock Correction"
AREA_COMMISSION = "Commission Accounting"

# --------------------------------------------------------------------------
# Capability matrix -- the single place that says who may do what.
#
# Roles are listed per capability rather than per page, because the same person
# may legitimately hold several. `Retail Accountant` and `Retail Finance Verifier`
# are created by the app so that "the accountant" is a real, grantable identity
# rather than an assumption that System Manager speaks for finance.
# --------------------------------------------------------------------------

CAP_VIEW = "view_finance_decisions"
CAP_PREPARE = "prepare_finance_proposal"
CAP_RECORD = "record_accountant_decision"
CAP_APPROVE_IMPLEMENTATION = "approve_implementation"
CAP_PREPARE_DRAFT = "prepare_accounting_draft"
CAP_SUBMIT_CORRECTION = "submit_accounting_correction"
CAP_VERIFY = "verify_after_posting"

CAPABILITIES: dict[str, tuple[str, ...]] = {
	CAP_VIEW: ("System Manager", "Accounts Manager", "Accounts User",
	           "Retail Accountant", "Retail Finance Verifier"),
	CAP_PREPARE: ("System Manager", "Accounts Manager"),
	# Deliberately excludes System Manager: an administrator must not be able to
	# manufacture an accountant's approval.
	CAP_RECORD: ("Retail Accountant",),
	CAP_APPROVE_IMPLEMENTATION: ("Retail Accountant", "Accounts Manager"),
	CAP_PREPARE_DRAFT: ("System Manager", "Accounts Manager"),
	# No role holds this in this build. Submission of a real correction is an
	# accountant action performed deliberately, never an API a session can reach.
	CAP_SUBMIT_CORRECTION: (),
	CAP_VERIFY: ("Retail Accountant", "Retail Finance Verifier", "Accounts Manager"),
}

# Capabilities that must not be exercised by the same person on the same record.
SEGREGATED_PAIRS = ((CAP_PREPARE, CAP_RECORD),)


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _roles(user: str | None = None) -> set[str]:
	return set(frappe.get_roles(user or frappe.session.user))


def has_capability(capability: str, user: str | None = None) -> bool:
	allowed = CAPABILITIES.get(capability, ())
	return bool(allowed) and bool(_roles(user) & set(allowed))


def _require_capability(capability: str) -> None:
	_require_login()
	if not has_capability(capability):
		frappe.throw(
			_("You do not hold the permission to {0}.").format(
				capability.replace("_", " ")),
			frappe.PermissionError,
		)


def capability_report(user: str | None = None) -> dict:
	"""What the current user may do. Drives the UI without becoming the boundary."""
	return {c: has_capability(c, user) for c in CAPABILITIES}


# --------------------------------------------------------------------------
# The catalogue of questions
#
# Every question an accountant must answer before this product may move money.
# The catalogue is data so the Centre can show the full set including the ones
# nobody has looked at yet -- an unasked question is the dangerous kind.
# --------------------------------------------------------------------------

CATALOGUE = (
	{
		"area": AREA_OPENING_STOCK,
		"topic": "Opening stock correction: account pair",
		"question": "Which accounts carry the reclassification?",
		"proposal": "Dr Stock Adjustment (Expense) / Cr Opening Balance Equity (Equity)",
		"why": "Three Material Receipt Stock Entries credited opening inventory value to "
		       "the Stock Adjustment expense account, understating cost and inflating profit.",
	},
	{
		"area": AREA_OPENING_STOCK,
		"topic": "Opening stock correction: amount",
		"question": "Is the measured overstatement the amount to correct?",
		"proposal": "LKR 11,820,700.00 (measured from GL, not typed in)",
		"why": "The figure is re-measured from the ledger at inspect time and the "
		       "correction refuses to run if the ledger no longer agrees with it.",
	},
	{
		"area": AREA_OPENING_STOCK,
		"topic": "Opening stock correction: posting date",
		"question": "On what date is the correction posted?",
		"proposal": "2025-07-01 (the opening date)",
		"why": "Posting on the opening date keeps the correction out of trading results "
		       "for the period. An accountant may prefer the current period instead.",
	},
	{
		"area": AREA_OPENING_STOCK,
		"topic": "Opening stock correction: authorisation to post",
		"question": "Is the correction authorised to be submitted?",
		"proposal": "Not proposed. Submission is an accountant action.",
		"why": "No automated process submits this entry. This record is the authorisation "
		       "itself and stays unapproved until an accountant signs it.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: earning trigger",
		"question": "When is commission earned?",
		"proposal": "Not proposed — invoicing and collection give materially different "
		            "liabilities and the choice is the accountant's.",
		"why": "Earning on invoicing recognises a liability before cash arrives; earning "
		       "on collection defers it. This drives every subsequent figure.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: calculation basis",
		"question": "What amount is commission calculated on?",
		"proposal": "Not proposed. Gross Profit additionally exposes cost prices.",
		"why": "Net total, net of discount, excluding tax, collected amount and gross "
		       "profit all give different answers on the same invoice.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: expense account",
		"question": "Which expense account carries commission cost?",
		"proposal": "Not proposed. Guessing an account misstates the P&L.",
		"why": "The account determines where the cost appears in the P&L and how it is "
		       "reported. There is no safe default.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: payable account",
		"question": "Which liability account carries unpaid commission?",
		"proposal": "Not proposed.",
		"why": "Determines how the obligation appears on the balance sheet until paid.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: payee party type",
		"question": "What is a commission recipient, in accounting terms?",
		"proposal": "Not proposed — Employee and Supplier have different tax and payroll "
		            "consequences.",
		"why": "Employee routes through payroll and withholding; Supplier routes through "
		       "purchase and may need a different tax treatment.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: payout document type",
		"question": "Which document type pays commission?",
		"proposal": "Not proposed. Journal Entry, Payment Entry, Expense Claim and "
		            "payroll component are compared in the decision package.",
		"why": "Each option differs in payment support, withholding support, "
		       "reconciliation and cancellation behaviour.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: payout cycle",
		"question": "How often is commission paid?",
		"proposal": "Not proposed.",
		"why": "Sets the period boundary that every statement and carry-forward uses.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: withholding",
		"question": "Is tax withheld at payout, and at what rate?",
		"proposal": "Not proposed. No rate is ever defaulted.",
		"why": "A withheld rate that nobody approved would be applied to real payments.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: tax treatment",
		"question": "How is commission treated for tax reporting?",
		"proposal": "Not proposed.",
		"why": "Depends on the payee party type and local rules, neither of which the "
		       "software may assume.",
	},
	{
		"area": AREA_COMMISSION,
		"topic": "Commission: returns and clawback",
		"question": "What happens to commission when a sale is returned?",
		"proposal": "Not proposed.",
		"why": "Reversing before payout, deducting from the next period and raising a "
		       "payable adjustment produce different balances for the same return.",
	},
)


def _catalogue_by_topic() -> dict:
	return {row["topic"]: row for row in CATALOGUE}


# --------------------------------------------------------------------------
# Structured detail per decision
#
# Kept beside the catalogue rather than inside it so the catalogue stays
# readable as a list of questions. Each entry gives the accountant the options,
# what each option does to the books, and what goes wrong if the choice is
# guessed -- which is the part a software default would silently decide.
#
# `options` are candidates, not recommendations. Nothing here ranks them.
# --------------------------------------------------------------------------

DECISION_DETAIL: dict[str, dict] = {
	"Commission: earning trigger": {
		"field": "earning_trigger",
		"options": [
			"Sales Invoice Submission",
			"Customer Payment Collection",
			"Full Payment Collection",
			"Approved Custom Rule",
		],
		"impact": "Fixes the period in which commission expense and the matching "
		          "liability are recognised.",
		"risk": "Earning on invoicing recognises a liability for money not yet "
		        "collected; if the customer never pays, commission was accrued on a "
		        "sale that did not happen. Earning on collection defers the cost away "
		        "from the period that produced the revenue.",
	},
	"Commission: calculation basis": {
		"field": "commission_basis",
		"options": [
			"Net Total",
			"Net Total After Discount",
			"Grand Total Excluding Tax",
			"Gross Profit",
			"Collected Amount",
			"Approved Custom Basis",
		],
		"impact": "Determines the amount commission is calculated on, and therefore "
		          "every figure downstream.",
		"risk": "Commission on a tax-inclusive total pays commission on tax the "
		        "business merely collects. Gross Profit additionally exposes cost "
		        "prices to whoever can see a commission statement.",
	},
	"Commission: expense account": {
		"field": "commission_expense_account",
		"options": ["An expense account chosen by the accountant"],
		"impact": "Sets where commission cost appears in the Profit and Loss.",
		"risk": "A guessed account misstates the P&L and can land commission inside "
		        "an unrelated cost line, where nobody reviewing the accounts will "
		        "recognise it.",
	},
	"Commission: payable account": {
		"field": "commission_payable_account",
		"options": ["A liability account chosen by the accountant"],
		"impact": "Sets where unpaid commission sits on the Balance Sheet until it "
		          "is settled.",
		"risk": "Without a distinct payable, commission owed is invisible on the "
		        "balance sheet and the obligation cannot be aged against the payee.",
	},
	"Commission: payee party type": {
		"field": "payee_party_type",
		"options": ["Employee", "Supplier", "Approved Other"],
		"impact": "Determines which subledger the obligation lives in and which tax "
		          "and payroll rules apply.",
		"risk": "Treating an employee as a supplier can bypass payroll withholding "
		        "entirely; treating a contractor as an employee pulls them into "
		        "payroll reporting they do not belong in.",
	},
	"Commission: payout document type": {
		"field": "accounting_document_type",
		"options": ["Journal Entry", "Payment Entry", "Expense Claim",
		            "Payroll Component", "Approved Other"],
		"impact": "Decides how the obligation is recognised and settled, and what "
		          "cancellation and reconciliation look like.",
		"risk": "Payment Entry alone skips the accrual, so commission earned in one "
		        "month and paid in the next misstates both. Expense Claim describes "
		        "earnings as a reimbursement and fails for non-employees. See "
		        "docs/accounting/SMJ_COMMISSION_ACCOUNTING_OPTIONS.md for the full "
		        "comparison.",
	},
	"Commission: payout cycle": {
		"field": "payout_cycle",
		"options": ["Weekly", "Fortnightly", "Monthly", "Quarterly", "Manual Period"],
		"impact": "Sets the period boundary every statement, carry-forward and "
		          "clawback calculation uses.",
		"risk": "Changing the cycle after periods exist re-cuts boundaries and makes "
		        "already-issued statements disagree with the system.",
	},
	"Commission: withholding": {
		"field": "withholding_mode",
		"options": ["No Withholding", "Fixed Percentage", "Rule Based",
		            "External Payroll"],
		"impact": "Determines what is deducted before the payee is paid.",
		"risk": "A withheld percentage nobody approved would be applied to real "
		        "payments; under-withholding creates a statutory liability for the "
		        "business, over-withholding underpays the payee.",
	},
	"Commission: tax treatment": {
		"field": None,
		"options": ["Recorded on the policy and in this decision"],
		"impact": "Determines how commission is reported for tax purposes.",
		"risk": "Depends on the payee party type and on local rules. The software "
		        "has no basis on which to assume either, and a wrong assumption is "
		        "discovered at filing.",
	},
	"Commission: returns and clawback": {
		"field": "returns_rule",
		"options": ["Reverse Before Payout", "Deduct From Next Period",
		            "Create Payable Adjustment", "Manual Review"],
		"impact": "Decides what happens to commission already earned when the "
		          "underlying sale is returned.",
		"risk": "Each option produces a different balance for the same return. "
		        "Deducting from the next period can drive a payee negative; "
		        "reversing before payout can reopen a closed period.",
	},
	"Opening stock correction: account pair": {
		"field": None,
		"options": ["Dr Stock Adjustment / Cr Opening Balance Equity",
		            "Another pair chosen by the accountant"],
		"impact": "Moves the opening inventory value out of the P&L and into equity.",
		"risk": "A different credit account changes where opening equity is reported "
		        "on the Balance Sheet.",
	},
	"Opening stock correction: amount": {
		"field": None,
		"options": ["The measured overstatement"],
		"impact": "Sets the size of the reclassification.",
		"risk": "The figure is re-measured from the ledger at run time; a correction "
		        "posted against a stale figure leaves a residue in the P&L.",
	},
	"Opening stock correction: posting date": {
		"field": None,
		"options": ["2025-07-01 (opening date)", "Current period",
		            "Another date chosen by the accountant"],
		"impact": "Decides which period absorbs the correction.",
		"risk": "Posting into a closed or already-reported period changes figures "
		        "that have been published.",
	},
	"Opening stock correction: authorisation to post": {
		"field": None,
		"options": ["Authorised", "Not authorised"],
		"impact": "This record is the authorisation itself.",
		"risk": "No automated process submits the correction. Without this record "
		        "the guarded apply path refuses.",
	},
}


def decision_detail(topic: str) -> dict:
	return DECISION_DETAIL.get(topic, {})


# --------------------------------------------------------------------------
# Reading the Centre
# --------------------------------------------------------------------------

def _existing(company: str | None) -> dict:
	"""Latest non-superseded decision per topic."""
	filters = {"superseded_by": ["is", "not set"]}
	if company:
		filters["company"] = company
	rows = frappe.get_all(
		DECISION, filters=filters, order_by="creation desc",
		fields=["name", "company", "topic_area", "topic", "status", "proposed_value",
		        "accountant_decision", "accountant_name", "accountant_user", "review_date",
		        "effective_date", "decision_comment", "rejection_reason",
		        "evidence_attachment", "evidence_reference", "prepared_by", "prepared_on",
		        "recorded_by", "recorded_on", "implemented_by", "implemented_on",
		        "implementation_reference", "verified_by", "verified_on",
		        "verification_note", "version_no"],
	)
	out: dict = {}
	for row in rows:
		out.setdefault(row["topic"], row)
	return out


def _live_policy_values(company: str | None) -> dict:
	"""What the active (or newest) policy currently holds for each decision field.

	Shown as *current value*, never as an answer. A field carrying a value because
	somebody typed it into a draft policy is not an accountant's decision, and the
	Centre is careful not to let one look like the other.
	"""
	rows = frappe.get_all(
		"Retail Commission Policy",
		filters={"company": company} if company else None,
		fields=["name", "status", "earning_trigger", "commission_basis",
		        "commission_expense_account", "commission_payable_account",
		        "payee_party_type", "accounting_document_type", "payout_cycle",
		        "withholding_mode", "returns_rule"],
		order_by="modified desc")
	if not rows:
		return {}
	active = next((r for r in rows if r.get("status") == "Active"), rows[0])
	return active


def _merge(company: str | None) -> list[dict]:
	existing = _existing(company)
	policy = _live_policy_values(company)
	merged = []
	for entry in CATALOGUE:
		record = existing.get(entry["topic"])
		detail = DECISION_DETAIL.get(entry["topic"], {})
		field = detail.get("field")
		current = policy.get(field) if field else None
		merged.append({
			"area": entry["area"],
			"topic": entry["topic"],
			"question": entry["question"],
			"system_proposal": entry["proposal"],
			"why_it_matters": entry["why"],
			"options": detail.get("options", []),
			"accounting_impact": detail.get("impact"),
			"risk": detail.get("risk"),
			"policy_field": field,
			"current_value": current or None,
			"current_value_is_a_decision": False,
			"decision": record,
			"status": (record or {}).get("status") or STATUS_NOT_REVIEWED,
			"accountant_answer": (record or {}).get("accountant_decision") or None,
			"evidence": ((record or {}).get("evidence_attachment")
			             or (record or {}).get("evidence_reference") or None),
			"effective_date": (record or {}).get("effective_date"),
			"recorded_by": (record or {}).get("recorded_by"),
			"verification_state": _verification_state(record),
			"answered": bool(record and record.get("status") in POSITIVE_STATUSES),
			"blocking": not (record and record.get("status") in POSITIVE_STATUSES),
		})
	return merged


def _verification_state(record: dict | None) -> str:
	if not record:
		return "Not verified"
	status = record.get("status")
	if status == STATUS_VERIFIED:
		return "Verified"
	if status == STATUS_IMPLEMENTED:
		return "Implemented, awaiting verification"
	if status in POSITIVE_STATUSES:
		return "Decided, not yet implemented"
	return "Not verified"


@frappe.whitelist(methods=["GET"])
def get_decision_centre(company: str = "") -> dict:
	"""Everything the Centre shows, in one call."""
	_require_capability(CAP_VIEW)
	company = company or (frappe.get_all("Company", pluck="name", limit_page_length=1)
	                      or [None])[0]
	items = _merge(company)
	by_area: dict = {}
	for item in items:
		by_area.setdefault(item["area"], []).append(item)

	answered = sum(1 for i in items if i["answered"])
	return {
		"company": company,
		"items": items,
		"by_area": by_area,
		"total": len(items),
		"answered": answered,
		"outstanding": len(items) - answered,
		"statuses": [STATUS_NOT_REVIEWED, STATUS_INFORMATION_REQUIRED, STATUS_UNDER_REVIEW,
		             STATUS_APPROVED, STATUS_REJECTED, STATUS_APPROVED_WITH_CHANGES,
		             STATUS_IMPLEMENTED, STATUS_VERIFIED],
		"capabilities": capability_report(),
		"opening_stock": _opening_stock_panel(company),
		"commission": _commission_panel(company),
		"summary": _(
			"{0} of {1} accountant decisions recorded. {2} outstanding. No accounting "
			"document is submitted by this page."
		).format(answered, len(items), len(items) - answered),
	}


def _opening_stock_panel(company: str | None) -> dict:
	"""Measured position of the opening-stock issue, read-only."""
	from my_store_ui.finance import opening_stock_correction as osc

	panel = {
		"root_cause": "Three Material Receipt Stock Entries credited opening inventory "
		              "value to the Stock Adjustment expense account.",
		"expected_amount": osc.EXPECTED_AMOUNT,
		"expected_vouchers": sorted(osc.EXPECTED_SOURCE),
		"opening_date": osc.OPENING_DATE,
		"debit_account_role": "Stock Adjustment (Expense)",
		"credit_account_role": "Opening Balance Equity (Equity)",
		"stock_quantity_impact": "None — no stock document is cancelled or re-posted.",
		"stock_valuation_impact": "None — the reclassification moves an amount between "
		                          "two accounts and touches no Stock Ledger Entry.",
		"posting_status": "Not submitted",
		"submission_route": "Accountant action only; no automated path exists.",
	}
	try:
		panel["measured"] = osc.inspect()
	except Exception as exc:  # inspect() refuses on protected/unknown sites by design
		panel["measured"] = None
		panel["measurement_note"] = str(exc)
	return panel


def _commission_panel(company: str | None) -> dict:
	"""Readiness of the commission chain, and the posting boundary."""
	policies = frappe.get_all(
		"Retail Commission Policy",
		filters={"company": company} if company else None,
		fields=["name", "policy_name", "status", "enabled", "earning_trigger",
		        "commission_basis", "commission_expense_account",
		        "commission_payable_account", "payee_party_type",
		        "accounting_document_type", "payout_cycle", "withholding_mode",
		        "returns_rule", "accountant_approval_reference"],
	)
	return {
		"policies": policies,
		"policy_count": len(policies),
		"active_policies": [p for p in policies if p.get("status") == "Active"],
		"posting_enabled": False,
		"posting_boundary": _(
			"Commission posting is disabled in this build. The payout endpoint exists, "
			"is reachable, and always refuses with the list of unapproved decisions."),
		"worked_example": {
			"eligible_base": 100000.0,
			"rate_percent": 2.0,
			"pool": 2000.0,
			"manager": 1000.0,
			"representative_1": 500.0,
			"representative_2": 500.0,
			"note": "Illustrative split used throughout the decision package.",
		},
	}


# --------------------------------------------------------------------------
# Writing decisions
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def prepare_proposal(topic: str, company: str = "", proposed_value: str = "",
                     system_evidence: str = "") -> dict:
	"""Raise the proposal an accountant will answer. Grants no authority."""
	_require_capability(CAP_PREPARE)
	entry = _catalogue_by_topic().get(topic)
	if not entry:
		frappe.throw(_("{0} is not a known accountant decision.").format(topic),
		             frappe.ValidationError)
	company = company or (frappe.get_all("Company", pluck="name", limit_page_length=1)
	                      or [None])[0]
	if not company:
		frappe.throw(_("A company is required."), frappe.ValidationError)

	open_existing = frappe.db.get_value(
		DECISION,
		{"company": company, "topic": topic, "superseded_by": ["is", "not set"],
		 "status": ["in", list(OPEN_STATUSES)]},
		"name")
	if open_existing:
		return {"name": open_existing, "created": False,
		        "message": _("A proposal for this topic is already open.")}

	doc = frappe.new_doc(DECISION)
	doc.company = company
	doc.topic_area = entry["area"]
	doc.topic = topic
	doc.status = STATUS_NOT_REVIEWED
	doc.proposed_value = proposed_value or entry["proposal"]
	doc.system_evidence = system_evidence or json.dumps(
		{"question": entry["question"], "why_it_matters": entry["why"]}, indent=1)
	doc.prepared_by = frappe.session.user
	doc.prepared_on = now_datetime()
	doc.version_no = 1
	doc.insert()
	return {"name": doc.name, "created": True,
	        "message": _("Proposal raised for accountant review.")}


@frappe.whitelist(methods=["POST"])
def move_to_review(name: str, status: str, comment: str = "") -> dict:
	"""Move an open proposal between the pre-decision stages."""
	_require_capability(CAP_PREPARE)
	if status not in (STATUS_UNDER_REVIEW, STATUS_INFORMATION_REQUIRED):
		frappe.throw(_("{0} is not a review stage.").format(status),
		             frappe.ValidationError)
	doc = frappe.get_doc(DECISION, name)
	if doc.status in DECIDED_STATUSES:
		frappe.throw(_("{0} has already been decided.").format(name),
		             frappe.ValidationError)
	doc.flags.decision_transition = True
	doc.status = status
	if comment:
		doc.decision_comment = comment
	doc.save()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist(methods=["POST"])
def record_decision(name: str, status: str, accountant_decision: str = "",
                    accountant_name: str = "", effective_date: str = "",
                    comment: str = "", rejection_reason: str = "",
                    evidence_reference: str = "") -> dict:
	"""Record what the accountant actually decided.

	Refuses when the caller is not the accountant, when the caller prepared the
	proposal, when an approval has no evidence, or when a rejection has no reason.
	"""
	_require_capability(CAP_RECORD)
	if status not in (STATUS_APPROVED, STATUS_REJECTED, STATUS_APPROVED_WITH_CHANGES):
		frappe.throw(_("{0} is not a decision.").format(status), frappe.ValidationError)

	doc = frappe.get_doc(DECISION, name)
	if doc.status in DECIDED_STATUSES:
		frappe.throw(
			_("{0} was already decided as {1}. Supersede it instead of re-deciding it.")
			.format(name, doc.status), frappe.ValidationError)
	if doc.superseded_by:
		frappe.throw(_("{0} has been superseded.").format(name), frappe.ValidationError)

	doc.flags.decision_transition = True
	doc.status = status
	doc.accountant_decision = accountant_decision
	doc.accountant_name = accountant_name
	doc.accountant_user = frappe.session.user
	doc.review_date = nowdate()
	doc.effective_date = effective_date or None
	doc.decision_comment = comment
	doc.rejection_reason = rejection_reason
	doc.evidence_reference = evidence_reference
	doc.recorded_by = frappe.session.user
	doc.recorded_on = now_datetime()
	doc.save()
	return {"name": doc.name, "status": doc.status,
	        "message": _("Decision recorded against {0}.").format(doc.topic)}


@frappe.whitelist(methods=["POST"])
def supersede_decision(name: str, reason: str = "") -> dict:
	"""Replace a decided record with a fresh proposal, keeping the original intact."""
	_require_capability(CAP_PREPARE)
	old = frappe.get_doc(DECISION, name)
	if old.superseded_by:
		frappe.throw(_("{0} has already been superseded.").format(name),
		             frappe.ValidationError)

	new = frappe.new_doc(DECISION)
	new.company = old.company
	new.topic_area = old.topic_area
	new.topic = old.topic
	new.status = STATUS_NOT_REVIEWED
	new.proposed_value = old.proposed_value
	new.system_evidence = json.dumps(
		{"supersedes": old.name, "previous_status": old.status, "reason": reason}, indent=1)
	new.prepared_by = frappe.session.user
	new.prepared_on = now_datetime()
	new.version_no = (old.version_no or 1) + 1
	new.insert()

	old.flags.decision_transition = True
	old.superseded_by = new.name
	old.save()
	return {"name": new.name, "supersedes": old.name, "version": new.version_no}


@frappe.whitelist(methods=["POST"])
def mark_implemented(name: str, implementation_reference: str = "") -> dict:
	"""Record that an approved decision has been carried out in the system."""
	_require_capability(CAP_APPROVE_IMPLEMENTATION)
	doc = frappe.get_doc(DECISION, name)
	if doc.status not in (STATUS_APPROVED, STATUS_APPROVED_WITH_CHANGES):
		frappe.throw(
			_("Only an approved decision can be implemented. {0} is {1}.").format(
				name, doc.status), frappe.ValidationError)
	doc.flags.decision_transition = True
	doc.status = STATUS_IMPLEMENTED
	doc.implemented_by = frappe.session.user
	doc.implemented_on = now_datetime()
	doc.implementation_reference = implementation_reference
	doc.save()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist(methods=["POST"])
def mark_verified(name: str, verification_note: str = "") -> dict:
	"""Record that the implemented result was checked against the ledger."""
	_require_capability(CAP_VERIFY)
	doc = frappe.get_doc(DECISION, name)
	if doc.status != STATUS_IMPLEMENTED:
		frappe.throw(
			_("Only an implemented decision can be verified. {0} is {1}.").format(
				name, doc.status), frappe.ValidationError)
	doc.flags.decision_transition = True
	doc.status = STATUS_VERIFIED
	doc.verified_by = frappe.session.user
	doc.verified_on = now_datetime()
	doc.verification_note = verification_note
	doc.save()
	return {"name": doc.name, "status": doc.status}


# --------------------------------------------------------------------------
# What downstream code asks
# --------------------------------------------------------------------------

def approved_decision(topic: str, company: str) -> dict | None:
	"""The live, positively-decided record for a topic, or None."""
	name = frappe.db.get_value(
		DECISION,
		{"company": company, "topic": topic, "superseded_by": ["is", "not set"],
		 "status": ["in", list(POSITIVE_STATUSES)]},
		"name")
	return frappe.get_doc(DECISION, name).as_dict() if name else None


def unresolved_topics(area: str, company: str) -> list[str]:
	"""Topics in an area with no recorded accountant answer."""
	out = []
	for entry in CATALOGUE:
		if entry["area"] != area:
			continue
		if not approved_decision(entry["topic"], company):
			out.append(entry["topic"])
	return out


@frappe.whitelist(methods=["GET"])
def decision_history(topic: str = "", company: str = "") -> list[dict]:
	"""Every version of a decision, including superseded ones."""
	_require_capability(CAP_VIEW)
	filters = {}
	if topic:
		filters["topic"] = topic
	if company:
		filters["company"] = company
	return frappe.get_all(
		DECISION, filters=filters, order_by="creation asc",
		fields=["name", "topic", "topic_area", "status", "version_no", "superseded_by",
		        "accountant_decision", "accountant_name", "review_date", "effective_date",
		        "prepared_by", "recorded_by", "recorded_on", "rejection_reason"])
