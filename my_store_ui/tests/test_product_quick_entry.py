"""Product quick-entry: identifiers, prices, batch, locations, atomicity, security."""

from __future__ import annotations

import unittest

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product, get_product

SALES_USER = "smj-pqe-sales@example.com"
MADE: list[str] = []


class TestProductQuickEntry(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.whs = frappe.get_all("Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name")
		if not frappe.db.exists("User", SALES_USER):
			d = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "PQE",
			                    "send_welcome_email": 0, "enabled": 1})
			d.insert(ignore_permissions=True)
			d.append("roles", {"role": "Sales User"})
			d.save(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for code in MADE:
			for ip in frappe.get_all("Item Price", filters={"item_code": code}, pluck="name"):
				frappe.delete_doc("Item Price", ip, force=True, ignore_permissions=True)
			if frappe.db.exists("Item", code):
				frappe.delete_doc("Item", code, force=True, ignore_permissions=True)
		if frappe.db.exists("User", SALES_USER):
			frappe.delete_doc("User", SALES_USER, force=True, ignore_permissions=True)
		frappe.db.commit()

	def _base(self, **over):
		v = {"product_name": "PQE Test", "category": self.group, "material": "Steel", "size": "L",
		     "carton_qty": 12, "restock_qty": 20, "stock_location_1": self.whs[0],
		     "cost_price": 1000, "margin": 25, "wholesale_price": 1200, "retail_price": 1500, "department_price": 1350}
		v.update(over)
		return v

	def _create(self, **over):
		res = create_product(self._base(**over))
		MADE.append(res["name"])
		return res

	def test_product_id_and_sku_formats(self):
		res = self._create()
		self.assertRegex(res["product_id"], r"^P1\d{5}$")
		self.assertRegex(res["sku"], r"^5\d{3,}$")

	def test_ids_are_unique_across_creations(self):
		a = self._create()
		b = self._create()
		self.assertNotEqual(a["product_id"], b["product_id"])
		self.assertNotEqual(a["sku"], b["sku"])

	def test_all_four_item_prices_are_synced(self):
		res = self._create()
		prices = {r.price_list: flt(r.price_list_rate) for r in frappe.get_all(
			"Item Price", filters={"item_code": res["name"]}, fields=["price_list", "price_list_rate"])}
		self.assertEqual(prices.get("Standard Buying"), 1000.0)
		self.assertEqual(prices.get("Wholesale Price List"), 1200.0)
		self.assertEqual(prices.get("Retail Price List"), 1500.0)
		self.assertEqual(prices.get("Department Price List"), 1350.0)

	def test_selling_prices_are_selling_only(self):
		res = self._create()
		for pl in ("Wholesale Price List", "Retail Price List", "Department Price List"):
			row = frappe.get_all("Item Price", filters={"item_code": res["name"], "price_list": pl},
			                     fields=["buying", "selling"])[0]
			self.assertTrue(row.selling)
			self.assertFalse(row.buying)

	def test_new_stock_product_is_batch_managed(self):
		res = self._create()
		it = frappe.get_doc("Item", res["name"])
		self.assertTrue(it.has_batch_no)
		self.assertTrue(it.create_new_batch)
		self.assertTrue(it.batch_number_series)

	def test_stock_locations_and_reorder(self):
		if len(self.whs) < 2:
			self.skipTest("need 2 warehouses")
		res = self._create(stock_location_2=self.whs[1])
		it = frappe.get_doc("Item", res["name"])
		self.assertEqual(it.custom_stock_location_1, self.whs[0])
		self.assertEqual(it.custom_stock_location_2, self.whs[1])
		self.assertEqual(flt(next(r.warehouse_reorder_qty for r in it.reorder_levels)), 20.0)

	def test_duplicate_stock_location_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._create(stock_location_2=self.whs[0])

	def test_product_name_required(self):
		with self.assertRaises(frappe.ValidationError):
			create_product(self._base(product_name=""))

	def test_invalid_category_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			create_product(self._base(category="No Such Group XYZ"))

	def test_negative_values_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			create_product(self._base(carton_qty=-1))

	def test_edit_keeps_id_and_sku_and_no_duplicate_prices(self):
		res = self._create()
		create_product(self._base(product_name="PQE v2", department_price=1400), name=res["name"])
		it = frappe.get_doc("Item", res["name"])
		self.assertEqual(it.item_name, "PQE v2")
		self.assertEqual(it.item_code, res["product_id"])
		self.assertEqual(it.custom_sku, res["sku"])
		dept = frappe.get_all("Item Price", filters={"item_code": res["name"], "price_list": "Department Price List"})
		self.assertEqual(len(dept), 1)
		self.assertEqual(flt(get_product(res["name"])["department_price"]), 1400.0)

	def test_arbitrary_field_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			create_product({"product_name": "x", "category": self.group, "malicious_field": 1})

	def test_atomic_rollback_on_failure(self):
		"""A failure mid-way must not leave a half-created product."""
		before = frappe.db.count("Item")
		with self.assertRaises(frappe.ValidationError):
			# valid item fields but an invalid warehouse -> should raise before/at insert
			create_product(self._base(stock_location_1="No Such WH"))
		self.assertEqual(frappe.db.count("Item"), before)


if __name__ == "__main__":
	unittest.main()
