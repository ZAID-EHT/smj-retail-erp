from __future__ import annotations

import unittest
from unittest.mock import patch

import frappe


from my_store_ui.entity_api import get_entity_detail, get_entity_list
from my_store_ui.services.entity_schemas import DETAIL_SCHEMAS, ENTITY_SCHEMAS, validate_registry_against_metadata


class TestEntityListApi(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")


	def test_registry_is_metadata_safe(self):
		validate_registry_against_metadata()
		self.assertEqual(set(ENTITY_SCHEMAS), {"customers", "items", "sales_orders", "delivery_notes", "sales_invoices", "payment_entries"})
		self.assertEqual(set(DETAIL_SCHEMAS), {"customers", "items", "sales_orders"})

	def test_each_approved_entity_returns_only_approved_fields(self):
		for entity_key, schema in ENTITY_SCHEMAS.items():
			with self.subTest(entity_key=entity_key):
				result = get_entity_list(entity_key, page_size=1)
				self.assertLessEqual(result["pagination"]["page_size"], 100)
				for record in result["records"]:
					self.assertLessEqual(set(record), set(schema["fields"]))

	def test_page_size_is_capped(self):
		result = get_entity_list("items", page_size=999)
		self.assertEqual(result["pagination"]["page_size"], 100)

	def test_unknown_entity_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			get_entity_list("not_approved")

	def test_unapproved_filter_sort_and_field_selection_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			get_entity_list("customers", filters={"owner": "Administrator"})
		with self.assertRaises(frappe.ValidationError):
			get_entity_list("items", sort_field="valuation_rate")
		with self.assertRaises(frappe.ValidationError):
			get_entity_list("items", fields=["valuation_rate"])

	@patch("my_store_ui.entity_api.frappe.get_list")
	@patch("my_store_ui.entity_api.get_doctype_permissions")
	def test_permission_denial_occurs_before_any_record_query(self, permissions, get_list):
		permissions.return_value = {"can_read": False, "can_create": False}
		with self.assertRaises(frappe.PermissionError):
			get_entity_list("customers")
		get_list.assert_not_called()

	def test_real_detail_records_use_approved_fields_and_children(self):
		fixtures = {
			"customers": frappe.get_list("Customer", filters={"disabled": 0}, pluck="name", limit_page_length=1)[0],
			"items": frappe.get_list("Item", filters={"disabled": 0}, pluck="name", limit_page_length=1)[0],
			"sales_orders": frappe.get_list("Sales Order", filters={"docstatus": 1}, pluck="name", limit_page_length=1)[0],
		}
		for entity_key, name in fixtures.items():
			with self.subTest(entity_key=entity_key):
				result = get_entity_detail(entity_key, name)
				schema = DETAIL_SCHEMAS[entity_key]
				approved = set(schema["fields"]) | set(schema.get("computed_fields", ())) | set(schema.get("optional_custom_fields", ()))
				self.assertLessEqual(set(result["document"]), approved)
				approved_children = {child["fieldname"]: {column[0] for column in child["columns"]} for child in schema["child_tables"]}
				for table in result["child_tables"]:
					for row in table["rows"]:
						self.assertLessEqual(set(row), approved_children[table["fieldname"]])

	def test_sales_order_detail_returns_items_read_only(self):
		so_name = frappe.get_list("Sales Order", filters={"docstatus": 1}, pluck="name", limit_page_length=1)[0]
		result = get_entity_detail("sales_orders", so_name)
		items = next(table for table in result["child_tables"] if table["fieldname"] == "items")
		self.assertGreater(items["count"], 0)
		self.assertIn("item_code", items["rows"][0])

	def test_unknown_detail_entity_invalid_name_and_missing_record_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			get_entity_detail("not_approved", "anything")
		with self.assertRaises(frappe.ValidationError):
			get_entity_detail("items", "")
		with self.assertRaises(frappe.DoesNotExistError):
			get_entity_detail("items", "THIS-ITEM-DOES-NOT-EXIST")

	@patch("my_store_ui.entity_api.frappe.get_doc")
	@patch("my_store_ui.entity_api.frappe.get_list")
	def test_unavailable_detail_does_not_load_or_leak_document(self, get_list, get_doc):
		get_list.return_value = []
		with self.assertRaisesRegex(frappe.DoesNotExistError, "not found or unavailable"):
			get_entity_detail("customers", "restricted-or-missing")
		get_doc.assert_not_called()

	@patch("my_store_ui.entity_api.frappe.get_list")
	@patch("my_store_ui.entity_api.frappe.has_permission", return_value=False)
	def test_detail_doctype_permission_denial_occurs_before_record_query(self, _has_permission, get_list):
		with self.assertRaises(frappe.PermissionError):
			get_entity_detail("sales_orders", "SAL-ORD-2026-00006")
		get_list.assert_not_called()

	@patch("my_store_ui.entity_api.can_open_standard_desk", return_value=False)
	def test_standard_desk_urls_are_omitted_for_ordinary_users(self, _allow_desk):
		customer = frappe.get_list("Customer", filters={"disabled": 0}, pluck="name", limit_page_length=1)[0]
		result = get_entity_detail("customers", customer)
		self.assertIsNone(result["entity"]["desk_route"])
		self.assertTrue(all("desk_route" not in row for group in result["related"] for row in group["records"]))

	def test_unreadable_related_doctype_is_omitted(self):
		original = frappe.has_permission

		def permission(doctype, *args, **kwargs):
			if doctype == "Sales Invoice":
				return False
			return original(doctype, *args, **kwargs)

		customer = frappe.get_list("Customer", filters={"disabled": 0}, pluck="name", limit_page_length=1)[0]
		with patch("my_store_ui.entity_api.frappe.has_permission", side_effect=permission):
			result = get_entity_detail("customers", customer)
		self.assertNotIn("Sales Invoice", {group["doctype"] for group in result["related"]})


if __name__ == "__main__":
	unittest.main()
