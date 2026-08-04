"""One accountant-controlled question, and the answer a named accountant gave it.

A decision record is deliberately dull: it holds a proposal the system prepared, the
answer a person gave, who gave it, when, from when it applies, and the evidence. It
grants no authority by itself — code that needs an approved decision asks for one and
is refused when the answer is missing.

Two properties matter more than the fields:

**A decided record is frozen.** Once the status leaves the review stages, the decision
fields stop accepting edits. Changing an answer means recording a new version and
pointing the old one at it, so the history of what was approved on what date survives.

**Filling the fields in is not approval.** `Approved` additionally requires evidence and
a recorder who is not the person who prepared the proposal. Both are checked here rather
than in the UI, because the UI is not the boundary.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

STATUS_NOT_REVIEWED = "Not Reviewed"
STATUS_INFORMATION_REQUIRED = "Information Required"
STATUS_UNDER_REVIEW = "Under Accountant Review"
STATUS_APPROVED = "Approved"
STATUS_REJECTED = "Rejected"
STATUS_APPROVED_WITH_CHANGES = "Approved with Changes"
STATUS_IMPLEMENTED = "Implemented"
STATUS_VERIFIED = "Verified"

# Stages where the proposal may still be reworked.
OPEN_STATUSES = (STATUS_NOT_REVIEWED, STATUS_INFORMATION_REQUIRED, STATUS_UNDER_REVIEW)

# Stages that represent a recorded human answer. These freeze the record.
DECIDED_STATUSES = (STATUS_APPROVED, STATUS_REJECTED, STATUS_APPROVED_WITH_CHANGES,
                    STATUS_IMPLEMENTED, STATUS_VERIFIED)

# An answer that permits downstream accounting work to be prepared.
POSITIVE_STATUSES = (STATUS_APPROVED, STATUS_APPROVED_WITH_CHANGES,
                     STATUS_IMPLEMENTED, STATUS_VERIFIED)

# Fields that are part of the recorded answer and must not drift afterwards.
FROZEN_FIELDS = (
	"topic_area", "topic", "accountant_decision", "accountant_name", "accountant_user",
	"review_date", "effective_date", "decision_comment", "rejection_reason",
	"evidence_attachment", "evidence_reference", "recorded_by", "recorded_on",
	"proposed_value",
)


class RetailAccountantDecision(Document):
	def validate(self):
		self._guard_frozen_fields()
		self._require_evidence_for_approval()
		self._require_reason_for_rejection()
		self._require_segregation()

	def _guard_frozen_fields(self):
		"""A decided record only moves forward through the workflow, never sideways.

		The workflow itself sets `flags.decision_transition` when it is legitimately
		writing these fields; anything else editing a decided record is refused.
		"""
		if self.is_new() or self.flags.decision_transition:
			return
		before = self.get_doc_before_save()
		if not before or before.status not in DECIDED_STATUSES:
			return
		changed = [f for f in FROZEN_FIELDS if (self.get(f) or "") != (before.get(f) or "")]
		if changed:
			frappe.throw(
				_("{0} has already been decided. Record a new version instead of editing "
				  "{1}.").format(self.name, ", ".join(changed)),
				frappe.ValidationError,
			)

	def _require_evidence_for_approval(self):
		if self.status not in (STATUS_APPROVED, STATUS_APPROVED_WITH_CHANGES):
			return
		if not (self.evidence_attachment or self.evidence_reference):
			frappe.throw(
				_("An approval needs evidence. Attach the signed approval or record its "
				  "reference before setting {0}.").format(self.status),
				frappe.ValidationError,
			)
		if not self.accountant_name:
			frappe.throw(
				_("An approval needs the name of the accountant who gave it."),
				frappe.ValidationError,
			)

	def _require_reason_for_rejection(self):
		if self.status == STATUS_REJECTED and not (self.rejection_reason or "").strip():
			frappe.throw(
				_("A rejection needs a reason."), frappe.ValidationError)

	def _require_segregation(self):
		"""The person who prepared a proposal cannot be the one who approves it."""
		if self.status not in DECIDED_STATUSES:
			return
		if self.prepared_by and self.recorded_by and self.prepared_by == self.recorded_by:
			frappe.throw(
				_("{0} prepared this proposal and cannot also record the decision on it. "
				  "The decision must be recorded by the responsible accountant.").format(
					self.prepared_by),
				frappe.ValidationError,
			)

	def is_positively_decided(self) -> bool:
		return self.status in POSITIVE_STATUSES

	def blocking_reason(self) -> str | None:
		"""Why this decision does not yet authorise downstream work."""
		if self.superseded_by:
			return _("Decision {0} was superseded by {1}.").format(self.name, self.superseded_by)
		if self.status in OPEN_STATUSES:
			return _("Decision {0} ({1}) is {2}; no accountant answer has been recorded.").format(
				self.name, self.topic, self.status)
		if self.status == STATUS_REJECTED:
			return _("Decision {0} ({1}) was rejected: {2}").format(
				self.name, self.topic, self.rejection_reason or _("no reason recorded"))
		return None
