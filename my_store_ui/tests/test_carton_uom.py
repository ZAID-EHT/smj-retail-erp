"""Carton UOM is a real ERPNext conversion, not a display number.

Carton Qty entered on the Product form must become a UOM Conversion Detail row on
the Item so that selling and buying in Cartons converts to stock units through
ERPNext's own controllers. Everything runs in a savepoint and rolls back.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.uom import (
	CARTON_UOM,
	allowed_uoms,
	conversion_factor,
	get_item_uoms,
	to_stock_qty,
)

SUFFIX = uuid.uuid4().hex[:6]


class TestCartonUom(unittest.TestCase):
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
		self.sp = f"carton_{SUFFIX}_{uuid.uuid4().hex[:4]}"
		frappe.db.savepoint(self.sp)

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _product(self, carton_qty=None):
		values = {
			"product_name": f"Carton {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": 1200,
			"retail_price": 1500,
		}
		if carton_qty is not None:
			values["carton_qty"] = carton_qty
		return create_product(values)["name"]

	def test_carton_qty_creates_uom_conversion(self):
		item = self._product(carton_qty=12)
		factor = frappe.db.get_value(
			"UOM Conversion Detail", {"parent": item, "parenttype": "Item", "uom": CARTON_UOM},
			"conversion_factor",
		)
		self.assertEqual(flt(factor), 12.0)
		self.assertEqual(conversion_factor(item, CARTON_UOM), 12.0)

	def test_stock_uom_row_is_preserved_at_factor_one(self):
		item = self._product(carton_qty=6)
		stock_uom = frappe.db.get_value("Item", item, "stock_uom")
		self.assertEqual(conversion_factor(item, stock_uom), 1.0)
		self.assertIn(stock_uom, allowed_uoms(item))
		self.assertIn(CARTON_UOM, allowed_uoms(item))

	def test_no_carton_qty_means_no_carton_uom(self):
		item = self._product()
		self.assertNotIn(CARTON_UOM, allowed_uoms(item))

	def test_carton_qty_of_one_is_not_a_conversion(self):
		"""A carton of 1 unit is meaningless -- it must not create a Carton UOM."""
		item = self._product(carton_qty=1)
		self.assertNotIn(CARTON_UOM, allowed_uoms(item))

	def test_editing_carton_qty_updates_the_conversion(self):
		item = self._product(carton_qty=12)
		create_product({
			"product_name": frappe.db.get_value("Item", item, "item_name"), "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": 1200,
			"retail_price": 1500, "carton_qty": 24,
		}, name=item)
		self.assertEqual(conversion_factor(item, CARTON_UOM), 24.0)
		rows = frappe.get_all(
			"UOM Conversion Detail", filters={"parent": item, "parenttype": "Item", "uom": CARTON_UOM}
		)
		self.assertEqual(len(rows), 1, "editing must update the row, not add a duplicate")

	def test_clearing_carton_qty_removes_the_conversion(self):
		item = self._product(carton_qty=12)
		create_product({
			"product_name": frappe.db.get_value("Item", item, "item_name"), "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": 1200,
			"retail_price": 1500, "carton_qty": 0,
		}, name=item)
		self.assertNotIn(CARTON_UOM, allowed_uoms(item))

	def test_to_stock_qty_converts_cartons(self):
		item = self._product(carton_qty=12)
		self.assertEqual(to_stock_qty(item, 3, CARTON_UOM), 36.0)
		stock_uom = frappe.db.get_value("Item", item, "stock_uom")
		self.assertEqual(to_stock_qty(item, 3, stock_uom), 3.0)
		self.assertEqual(to_stock_qty(item, 3, None), 3.0)

	def test_undeclared_uom_is_rejected(self):
		"""A caller cannot invent a factor to inflate the stock movement."""
		item = self._product(carton_qty=12)
		with self.assertRaises(frappe.ValidationError):
			conversion_factor(item, "Pallet-Not-Declared")

	def test_carton_uom_is_whole_number(self):
		self._product(carton_qty=12)
		self.assertTrue(frappe.db.get_value("UOM", CARTON_UOM, "must_be_whole_number"))

	def test_get_item_uoms_lists_unit_and_carton(self):
		item = self._product(carton_qty=12)
		res = get_item_uoms(item)
		by_uom = {r["uom"]: r for r in res["uoms"]}
		self.assertEqual(by_uom[CARTON_UOM]["conversion_factor"], 12.0)
		self.assertFalse(by_uom[CARTON_UOM]["is_stock_uom"])
		self.assertTrue(by_uom[res["stock_uom"]]["is_stock_uom"])

	def test_get_item_uoms_rejects_unknown_item(self):
		with self.assertRaises(frappe.ValidationError):
			get_item_uoms("NO-SUCH-ITEM-XYZ")


if __name__ == "__main__":
	unittest.main()
