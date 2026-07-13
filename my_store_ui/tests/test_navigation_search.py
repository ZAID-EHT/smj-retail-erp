from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.search import SEARCH_REGISTRY, global_search
from my_store_ui.services.frontend_routes import get_permitted_navigation


class TestRetailNavigationAndSearch(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
		frappe.connect()
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	@classmethod
	def tearDownClass(cls):
		frappe.destroy()

	def test_navigation_contains_real_permission_filtered_links(self):
		navigation = get_permitted_navigation()
		by_name = {module["name"]: module for module in navigation}
		self.assertIn("sales", by_name)
		self.assertIn("operations", by_name)
		self.assertIn("admin", by_name)
		self.assertGreater(len(by_name["sales"]["links"]), 5)
		self.assertIn("/sales/orders", {link["path"] for link in by_name["sales"]["links"]})
		self.assertNotIn("Detailed permitted links will be added", str(navigation))

	def test_search_registry_is_server_owned_and_allowlisted(self):
		doctypes = {entry["doctype"] for entry in SEARCH_REGISTRY}
		self.assertIn("Customer", doctypes)
		self.assertIn("Item", doctypes)
		self.assertIn("Sales Invoice", doctypes)
		self.assertIn("Purchase Invoice", doctypes)
		self.assertIn("Payment Entry", doctypes)
		self.assertNotIn("DocType", doctypes)

	def test_real_search_is_limited_and_routes_stay_inside_retail_erp(self):
		result = global_search("ACC", limit=10)
		self.assertLessEqual(len(result["results"]), 10)
		for row in result["results"]:
			self.assertTrue(row["route"].startswith("/"))
			self.assertNotIn("/app/", row["route"])
			self.assertIn(row["doctype"], {entry["doctype"] for entry in SEARCH_REGISTRY})

	def test_minimum_length_and_permission_filtering(self):
		self.assertEqual(global_search("A")["results"], [])
		self.assertEqual(global_search("%%")["results"], [])
		with patch("my_store_ui.search.frappe.has_permission", return_value=False):
			self.assertEqual(global_search("ACC")["results"], [])

	def test_guest_search_is_rejected_without_data(self):
		original = frappe.session.user
		try:
			frappe.session.user = "Guest"
			with self.assertRaises(frappe.AuthenticationError):
				global_search("ACC")
		finally:
			frappe.session.user = original


if __name__ == "__main__":
	unittest.main()
