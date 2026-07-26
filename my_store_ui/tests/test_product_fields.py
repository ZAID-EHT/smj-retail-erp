"""The seven Product quick-entry fields added to the curated form.

Colour, Published, Purchase UOM, Selling UOM, Safety Stock are scalar Item fields;
Default Warehouse and Reorder Level/Qty are backed by the item_defaults and
reorder_levels child tables and must not duplicate on edit. Item Price
synchronisation, permissions and rollback must all still hold.
"""

from __future__ import annotations

import json
import unittest

import frappe
from frappe.utils import flt

from my_store_ui.form_api import save_entity_form

ITEM = "SMJ-PFIELDS-TEST"


class TestProductFields(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.warehouse = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company}, pluck="name"
		)[0]

	def tearDown(self):
		frappe.set_user("Administrator")
		for name in frappe.get_all("Item Price", filters={"item_code": ITEM}, pluck="name"):
			frappe.delete_doc("Item Price", name, force=True, ignore_permissions=True)
		if frappe.db.exists("Item", ITEM):
			frappe.delete_doc("Item", ITEM, force=True, ignore_permissions=True)
		frappe.db.commit()

	def _save(self, **overrides):
		values = {
			"item_code": ITEM, "item_name": "SMJ PFields", "item_group": self.group,
			"stock_uom": "Nos", "is_stock_item": 1,
			"custom_purchase_price": 100, "custom_additional_cost": 0,
			"custom_retail_profit_percentage": 50, "custom_wholesale_profit_percentage": 20,
		}
		values.update(overrides)
		name = ITEM if frappe.db.exists("Item", ITEM) else None
		return save_entity_form("items", json.dumps(values), name=name)

	def test_all_seven_fields_persist_on_create(self):
		self._save(
			custom_product_colour="Red", custom_published=1,
			purchase_uom="Nos", sales_uom="Nos", safety_stock=5,
			default_warehouse=self.warehouse, reorder_level=10, reorder_qty=20,
		)
		it = frappe.get_doc("Item", ITEM)
		self.assertEqual(it.custom_product_colour, "Red")
		self.assertEqual(it.custom_published, 1)
		self.assertEqual(it.purchase_uom, "Nos")
		self.assertEqual(it.sales_uom, "Nos")
		self.assertEqual(flt(it.safety_stock), 5.0)
		defaults = [r for r in it.item_defaults if r.company == self.company]
		self.assertEqual(len(defaults), 1)
		self.assertEqual(defaults[0].default_warehouse, self.warehouse)
		reorder = [r for r in it.reorder_levels if r.warehouse == self.warehouse]
		self.assertEqual(len(reorder), 1)
		self.assertEqual(flt(reorder[0].warehouse_reorder_level), 10.0)
		self.assertEqual(flt(reorder[0].warehouse_reorder_qty), 20.0)

	def test_editing_does_not_duplicate_child_rows(self):
		self._save(default_warehouse=self.warehouse, reorder_level=10, reorder_qty=20, custom_product_colour="Red")
		self._save(default_warehouse=self.warehouse, reorder_level=12, reorder_qty=24, custom_product_colour="Blue")
		it = frappe.get_doc("Item", ITEM)
		self.assertEqual(it.custom_product_colour, "Blue")
		self.assertEqual(len([r for r in it.item_defaults if r.company == self.company]), 1)
		reorder = [r for r in it.reorder_levels if r.warehouse == self.warehouse]
		self.assertEqual(len(reorder), 1)
		self.assertEqual(flt(reorder[0].warehouse_reorder_level), 12.0)

	def test_item_price_sync_still_runs_with_the_new_fields(self):
		self._save(
			custom_product_colour="Green", purchase_uom="Nos", safety_stock=3,
			default_warehouse=self.warehouse, reorder_level=5, reorder_qty=5,
		)
		prices = {
			row.price_list: flt(row.price_list_rate)
			for row in frappe.get_all("Item Price", filters={"item_code": ITEM}, fields=["price_list", "price_list_rate"])
		}
		# 100 cost, 50% retail / 20% wholesale.
		self.assertEqual(prices.get("Retail Price List"), 150.0)
		self.assertEqual(prices.get("Wholesale Price List"), 120.0)
		self.assertEqual(prices.get("Standard Buying"), 100.0)

	def test_reorder_row_is_skipped_without_a_warehouse(self):
		"""A reorder level with no default warehouse must not create an invalid row."""
		self._save(reorder_level=10, custom_product_colour="Grey")
		it = frappe.get_doc("Item", ITEM)
		self.assertEqual(it.reorder_levels, [])


if __name__ == "__main__":
	unittest.main()
