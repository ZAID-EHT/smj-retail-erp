from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]

from my_store_ui.search import (
	SEARCH_REGISTRY,
	_document_results,
	_page_results,
	_report_results,
	global_search,
)
from my_store_ui.services.frontend_routes import get_permitted_navigation


class TestRetailNavigationAndSearch(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")


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
			self.assertIn(row["kind"], {"page", "report", "document"})
			if row["kind"] == "document":
				self.assertIn(row["doctype"], {entry["doctype"] for entry in SEARCH_REGISTRY})

	def test_pages_functions_and_reports_are_organised(self):
		smart_sales = global_search("smart sales")
		self.assertTrue(any(row["route"] == "/smart-sales" for row in smart_sales["results"]))
		self.assertTrue(all(row["group"] in {"Pages & Functions", "Reports", "Documents"} for row in smart_sales["results"]))

		receipts = global_search("purchase receipt")
		self.assertTrue(any(row["route"] == "/purchases/receipts" for row in receipts["results"]))

		petty_cash = global_search("petty cash")
		self.assertTrue(any(row["route"] == "/finance/journal-entries" for row in petty_cash["results"]))

	def test_frontend_search_presents_group_counts_and_result_types(self):
		source = (BENCH_PATH / "apps/my_store_ui/frontend/src/components/shell/GlobalSearch.vue").read_text()
		self.assertIn("group.records.length", source)
		self.assertIn("result.type_label", source)
		self.assertIn("Pages & Functions", (BENCH_PATH / "apps/my_store_ui/my_store_ui/search.py").read_text())

	def test_route_authorisation_is_rechecked_before_page_is_returned(self):
		navigation = [{
			"name": "restricted", "label": "Restricted", "path": "/restricted",
			"links": [{"label": "Quux Permission Launcher", "path": "/restricted/quux"}],
		}]
		with (
			patch("my_store_ui.search.get_permitted_navigation", return_value=navigation),
			patch("my_store_ui.search.resolve_frontend_route", return_value=({"name": "restricted"}, {})),
			patch("my_store_ui.search.route_is_permitted", return_value=False),
		):
			self.assertEqual(_page_results("quux permission launcher", 5), [])

	def test_document_level_denial_and_report_denial_omit_results(self):
		customer = frappe._dict(name="RESTRICTED-CUSTOMER", customer_name="Restricted Customer", mobile_no="")

		def document_permission(_doctype, _permission, doc=None, **_kwargs):
			return doc is None

		with (
			patch("my_store_ui.search.SEARCH_REGISTRY", (SEARCH_REGISTRY[0],)),
			patch("my_store_ui.search.frappe.get_list", return_value=[customer]),
			patch("my_store_ui.search.frappe.has_permission", side_effect=document_permission),
		):
			self.assertEqual(_document_results("Restricted", 5), [])

		with patch("my_store_ui.search.frappe.has_permission", return_value=False):
			self.assertEqual(_report_results("General Ledger", 5), [])

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
