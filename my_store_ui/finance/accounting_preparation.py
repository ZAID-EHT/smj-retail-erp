"""One guarded way to prepare accounting, and no way at all to submit it.

Three kinds of accounting are waiting on an accountant in this product: the
opening-stock reclassification, commission recognition and commission payout. Each had
its own half-path, which is how a codebase ends up with three different ideas about what
"ready to post" means. This service gives them one vocabulary and one set of guards.

Modes, in the order they are meant to be used:

    inspect        read-only; what is the position and what is missing
    dry_run        build the document inside a savepoint, report it, roll back
    prepare_draft  create a real draft (docstatus 0) for an accountant to look at
    verify_draft   re-check an existing draft against the guards
    cancel_draft   delete a draft this service created

**There is no submit mode, and adding one is not a small change.** Submission of real
accounting is a deliberate act performed with the accountant's authority through the
purpose-built path for that proposal type, which has its own confirmation string. A
general "prepare anything" service that could also submit would be the single most
dangerous function in the application.

Every writing mode refuses unless: the site is allowlisted and is not site1.local, a
recent backup exists, the governing accountant decisions are recorded and positively
decided, the evidence is present, the company and accounts are right, the amount matches
what the ledger currently says, no duplicate already exists, and the caller holds the
capability. The refusals are the product; the happy path is almost incidental.
"""

from __future__ import annotations

import os
import time

import frappe
from frappe import _
from frappe.utils import flt

from my_store_ui.finance import accountant_decisions as decisions
from my_store_ui.finance import opening_stock_correction as osc

# Proposal types
OPENING_STOCK = "Opening Stock Reclassification"
COMMISSION_RECOGNITION = "Commission Recognition"
COMMISSION_PAYOUT = "Commission Payout"

PROPOSAL_TYPES = (OPENING_STOCK, COMMISSION_RECOGNITION, COMMISSION_PAYOUT)

# Modes
INSPECT = "inspect"
DRY_RUN = "dry_run"
PREPARE_DRAFT = "prepare_draft"
VERIFY_DRAFT = "verify_draft"
CANCEL_DRAFT = "cancel_draft"

MODES = (INSPECT, DRY_RUN, PREPARE_DRAFT, VERIFY_DRAFT, CANCEL_DRAFT)

# Modes that create or change anything at all.
WRITING_MODES = (PREPARE_DRAFT, CANCEL_DRAFT)

# Sites where preparation may run. site1.local is never in this set and is also
# refused explicitly, so a careless edit to the allowlist cannot expose it.
ALLOWED_SITES = {"staging.local", "financeqa.local", "freshrelease.local"}
PROTECTED_SITES = {"site1.local"}

# A backup older than this is not a backup you would want to rely on if a draft
# turned out to be wrong.
BACKUP_MAX_AGE_HOURS = 24

# The decisions that must be positively recorded before each proposal type may be
# prepared. Preparation is not posting, but a draft that nobody asked for is still a
# document an auditor will find and ask about.
REQUIRED_DECISIONS: dict[str, tuple[str, ...]] = {
	OPENING_STOCK: (
		"Opening stock correction: account pair",
		"Opening stock correction: amount",
		"Opening stock correction: posting date",
	),
	COMMISSION_RECOGNITION: (
		"Commission: earning trigger",
		"Commission: calculation basis",
		"Commission: expense account",
		"Commission: payable account",
	),
	COMMISSION_PAYOUT: (
		"Commission: earning trigger",
		"Commission: calculation basis",
		"Commission: expense account",
		"Commission: payable account",
		"Commission: payee party type",
		"Commission: payout document type",
		"Commission: withholding",
		"Commission: returns and clawback",
	),
}


class PreparationRefused(Exception):
	"""Raised for every refusal. Carries the reason, never a credential."""


# --------------------------------------------------------------------------
# Guards
# --------------------------------------------------------------------------

def _guard_site() -> str:
	site = frappe.local.site
	if site in PROTECTED_SITES:
		raise PreparationRefused(f"refusing: {site} is protected")
	if site not in ALLOWED_SITES:
		raise PreparationRefused(
			f"refusing: {site!r} is not an allowlisted preparation site "
			f"{sorted(ALLOWED_SITES)}")
	return site


def _guard_proposal_type(proposal_type: str) -> None:
	if proposal_type not in PROPOSAL_TYPES:
		raise PreparationRefused(
			f"unknown proposal type {proposal_type!r}; expected one of "
			f"{list(PROPOSAL_TYPES)}")


def _guard_mode(mode: str) -> None:
	if mode not in MODES:
		raise PreparationRefused(f"unknown mode {mode!r}; expected one of {list(MODES)}")
	if mode == "apply" or mode == "submit":  # defensive; unreachable via MODES
		raise PreparationRefused("this service cannot submit accounting")


