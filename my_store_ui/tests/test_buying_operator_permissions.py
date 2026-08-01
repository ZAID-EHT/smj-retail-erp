"""Buying operators must be able to create Suppliers, like selling operators can create Customers.

Stock ERPNext v15 restricts Supplier to `Purchase Master Manager`, while `Sales User`
can create a Customer. That asymmetry hid "+ New Supplier" from every real operator
role and left Administrator with a form nobody else could save -- the "this button
does not work" report in the requirements document.
"""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui.services.frontend_routes import get_quick_create_actions

PURCHASE_USER = "buying-op-purchase@example.invalid"
SALES_ONLY_USER = "buying-op-salesonly@example.invalid"


class TestBuyingOperatorPermissions(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def setUp(self):
		self.sp = f"buyperm_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _user(self, email, roles):
		if not frappe.db.exists("User", email):
			doc = frappe.get_doc({
				"doctype": "User", "email": email, "first_name": email.split("@")[0],
				"send_welcome_email": 0,
			})
			doc.insert(ignore_permissions=True)
			doc.add_roles(*roles)
		return email

	def test_purchase_user_can_create_a_supplier(self):
		user = self._user(PURCHASE_USER, ["Purchase User"])
		frappe.set_user(user)
		try:
			self.assertTrue(
				frappe.has_permission("Supplier", "create"),
				"a Purchase User must be able to create a Supplier",
			)
		finally:
			frappe.set_user("Administrator")

	def test_purchase_user_actually_saves_a_supplier(self):
		"""Permission alone is not proof -- the record must really insert."""
		user = self._user(PURCHASE_USER, ["Purchase User"])
		group = frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0]
		frappe.set_user(user)
		try:
			doc = frappe.get_doc({
				"doctype": "Supplier", "supplier_name": f"PermSup {uuid.uuid4().hex[:6]}",
				"supplier_group": group,
			})
			doc.insert()
			self.assertTrue(frappe.db.exists("Supplier", doc.name))
		finally:
			frappe.set_user("Administrator")

	def test_quick_create_offers_supplier_to_a_purchase_user(self):
		user = self._user(PURCHASE_USER, ["Purchase User"])
		frappe.set_user(user)
		try:
			labels = {
				item["doctype"]
				for group in get_quick_create_actions()["groups"]
				for item in group["items"]
			}
			self.assertIn("Supplier", labels)
		finally:
			frappe.set_user("Administrator")

	def test_a_sales_only_user_still_cannot_create_a_supplier(self):
		"""The fix must widen buying roles, not remove the permission boundary."""
		user = self._user(SALES_ONLY_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			self.assertFalse(frappe.has_permission("Supplier", "create"))
			labels = {
				item["doctype"]
				for group in get_quick_create_actions()["groups"]
				for item in group["items"]
			}
			self.assertNotIn("Supplier", labels)
		finally:
			frappe.set_user("Administrator")

	def test_selling_side_parity_is_unchanged(self):
		user = self._user(SALES_ONLY_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			self.assertTrue(frappe.has_permission("Customer", "create"))
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
