from __future__ import annotations

import unittest
from pathlib import Path

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.analytics_pages import get_sales_funnel, get_warehouse_capacity, search_link
from my_store_ui.audit.parity_registry import PAGE_OVERRIDES
from my_store_ui.priority_pages import get_priority_route_definition


class TestAnalyticsPages(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def _company(self, page):
		companies = search_link(page, "company", "")
		return companies[0]["value"] if companies else None

	def test_native_pages_resolve_to_real_vue_components(self):
		self.assertEqual(get_priority_route_definition("/sales/funnel")["component"], "sales_funnel")
		self.assertEqual(get_priority_route_definition("/inventory/warehouse-capacity")["component"], "warehouse_capacity")
		self.assertEqual(PAGE_OVERRIDES["sales-funnel"][2], "/retail-erp/sales/funnel")
		self.assertEqual(PAGE_OVERRIDES["warehouse-capacity-summary"][2], "/retail-erp/inventory/warehouse-capacity")

	def test_sales_funnel_reads_live_permitted_records(self):
		company = self._company("sales-funnel")
		if not company:
			self.skipTest("No permitted Company on site1")
		result = get_sales_funnel("2020-01-01", "2035-12-31", company)
		self.assertEqual(result["filters"]["company"], company)
		self.assertEqual([row["label"] for row in result["funnel"]], ["Active Leads", "Opportunities", "Quotations", "Converted"])
		self.assertTrue(all(isinstance(row["value"], int) for row in result["funnel"]))

	def test_warehouse_capacity_uses_bounded_standard_dashboard_results(self):
		company = self._company("warehouse-capacity-summary")
		if not company:
			self.skipTest("No permitted Company on site1")
		result = get_warehouse_capacity(company=company)
		self.assertLessEqual(len(result["records"]), 10)
		for row in result["records"]:
			self.assertTrue(frappe.get_list("Item", filters={"name": row["item_code"]}, pluck="name", limit_page_length=1))
			self.assertTrue(frappe.get_list("Warehouse", filters={"name": row["warehouse"]}, pluck="name", limit_page_length=1))

	def test_invalid_capacity_sort_is_rejected(self):
		company = self._company("warehouse-capacity-summary")
		if not company:
			self.skipTest("No permitted Company on site1")
		with self.assertRaises(frappe.ValidationError):
			get_warehouse_capacity(company=company, sort_by="name; drop table")

	def test_guest_cannot_access_analytics_or_searches(self):
		frappe.set_user("Guest")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			search_link("sales-funnel", "company", "")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			get_sales_funnel("2026-01-01", "2026-12-31", "SMJ")

	def test_frontend_wiring_and_backend_have_no_generic_method_rpc(self):
		route_page = (APP_PATH / "frontend/src/pages/priority/PriorityRoutePage.vue").read_text()
		service = (APP_PATH / "frontend/src/services/analyticsPages.js").read_text()
		backend = (APP_PATH / "my_store_ui/analytics_pages.py").read_text()
		self.assertIn("SalesFunnelPage", route_page)
		self.assertIn("WarehouseCapacityPage", route_page)
		self.assertIn("get_sales_funnel", service)
		self.assertIn("get_warehouse_capacity", service)
		self.assertNotIn("ignore_permissions", backend)
		self.assertNotIn("frappe.call(", backend)


if __name__ == "__main__":
	unittest.main()
