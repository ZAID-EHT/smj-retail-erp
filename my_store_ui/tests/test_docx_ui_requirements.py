"""UI requirements from ACCOUNT CREATION.docx that were previously missed.

- Three selling prices on the Product form: Wholesale, Retail AND Department.
- A default margin percentage that can be saved and reused.
- Warehouse drill-down: item-wise and batch-wise stock with date filtering.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt, nowdate

from my_store_ui.quick_entry.product import (
	DEPARTMENT_PRICE_LIST,
	create_product,
	get_default_margin,
	get_product,
	save_default_margin,
)
from my_store_ui.standalone import authorize_frontend_route
from my_store_ui.warehouse_stock import (
	get_warehouse_batches,
	get_warehouse_movements,
	get_warehouse_stock,
)

WHOLESALE = 1200.0
RETAIL = 1500.0
DEPARTMENT = 1350.0
SALES_USER = "docx-ui-sales@example.invalid"


class DocxUiBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name"
		)[0]

	def setUp(self):
		self.sp = f"docxui_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _product(self, **over):
		values = {
			"product_name": f"DocxUI {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": WHOLESALE,
			"retail_price": RETAIL, "department_price": DEPARTMENT,
		}
		values.update(over)
		return create_product(values)["name"]


class TestThreeSellingPrices(DocxUiBase):
	def test_department_price_list_exists_and_is_selling_only(self):
		row = frappe.db.get_value(
			"Price List", DEPARTMENT_PRICE_LIST, ["enabled", "selling", "buying"], as_dict=True
		)
		self.assertIsNotNone(row, "Department Price List must exist")
		self.assertTrue(row.enabled)
		self.assertTrue(row.selling)
		self.assertFalse(row.buying, "a Price Category must never be a buying list")

	def test_department_price_is_written_as_a_real_item_price(self):
		item = self._product()
		rate = frappe.db.get_value(
			"Item Price",
			{"item_code": item, "price_list": DEPARTMENT_PRICE_LIST, "selling": 1},
			"price_list_rate",
		)
		self.assertEqual(flt(rate), DEPARTMENT)

	def test_all_three_selling_prices_are_stored(self):
		item = self._product()
		prices = {
			r.price_list: flt(r.price_list_rate)
			for r in frappe.get_all(
				"Item Price", filters={"item_code": item, "selling": 1},
				fields=["price_list", "price_list_rate"],
			)
		}
		self.assertEqual(prices.get("Wholesale Price List"), WHOLESALE)
		self.assertEqual(prices.get("Retail Price List"), RETAIL)
		self.assertEqual(prices.get(DEPARTMENT_PRICE_LIST), DEPARTMENT)

	def test_get_product_returns_department_price_for_the_form(self):
		item = self._product()
		self.assertEqual(flt(get_product(item)["department_price"]), DEPARTMENT)

	def test_department_price_can_be_edited(self):
		item = self._product()
		create_product({
			"product_name": frappe.db.get_value("Item", item, "item_name"),
			"category": self.group, "stock_location_1": self.wh, "cost_price": 1000,
			"wholesale_price": WHOLESALE, "retail_price": RETAIL, "department_price": 1400,
		}, name=item)
		self.assertEqual(flt(get_product(item)["department_price"]), 1400.0)

	def test_negative_department_price_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			self._product(department_price=-5)

	def test_a_department_customer_is_priced_from_that_list(self):
		from my_store_ui.api import get_cart_pricing

		item = self._product()
		customer = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"Dept {uuid.uuid4().hex[:6]}",
			"customer_group": frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0],
			"territory": frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0],
			"default_price_list": DEPARTMENT_PRICE_LIST,
		}).insert(ignore_permissions=True).name
		result = get_cart_pricing(
			customer=customer, items=[{"item_code": item, "qty": 1}],
			warehouse=self.wh, company=self.company,
		)
		self.assertEqual(result["price_list"], DEPARTMENT_PRICE_LIST)
		self.assertEqual(flt(result["lines"][0]["rate"]), DEPARTMENT)


class TestDefaultMargin(DocxUiBase):
	def test_save_and_read_back_the_default_margin(self):
		save_default_margin(18)
		self.assertEqual(flt(get_default_margin()["margin"]), 18.0)

	def test_default_margin_can_be_changed(self):
		save_default_margin(12)
		save_default_margin(25)
		self.assertEqual(flt(get_default_margin()["margin"]), 25.0)

	def test_out_of_range_margin_is_refused(self):
		for value in (-1, 140):
			with self.assertRaises(frappe.ValidationError):
				save_default_margin(value)

	def test_an_unauthorised_user_cannot_change_the_default(self):
		if not frappe.db.exists("User", SALES_USER):
			user = frappe.get_doc({
				"doctype": "User", "email": SALES_USER, "first_name": "Docx",
				"send_welcome_email": 0,
			})
			user.insert(ignore_permissions=True)
			user.add_roles("Sales User")
		frappe.set_user(SALES_USER)
		try:
			with self.assertRaises(frappe.PermissionError):
				save_default_margin(30)
		finally:
			frappe.set_user("Administrator")


class TestWarehouseDrillDown(DocxUiBase):
	def _receive(self, item, qty, rate=1000):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": item, "qty": qty, "t_warehouse": self.wh, "basic_rate": rate}],
		})
		se.insert(ignore_permissions=True)
		se.submit()

	def test_route_resolves(self):
		self.assertEqual(
			authorize_frontend_route("/inventory/warehouse-stock")["outcome"], "allowed"
		)

	def test_item_wise_stock_reports_the_triplet(self):
		item = self._product()
		self._receive(item, 40)
		data = get_warehouse_stock(warehouse=self.wh, search=item)
		row = next((r for r in data["rows"] if r["item_code"] == item), None)
		self.assertIsNotNone(row, "the received product must appear")
		self.assertEqual(flt(row["actual_qty"]), 40.0)
		self.assertEqual(
			flt(row["available_to_sell"]), flt(row["actual_qty"]) - flt(row["reserved_qty"])
		)

	def test_batch_wise_stock_is_oldest_first(self):
		item = self._product()
		self._receive(item, 10, 1000)
		self._receive(item, 10, 1200)
		data = get_warehouse_batches(warehouse=self.wh, item_code=item)
		self.assertGreaterEqual(len(data["rows"]), 2)
		created = [r["created"] for r in data["rows"]]
		self.assertEqual(created, sorted(created), "batches must be listed oldest first")

	def test_movements_are_listed_with_direction(self):
		item = self._product()
		self._receive(item, 15)
		data = get_warehouse_movements(warehouse=self.wh, item_code=item)
		self.assertTrue(data["rows"])
		self.assertIn(data["rows"][0]["direction"], ("in", "out"))

	def test_date_filter_narrows_the_result(self):
		item = self._product()
		self._receive(item, 12)
		future = frappe.utils.add_days(nowdate(), 5)
		later = frappe.utils.add_days(nowdate(), 10)
		empty = get_warehouse_stock(warehouse=self.wh, from_date=future, to_date=later)
		self.assertFalse(
			[r for r in empty["rows"] if r["item_code"] == item],
			"a future-only window must not include today's receipt",
		)

	def test_inverted_date_range_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			get_warehouse_stock(
				warehouse=self.wh, from_date=nowdate(),
				to_date=frappe.utils.add_days(nowdate(), -5),
			)

	def test_out_of_stock_filter_excludes_stocked_products(self):
		item = self._product()
		self._receive(item, 25)
		data = get_warehouse_stock(warehouse=self.wh, stock_status="out_of_stock")
		self.assertFalse([r for r in data["rows"] if r["item_code"] == item])

	def test_invalid_stock_status_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			get_warehouse_stock(warehouse=self.wh, stock_status="whatever")

	def test_unknown_warehouse_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			get_warehouse_stock(warehouse="No-Such-Warehouse-XYZ")

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				get_warehouse_stock(warehouse=self.wh)
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
