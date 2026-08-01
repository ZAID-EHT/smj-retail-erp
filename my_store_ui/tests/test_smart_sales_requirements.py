"""Smart Sales behaviour required by the ACCOUNT CREATION document.

Covers: carton quantity exposed on the catalogue, a wholesale customer being able
to order below a full carton, the customer's Price Category driving the rate, and
the cart repricing when the customer changes.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.api import create_draft_sales_order, get_bootstrap, get_cart_pricing
from my_store_ui.quick_entry.product import create_product

CARTON_SIZE = 12
WHOLESALE = 1200.0
RETAIL = 1500.0


class TestSmartSalesRequirements(unittest.TestCase):
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

	def setUp(self):
		self.sp = f"ssreq_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"SSReq {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": WHOLESALE,
			"retail_price": RETAIL, "carton_qty": CARTON_SIZE,
		})["name"]
		self._receive(120)

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _receive(self, qty):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": self.item, "qty": qty, "t_warehouse": self.wh, "basic_rate": 1000}],
		})
		se.insert(ignore_permissions=True)
		se.submit()

	def _customer(self, price_list):
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": f"SSReq {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
			"default_price_list": price_list,
		}).insert(ignore_permissions=True).name

	# --- carton quantity ---

	def test_catalogue_exposes_carton_quantity(self):
		"""The product card must be able to show Carton Qty."""
		data = get_bootstrap(page_length=100, search=self.item)
		row = next((i for i in data["items"] if i["item_code"] == self.item), None)
		self.assertIsNotNone(row, "the product must appear in the catalogue")
		self.assertEqual(flt(row["carton_qty"]), float(CARTON_SIZE))

	def test_wholesale_customer_may_order_below_a_full_carton(self):
		"""Explicit business rule: an under-carton quantity must not be blocked."""
		customer = self._customer("Wholesale Price List")
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": customer, "company": self.company,
			"warehouse": self.wh,
			"items": [{"item_code": self.item, "qty": 5}],   # 5 < carton of 12
		})
		order = frappe.get_doc("Sales Order", res["name"])
		self.assertEqual(flt(order.items[0].qty), 5.0)

	def test_a_single_unit_below_carton_is_accepted(self):
		customer = self._customer("Wholesale Price List")
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": customer, "company": self.company,
			"warehouse": self.wh, "items": [{"item_code": self.item, "qty": 1}],
		})
		self.assertTrue(res["name"])

	# --- price category ---

	def test_wholesale_customer_is_priced_from_the_wholesale_list(self):
		customer = self._customer("Wholesale Price List")
		res = get_cart_pricing(
			customer=customer, items=[{"item_code": self.item, "qty": 1}],
			warehouse=self.wh, company=self.company,
		)
		self.assertEqual(res["price_list"], "Wholesale Price List")
		self.assertEqual(flt(res["lines"][0]["rate"]), WHOLESALE)

	def test_retail_customer_is_priced_from_the_retail_list(self):
		customer = self._customer("Retail Price List")
		res = get_cart_pricing(
			customer=customer, items=[{"item_code": self.item, "qty": 1}],
			warehouse=self.wh, company=self.company,
		)
		self.assertEqual(res["price_list"], "Retail Price List")
		self.assertEqual(flt(res["lines"][0]["rate"]), RETAIL)

	def test_changing_the_customer_reprices_the_cart(self):
		"""The same cart must reprice when the customer changes."""
		wholesale = self._customer("Wholesale Price List")
		retail = self._customer("Retail Price List")
		cart = [{"item_code": self.item, "qty": 3}]
		first = get_cart_pricing(customer=wholesale, items=cart, warehouse=self.wh, company=self.company)
		second = get_cart_pricing(customer=retail, items=cart, warehouse=self.wh, company=self.company)
		self.assertEqual(flt(first["lines"][0]["rate"]), WHOLESALE)
		self.assertEqual(flt(second["lines"][0]["rate"]), RETAIL)

	def test_the_order_uses_the_customers_price_list_not_the_site_default(self):
		customer = self._customer("Wholesale Price List")
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": customer, "company": self.company,
			"warehouse": self.wh, "items": [{"item_code": self.item, "qty": 2}],
		})
		order = frappe.get_doc("Sales Order", res["name"])
		self.assertEqual(order.selling_price_list, "Wholesale Price List")
		self.assertEqual(flt(order.items[0].rate), WHOLESALE)

	def test_price_comes_from_item_price_records(self):
		"""The rate must trace to a real ERPNext Item Price, not a frontend field."""
		rate = frappe.db.get_value(
			"Item Price",
			{"item_code": self.item, "price_list": "Wholesale Price List", "selling": 1},
			"price_list_rate",
		)
		self.assertEqual(flt(rate), WHOLESALE)


if __name__ == "__main__":
	unittest.main()
