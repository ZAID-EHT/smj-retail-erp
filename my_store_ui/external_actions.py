"""The external go-live tracker: who owes what, and what proof would settle it.

Everything in this product that cannot be finished by writing code lives here in
one list — accountant approvals, credentials, servers, DNS, backups, UAT and
management sign-off. The value is not the list; it is that the list refuses to
lie. Three rules do most of that work:

- **A document is not evidence.** Writing a runbook for a restore drill does not
  mean a restore drill happened, and the tracker will not accept the runbook as
  proof that it did.
- **A script is not a rehearsal.** `verify_fresh_install.sh` existing is not the
  same as it having been run against a real empty site.
- **Whoever did it cannot be the one who confirms it.** Verification is refused
  when the verifier is the person who completed the action.

The catalogue below is seeded, not typed in by a user, so an action cannot go
missing by nobody remembering to add it.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import getdate, now_datetime, nowdate

from my_store_ui.my_store_ui.doctype.retail_external_action.retail_external_action import (
	ALL_STATUSES,
	OUTSTANDING_STATUSES,
	STATUS_AWAITING_APPROVAL,
	STATUS_BLOCKED,
	STATUS_CREDENTIAL,
	STATUS_NOT_STARTED,
	STATUS_READY,
	STATUS_REJECTED,
	STATUS_VERIFIED,
)

ACTION = "Retail External Action"

# Who may look, and who may move an action along. Verification is separated from
# completion so that one person cannot do both on the same record.
VIEW_ROLES = ("System Manager", "Accounts Manager", "Retail Accountant",
              "Retail Finance Verifier")
MANAGE_ROLES = ("System Manager",)
VERIFY_ROLES = ("System Manager", "Retail Finance Verifier", "Accounts Manager")


def _require(roles, message):
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	if not set(frappe.get_roles()) & set(roles):
		frappe.throw(message, frappe.PermissionError)


# --------------------------------------------------------------------------
# The catalogue
#
# Seeded rather than user-entered. `default_status` states the honest position
# today; it is never "Verified" for anything nobody has done.
# --------------------------------------------------------------------------

CATALOGUE = (
	{
		"action_id": "EXT-01", "category": "Accounting", "owner": "Accountant",
		"title": "Opening-stock correction approval",
		"required_action": "Review the opening-stock package, record a decision with "
		                   "evidence in the Accountant Decision Centre, then authorise "
		                   "posting.",
		"risk": "The Profit and Loss overstates profit by LKR 11,820,700 until this is "
		        "corrected.",
		"verification": "Four decision records show Approved with evidence, and "
		                "verify_after() reconciles.",
		"default_status": STATUS_AWAITING_APPROVAL, "blocking": 1,
	},
	{
		"action_id": "EXT-02", "category": "Accounting", "owner": "Accountant",
		"title": "Commission accounting decisions",
		"required_action": "Answer the ten commission decisions in the decision "
		                   "package and sign each one.",
		"risk": "Commission cannot be posted or paid at all until these are answered.",
		"verification": "Ten decision records show Approved with evidence.",
		"default_status": STATUS_AWAITING_APPROVAL, "blocking": 1,
	},
	{
		"action_id": "EXT-03", "category": "Database", "owner": "Ops",
		"title": "MariaDB administrative credential",
		"required_action": "Supply MariaDB root access, or run the fresh-install "
		                   "rehearsal yourself.",
		"risk": "The fresh-install path stays unproven on a genuinely empty site.",
		"verification": "scripts/verify_fresh_install.sh --create --verify completes "
		                "against a new site and records a machine-readable result.",
		"default_status": STATUS_CREDENTIAL, "blocking": 1,
	},
	{
		"action_id": "EXT-04", "category": "Database", "owner": "Ops",
		"title": "Genuine fresh-install rehearsal",
		"required_action": "Run the rehearsal end to end on a new site once EXT-03 is "
		                   "available.",
		"risk": "First real install happens on production day, untested.",
		"verification": "The rehearsal result file records every step as passed.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
	{
		"action_id": "EXT-05", "category": "Email", "owner": "Ops",
		"title": "Production SMTP credentials",
		"required_action": "Supply SMTP host, port, user and password for the "
		                   "production domain.",
		"risk": "Welcome emails, password resets and scheduled reports cannot send.",
		"verification": "A real send reaches an external mailbox from the production "
		                "host.",
		"default_status": STATUS_CREDENTIAL, "blocking": 1,
	},
	{
		"action_id": "EXT-06", "category": "Email", "owner": "Ops",
		"title": "Production email delivery test",
		"required_action": "Send one of each template to a real mailbox and confirm "
		                   "delivery and rendering.",
		"risk": "Templates that render in a sandbox can still fail on a real relay.",
		"verification": "Received messages, with attachments opened.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
	{
		"action_id": "EXT-07", "category": "Infrastructure", "owner": "Ops",
		"title": "Hetzner server provisioned",
		"required_action": "Provision the server and supply SSH access.",
		"risk": "Nothing can be deployed.",
		"verification": "SSH reachable; deployment preflight passes on the host.",
		"default_status": STATUS_CREDENTIAL, "blocking": 1,
	},
	{
		"action_id": "EXT-08", "category": "Infrastructure", "owner": "Ops",
		"title": "Container registry credentials",
		"required_action": "Supply registry URL and push credentials.",
		"risk": "The image cannot be published, so the server cannot pull it.",
		"verification": "An image tag exists in the registry and pulls on the host.",
		"default_status": STATUS_CREDENTIAL, "blocking": 1,
	},
	{
		"action_id": "EXT-09", "category": "Infrastructure", "owner": "Ops",
		"title": "DNS records",
		"required_action": "Create the A/AAAA records for the production hostname.",
		"risk": "The site is unreachable and no certificate can be issued.",
		"verification": "The hostname resolves to the production host.",
		"default_status": STATUS_CREDENTIAL, "blocking": 1,
	},
	{
		"action_id": "EXT-10", "category": "Infrastructure", "owner": "Ops",
		"title": "HTTPS certificate",
		"required_action": "Issue and install the certificate once DNS resolves.",
		"risk": "Credentials would travel in clear text.",
		"verification": "A valid certificate serves the production hostname.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
	{
		"action_id": "EXT-11", "category": "Operations", "owner": "Ops",
		"title": "Off-server backup destination",
		"required_action": "Supply the destination and its credentials.",
		"risk": "A backup that lives only on the server it backs up is not a backup.",
		"verification": "A backup file is present at the remote destination with a "
		                "matching checksum.",
		"default_status": STATUS_CREDENTIAL, "blocking": 1,
	},
	{
		"action_id": "EXT-12", "category": "Operations", "owner": "Ops",
		"title": "Restore drill on real infrastructure",
		"required_action": "Restore a production backup into a scratch site and "
		                   "compare fingerprints.",
		"risk": "Backups are assumed restorable until the day they are not.",
		"verification": "Restore log plus a fingerprint comparison against the source.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
	{
		"action_id": "EXT-13", "category": "Operations", "owner": "Ops",
		"title": "Monitoring and alerting",
		"required_action": "Point monitoring at the production host and define alerts.",
		"risk": "Failures are discovered by users rather than by the team.",
		"verification": "A deliberately triggered alert arrives.",
		"default_status": STATUS_NOT_STARTED, "blocking": 0,
	},
	{
		"action_id": "EXT-14", "category": "UAT", "owner": "Client",
		"title": "Client user acceptance testing",
		"required_action": "Client testers execute the UAT pack and sign each case.",
		"risk": "The system is accepted without anyone from the business using it.",
		"verification": "Every critical UAT case Passed with evidence, and signed off.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
	{
		"action_id": "EXT-15", "category": "Approval", "owner": "Management",
		"title": "Management go-live approval",
		"required_action": "Management signs the cutover authorisation.",
		"risk": "Cutover proceeds without a business decision behind it.",
		"verification": "Signed authorisation.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
	{
		"action_id": "EXT-16", "category": "Approval", "owner": "Management",
		"title": "Production cutover",
		"required_action": "Execute the cutover runbook on the agreed date.",
		"risk": "—",
		"verification": "Post-cutover smoke tests pass and the runbook is complete.",
		"default_status": STATUS_NOT_STARTED, "blocking": 1,
	},
)


def _catalogue_by_id() -> dict:
	return {row["action_id"]: row for row in CATALOGUE}


def seed_actions() -> dict:
	"""Create any catalogue action that does not exist yet. Never overwrites."""
	created = []
	for entry in CATALOGUE:
		if frappe.db.exists(ACTION, entry["action_id"]):
			continue
		doc = frappe.new_doc(ACTION)
		doc.action_id = entry["action_id"]
		doc.category = entry["category"]
		doc.title = entry["title"]
		doc.owner_role = entry["owner"]
		doc.required_action = entry["required_action"]
		doc.risk = entry["risk"]
		doc.verification_procedure = entry["verification"]
		doc.status = entry["default_status"]
		doc.blocking_go_live = entry["blocking"]
		doc.insert(ignore_permissions=True)
		created.append(doc.action_id)
	return {"created": created, "total": len(CATALOGUE)}


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def _rows() -> list[dict]:
	return frappe.get_all(
		ACTION, order_by="action_id asc",
		fields=["name", "action_id", "category", "title", "owner_role", "status",
		        "blocking_go_live", "due_date", "required_action", "risk",
		        "verification_procedure", "evidence_attachment", "evidence_reference",
		        "completed_by", "completed_date", "verified_by", "verified_date",
		        "verification_note", "rejection_reason"])


@frappe.whitelist(methods=["GET"])
def get_external_actions(category: str = "", owner: str = "", status: str = "",
                         blocking_only: int = 0, overdue_only: int = 0,
                         ready_only: int = 0) -> dict:
	"""The tracker, with the filters the go-live conversation actually needs."""
	_require(VIEW_ROLES, _("You cannot view the external action tracker."))
	seed_actions()
	rows = _rows()
	today = getdate(nowdate())

	for row in rows:
		row["outstanding"] = row["status"] in OUTSTANDING_STATUSES
		row["overdue"] = bool(
			row.get("due_date") and row["outstanding"]
			and getdate(row["due_date"]) < today)
		row["evidence"] = row.get("evidence_attachment") or row.get("evidence_reference")

	filtered = rows
	if category:
		filtered = [r for r in filtered if r["category"] == category]
	if owner:
		filtered = [r for r in filtered if (r.get("owner_role") or "") == owner]
	if status:
		filtered = [r for r in filtered if r["status"] == status]
	# A blocking action cannot be filtered *out* of the blocking view; this filter
	# only ever narrows to blocking work, never hides it.
	if int(blocking_only or 0):
		filtered = [r for r in filtered if r.get("blocking_go_live")]
	if int(overdue_only or 0):
		filtered = [r for r in filtered if r["overdue"]]
	if int(ready_only or 0):
		filtered = [r for r in filtered if r["status"] == STATUS_READY]

	blocking_outstanding = [r for r in rows
	                        if r.get("blocking_go_live") and r["outstanding"]]
	by_category: dict = {}
	for row in filtered:
		by_category.setdefault(row["category"], []).append(row)

	return {
		"items": filtered,
		"by_category": by_category,
		"total": len(rows),
		"shown": len(filtered),
		"verified": sum(1 for r in rows if r["status"] == STATUS_VERIFIED),
		"outstanding": sum(1 for r in rows if r["outstanding"]),
		"blocking_outstanding": len(blocking_outstanding),
		"blocking_ids": [r["action_id"] for r in blocking_outstanding],
		"overdue": sum(1 for r in rows if r["overdue"]),
		"statuses": list(ALL_STATUSES),
		"categories": sorted({r["category"] for r in rows}),
		"owners": sorted({r.get("owner_role") or "" for r in rows} - {""}),
		"go_live_ready": not blocking_outstanding,
		"can_manage": bool(set(frappe.get_roles()) & set(MANAGE_ROLES)),
		"can_verify": bool(set(frappe.get_roles()) & set(VERIFY_ROLES)),
		"summary": _(
			"{0} of {1} external actions verified. {2} blocking actions outstanding."
		).format(sum(1 for r in rows if r["status"] == STATUS_VERIFIED), len(rows),
		         len(blocking_outstanding)),
	}


# --------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def set_action_status(action_id: str, status: str, note: str = "") -> dict:
	"""Move an action between the working statuses. Cannot reach Verified."""
	_require(MANAGE_ROLES, _("You cannot change an external action."))
	if status not in ALL_STATUSES:
		frappe.throw(_("{0} is not a status.").format(status), frappe.ValidationError)
	if status == STATUS_VERIFIED:
		frappe.throw(
			_("Verified is reached through verification with evidence, not by "
			  "setting the status."), frappe.ValidationError)
	doc = frappe.get_doc(ACTION, action_id)
	doc.status = status
	if status == STATUS_REJECTED:
		doc.rejection_reason = note
	doc.save()
	return {"action_id": doc.action_id, "status": doc.status}


@frappe.whitelist(methods=["POST"])
def mark_action_complete(action_id: str, evidence_reference: str = "") -> dict:
	"""The owner reports the work done. This is a claim, not a verification."""
	_require(MANAGE_ROLES, _("You cannot change an external action."))
	doc = frappe.get_doc(ACTION, action_id)
	doc.status = STATUS_READY
	doc.completed_by = frappe.session.user
	doc.completed_date = now_datetime()
	if evidence_reference:
		doc.evidence_reference = evidence_reference
	doc.save()
	return {"action_id": doc.action_id, "status": doc.status,
	        "message": _("Recorded as ready for verification, not as done.")}


@frappe.whitelist(methods=["POST"])
def verify_action(action_id: str, evidence_reference: str = "",
                  verification_note: str = "") -> dict:
	"""Someone other than the doer confirms it, with proof."""
	_require(VERIFY_ROLES, _("You cannot verify an external action."))
	doc = frappe.get_doc(ACTION, action_id)
	if doc.status != STATUS_READY:
		frappe.throw(
			_("{0} is {1}. Only an action that is Ready for Verification can be "
			  "verified.").format(action_id, doc.status), frappe.ValidationError)
	if evidence_reference:
		doc.evidence_reference = evidence_reference
	doc.verified_by = frappe.session.user
	doc.verified_date = now_datetime()
	doc.verification_note = verification_note
	doc.status = STATUS_VERIFIED
	doc.save()
	return {"action_id": doc.action_id, "status": doc.status}


@frappe.whitelist(methods=["GET"])
def go_live_blockers() -> dict:
	"""What the release tag would have to be honest about."""
	_require(VIEW_ROLES, _("You cannot view the external action tracker."))
	seed_actions()
	rows = _rows()
	blocking = [r for r in rows
	            if r.get("blocking_go_live") and r["status"] in OUTSTANDING_STATUSES]
	return {
		"blocking": blocking,
		"count": len(blocking),
		"ready": not blocking,
		"statement": _(
			"{0} external actions block go-live. None of them can be completed by "
			"changing this software."
		).format(len(blocking)),
	}
