"""One thing somebody outside this system must do before go-live.

The tracker's only real job is to resist the temptation to mark things done. A
go-live checklist that can be ticked off without evidence is worse than no
checklist, because it converts "nobody has done this" into "somebody says this is
fine" without anything changing in the world.

So: `Verified` requires evidence and a verifier who is not the person who
completed the action, `Rejected` requires a reason, and a blocking action cannot
quietly stop being blocking.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

STATUS_NOT_STARTED = "Not Started"
STATUS_WAITING = "Waiting for Owner"
STATUS_CREDENTIAL = "Credential Required"
STATUS_AWAITING_APPROVAL = "Awaiting Approval"
STATUS_IN_PROGRESS = "In Progress"
STATUS_READY = "Ready for Verification"
STATUS_VERIFIED = "Verified"
STATUS_REJECTED = "Rejected"
STATUS_BLOCKED = "Blocked"

ALL_STATUSES = (STATUS_NOT_STARTED, STATUS_WAITING, STATUS_CREDENTIAL,
                STATUS_AWAITING_APPROVAL, STATUS_IN_PROGRESS, STATUS_READY,
                STATUS_VERIFIED, STATUS_REJECTED, STATUS_BLOCKED)

# Statuses that mean the action is still outstanding for go-live purposes.
OUTSTANDING_STATUSES = (STATUS_NOT_STARTED, STATUS_WAITING, STATUS_CREDENTIAL,
                        STATUS_AWAITING_APPROVAL, STATUS_IN_PROGRESS, STATUS_READY,
                        STATUS_REJECTED, STATUS_BLOCKED)


class RetailExternalAction(Document):
	def validate(self):
		self._require_evidence_for_verification()
		self._require_separate_verifier()
		self._require_reason_for_rejection()

	def _require_evidence_for_verification(self):
		if self.status != STATUS_VERIFIED:
			return
		if not (self.evidence_attachment or self.evidence_reference):
			frappe.throw(
				_("{0} cannot be Verified without evidence. A document describing "
				  "the step, or a script that would perform it, is not evidence that "
				  "it happened.").format(self.action_id),
				frappe.ValidationError,
			)

	def _require_separate_verifier(self):
		if self.status != STATUS_VERIFIED:
			return
		if self.completed_by and self.verified_by and self.completed_by == self.verified_by:
			frappe.throw(
				_("{0} was completed by {1}, who cannot also verify it.").format(
					self.action_id, self.completed_by),
				frappe.ValidationError,
			)

	def _require_reason_for_rejection(self):
		if self.status == STATUS_REJECTED and not (self.rejection_reason or "").strip():
			frappe.throw(_("A rejected action needs a reason."), frappe.ValidationError)

	def is_outstanding(self) -> bool:
		return self.status in OUTSTANDING_STATUSES
