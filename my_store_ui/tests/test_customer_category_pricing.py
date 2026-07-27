"""On a sale, the price auto-applies from the customer's Price Category.

A product created via quick-entry has Wholesale 1200 / Retail 1500. A customer whose
Price Category is Wholesale must be priced at 1200; a Retail customer at 1500 -- via
the standard get_cart_pricing (ERPNext get_item_details), no pricing duplicated.
Runs in a savepoint and rolls back.
"""

from __future__ import annotations

import json
import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.api import get_cart_pricing
from my_store_ui.quick_entry.customer import create_customer
from my_store_ui.quick_entry.product import create_product

SUFFIX = uuid.uuid4().hex[:6]


class TestCustomerCategoryPricing(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all("Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name")[0]
		cls.sp = f"cat_pricing_{SUFFIX}"
		frappe.db.savepoint(cls.sp)
		try:
			res = create_product({"product_name": f"CatPrice {SUFFIX}", "category": cls.group,
			                      "stock_location_1": cls.wh, "cost_price": 1000,
			                      "wholesale_price": 1200, "retail_price": 1500})
			cls.item = res["name"]
			cls.wholesale_customer = create_customer({
				"customer_name": f"Wholesale Cust {SUFFIX}", "price_category": "Wholesale Price List",
				"payment_type": "Non-Credit"})["name"]
			cls.retail_customer = create_customer({
				"customer_name": f"Retail Cust {SUFFIX}", "price_category": "Retail Price List",
				"payment_type": "Non-Credit"})["name"]
		except Exception:
			frappe.db.rollback(save_point=cls.sp)
			raise

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=cls.sp)

	def _price(self, customer):
		result = get_cart_pricing(customer=customer, items=json.dumps([{"item_code": self.item, "qty": 1}]),
		                          warehouse=self.wh, company=self.company)
		self.assertTrue(result["lines"], "cart pricing returned no lines")
		return flt(result["lines"][0].get("price_list_rate"))

	def test_wholesale_customer_gets_wholesale_price(self):
		self.assertEqual(self._price(self.wholesale_customer), 1200.0)

	def test_retail_customer_gets_retail_price(self):
		self.assertEqual(self._price(self.retail_customer), 1500.0)

	def test_changing_customer_changes_price(self):
		# The whole point: the same product reprices per customer category.
		self.assertNotEqual(self._price(self.wholesale_customer), self._price(self.retail_customer))


if __name__ == "__main__":
	unittest.main()
