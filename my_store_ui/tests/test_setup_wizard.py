"""Phase 7: first-time setup detection, gating and the checklist.

Staging already has a Company, so the empty-system path is exercised by asserting
detection reflects the real company count and by checking the gate on create_company.
Company creation itself is validated in a savepoint that is rolled back.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.setup_wizard import (
	REQUIRED_PRICE_LISTS,
	get_setup_options,
	get_setup_status,
)

SALES_USER = "smj-setup-sales@example.com"


class TestSetupWizard(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Setup",
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

	def test_status_reflects_real_company_count(self):
		status = get_setup_status()
		self.assertEqual(status["company_count"], frappe.db.count("Company"))
		self.assertEqual(status["setup_required"], frappe.db.count("Company") == 0)

	def test_status_reports_checklist_for_configured_company(self):
		status = get_setup_status()
		if status["company_count"] == 0:
			self.skipTest("no company on this site")
		items = {row["item"]: row for row in status["checklist"]}
		self.assertTrue(items["Company"]["done"])
		self.assertTrue(items["Chart of Accounts"]["done"])
		self.assertTrue(items["Price Lists"]["done"])

	def test_status_is_readable_by_any_authenticated_user(self):
		"""Detection is not secret -- a normal user must be able to learn setup is
		(or is not) required, so the SPA can route them correctly."""
		frappe.set_user(SALES_USER)
		status = get_setup_status()
		self.assertIn("setup_required", status)
		self.assertFalse(status["can_create_company"])  # but they cannot create one

	def test_setup_options_are_manager_only(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			get_setup_options()

	def test_create_company_builds_coa_and_price_lists(self):
		"""Full company creation via the standard controller, rolled back."""
		from my_store_ui.setup_wizard import create_company

		name = "SMJ Setup Test Co"
		savepoint = "setup_create"
		frappe.db.savepoint(savepoint)
		try:
			result = create_company({
				"company_name": name, "abbr": "SSTC", "default_currency": "LKR",
				"country": "Sri Lanka", "chart_of_accounts": "Standard",
			})
			self.assertEqual(result["company"], name)
			# Standard controller must have built a Chart of Accounts.
			self.assertTrue(frappe.get_all("Account", filters={"company": name}, limit_page_length=1))
			# Required price lists exist.
			for spec in REQUIRED_PRICE_LISTS:
				self.assertTrue(frappe.db.exists("Price List", spec["price_list_name"]))
			checklist = {row["item"]: row for row in result["checklist"]}
			self.assertTrue(checklist["Company"]["done"])
			self.assertTrue(checklist["Chart of Accounts"]["done"])
		finally:
			frappe.db.rollback(save_point=savepoint)
		self.assertFalse(frappe.db.exists("Company", name), "savepoint rollback must remove the test company")

	def test_create_company_is_manager_gated(self):
		from my_store_ui.setup_wizard import create_company

		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			create_company({"company_name": "Nope Co"})


if __name__ == "__main__":
	unittest.main()
