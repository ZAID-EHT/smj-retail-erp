"""Phase 7 regression: product prices reach ERPNext's pricing engine.

The confirmed defect this covers: `_apply_item_pricing` computed retail/wholesale
prices into `custom_*` fields only, so no `Item Price` existed and
`get_item_details` -- and therefore Smart Sales, quotations and every transaction --
never saw a price for products created through the SMJ product form.
"""

from __future__ import annotations

import json
import unittest

import frappe
from frappe.utils import flt, nowdate

from my_store_ui.form_api import ITEM_PRICE_SYNC, _resolve_price_list, save_entity_form

ITEM_CODE = "SMJ-PRICE-SYNC-TEST"
PURCHASE, ADDITIONAL = 1000.0, 200.0
RETAIL_PCT, WHOLESALE_PCT = 50.0, 25.0
TOTAL_COST = PURCHASE + ADDITIONAL              # 1200
EXPECTED_RETAIL = TOTAL_COST * 1.5              # 1800
EXPECTED_WHOLESALE = TOTAL_COST * 1.25          # 1500

# Item Manager can create an Item but, in stock ERPNext, cannot price one.
ITEM_MANAGER_USER = "smj-price-item-manager@example.com"
PRICE_MANAGER_USER = "smj-price-master-manager@example.com"


