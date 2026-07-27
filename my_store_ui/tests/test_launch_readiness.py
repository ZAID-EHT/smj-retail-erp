"""Phase 6: the launch-readiness dashboard is manager-gated and truthful."""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.launch_readiness import (
	AWAITING_APPROVAL,
	CREDENTIAL_REQUIRED,
	get_launch_readiness,
)

SALES_USER = "smj-readiness-sales@example.com"


class TestLaunchReadiness(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Readiness",
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

	def test_is_manager_only(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			get_launch_readiness()

	def test_reports_categories_and_summary(self):
		result = get_launch_readiness()
		cats = set(result["by_category"])
		for expected in ("Code & release", "Finance", "Setup", "Infrastructure", "Business approval"):
			self.assertIn(expected, cats)
		self.assertGreater(result["total"], 0)
		self.assertIn("summary", result)

	def test_accountant_approval_is_not_marked_complete(self):
		"""Truthfulness: external items must not be marked verified/complete."""
		result = get_launch_readiness()
		items = {i["name"]: i for i in result["items"]}
		self.assertEqual(items["Accountant approval"]["status"], AWAITING_APPROVAL)
		# Fresh-site test needs MariaDB root -> credential required, not verified.
		self.assertEqual(items["Genuine fresh-site test"]["status"], CREDENTIAL_REQUIRED)

	def test_email_item_reflects_real_state(self):
		result = get_launch_readiness()
		items = {i["name"]: i for i in result["items"]}
		configured = bool(frappe.get_all("Email Account", filters={"enable_outgoing": 1}, limit_page_length=1))
		if not configured:
			self.assertEqual(items["SMTP configured"]["status"], CREDENTIAL_REQUIRED)

	def test_blocker_count_is_consistent(self):
		result = get_launch_readiness()
		manual = sum(1 for i in result["items"] if i["blocker"])
		self.assertEqual(result["blocker_count"], manual)
		self.assertGreater(result["blocker_count"], 0)  # external items exist

	def test_no_credentials_or_paths_leaked(self):
		import json
		blob = json.dumps(get_launch_readiness(), default=str)
		self.assertNotIn("db_password", blob)
		self.assertNotIn("/home/", blob)


if __name__ == "__main__":
	unittest.main()
