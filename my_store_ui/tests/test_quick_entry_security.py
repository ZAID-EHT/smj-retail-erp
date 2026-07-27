"""Security for Product/Customer quick-entry: permissions, cost hiding, arbitrary payloads."""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui.quick_entry.customer import create_customer
from my_store_ui.quick_entry.product import create_product, get_product
from my_store_ui.quick_entry.options import search as options_search

SUFFIX = uuid.uuid4().hex[:6]
SALES_USER = f"smj-qesec-sales-{SUFFIX}@example.com"
ITEM_MANAGER = f"smj-qesec-im-{SUFFIX}@example.com"


def _make(email, roles):
	if frappe.db.exists("User", email):
		frappe.delete_doc("User", email, force=True, ignore_permissions=True)
	d = frappe.get_doc({"doctype": "User", "email": email, "first_name": "QESec",
	                    "send_welcome_email": 0, "enabled": 1})
	d.insert(ignore_permissions=True)
	for r in roles:
		d.append("roles", {"role": r})
	d.save(ignore_permissions=True)
	frappe.clear_cache(user=email)


class TestQuickEntrySecurity(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.wh = frappe.get_all("Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name")[0]
		_make(SALES_USER, ["Sales User"])
		_make(ITEM_MANAGER, ["Item Manager"])
		cls.made = []
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for code in cls.made:
			for ip in frappe.get_all("Item Price", filters={"item_code": code}, pluck="name"):
				frappe.delete_doc("Item Price", ip, force=True, ignore_permissions=True)
			if frappe.db.exists("Item", code):
				frappe.delete_doc("Item", code, force=True, ignore_permissions=True)
		for u in (SALES_USER, ITEM_MANAGER):
			if frappe.db.exists("User", u):
				frappe.delete_doc("User", u, force=True, ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.set_user("Administrator")

	def _base(self, **over):
		v = {"product_name": f"Sec {uuid.uuid4().hex[:5]}", "category": self.group,
		     "stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": 1200,
		     "retail_price": 1500, "department_price": 1350}
		v.update(over)
		return v

	def test_sales_user_cannot_create_product(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			create_product(self._base())

	def test_item_manager_without_price_perm_is_refused_atomically(self):
		"""Item Manager can create an Item but not Item Price -> refused, no residue."""
		frappe.set_user(ITEM_MANAGER)
		before = frappe.db.count("Item")
		with self.assertRaises(frappe.PermissionError):
			create_product(self._base())
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.count("Item"), before)

	def test_cost_price_hidden_from_sales_user(self):
		# Admin creates a priced product.
		frappe.set_user("Administrator")
		res = create_product(self._base())
		self.made.append(res["name"])
		# A Sales User reading it does not see the cost price.
		frappe.set_user(SALES_USER)
		detail = get_product(res["name"])
		self.assertFalse(detail["cost_visible"])
		self.assertIsNone(detail["cost_price"])
		# Selling prices remain visible.
		self.assertEqual(detail["retail_price"], 1500.0)

	def test_cross_company_warehouse_denied(self):
		"""A warehouse from another company is rejected."""
		other = frappe.get_all("Warehouse", filters={"is_group": 0, "company": ["!=", self.company], "disabled": 0}, pluck="name")
		if not other:
			self.skipTest("no second-company warehouse on this site")
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.PermissionError):
			create_product(self._base(stock_location_1=other[0]))

	def test_options_endpoint_rejects_arbitrary_kind(self):
		with self.assertRaises(frappe.ValidationError):
			options_search(kind="User")

	def test_customer_arbitrary_payload_rejected(self):
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.ValidationError):
			create_customer({"customer_name": "x", "price_category": "Retail Price List", "drop_table": 1})

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			create_product(self._base())
		with self.assertRaises(frappe.AuthenticationError):
			create_customer({"customer_name": "x"})


if __name__ == "__main__":
	unittest.main()