def _guard_capability(mode: str) -> None:
	if mode not in WRITING_MODES:
		if not decisions.has_capability(decisions.CAP_VIEW):
			raise PreparationRefused("you do not hold the permission to view finance work")
		return
	if not decisions.has_capability(decisions.CAP_PREPARE_DRAFT):
		raise PreparationRefused(
			"you do not hold the permission to prepare an accounting draft")


def _latest_backup_age_hours() -> float | None:
	"""Age of the newest database backup, or None when there is none."""
	path = frappe.get_site_path("private", "backups")
	if not os.path.isdir(path):
		return None
	newest = None
	for name in os.listdir(path):
		if not name.endswith("-database.sql.gz"):
			continue
		stamp = os.path.getmtime(os.path.join(path, name))
		newest = stamp if newest is None else max(newest, stamp)
	if newest is None:
		return None
	return (time.time() - newest) / 3600.0


def _guard_backup() -> float:
	age = _latest_backup_age_hours()
	if age is None:
		raise PreparationRefused(
			"refusing: no database backup exists for this site. Take one before "
			"preparing accounting drafts.")
	if age > BACKUP_MAX_AGE_HOURS:
		raise PreparationRefused(
			f"refusing: the newest backup is {age:.1f} hours old, older than the "
			f"{BACKUP_MAX_AGE_HOURS}-hour limit. Take a fresh backup first.")
	return age


def _company(company: str | None) -> str:
	resolved = company or (frappe.get_all("Company", pluck="name", limit_page_length=1)
	                       or [None])[0]
	if not resolved:
		raise PreparationRefused("refusing: no company exists on this site")
	if not frappe.db.exists("Company", resolved):
		raise PreparationRefused(f"refusing: company {resolved!r} does not exist")
	return resolved


def _decision_state(proposal_type: str, company: str) -> dict:
	"""Which governing decisions are recorded, and which are not."""
	required = REQUIRED_DECISIONS[proposal_type]
	recorded, missing = [], []
	for topic in required:
		found = decisions.approved_decision(topic, company)
		if found:
			recorded.append({
				"topic": topic,
				"decision": found.get("accountant_decision"),
				"accountant": found.get("accountant_name"),
				"evidence": found.get("evidence_attachment") or found.get("evidence_reference"),
				"recorded_by": found.get("recorded_by"),
				"prepared_by": found.get("prepared_by"),
				"status": found.get("status"),
			})
		else:
			missing.append(topic)
	return {"required": list(required), "recorded": recorded, "missing": missing,
	        "complete": not missing}


def _guard_decisions(proposal_type: str, company: str) -> dict:
	state = _decision_state(proposal_type, company)
	if state["missing"]:
		raise PreparationRefused(
			"refusing: no accountant decision is recorded for "
			+ "; ".join(state["missing"]))
	for row in state["recorded"]:
		if not row["evidence"]:
			raise PreparationRefused(
				f"refusing: decision on {row['topic']!r} carries no evidence")
		if row["prepared_by"] and row["recorded_by"] and row["prepared_by"] == row["recorded_by"]:
			raise PreparationRefused(
				f"refusing: decision on {row['topic']!r} was recorded by the same "
				f"user who prepared it")
	return state


# --------------------------------------------------------------------------
# Per-proposal-type adapters
#
# Each adapter knows how to inspect its own situation and how to delegate to the
# purpose-built module. None of them knows how to submit.
# --------------------------------------------------------------------------

def _inspect_opening_stock(company: str) -> dict:
	measured = osc.inspect()
	return {
		"amount": measured.get("opening_amount"),
		"expected_amount": measured.get("expected_amount"),
		"amount_matches": flt(measured.get("opening_amount")) == flt(measured.get("expected_amount")),
		"debit_account": measured.get("from_account"),
		"credit_account": measured.get("to_account"),
		"source_vouchers": measured.get("source_vouchers"),
		"existing_draft": measured.get("existing_draft"),
		"already_submitted": measured.get("already_submitted"),
		"totals": measured.get("totals"),
		"correctable": measured.get("correctable"),
	}


def _inspect_commission(company: str, proposal_type: str) -> dict:
	policies = frappe.get_all(
		"Retail Commission Policy", filters={"company": company},
		fields=["name", "policy_name", "status", "enabled"])
	active = [p for p in policies if p.get("status") == "Active"]
	blockers = [_(
		"Commission posting is disabled in this build; no accounting document can be "
		"produced for this proposal type regardless of configuration.")]
	if not policies:
		blockers.append(_("No commission policy exists for this company."))
	elif not active:
		blockers.append(_("No commission policy is Active."))
	return {
		"policies": policies,
		"active_policies": active,
		"posting_enabled": False,
		"blockers": blockers,
		"preparable": False,
	}


# --------------------------------------------------------------------------
# The service
# --------------------------------------------------------------------------

