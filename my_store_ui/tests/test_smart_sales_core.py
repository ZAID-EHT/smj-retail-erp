"""Core Smart Sales wholesale workflow: customer-first pricing + stock gating.

Builds its own controlled staging-only fixtures (a dedicated selling Price List,
a stock Item with an Item Price, a Customer whose default_price_list is that list,
and a customer-scoped Pricing Rule) so the assertions do not depend on demo data.
All fixtures are removed in tearDownClass. No Bin / Stock Ledger / GL is written
directly — the out-of-stock item simply has no Bin, so Available-to-Sell is 0.
"""
from __future__ import annotations

import unittest

import frappe

from my_store_ui.api import (
	_customer_price_list,
	create_draft_sales_order,
	get_bootstrap,
	get_cart_pricing,
)

COMPANY = "SMJ Retail ERP"
WAREHOUSE = "Main Warehouse - SMJ"
PRICE_LIST = "SMJ Core Test PL"
ITEM = "SMJ-CORE-TEST-ITEM"
CUSTOMER_NAME = "SMJ Core Test Customer"
LIST_RATE = 1000.0
RULE_DISCOUNT = 10.0


class TestSmartSalesCore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")
		if not frappe.db.exists("Price List", PRICE_LIST):
			frappe.get_doc({
				"doctype": "Price List", "price_list_name": PRICE_LIST,
				"selling": 1, "enabled": 1, "currency": "LKR",
			}).insert(ignore_permissions=True)
		if not frappe.db.exists("Item", ITEM):
			frappe.get_doc({
				"doctype": "Item", "item_code": ITEM, "item_name": "SMJ Core Test Item",
				"item_group": frappe.db.get_value("Item Group", {"is_group": 0}, "name"),
				"stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1,
			}).insert(ignore_permissions=True)
		if not frappe.db.exists("Item Price", {"item_code": ITEM, "price_list": PRICE_LIST}):
			frappe.get_doc({
				"doctype": "Item Price", "item_code": ITEM, "price_list": PRICE_LIST,
				"selling": 1, "price_list_rate": LIST_RATE, "currency": "LKR",
			}).insert(ignore_permissions=True)
		cls.customer = _ensure_customer(CUSTOMER_NAME, PRICE_LIST)
		# Customer-scoped 10% discount rule on the test item.
		if not frappe.db.exists("Pricing Rule", {"title": "SMJ Core Test Rule"}):
			frappe.get_doc({
				"doctype": "Pricing Rule", "title": "SMJ Core Test Rule",
				"apply_on": "Item Code", "price_or_product_discount": "Price",
				"selling": 1, "applicable_for": "Customer", "customer": cls.customer,
				"rate_or_discount": "Discount Percentage", "discount_percentage": RULE_DISCOUNT,
				"company": COMPANY, "items": [{"item_code": ITEM, "uom": "Nos"}],
			}).insert(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		for dt, name in [
			("Pricing Rule", frappe.db.get_value("Pricing Rule", {"title": "SMJ Core Test Rule"})),
			("Item Price", frappe.db.get_value("Item Price", {"item_code": ITEM, "price_list": PRICE_LIST})),
			("Item", ITEM), ("Customer", cls.customer if hasattr(cls, "customer") else None),
			("Price List", PRICE_LIST),
		]:
			if name and frappe.db.exists(dt, name):
				frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
		frappe.db.commit()

	def test_customer_price_list_resolves_to_customer_default(self):
		self.assertEqual(_customer_price_list(self.customer), PRICE_LIST)
		self.assertIsNone(_customer_price_list(None))

	def test_bootstrap_prices_against_the_customers_price_list(self):
		data = get_bootstrap(search=ITEM, customer=self.customer)
		self.assertEqual(data["customer"], self.customer)
		self.assertEqual(data["customer_price_list"], PRICE_LIST)
		row = next((i for i in data["items"] if i["item_code"] == ITEM), None)
		self.assertIsNotNone(row)
		self.assertEqual(row["rate"], LIST_RATE)

	def test_cart_pricing_applies_customer_pricing_rule(self):
		result = get_cart_pricing(
			customer=self.customer, company=COMPANY, warehouse=WAREHOUSE,
			items=[{"item_code": ITEM, "qty": 1}],
		)
		line = result["lines"][0]
		self.assertEqual(line["price_list_rate"], LIST_RATE)
		# The customer-scoped 10% rule must lower the effective rate below list.
		self.assertLess(line["rate"], LIST_RATE)
		self.assertEqual(line["source"], "pricing_rule")
		self.assertEqual(line["price_list"], PRICE_LIST)

	def test_a_different_customer_does_not_get_the_scoped_rule(self):
		other = _ensure_customer("SMJ Core Other Customer", PRICE_LIST)
		try:
			line = get_cart_pricing(
				customer=other, company=COMPANY, warehouse=WAREHOUSE,
				items=[{"item_code": ITEM, "qty": 1}],
			)["lines"][0]
			# Same price list, but no customer-scoped rule → rate stays at list.
			self.assertEqual(line["rate"], LIST_RATE)
			self.assertNotEqual(line["source"], "pricing_rule")
		finally:
			frappe.delete_doc("Customer", other, force=True, ignore_permissions=True)
			frappe.db.commit()

	def test_out_of_stock_item_reports_status_and_blocks_order(self):
		# The test item has no Bin, so Available-to-Sell is 0.
		line = get_cart_pricing(
			customer=self.customer, company=COMPANY, warehouse=WAREHOUSE,
			items=[{"item_code": ITEM, "qty": 3}],
		)["lines"][0]
		self.assertEqual(line["available_to_sell"], 0)
		self.assertEqual(line["stock_status"], "out_of_stock")

		with self.assertRaises(frappe.ValidationError):
			create_draft_sales_order({
				"request_id": frappe.generate_hash(length=12),
				"customer": self.customer, "company": COMPANY, "warehouse": WAREHOUSE,
				"price_list": PRICE_LIST, "items": [{"item_code": ITEM, "qty": 3}],
			})
		# No stray draft order was created for this customer+item.
		self.assertFalse(frappe.db.exists("Sales Order Item", {"item_code": ITEM}))


def _ensure_customer(name: str, price_list: str) -> str:
	existing = frappe.db.get_value("Customer", {"customer_name": name})
	if existing:
		return existing
	doc = frappe.get_doc({
		"doctype": "Customer", "customer_name": name,
		"customer_type": "Company",
		"customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name"),
		"territory": frappe.db.get_value("Territory", {"is_group": 0}, "name"),
		"default_price_list": price_list,
	}).insert(ignore_permissions=True)
	return doc.name
