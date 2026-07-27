"""Phase 12: safe system operations are manager-only and leak nothing sensitive."""

from __future__ import annotations

import json
import unittest

import frappe

from my_store_ui.system_operations import (
	get_backup_status,
	get_error_log_summary,
	get_readiness,
	get_system_health,
)

SALES_USER = "smj-sysops-sales@example.com"


class TestSystemOperations(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Sysops",
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

	def test_all_endpoints_are_manager_only(self):
		frappe.set_user(SALES_USER)
		for call in (get_system_health, get_readiness, get_backup_status, get_error_log_summary):
			with self.subTest(endpoint=call.__name__):
				with self.assertRaises(frappe.PermissionError):
					call()

	def test_health_reports_core_services(self):
		health = get_system_health()
		self.assertIn("database", health)
		self.assertTrue(health["database"]["connected"])
		self.assertIn("scheduler", health)
		self.assertIn("errors", health)

	def test_readiness_reports_versions_and_flags(self):
		readiness = get_readiness()
		self.assertIn("frappe", readiness["app_versions"])
		self.assertIn("my_store_ui", readiness["app_versions"])
		self.assertIn("first_time_setup_required", readiness)
		self.assertEqual(readiness["first_time_setup_required"], frappe.db.count("Company") == 0)

	def test_backup_status_leaks_no_absolute_path(self):
		status = get_backup_status()
		blob = json.dumps(status, default=str)
		self.assertNotIn("/home/", blob)
		self.assertNotIn("/private/", blob)
		for row in status["backups"]:
			# Only the basename, never a path separator.
			self.assertNotIn("/", row["file"])

	def test_no_endpoint_leaks_credentials(self):
		# High-signal credential KEYS -- these would only appear if a real secret
		# leaked. The bare word "password" is excluded because it legitimately
		# occurs inside Error Log method names (e.g. "send new password
		# notification"), which is a label, not a credential.
		blob = json.dumps({
			"h": get_system_health(), "r": get_readiness(),
			"b": get_backup_status(),
		}, default=str).lower()
		for secret in ("db_password", "api_secret", "api_key", "encryption_key", "secret_key", "auth_token"):
			self.assertNotIn(secret, blob)
		# The site's real db password must never appear anywhere.
		real_pw = frappe.conf.get("db_password")
		if real_pw:
			full = json.dumps({
				"h": get_system_health(), "r": get_readiness(),
				"b": get_backup_status(), "e": get_error_log_summary(),
			}, default=str)
			self.assertNotIn(real_pw, full)


if __name__ == "__main__":
	unittest.main()