def run(proposal_type: str, mode: str, company: str = "", draft: str = "") -> dict:
	"""Single entry point. Every guard runs before any adapter does."""
	_guard_proposal_type(proposal_type)
	_guard_mode(mode)
	_guard_capability(mode)
	site = _guard_site()
	resolved_company = _company(company)

	result = {
		"proposal_type": proposal_type,
		"mode": mode,
		"site": site,
		"company": resolved_company,
		"submitted": False,
		"posting_available_through_this_service": False,
	}

	decision_state = _decision_state(proposal_type, resolved_company)
	result["decisions"] = decision_state

	if mode == INSPECT:
		if proposal_type == OPENING_STOCK:
			result["position"] = _inspect_opening_stock(resolved_company)
		else:
			result["position"] = _inspect_commission(resolved_company, proposal_type)
		result["backup_age_hours"] = _latest_backup_age_hours()
		result["ready_to_prepare"] = bool(
			decision_state["complete"] and proposal_type == OPENING_STOCK)
		return result

	# Everything past this point needs the decisions and a backup.
	_guard_backup()
	_guard_decisions(proposal_type, resolved_company)

	if proposal_type in (COMMISSION_RECOGNITION, COMMISSION_PAYOUT):
		# Reached only when every governing decision is recorded -- and still
		# refused, because recording decisions does not write the posting code.
		raise PreparationRefused(
			"refusing: commission posting is not implemented in this build. The "
			"accountant decisions may be complete, but the code that would produce "
			"the accounting has not been written or reviewed.")

	if mode == DRY_RUN:
		result["dry_run"] = osc.dry_run()
		result["persisted"] = False
		return result

	if mode == PREPARE_DRAFT:
		existing = osc._applied_je(osc._context(), 0)
		if existing:
			raise PreparationRefused(
				f"refusing: draft {existing} already exists for this correction")
		if osc._applied_je(osc._context(), 1):
			raise PreparationRefused(
				"refusing: this correction has already been submitted")
		result["draft"] = osc.prepare_draft()
		return result

	if mode == VERIFY_DRAFT:
		name = draft or osc._applied_je(osc._context(), 0)
		if not name:
			raise PreparationRefused("refusing: no draft to verify")
		doc = frappe.get_doc("Journal Entry", name)
		if doc.docstatus != 0:
			raise PreparationRefused(
				f"refusing: {name} is not a draft (docstatus {doc.docstatus})")
		measured = _inspect_opening_stock(resolved_company)
		total = round(sum(flt(r.debit) for r in doc.get("accounts") or []), 2)
		result["draft"] = name
		result["draft_total"] = total
		result["amount_agrees_with_ledger"] = total == flt(measured["amount"])
		result["accounts"] = [r.account for r in doc.get("accounts") or []]
		return result

	if mode == CANCEL_DRAFT:
		name = draft or osc._applied_je(osc._context(), 0)
		if not name:
			raise PreparationRefused("refusing: no draft to cancel")
		doc = frappe.get_doc("Journal Entry", name)
		if doc.docstatus != 0:
			raise PreparationRefused(
				f"refusing: {name} is not a draft; this service does not cancel "
				f"submitted accounting")
		# Only ever remove a draft this service produced. The marker is the proof;
		# without it we could be deleting somebody else's unrelated draft.
		if osc.MARKER not in (doc.user_remark or ""):
			raise PreparationRefused(
				f"refusing: {name} was not prepared by this service")
		# force=True skips the link check. A draft Journal Entry accumulates
		# incidental links (versions, comments) that block an ordinary delete, and
		# having established both that it is a draft and that it is ours, those
		# links are not a reason to leave accounting residue behind.
		frappe.delete_doc("Journal Entry", name, force=True)
		result["cancelled"] = name
		return result

	raise PreparationRefused(f"unhandled mode {mode!r}")


@frappe.whitelist(methods=["GET"])
def inspect_proposal(proposal_type: str, company: str = "") -> dict:
	"""Read-only. Safe to call from the Decision Centre."""
	try:
		return run(proposal_type, INSPECT, company=company)
	except PreparationRefused as refused:
		return {"proposal_type": proposal_type, "mode": INSPECT, "refused": str(refused),
		        "submitted": False}


@frappe.whitelist(methods=["GET"])
def preparation_status(company: str = "") -> dict:
	"""Every proposal type at a glance, with the reason each is not ready."""
	if not decisions.has_capability(decisions.CAP_VIEW):
		frappe.throw(_("You do not hold the permission to view finance work."),
		             frappe.PermissionError)
	out = []
	for proposal_type in PROPOSAL_TYPES:
		try:
			out.append(run(proposal_type, INSPECT, company=company))
		except PreparationRefused as refused:
			out.append({"proposal_type": proposal_type, "refused": str(refused),
			            "submitted": False})
	return {
		"proposals": out,
		"submission_available": False,
		"boundary": _(
			"This service prepares and inspects. It has no submit mode. Real "
			"accounting is submitted through the purpose-built path for each "
			"proposal type, with the accountant's authority."),
	}
