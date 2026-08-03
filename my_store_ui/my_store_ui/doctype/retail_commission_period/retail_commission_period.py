"""A commission period: one closing cycle for one company under one policy.

The period is where calculation becomes a claim. Its structural rules live here so
they hold whatever creates it -- the Retail ERP screen, an API call or the Desk.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

STATUS_DRAFT = "Draft"
STATUS_PREPARED = "Prepared"
STATUS_UNDER_REVIEW = "Under Review"
STATUS_APPROVED = "Approved"
STATUS_PAYMENT_PREPARED = "Payment Prepared"
STATUS_PARTIALLY_PAID = "Partially Paid"
STATUS_PAID = "Paid"
STATUS_REOPENED = "Reopened"
STATUS_CANCELLED = "Cancelled"

# Once a period is approved its rows are evidence, not a worksheet.
LOCKED_STATUSES = (STATUS_APPROVED, STATUS_PAYMENT_PREPARED, STATUS_PARTIALLY_PAID, STATUS_PAID)
# Statuses that still occupy the calendar for overlap purposes.
LIVE_STATUSES = (STATUS_DRAFT, STATUS_PREPARED, STATUS_UNDER_REVIEW, STATUS_APPROVED,
                 STATUS_PAYMENT_PREPARED, STATUS_PARTIALLY_PAID, STATUS_PAID, STATUS_REOPENED)

BLOCKING = "Blocking"


class RetailCommissionPeriod(Document):
	def validate(self):
		self._validate_dates()
		self._validate_policy()
		self._validate_no_overlap()
		self._recalculate_totals()

	def _validate_dates(self):
		if not self.from_date or not self.to_date:
			return
		if self.to_date < self.from_date:
			frappe.throw(_("To Date cannot be before From Date."), frappe.ValidationError)

	def _validate_policy(self):
		if not self.policy:
			return
		policy = frappe.get_cached_doc("Retail Commission Policy", self.policy)
		if policy.company != self.company:
			frappe.throw(
				_("{0} belongs to {1}, not {2}.").format(self.policy, policy.company, self.company),
				frappe.ValidationError,
			)
		if not self.currency:
			self.currency = policy.currency or frappe.db.get_value(
				"Company", self.company, "default_currency")
		elif policy.currency and self.currency != policy.currency:
			frappe.throw(
				_("The period currency {0} does not match the policy currency {1}.").format(
					self.currency, policy.currency),
				frappe.ValidationError,
			)

	def _validate_no_overlap(self):
		"""One live period per company and policy for any given day."""
		if not (self.from_date and self.to_date and self.company and self.policy):
			return
		clash = frappe.get_all(
			"Retail Commission Period",
			filters={
				"name": ["!=", self.name or ""],
				"company": self.company,
				"policy": self.policy,
				"status": ["in", LIVE_STATUSES],
				"from_date": ["<=", self.to_date],
				"to_date": [">=", self.from_date],
			},
			fields=["name", "from_date", "to_date"], limit_page_length=1,
		)
		if clash:
			frappe.throw(
				_("{0} already covers {1} to {2} for this company and policy.").format(
					clash[0]["name"], clash[0]["from_date"], clash[0]["to_date"]),
				frappe.ValidationError,
			)

	# ----------------------------------------------------------------

	def _recalculate_totals(self):
		rows = self.get("details") or []
		self.gross_commission = flt(sum(flt(r.gross_commission) for r in rows), 2)
		self.reversals = flt(sum(flt(r.return_reversal) for r in rows), 2)
		self.withholding = flt(sum(flt(r.withholding) for r in rows), 2)
		self.adjustments = flt(sum(flt(r.adjustment) for r in rows), 2)
		self.net_payable = flt(sum(flt(r.net_commission) for r in rows), 2)
		# paid_amount is only ever moved by an accounting-backed payout, which does
		# not exist yet; outstanding therefore equals the whole net payable.
		self.outstanding = flt(flt(self.net_payable) - flt(self.paid_amount), 2)

	def blocking_exceptions(self) -> list:
		return [
			row for row in self.get("exceptions") or []
			if row.severity == BLOCKING and row.resolution_status in ("Open", "Acknowledged")
		]

	def is_closed(self) -> bool:
		"""Deliberately not named `is_locked`.

		`Document.is_locked` is a Frappe *property* backing its file-lock mechanism.
		A method of that name here shadows it, and a bound method is always truthy --
		so every save looked locked and then crashed stat-ing a lock file that had
		never been created.
		"""
		return self.status in LOCKED_STATUSES

	def assert_editable(self):
		if self.is_closed():
			frappe.throw(
				_("{0} is {1}. Reopen it, or raise an adjustment instead of editing it.").format(
					self.name, self.status),
				frappe.ValidationError,
			)
