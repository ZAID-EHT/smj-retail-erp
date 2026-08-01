"""Henderson strategic-alignment assessment.

A management record, deliberately isolated from the operational modules: it never
touches pricing, stock, reservations or any sales/purchase document.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

MIN_SCORE = 0
MAX_SCORE = 5

DOMAINS = (
	"Business Strategy",
	"IT Strategy",
	"Business Operations",
	"IT Systems",
	"Infrastructure",
	"Strategic Alignment",
)


class HendersonAssessment(Document):
	def validate(self):
		self._validate_scores()
		self._validate_unique_domains()

	def _validate_scores(self):
		for row in self.get("domains") or []:
			for fieldname, label in (("current_score", _("Current Score")),
			                         ("target_score", _("Target Score"))):
				value = cint(row.get(fieldname))
				if value < MIN_SCORE or value > MAX_SCORE:
					frappe.throw(
						_("Row {0}: {1} must be between {2} and {3}.").format(
							row.idx, label, MIN_SCORE, MAX_SCORE),
						frappe.ValidationError,
					)

	def _validate_unique_domains(self):
		seen = set()
		for row in self.get("domains") or []:
			if row.domain in seen:
				frappe.throw(
					_("{0} appears more than once.").format(row.domain), frappe.ValidationError
				)
			seen.add(row.domain)