class TestItemPriceSync(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.item_group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls._make_user(ITEM_MANAGER_USER, ["Item Manager"])
		cls._make_user(PRICE_MANAGER_USER, ["Item Manager", "Sales Master Manager", "Purchase Master Manager"])
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for user in (ITEM_MANAGER_USER, PRICE_MANAGER_USER):
			if frappe.db.exists("User", user):
				frappe.delete_doc("User", user, force=True, ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def _make_user(cls, email: str, roles: list[str]) -> None:
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		doc = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "SMJ Price Test",
			"send_welcome_email": 0, "enabled": 1,
		})
		doc.insert(ignore_permissions=True)
		for role in roles:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)
		frappe.clear_cache(user=email)

	def tearDown(self):
		frappe.set_user("Administrator")
		for name in frappe.get_all("Item Price", filters={"item_code": ITEM_CODE}, pluck="name"):
			frappe.delete_doc("Item Price", name, force=True, ignore_permissions=True)
		if frappe.db.exists("Item", ITEM_CODE):
			frappe.delete_doc("Item", ITEM_CODE, force=True, ignore_permissions=True)
		frappe.db.commit()

	def _create_product(self, name: str | None = None, **overrides):
		values = {
			"item_code": ITEM_CODE,
			"item_name": "SMJ Price Sync Test",
			"item_group": self.item_group,
			"stock_uom": "Nos",
			"is_stock_item": 1,
			"custom_purchase_price": PURCHASE,
			"custom_additional_cost": ADDITIONAL,
			"custom_retail_profit_percentage": RETAIL_PCT,
			"custom_wholesale_profit_percentage": WHOLESALE_PCT,
		}
		values.update(overrides)
		return save_entity_form("items", json.dumps(values), name=name)

	def _edit_product(self, **overrides):
		return self._create_product(name=ITEM_CODE, **overrides)

	def _prices(self) -> dict[str, float]:
		return {
			row.price_list: flt(row.price_list_rate)
			for row in frappe.get_all(
				"Item Price", filters={"item_code": ITEM_CODE},
				fields=["price_list", "price_list_rate"],
			)
		}

	def test_every_configured_price_list_is_usable(self):
		"""A misconfigured list would silently skip a price, so fail loudly here."""
		for target in ITEM_PRICE_SYNC:
			with self.subTest(fieldname=target["fieldname"]):
				resolved = _resolve_price_list(target)
				self.assertIsNotNone(
					resolved,
					f"{target['price_list']} is missing, disabled, or not "
					f"{target['flag']}-enabled, so {target['fieldname']} cannot sync",
				)
				self.assertTrue(frappe.db.get_value("Price List", resolved, target["flag"]))

	def test_creating_a_product_writes_standard_item_prices(self):
		self._create_product()
		prices = self._prices()
		self.assertEqual(len(prices), 3, f"expected 3 Item Price rows, got {prices}")
		self.assertEqual(prices.get("Retail Price List"), EXPECTED_RETAIL)
		self.assertEqual(prices.get("Wholesale Price List"), EXPECTED_WHOLESALE)
		self.assertEqual(prices.get("Standard Buying"), PURCHASE)
		# The custom fields still carry the computed values for the form.
		item = frappe.get_doc("Item", ITEM_CODE)
		self.assertEqual(flt(item.custom_total_cost), TOTAL_COST)
		self.assertEqual(flt(item.custom_retail_price), EXPECTED_RETAIL)
		self.assertEqual(flt(item.custom_wholesale_price), EXPECTED_WHOLESALE)

	def test_synced_price_is_visible_to_the_pricing_engine(self):
		"""The whole point: get_item_details must now return the retail price."""
		from erpnext.stock.get_item_details import get_item_details

		self._create_product()
		company = frappe.get_all("Company", pluck="name")[0]
		details = get_item_details({
			"doctype": "Sales Order",
			"company": company,
			"item_code": ITEM_CODE,
			"qty": 1,
			"selling_price_list": "Retail Price List",
			"price_list_currency": frappe.db.get_value("Price List", "Retail Price List", "currency"),
			"currency": frappe.db.get_value("Company", company, "default_currency"),
			"conversion_rate": 1,
			"plc_conversion_rate": 1,
			"transaction_date": nowdate(),
			"customer": None,
		}, for_validate=True)
		self.assertEqual(flt(details.get("price_list_rate")), EXPECTED_RETAIL)

	def test_wholesale_price_list_is_selling_only(self):
		"""A wholesale price must apply to sales and never to purchasing.

		Selling-disabled would mean the price never applies to a sale; buying-enabled
		would let the marked-up wholesale rate be picked as a purchase cost, because
		ERPNext stamps the list's flags onto every Item Price row.
		"""
		details = frappe.db.get_value(
			"Price List", "Wholesale Price List", ["buying", "selling", "enabled"], as_dict=True
		)
		self.assertTrue(details.enabled)
		self.assertTrue(details.selling, "Wholesale Price List must be selling-enabled")
		self.assertFalse(details.buying, "Wholesale Price List must not be buying-enabled")

	def test_retail_and_wholesale_rows_are_selling_only_and_purchase_is_buying_only(self):
		"""The three prices must stay separate at the Item Price row level."""
		self._create_product()
		rows = {
			row.price_list: row
			for row in frappe.get_all(
				"Item Price", filters={"item_code": ITEM_CODE},
				fields=["price_list", "buying", "selling"],
			)
		}
		for price_list in ("Retail Price List", "Wholesale Price List"):
			with self.subTest(price_list=price_list):
				self.assertTrue(rows[price_list].selling)
				self.assertFalse(rows[price_list].buying, "a selling price must not be usable as a cost")
		self.assertTrue(rows["Standard Buying"].buying)
		self.assertFalse(rows["Standard Buying"].selling, "a purchase cost must not be sellable")

	def test_editing_a_product_updates_instead_of_duplicating_item_prices(self):
		self._create_product()
		self._edit_product(custom_purchase_price=2000.0)
		prices = self._prices()
		self.assertEqual(len(prices), 3, f"prices must be updated, not duplicated: {prices}")
		new_total = 2000.0 + ADDITIONAL
		self.assertEqual(prices["Retail Price List"], new_total * 1.5)
		self.assertEqual(prices["Wholesale Price List"], new_total * 1.25)
		self.assertEqual(prices["Standard Buying"], 2000.0)

	def test_clearing_a_price_removes_the_item_price(self):
		self._create_product()
		self.assertIn("Standard Buying", self._prices())
		# Zero cost and zero margins mean every computed price is zero.
		self._edit_product(
			custom_purchase_price=0.0, custom_additional_cost=0.0,
			custom_retail_profit_percentage=0.0, custom_wholesale_profit_percentage=0.0,
		)
		self.assertEqual(self._prices(), {}, "cleared prices must stop applying")

	def test_pricing_validation_still_rejects_impossible_margins(self):
		with self.assertRaises(frappe.ValidationError):
			self._create_product(custom_retail_profit_percentage=10.0, custom_wholesale_profit_percentage=50.0)
		self.assertFalse(frappe.db.exists("Item", ITEM_CODE))

	# -- ownership: rows entered deliberately elsewhere must survive -------------

	def test_a_customer_specific_price_is_never_overwritten(self):
		"""A negotiated party price is not ours to touch."""
		self._create_product()
		customer = frappe.get_all("Customer", pluck="name")[0]
		negotiated = frappe.get_doc({
			"doctype": "Item Price", "item_code": ITEM_CODE, "price_list": "Retail Price List",
			"price_list_rate": 999.0, "customer": customer,
		}).insert(ignore_permissions=True)

		self._edit_product(custom_purchase_price=2000.0)

		self.assertEqual(flt(frappe.db.get_value("Item Price", negotiated.name, "price_list_rate")), 999.0)
		owned = frappe.get_all(
			"Item Price", filters={"item_code": ITEM_CODE, "price_list": "Retail Price List", "customer": ["is", "not set"]},
			fields=["price_list_rate"],
		)
		self.assertEqual(len(owned), 1)
		self.assertEqual(flt(owned[0].price_list_rate), (2000.0 + ADDITIONAL) * 1.5)

	def test_a_legacy_row_without_a_uom_is_adopted_not_duplicated(self):
		"""Rows imported before ERPNext defaulted uom must be updated in place."""
		self._create_product()
		retail = frappe.get_all(
			"Item Price", filters={"item_code": ITEM_CODE, "price_list": "Retail Price List"}, pluck="name"
		)[0]
		frappe.db.set_value("Item Price", retail, "uom", None, update_modified=False)

		self._edit_product(custom_purchase_price=2000.0)

		rows = frappe.get_all(
			"Item Price", filters={"item_code": ITEM_CODE, "price_list": "Retail Price List"},
			fields=["name", "price_list_rate"],
		)
		self.assertEqual(len(rows), 1, "the legacy row must be reused, not duplicated")
		self.assertEqual(rows[0].name, retail)
		self.assertEqual(flt(rows[0].price_list_rate), (2000.0 + ADDITIONAL) * 1.5)

	def test_duplicate_owned_rows_converge_to_a_single_price(self):
		"""Two owned rows would keep applying a stale rate, so extras are removed."""
		self._create_product()
		# A second row is reachable via a different valid_from, which ERPNext permits.
		stale = frappe.get_doc({
			"doctype": "Item Price", "item_code": ITEM_CODE, "price_list": "Retail Price List",
			"price_list_rate": 1.0, "valid_from": "2020-01-01",
		}).insert(ignore_permissions=True)
		self.assertEqual(
			frappe.db.count("Item Price", {"item_code": ITEM_CODE, "price_list": "Retail Price List"}), 2
		)

		self._edit_product(custom_purchase_price=2000.0)

		rows = frappe.get_all(
			"Item Price", filters={"item_code": ITEM_CODE, "price_list": "Retail Price List"},
			fields=["name", "price_list_rate"],
		)
		self.assertEqual(len(rows), 1, "duplicates must converge to one owned row")
		self.assertEqual(flt(rows[0].price_list_rate), (2000.0 + ADDITIONAL) * 1.5)
		self.assertFalse(frappe.db.exists("Item Price", stale.name))

	# -- permissions ------------------------------------------------------------

	def test_pricing_a_product_without_item_price_rights_is_refused_atomically(self):
		"""ERPNext restricts Item Price to master managers.

		An Item Manager can create an Item but not price it, so the save must fail
		with an actionable message and leave no half-created product behind.
		"""
		savepoint = "item_price_perm"
		frappe.db.savepoint(savepoint)
		try:
			frappe.set_user(ITEM_MANAGER_USER)
			self.assertTrue(frappe.has_permission("Item", "create"))
			self.assertFalse(frappe.has_permission("Item Price", "create"))
			with self.assertRaises(frappe.PermissionError) as caught:
				self._create_product()
			message = str(caught.exception)
			self.assertIn("Item Price", message)
			self.assertIn("Sales Master Manager", message)
		finally:
			frappe.set_user("Administrator")
			frappe.db.rollback(save_point=savepoint)
		self.assertFalse(
			frappe.db.exists("Item", ITEM_CODE), "a refused price must not leave an unpriced product"
		)

	def test_an_unpriced_product_is_still_allowed_without_item_price_rights(self):
		"""Nothing needs writing, so the permission gate must not fire."""
		savepoint = "item_price_noprice"
		frappe.db.savepoint(savepoint)
		try:
			frappe.set_user(ITEM_MANAGER_USER)
			self._create_product(
				custom_purchase_price=0.0, custom_additional_cost=0.0,
				custom_retail_profit_percentage=0.0, custom_wholesale_profit_percentage=0.0,
			)
			self.assertTrue(frappe.db.exists("Item", ITEM_CODE))
			self.assertEqual(frappe.db.count("Item Price", {"item_code": ITEM_CODE}), 0)
		finally:
			frappe.set_user("Administrator")
			frappe.db.rollback(save_point=savepoint)

	def test_a_master_manager_can_create_a_priced_product(self):
		"""The same flow succeeds once the standard ERPNext roles are held."""
		savepoint = "item_price_master"
		frappe.db.savepoint(savepoint)
		try:
			frappe.set_user(PRICE_MANAGER_USER)
			self.assertTrue(frappe.has_permission("Item Price", "create"))
			self._create_product()
			prices = self._prices()
			self.assertEqual(len(prices), 3)
			self.assertEqual(prices["Retail Price List"], EXPECTED_RETAIL)
		finally:
			frappe.set_user("Administrator")
			frappe.db.rollback(save_point=savepoint)


if __name__ == "__main__":
	unittest.main()
