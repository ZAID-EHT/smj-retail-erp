"""Daily operations dashboard: real counts and permission filtering."""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.api import create_draft_sales_order
from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.credit import NON_CREDIT_CUSTOMER
from my_store_ui.wholesale.operations_dashboard import get_operations_dashboard
from my_store_ui.wholesale.purchasing import create_purchase_order

RATE = 1200.0
SALES_USER = "ops-dash-sales@example.invalid"


class TestOperationsDashboard(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name"
		)[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
		cls.supplier_group = frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"ops_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _product(self):
		return create_product({
			"product_name": f"Ops {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": RATE,
			"retail_price": 1500,
		})["name"]

	def _customer(self):
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": f"OpsCust {uuid.uuid4().hex[:6]}",
			"custom_credit_type": NON_CREDIT_CUSTOMER, "customer_group": self.customer_group,
			"territory": self.territory, "default_price_list": "Wholesale Price List",
		}).insert(ignore_permissions=True).name

	def _receive(self, item, qty):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": item, "qty": qty, "t_warehouse": self.wh, "basic_rate": 1000}],
		})
		se.insert(ignore_permissions=True)
		se.submit()

	def test_dashboard_returns_all_sections(self):
		data = get_operations_dashboard(self.company)
		self.assertEqual(data["company"], self.company)
		for section in ("sales", "inventory", "purchasing"):
			self.assertIn(section, data)
		self.assertIn("awaiting_delivery", data["sales"])
		self.assertIn("open_orders", data["purchasing"])

	def test_new_order_increases_awaiting_delivery(self):
		item = self._product()
		self._receive(item, 50)
		customer = self._customer()
		before = get_operations_dashboard(self.company)["sales"]["awaiting_delivery"]
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": customer, "company": self.company,
			"warehouse": self.wh, "items": [{"item_code": item, "qty": 5}],
		})
		frappe.get_doc("Sales Order", res["name"]).submit()
		after = get_operations_dashboard(self.company)["sales"]["awaiting_delivery"]
		self.assertEqual(after, before + 1)

	def test_new_purchase_order_increases_open_orders(self):
		item = self._product()
		supplier = frappe.get_doc({
			"doctype": "Supplier", "supplier_name": f"OpsSup {uuid.uuid4().hex[:6]}",
			"supplier_group": self.supplier_group,
		}).insert(ignore_permissions=True).name
		before = get_operations_dashboard(self.company)["purchasing"]["open_orders"]
		create_purchase_order(
			supplier=supplier, company=self.company, warehouse=self.wh,
			items=[{"item_code": item, "qty": 10, "rate": 1000}], submit=1,
			request_id=uuid.uuid4().hex,
		)
		after = get_operations_dashboard(self.company)["purchasing"]["open_orders"]
		self.assertEqual(after, before + 1)

	def test_administrator_sees_financial_figures(self):
		data = get_operations_dashboard(self.company)
		self.assertTrue(data["shows_financials"])
		self.assertIsNotNone(data["finance"])
		self.assertIn("customer_outstanding", data["finance"])

	def test_inventory_section_reports_availability(self):
		item = self._product()
		self._receive(item, 50)
		inventory = get_operations_dashboard(self.company)["inventory"]
		self.assertGreaterEqual(flt(inventory["available_to_sell"]), 50.0)

	def test_non_finance_user_is_denied_financial_figures(self):
		"""A user without a finance role must not receive money totals."""
		if not frappe.db.exists("User", SALES_USER):
			user = frappe.get_doc({
				"doctype": "User", "email": SALES_USER, "first_name": "Ops Sales",
				"send_welcome_email": 0,
			})
			user.insert(ignore_permissions=True)
			user.add_roles("Sales User")
		frappe.set_user(SALES_USER)
		try:
			data = get_operations_dashboard(self.company)
			self.assertFalse(data["shows_financials"])
			self.assertIsNone(data["finance"])
			self.assertNotIn("receivable_total", data["sales"])
			self.assertNotIn("overdue_amount", data["sales"])
		finally:
			frappe.set_user("Administrator")

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				get_operations_dashboard(self.company)
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
