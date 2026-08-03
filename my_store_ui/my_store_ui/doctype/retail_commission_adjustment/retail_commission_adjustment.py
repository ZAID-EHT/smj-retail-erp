"""A manual change to what a member is owed, with the duties kept apart.

Nothing here touches an invoice. An adjustment is a separate, auditable record that
the period totals read; the source documents stay exactly as they were.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

STATUS_REQUESTED = "Requested"
STATUS_APPROVED = "Approved"
STATUS_REJECTED = "Rejected"
STATUS_CANCELLED = "Cancelled"


class RetailCommissionAdjustment(Document):
	def validate(self):
		if not flt(self.amount):
			frappe.throw(_("An adjustment needs a non-zero amount."), frappe.ValidationError)
		if not (self.reason or "").strip():
			frappe.throw(_("An adjustment needs a reason."), frappe.ValidationError)
		self._validate_member_belongs_to_period()
		if not self.requested_by:
			self.requested_by = frappe.session.user
		if not self.requested_on:
			self.requested_on = now_datetime()

	def _validate_member_belongs_to_period(self):
		"""An adjustment must attach to someone the period actually pays."""
		if not (self.period and self.sales_person):
			return
		known = frappe.db.exists("Retail Commission Period Detail", {
			"parent": self.period, "parenttype": "Retail Commission Period",
			"sales_person": self.sales_person,
		})
		if not known:
			frappe.throw(
				_("{0} has no commission rows in {1}, so there is nothing to adjust.").format(
					self.sales_person, self.period),
				frappe.ValidationError,
			)
