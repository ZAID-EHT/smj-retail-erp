"""Phase 5: scheduled report management is permission-safe and truthful about SMTP."""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.scheduled_reports import (
	create_scheduled_report,
	get_schedulable_reports,
	get_scheduled_reports_overview,
	set_schedule_enabled,
)

SALES_USER = "smj-sched-sales@example.com"
MADE = []


class TestScheduledReports(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Sched",
			                      "send_welcome_email": 0, "enabled": 1})
			doc.insert(ignore_permissions=True)
			doc.append("roles", {"role": "Sales User"})
			doc.save(ignore_permissions=True)
		cls.email_ok = _email_ok()
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for name in MADE:
			if frappe.db.exists("Auto Email Report", name):
				frappe.delete_doc("Auto Email Report", name, force=True, ignore_permissions=True)
		if frappe.db.exists("User", SALES_USER):
			frappe.delete_doc("User", SALES_USER, force=True, ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.set_user("Administrator")

	def _a_permitted_report(self):
		reports = get_schedulable_reports()["reports"]
		return reports[0]["name"] if reports else None

	def test_overview_reports_smtp_status(self):
		overview = get_scheduled_reports_overview()
		self.assertIn("email", overview)
		self.assertIn("can_send_welcome_email", overview["email"])
		self.assertIn("schedules", overview)

	def test_schedulable_reports_are_permission_filtered(self):
		frappe.set_user(SALES_USER)
		reports = get_schedulable_reports()["reports"]
		# A Sales User should not be offered, e.g., a purchase/accounts-only report they
		# cannot read. We assert every offered report is actually readable by them.
		for row in reports:
			self.assertTrue(frappe.has_permission("Report", "read", doc=row["name"]))

	def test_create_is_denied_without_permission(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_scheduled_reports_overview()

	def test_create_rejects_report_without_access(self):
		"""Scheduling a report the caller cannot read is refused."""
		report = self._a_permitted_report()
		if not report:
			self.skipTest("no schedulable report on this site")
		frappe.set_user(SALES_USER)
		# Try to schedule a report the Sales User cannot read, if one exists.
		blocked = frappe.get_all("Report", filters={"ref_doctype": "Purchase Invoice"}, pluck="name")
		blocked = [r for r in blocked if not frappe.has_permission("Report", "read", doc=r)]
		if not blocked:
			self.skipTest("no report the Sales User is blocked from")
		with self.assertRaises((frappe.PermissionError, frappe.DoesNotExistError)):
			create_scheduled_report(report=blocked[0], email_to="x@example.com")

	def test_create_disabled_when_email_not_configured(self):
		report = self._a_permitted_report()
		if not report:
			self.skipTest("no schedulable report")
		result = create_scheduled_report(report=report, frequency="Weekly", output_format="HTML",
		                                 email_to="ops@example.com")
		MADE.append(result["name"])
		if not self.email_ok:
			# Created DISABLED so nothing claims to send.
			self.assertFalse(result["enabled"])
			self.assertIn("not configured", (result["message"] or "").lower())

	def test_cannot_enable_when_email_not_configured(self):
		report = self._a_permitted_report()
		if not report:
			self.skipTest("no schedulable report")
		if self.email_ok:
			self.skipTest("email is configured on this site")
		result = create_scheduled_report(report=report, email_to="ops@example.com")
		MADE.append(result["name"])
		with self.assertRaises(frappe.ValidationError):
			set_schedule_enabled(name=result["name"], enabled=1)

	def test_create_requires_a_recipient(self):
		report = self._a_permitted_report()
		if not report:
			self.skipTest("no schedulable report")
		with self.assertRaises(frappe.ValidationError):
			create_scheduled_report(report=report, email_to="")


def _email_ok() -> bool:
	from my_store_ui.access_management import _email_configuration_status
	return _email_configuration_status()["can_send_welcome_email"]


if __name__ == "__main__":
	unittest.main()
