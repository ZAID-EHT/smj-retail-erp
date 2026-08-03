"""Retail Sales Team: a manager plus their representatives, and how the team
commission pool is split between them.

All structural rules live here, in the controller, so they hold no matter how the
record is created -- the Retail ERP form, an API call, or the Desk.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MANAGER_ROLE = "Sales Manager"
REPRESENTATIVE_ROLE = "Sales Representative"

# Shares are percentages; allow for float representation error only.
SHARE_TOLERANCE = 0.01
TOTAL_SHARE = 100.0


class RetailSalesTeam(Document):
	def validate(self):
		self._validate_dates()
		self._validate_members()
		self._set_manager()

	def _validate_dates(self):
		if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
			frappe.throw(
				_("Effective To cannot be before Effective From."), frappe.ValidationError
			)
		if flt(self.commission_rate) < 0 or flt(self.commission_rate) > 100:
			frappe.throw(
				_("Team Commission Rate must be between 0 and 100."), frappe.ValidationError
			)

	def _validate_members(self):
		members = self.get("members") or []
		if not members:
			frappe.throw(_("A sales team needs at least one member."), frappe.ValidationError)

		seen = {}
		active_total = 0.0
		managers = []
		for row in members:
			if row.team_role not in (MANAGER_ROLE, REPRESENTATIVE_ROLE):
				frappe.throw(
					_("Row {0}: Role in Team must be {1} or {2}.").format(
						row.idx, MANAGER_ROLE, REPRESENTATIVE_ROLE),
					frappe.ValidationError,
				)
			if row.sales_person in seen:
				frappe.throw(
					_("{0} appears twice (rows {1} and {2}). Each person may appear once.").format(
						row.sales_person, seen[row.sales_person], row.idx),
					frappe.ValidationError,
				)
			seen[row.sales_person] = row.idx

			share = flt(row.share_percentage)
			if share < 0:
				frappe.throw(
					_("Row {0}: Share % cannot be negative.").format(row.idx), frappe.ValidationError
				)
			if row.effective_to and row.effective_from and row.effective_to < row.effective_from:
				frappe.throw(
					_("Row {0}: Effective To cannot be before Effective From.").format(row.idx),
					frappe.ValidationError,
				)
			if row.is_active:
				active_total += share
				if row.team_role == MANAGER_ROLE:
					managers.append(row.sales_person)

		if not managers:
			frappe.throw(
				_("A sales team needs one active Sales Manager."), frappe.ValidationError
			)
		if len(managers) > 1:
			frappe.throw(
				_("A sales team can have only one active Sales Manager. Found {0}.").format(
					", ".join(managers)),
				frappe.ValidationError,
			)
		if abs(active_total - TOTAL_SHARE) > SHARE_TOLERANCE:
			frappe.throw(
				_("Active member shares must total 100%. They currently total {0}%.").format(
					round(active_total, 2)),
				frappe.ValidationError,
			)

	def _set_manager(self):
		self.sales_manager = next(
			(row.sales_person for row in self.get("members") or []
			 if row.is_active and row.team_role == MANAGER_ROLE),
			None,
		)

	def active_members(self) -> list:
		return [row for row in self.get("members") or [] if row.is_active]
