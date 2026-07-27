"""Phase 9: email administration is manager-only, truthful, and leaks no secrets."""

from __future__ import annotations

import json
import unittest

import frappe

from my_store_ui.email_admin import get_email_overview, get_notification_coverage

SALES_USER = "smj-email-sales@example.com"


class TestEmailAdmin(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Email",
			                      "send_welcome_email": 0, "enabled": 1})
			doc.insert(ignore_permissions=True)
			doc.append("roles", {"role": "Sales User"})
			doc.save(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		if frappe.db.exists("User", SALES_USER):
			frappe.delete_doc("User", SALES_USER, force=True, ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_overview_is_manager_only(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			get_email_overview()
		with self.assertRaises(frappe.PermissionError):
			get_notification_coverage()

	def test_overview_reports_truthful_delivery_status(self):
		overview = get_email_overview()
		delivery = overview["delivery"]
		configured = bool(frappe.get_all(
			"Email Account", filters={"enable_outgoing": 1}, limit_page_length=1))
		self.assertEqual(delivery["outgoing_configured"], configured or delivery["site_config_fallback"])
		self.assertIn("templates", overview)
		self.assertIn("notifications", overview)
		self.assertIn("queue", overview)

	def test_overview_never_returns_a_credential(self):
		overview = get_email_overview()
		# Exclude the human-readable delivery message, which legitimately says
		# "administrator-set temporary password" -- an instruction, not a secret.
		overview_no_message = {k: v for k, v in overview.items()}
		overview_no_message["delivery"] = {
			k: v for k, v in overview["delivery"].items() if k != "message"
		}
		blob = json.dumps(overview_no_message, default=str).lower()
		for secret in ("password", "smtp_server", "smtp_", "api_key", "api_secret", "access_token", "auth_token"):
			self.assertNotIn(secret, blob)

	def test_notification_coverage_lists_wholesale_events(self):
		coverage = get_notification_coverage()["coverage"]
		events = {row["event"] for row in coverage}
		self.assertIn("Sales Order", events)
		self.assertIn("Sales Invoice", events)
		for row in coverage:
			self.assertIn("has_enabled_notification", row)


if __name__ == "__main__":
	unittest.main()
