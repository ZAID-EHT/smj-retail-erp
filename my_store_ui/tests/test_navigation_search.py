from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]

from my_store_ui.search import (
	SEARCH_REGISTRY,
	_approved_fields,
	_document_results,
	_page_results,
	_report_results,
	_searchable_meta,
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

		# `my_store_ui.search.frappe` is the frappe module itself, so patching
		# `get_list` here replaces it process-wide -- including the `get_all`
		# that `Meta.set_custom_permissions` uses while loading metadata.  Only
		# stub the searched doctype and delegate everything else to the real
		# implementation, or frappe's own internals receive these fake rows.
		real_get_list = frappe.get_list

		def only_stub_searched_doctype(doctype, *args, **kwargs):
			if doctype == SEARCH_REGISTRY[0]["doctype"]:
				return [customer]
			return real_get_list(doctype, *args, **kwargs)

		with (
			patch("my_store_ui.search.SEARCH_REGISTRY", (SEARCH_REGISTRY[0],)),
			patch("my_store_ui.search.frappe.get_list", side_effect=only_stub_searched_doctype),
			patch("my_store_ui.search.frappe.has_permission", side_effect=document_permission),
		):
			self.assertEqual(_document_results("Restricted", 5), [])

		with patch("my_store_ui.search.frappe.has_permission", return_value=False):
			self.assertEqual(_report_results("General Ledger", 5), [])

	def test_unusable_registry_doctype_is_skipped_without_breaking_search(self):
		"""Regression: one stale registry entry must not take global search down.

		`frappe.get_meta` raises `DoesNotExistError` for a removed, renamed or
		`None` doctype.  Before the fix that exception escaped `_document_results`
		and failed the whole request instead of skipping the single bad entry.
		"""
		valid = SEARCH_REGISTRY[0]
		broken = (
			{**valid, "doctype": "Zzz Removed Doctype"},
			{**valid, "doctype": None},
			{**valid, "doctype": ""},
		)

		# Each bad entry on its own: skipped, no exception, no results.
		for entry in broken:
			with self.subTest(doctype=entry["doctype"]):
				with patch("my_store_ui.search.SEARCH_REGISTRY", (entry,)):
					self.assertEqual(_document_results("Restricted", 5), [])
				self.assertEqual(_searchable_meta(entry["doctype"]), None)

		# A bad entry must not stop a following valid entry from being searched.
		with patch("my_store_ui.search.SEARCH_REGISTRY", (broken[0], valid)):
			searched = []
			real_get_list = frappe.get_list

			def record_get_list(doctype, *args, **kwargs):
				searched.append(doctype)
				return real_get_list(doctype, *args, **kwargs)

			with patch("my_store_ui.search.frappe.get_list", side_effect=record_get_list):
				_document_results("Restricted", 5)
			self.assertIn(valid["doctype"], searched)
			self.assertNotIn("Zzz Removed Doctype", searched)

		# global_search stays healthy end to end with a stale entry present.
		with patch("my_store_ui.search.SEARCH_REGISTRY", (broken[0], valid)):
			result = global_search("Restricted", limit=10)
		self.assertEqual(result["minimum_length"], 2)
		self.assertTrue(all(row["doctype"] != "Zzz Removed Doctype" for row in result["results"]))

	def test_unusable_registry_entry_does_not_bypass_permissions(self):
		"""A skipped entry must not become an unchecked read of another doctype."""
		entry = {**SEARCH_REGISTRY[0], "doctype": "Zzz Removed Doctype"}
		with (
			patch("my_store_ui.search.SEARCH_REGISTRY", (entry,)),
			patch("my_store_ui.search.frappe.has_permission", return_value=True),
		):
			self.assertEqual(_document_results("Restricted", 5), [])
		self.assertEqual(_approved_fields(entry), ["name"])

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
