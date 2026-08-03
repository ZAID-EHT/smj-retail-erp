"""Commission policy: the decisions that turn a calculation into money owed.

Nothing here has a business default. An unset earning trigger, basis, rate source,
payout cycle, withholding mode or returns rule keeps the policy `Incomplete`, and an
incomplete policy cannot prepare a payout. Guessing any of them would produce
authoritative-looking figures that nobody approved.

Two separate levels of completeness:

- **calculation** -- enough to work out what is owed
- **posting** -- additionally, the accounting configuration and the accountant's
  recorded sign-off

A policy can reach Active on calculation completeness alone. It can never permit
posting without the second.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

# Answers that require an explicit approved note rather than standing alone.
NEEDS_NOTE = {
	"earning_trigger": ("Approved Custom Rule", "custom_rule_note"),
	"commission_basis": ("Approved Custom Basis", "custom_basis_note"),
	"rate_source": ("Approved Priority Order", "rate_priority_note"),
}

CALCULATION_FIELDS = (
	("earning_trigger", "Commission Is Earned On"),
	("commission_basis", "Commission Basis"),
	("rate_source", "Rate Source"),
	("payout_cycle", "Payout Cycle"),
	("withholding_mode", "Withholding"),
	("returns_rule", "Returns and Clawbacks"),
)

POSTING_FIELDS = (
	("commission_expense_account", "Commission Expense Account"),
	("commission_payable_account", "Commission Payable Account"),
	("payee_party_type", "Payee Party Type"),
	("cost_center", "Cost Center"),
	("accounting_document_type", "Accounting Document"),
	("accountant_approval_reference", "Accountant Approval Reference"),
)

STATUS_DRAFT = "Draft"
STATUS_INCOMPLETE = "Incomplete"
STATUS_READY = "Ready for Review"
STATUS_APPROVED = "Approved"
STATUS_ACTIVE = "Active"
STATUS_SUSPENDED = "Suspended"
STATUS_RETIRED = "Retired"

# Statuses a user sets deliberately; the controller must not compute over them.
MANUAL_STATUSES = (STATUS_SUSPENDED, STATUS_RETIRED)


class RetailCommissionPolicy(Document):
	def validate(self):
		self._validate_dates()
		self._validate_dependent_values()
		self._set_status()

	def _validate_dates(self):
		if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
			frappe.throw(_("Effective To cannot be before Effective From."), frappe.ValidationError)

	def _validate_dependent_values(self):
		if self.rate_source == "Fixed Policy Rate":
			rate = flt(self.fixed_rate)
			if rate <= 0 or rate > 100:
				frappe.throw(
					_("A fixed policy rate must be between 0 and 100."), frappe.ValidationError)
		if self.withholding_mode == "Fixed Percentage":
			pct = flt(self.withholding_percentage)
			if pct < 0 or pct > 100:
				frappe.throw(
					_("Withholding must be between 0 and 100."), frappe.ValidationError)
			if not pct:
				frappe.throw(
					_("Fixed Percentage withholding needs an approved percentage. "
					  "Leave the mode unset until it is approved."),
					frappe.ValidationError,
				)
		for fieldname, (trigger_value, note_field) in NEEDS_NOTE.items():
			if self.get(fieldname) == trigger_value and not (self.get(note_field) or "").strip():
				frappe.throw(
					_("{0} is set to {1}, so the approved wording must be recorded.").format(
						self.meta.get_label(fieldname), trigger_value),
					frappe.ValidationError,
				)

	# ----------------------------------------------------------------
	# Completeness
	# ----------------------------------------------------------------

	def missing_for_calculation(self) -> list[str]:
		return [label for fieldname, label in CALCULATION_FIELDS if not self.get(fieldname)]

	def missing_for_posting(self) -> list[str]:
		missing = self.missing_for_calculation()
		missing += [label for fieldname, label in POSTING_FIELDS if not self.get(fieldname)]
		return missing

	def is_complete_for_calculation(self) -> bool:
		return not self.missing_for_calculation()

	def is_complete_for_posting(self) -> bool:
		return not self.missing_for_posting()

	def is_active(self) -> bool:
		return self.status == STATUS_ACTIVE

	def may_post(self) -> bool:
		"""The only place that answers "can real money move?"."""
		return self.is_active() and self.is_complete_for_posting()

	def _set_status(self):
		if self.status in MANUAL_STATUSES:
			# Retired and Suspended are deliberate; do not compute over them.
			if self.status == STATUS_RETIRED:
				return
			if self.status == STATUS_SUSPENDED and not self.enabled:
				return
		if self.effective_to and str(self.effective_to) < nowdate():
			self.status = STATUS_RETIRED
			return
		if not self.is_complete_for_calculation():
			self.status = STATUS_INCOMPLETE if self._anything_chosen() else STATUS_DRAFT
			return
		if not self.approved_by:
			self.status = STATUS_READY
			return
		self.status = STATUS_ACTIVE if self.enabled else STATUS_APPROVED

	def _anything_chosen(self) -> bool:
		return any(self.get(fieldname) for fieldname, _label in CALCULATION_FIELDS)

	def summary(self) -> dict:
		return {
			"name": self.name,
			"policy_name": self.policy_name,
			"company": self.company,
			"currency": self.currency,
			"status": self.status,
			"enabled": bool(self.enabled),
			"effective_from": str(self.effective_from) if self.effective_from else None,
			"effective_to": str(self.effective_to) if self.effective_to else None,
			"earning_trigger": self.earning_trigger,
			"commission_basis": self.commission_basis,
			"rate_source": self.rate_source,
			"fixed_rate": flt(self.fixed_rate),
			"payout_cycle": self.payout_cycle,
			"withholding_mode": self.withholding_mode,
			"withholding_percentage": flt(self.withholding_percentage),
			"returns_rule": self.returns_rule,
			"minimum_payout_amount": flt(self.minimum_payout_amount),
			"carry_forward_small_balance": bool(self.carry_forward_small_balance),
			"maximum_negative_carry_forward": flt(self.maximum_negative_carry_forward),
			"manual_approval_threshold": flt(self.manual_approval_threshold),
			"accounting_document_type": self.accounting_document_type,
			"commission_expense_account": self.commission_expense_account,
			"commission_payable_account": self.commission_payable_account,
			"payee_party_type": self.payee_party_type,
			"mode_of_payment": self.mode_of_payment,
			"cost_center": self.cost_center,
			"accountant_approval_reference": self.accountant_approval_reference,
			"approved_by": self.approved_by,
			"approved_on": str(self.approved_on) if self.approved_on else None,
			"complete_for_calculation": self.is_complete_for_calculation(),
			"complete_for_posting": self.is_complete_for_posting(),
			"missing_for_calculation": self.missing_for_calculation(),
			"missing_for_posting": self.missing_for_posting(),
			"may_post": self.may_post(),
		}
