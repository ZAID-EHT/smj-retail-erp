"""The transaction-register route guard must require what its API requires.

Found by browser verification: the guard admitted any signed-in user while
get_wholesale_transactions refuses anyone without Sales Order read, so the page
rendered and then failed with a console 403 instead of showing permission-denied.
"""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui.standalone import authorize_frontend_route
from my_store_ui.wholesale.register import get_wholesale_transactions

ROUTE = "/sales/transactions"
NO_SALES_USER = "register-guard-nosales@example.invalid"


class TestRegisterRoutePermission(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def setUp(self):
		self.sp = f"guard_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _user_without_sales(self):
		if not frappe.db.exists("User", NO_SALES_USER):
			user = frappe.get_doc({
				"doctype": "User", "email": NO_SALES_USER, "first_name": "No Sales",
				"send_welcome_email": 0,
			})
			user.insert(ignore_permissions=True)
			user.add_roles("System Manager")
		return NO_SALES_USER

	def test_administrator_is_allowed(self):
		self.assertEqual(authorize_frontend_route(ROUTE)["outcome"], "allowed")

	def test_system_manager_without_sales_order_read_is_denied_the_route(self):
		"""System Manager is a Frappe role and grants no ERPNext selling rights."""
		user = self._user_without_sales()
		frappe.set_user(user)
		try:
			self.assertFalse(frappe.has_permission("Sales Order", "read"))
			self.assertEqual(authorize_frontend_route(ROUTE)["outcome"], "denied")
		finally:
			frappe.set_user("Administrator")

	def test_guard_and_api_agree(self):
		"""Whoever the guard admits must not then be refused by the register API."""
		user = self._user_without_sales()
		frappe.set_user(user)
		try:
			outcome = authorize_frontend_route(ROUTE)["outcome"]
			if outcome == "allowed":
				get_wholesale_transactions()   # must not raise
			else:
				with self.assertRaises(frappe.PermissionError):
					get_wholesale_transactions()
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
