"""A prepared payout. It never posts anything.

The record exists so the amounts, the payees and the proposed accounting can be
checked *before* anyone is asked to approve real money moving. Reaching `Posted`
requires an accounting document that this system deliberately cannot create yet --
see docs/sales/SMJ_COMMISSION_PAYOUT_PREPARATION.md.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

STATUS_DRAFT = "Draft"
STATUS_VALIDATED = "Validated"
STATUS_READY = "Ready for Posting"
STATUS_POSTED = "Posted"
STATUS_PARTIALLY_POSTED = "Partially Posted"
STATUS_CANCELLED = "Cancelled"

# Statuses that assert money has actually moved. Nothing in this mission may set them.
EVIDENCE_REQUIRED = (STATUS_POSTED, STATUS_PARTIALLY_POSTED)


class RetailCommissionPayout(Document):
	def validate(self):
		self._inherit_period_context()
		self._recalculate_total()
		self._refuse_unevidenced_posting()

	def _inherit_period_context(self):
		if not self.period:
			return
		period = frappe.get_cached_doc("Retail Commission Period", self.period)
		self.company = period.company
		self.currency = period.currency

	def _recalculate_total(self):
		self.total_net_payable = flt(
			sum(flt(row.net_payable) for row in self.get("lines") or []), 2)

	def _refuse_unevidenced_posting(self):
		"""The one rule that cannot be configured away.

		A Posted payout asserts that money left the business. Nothing in this system
		can verify that, because no accounting document is created, so the status is
		refused outright rather than left to a caller's discretion.
		"""
		if self.status in EVIDENCE_REQUIRED:
			frappe.throw(
				_("A payout cannot be marked {0} without a posted accounting document. "
				  "Commission posting is not enabled -- see the payout boundary."
				  ).format(self.status),
				frappe.ValidationError,
			)
