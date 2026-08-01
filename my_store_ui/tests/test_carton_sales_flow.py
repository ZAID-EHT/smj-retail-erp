"""Selling in Cartons converts to stock units through standard ERPNext.

Covers the Smart Sales path: cart pricing quotes per Carton, availability is judged
in stock units, and the resulting Sales Order line carries the real conversion so
ERPNext computes stock_qty itself. Savepoint + rollback; no residue.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.api import create_draft_sales_order, get_cart_pricing
from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.uom import CARTON_UOM

SUFFIX = uuid.uuid4().hex[:6]
CARTON_SIZE = 12


class TestCartonSalesFlow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name"
		)[0]
		cls.customer = frappe.get_all("Customer", filters={"disabled": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"carton_sale_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"CartonSale {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": 1200,
			"retail_price": 1500, "carton_qty": CARTON_SIZE,
		})["name"]

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _receive(self, qty, rate=1000):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": self.item, "qty": qty, "t_warehouse": self.wh, "basic_rate": rate}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		return se

	def test_cart_pricing_reports_carton_conversion(self):
		self._receive(120)
		res = get_cart_pricing(
			customer=self.customer, items=[{"item_code": self.item, "qty": 2, "uom": CARTON_UOM}],
			warehouse=self.wh, company=self.company,
		)
		line = res["lines"][0]
		self.assertEqual(line["uom"], CARTON_UOM)
		self.assertEqual(flt(line["conversion_factor"]), float(CARTON_SIZE))
		self.assertEqual(flt(line["stock_qty"]), 24.0)

	def test_max_qty_is_expressed_in_cartons(self):
		self._receive(120)
		res = get_cart_pricing(
			customer=self.customer, items=[{"item_code": self.item, "qty": 1, "uom": CARTON_UOM}],
			warehouse=self.wh, company=self.company,
		)
		# 120 stock units available / 12 per carton = 10 cartons.
		self.assertEqual(flt(res["lines"][0]["max_qty"]), 10.0)

	def test_availability_is_judged_in_stock_units(self):
		"""5 cartons = 60 units must be refused when only 24 units are in stock."""
		self._receive(24)
		with self.assertRaises(frappe.ValidationError):
			create_draft_sales_order({
				"request_id": uuid.uuid4().hex, "customer": self.customer, "company": self.company,
				"warehouse": self.wh,
				"items": [{"item_code": self.item, "qty": 5, "uom": CARTON_UOM}],
			})

	def test_sales_order_line_carries_real_conversion(self):
		self._receive(120)
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": self.customer, "company": self.company,
			"warehouse": self.wh,
			"items": [{"item_code": self.item, "qty": 3, "uom": CARTON_UOM}],
		})
		so = frappe.get_doc("Sales Order", res["name"])
		row = so.items[0]
		self.assertEqual(row.uom, CARTON_UOM)
		self.assertEqual(flt(row.conversion_factor), float(CARTON_SIZE))
		# ERPNext computes stock_qty itself from qty * conversion_factor.
		self.assertEqual(flt(row.stock_qty), 36.0)

	def test_browser_cannot_forge_a_conversion_factor(self):
		"""An undeclared UOM is refused outright -- no silent fallback to 1."""
		self._receive(120)
		with self.assertRaises(frappe.ValidationError):
			create_draft_sales_order({
				"request_id": uuid.uuid4().hex, "customer": self.customer, "company": self.company,
				"warehouse": self.wh,
				"items": [{"item_code": self.item, "qty": 1, "uom": "Pallet-Forged"}],
			})

	def test_unit_sale_still_works_without_uom(self):
		self._receive(50)
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": self.customer, "company": self.company,
			"warehouse": self.wh,
			"items": [{"item_code": self.item, "qty": 4}],
		})
		row = frappe.get_doc("Sales Order", res["name"]).items[0]
		self.assertEqual(flt(row.conversion_factor), 1.0)
		self.assertEqual(flt(row.stock_qty), 4.0)


if __name__ == "__main__":
	unittest.main()
