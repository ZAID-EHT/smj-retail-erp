"""Phase 3: the Administration landing is permission-aware and truthful."""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.admin_landing import get_admin_landing

SALES_USER = "smj-adminland-sales@example.com"


class TestAdminLanding(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ AdminLand",
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

	def test_manager_sees_all_admin_cards(self):
		result = get_admin_landing()
		self.assertTrue(result["is_manager"])
		keys = {c["key"] for c in result["cards"]}
		for expected in ("companies", "access", "printing", "email", "data", "finance",
		                 "scheduled", "system", "readiness"):
			self.assertIn(expected, keys)

	def test_non_manager_sees_no_manager_only_cards(self):
		frappe.set_user(SALES_USER)
		result = get_admin_landing()
		self.assertFalse(result["is_manager"])
		# A Sales User is not a System Manager, so the manager-gated cards are hidden.
		keys = {c["key"] for c in result["cards"]}
		self.assertNotIn("system", keys)
		self.assertNotIn("readiness", keys)
		self.assertNotIn("email", keys)

	def test_email_card_reflects_configuration(self):
		result = get_admin_landing()
		email = next(c for c in result["cards"] if c["key"] == "email")
		configured = bool(frappe.get_all("Email Account", filters={"enable_outgoing": 1}, limit_page_length=1))
		if not configured:
			self.assertFalse(email["status_ok"])
			self.assertIn("not configured", email["status"].lower())

	def test_finance_card_flags_pending_correction(self):
		result = get_admin_landing()
		finance = next(c for c in result["cards"] if c["key"] == "finance")
		# Correction is not applied on staging, so it should flag pending with a warning.
		applied = frappe.db.get_value(
			"Journal Entry", {"user_remark": ["like", "%opening-stock reclassification%"], "docstatus": 1}, "name")
		if not applied:
			self.assertIn("pending", finance["status"].lower())
			self.assertGreaterEqual(finance["warnings"], 1)

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_admin_landing()


if __name__ == "__main__":
	unittest.main()
