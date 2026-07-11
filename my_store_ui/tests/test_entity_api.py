from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.entity_api import get_entity_list
from my_store_ui.services.entity_schemas import ENTITY_SCHEMAS, validate_registry_against_metadata


class TestEntityListApi(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")

	@classmethod
	def tearDownClass(cls):
		frappe.destroy()

	def test_registry_is_metadata_safe(self):
		validate_registry_against_metadata()
		self.assertEqual(set(ENTITY_SCHEMAS), {"customers", "items", "sales_orders"})

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


if __name__ == "__main__":
	unittest.main()
