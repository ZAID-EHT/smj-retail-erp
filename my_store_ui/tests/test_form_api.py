from __future__ import annotations

import unittest
from uuid import uuid4
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.form_api import _apply_item_pricing, _validate_items, _validate_payload, get_entity_form, save_entity_form, search_link_options
from my_store_ui.services.form_schemas import FORM_SCHEMAS, validate_form_registry_against_metadata


class TestRetailEntityForms(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
		frappe.connect()
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	@classmethod
	def tearDownClass(cls):
		frappe.destroy()

	def test_form_registry_matches_site_metadata_and_custom_fields(self):
		validate_form_registry_against_metadata()
		self.assertEqual(set(FORM_SCHEMAS), {"customers", "items", "sales_orders", "delivery_notes", "sales_invoices"})
		for fieldname in ("custom_product_material", "custom_product_size", "custom_supplier", "custom_purchase_price", "custom_additional_cost", "custom_total_cost", "custom_retail_profit_percentage", "custom_wholesale_profit_percentage", "custom_retail_price", "custom_wholesale_price", "custom_sku_prefix"):
			self.assertTrue(frappe.get_meta("Item").has_field(fieldname))

	def test_new_forms_load_only_the_approved_schema(self):
		for entity_key in FORM_SCHEMAS:
			with self.subTest(entity_key=entity_key):
				if FORM_SCHEMAS[entity_key].get("create_via_mapping_only"):
					continue
				result = get_entity_form(entity_key)
				self.assertEqual(result["entity"]["doctype"], FORM_SCHEMAS[entity_key]["doctype"])
				self.assertTrue(result["is_new"])

	def test_customer_insert_uses_erpnext_controller_and_rolls_back(self):
		"""Exercise the write path without persisting test business data."""
		group = frappe.get_list("Customer Group", pluck="name", limit_page_length=1)[0]
		territory = frappe.get_list("Territory", pluck="name", limit_page_length=1)[0]
		name = f"Retail ERP Form Test {uuid4().hex[:10]}"
		try:
			result = save_entity_form("customers", {"customer_name": name, "customer_type": "Company", "customer_group": group, "territory": territory, "email_id": "form-test@example.invalid"}, request_id=f"test-{uuid4().hex}")
			self.assertTrue(result["name"])
			self.assertTrue(frappe.db.exists("Customer", result["name"]))
		finally:
			frappe.db.rollback()

	def test_item_insert_recalculates_prices_and_rolls_back(self):
		item_group = frappe.get_list("Item Group", filters={"is_group": 0}, pluck="name", limit_page_length=1)[0]
		uom = frappe.get_list("UOM", pluck="name", limit_page_length=1)[0]
		code = f"RETAIL-FORM-{uuid4().hex[:9].upper()}"
		try:
			result = save_entity_form("items", {"item_code": code, "item_name": "Retail ERP Form Test Item", "item_group": item_group, "stock_uom": uom, "is_stock_item": 1, "custom_purchase_price": 1000, "custom_additional_cost": 100, "custom_retail_profit_percentage": 30, "custom_wholesale_profit_percentage": 15}, request_id=f"test-{uuid4().hex}")
			doc = frappe.get_doc("Item", result["name"])
			self.assertEqual(doc.custom_total_cost, 1100)
			self.assertEqual(doc.custom_retail_price, 1430)
			self.assertEqual(doc.custom_wholesale_price, 1265)
		finally:
			frappe.db.rollback()

	def test_draft_sales_order_insert_and_edit_path_roll_back(self):
		customer = frappe.get_list("Customer", filters={"disabled": 0}, pluck="name", limit_page_length=1)[0]
		company = frappe.defaults.get_global_default("company") or frappe.get_list("Company", pluck="name", limit_page_length=1)[0]
		item = frappe.get_list("Item", filters={"disabled": 0, "is_sales_item": 1}, pluck="name", limit_page_length=1)[0]
		warehouse = frappe.get_list("Warehouse", filters={"is_group": 0, "company": company}, pluck="name", limit_page_length=1)
		values = {"customer": customer, "company": company, "transaction_date": "2026-07-13", "delivery_date": "2026-07-14", "order_type": "Sales", "set_warehouse": warehouse[0] if warehouse else None, "items": [{"item_code": item, "qty": 1, "warehouse": warehouse[0] if warehouse else None}]}
		try:
			created = save_entity_form("sales_orders", values, request_id=f"test-{uuid4().hex}")
			doc = frappe.get_doc("Sales Order", created["name"])
			self.assertEqual(doc.docstatus, 0)
			edited = save_entity_form("sales_orders", values, name=doc.name, request_id=f"test-{uuid4().hex}")
			self.assertEqual(edited["name"], doc.name)
		finally:
			frappe.db.rollback()

	def test_item_pricing_is_recalculated_server_side(self):
		doc = frappe._dict(custom_purchase_price=1000, custom_additional_cost=100, custom_retail_profit_percentage=30, custom_wholesale_profit_percentage=15)
		_apply_item_pricing(doc)
		self.assertEqual(doc.custom_total_cost, 1100)
		self.assertEqual(doc.custom_retail_price, 1430)
		self.assertEqual(doc.custom_wholesale_price, 1265)

	def test_negative_and_wholesale_above_retail_prices_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			_apply_item_pricing(frappe._dict(custom_purchase_price=-1, custom_additional_cost=0, custom_retail_profit_percentage=30, custom_wholesale_profit_percentage=15))
		with self.assertRaises(frappe.ValidationError):
			_apply_item_pricing(frappe._dict(custom_purchase_price=100, custom_additional_cost=0, custom_retail_profit_percentage=15, custom_wholesale_profit_percentage=30))

	def test_unapproved_parent_and_child_fields_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			_validate_payload(FORM_SCHEMAS["items"], {"owner": "Administrator"})
		with self.assertRaises(frappe.ValidationError):
			_validate_items(FORM_SCHEMAS["sales_orders"], {"items": [{"item_code": "SKU008", "qty": 1, "owner": "Administrator"}]})

	def test_sales_order_requires_positive_quantity(self):
		with self.assertRaises(frappe.ValidationError):
			_validate_items(FORM_SCHEMAS["sales_orders"], {"items": [{"item_code": "SKU008", "qty": 0}]})

	def test_new_forms_require_create_permission_before_document_creation(self):
		with patch("my_store_ui.form_api.get_doctype_permissions", return_value={"can_create": False}), patch("my_store_ui.form_api.frappe.new_doc") as new_doc:
			with self.assertRaises(frappe.PermissionError):
				get_entity_form("customers")
			new_doc.assert_not_called()

	def test_link_search_rejects_non_registry_field(self):
		with self.assertRaises(frappe.ValidationError):
			search_link_options("items", "owner", "Admin")


if __name__ == "__main__":
	unittest.main()
