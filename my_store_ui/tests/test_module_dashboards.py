from __future__ import annotations

import unittest
from pathlib import Path

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]

from my_store_ui.module_dashboards import (
	get_accounts_dashboard,
	get_admin_dashboard,
	get_buying_dashboard,
	get_crm_dashboard,
	get_operations_dashboard,
	get_payments_dashboard,
	get_selling_dashboard,
	get_stock_dashboard,
)

APP_PATH = BENCH_PATH / "apps" / "my_store_ui"

ACCOUNTS_CARD_KEYS = {
	"outstanding-receivables", "outstanding-payables", "overdue-receivables",
	"total-incoming-bills", "total-outgoing-bills",
}
ACCOUNTS_CHART_KEYS = {
	"accounts-payable-ageing", "accounts-receivable-ageing", "budget-variance",
	"incoming-bills-purchase-invoice", "outgoing-bills-sales-invoice", "profit-and-loss",
}
PAYMENTS_CARD_KEYS = {"total-incoming-payment", "total-outgoing-payment"}
PAYMENTS_CHART_KEYS = {"bank-balance"}
BUYING_CARD_KEYS = {
	"active-suppliers", "annual-purchase", "average-order-values", "purchase-orders-count",
	"purchase-orders-to-bill", "purchase-orders-to-receive", "total-purchase-amount",
}
BUYING_CHART_KEYS = {"material-request-analysis", "purchase-order-analysis", "purchase-order-trends", "top-suppliers"}
CRM_CARD_KEYS = {"open-pipeline-value", "new-lead-last-1-month", "new-opportunity-last-1-month", "open-opportunity", "won-opportunity-last-1-month"}
CRM_CHART_KEYS = {
	"incoming-leads", "lead-source", "opportunities-via-campaigns", "opportunity-trends",
	"territory-wise-opportunity-count", "territory-wise-sales", "won-opportunities",
}
SELLING_CARD_KEYS = {
	"active-customers", "annual-sales", "average-sales-order-value", "sales-orders-count",
	"sales-orders-to-bill", "sales-orders-to-deliver", "total-sales-amount",
}
SELLING_CHART_KEYS = {"item-wise-annual-sales", "sales-order-analysis", "sales-order-trends", "top-customers"}
STOCK_CARD_KEYS = {"total-active-items", "total-stock-value", "total-warehouses"}
STOCK_CHART_KEYS = {
	"delivery-trends", "item-shortage-summary", "oldest-items", "purchase-receipt-trends",
	"stock-value-by-item-group", "warehouse-wise-stock-value",
}
OPERATIONS_CARD_KEYS = {"open-projects", "open-tasks", "overdue-tasks", "open-issues", "active-assets"}
OPERATIONS_CHART_KEYS = {"project-status", "task-status", "tasks-created-trend", "issue-priority", "asset-status"}
ADMIN_CARD_KEYS = {"enabled-users", "disabled-users", "roles", "companies", "active-warehouses", "recent-errors"}
ADMIN_CHART_KEYS = {"user-growth", "user-types", "role-assignment", "error-activity", "scheduler-status"}
CUSTOM_CARD_KEYS = {
	"outstanding-receivables", "outstanding-payables", "overdue-receivables", "open-pipeline-value",
}


def _keys(collection, field="key"):
	return {entry[field] for entry in collection}


class TestModuleDashboards(unittest.TestCase):
	"""All 25 number cards + 28 dashboard charts + 6 dashboards required by the
	corrected production-parity registry, computed from real ERPNext data.
	Every assertion runs against site1 (Administrator, read-only) — no
	ignore_permissions, no site config or schema change."""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_accounts_dashboard_covers_its_registry_keys_with_real_data(self):
		result = get_accounts_dashboard()
		self.assertEqual(_keys(result["cards"]), ACCOUNTS_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), ACCOUNTS_CHART_KEYS)
		for card in result["cards"]:
			self.assertIsInstance(card["value"], (int, float))
		ageing = next(c for c in result["charts"] if c["key"] == "accounts-payable-ageing")
		self.assertEqual({bar["label"] for bar in ageing["bars"]}, {"0-30", "30-60", "60-90", "90+"})

	def test_payments_dashboard_covers_its_registry_keys(self):
		result = get_payments_dashboard()
		self.assertEqual(_keys(result["cards"]), PAYMENTS_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), PAYMENTS_CHART_KEYS)

	def test_buying_dashboard_covers_its_registry_keys_with_real_totals(self):
		result = get_buying_dashboard()
		self.assertEqual(_keys(result["cards"]), BUYING_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), BUYING_CHART_KEYS)
		po_count = next(c for c in result["cards"] if c["key"] == "purchase-orders-count")
		self.assertEqual(po_count["value"], frappe.db.count("Purchase Order", {"docstatus": 1}))

	def test_crm_dashboard_covers_its_registry_keys(self):
		result = get_crm_dashboard()
		self.assertEqual(_keys(result["cards"]), CRM_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), CRM_CHART_KEYS)

	def test_selling_dashboard_covers_its_registry_keys_with_real_totals(self):
		result = get_selling_dashboard()
		self.assertEqual(_keys(result["cards"]), SELLING_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), SELLING_CHART_KEYS)
		so_count = next(c for c in result["cards"] if c["key"] == "sales-orders-count")
		self.assertEqual(so_count["value"], frappe.db.count("Sales Order", {"docstatus": 1}))

	def test_stock_dashboard_covers_its_registry_keys_and_is_internally_consistent(self):
		result = get_stock_dashboard()
		self.assertEqual(_keys(result["cards"]), STOCK_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), STOCK_CHART_KEYS)
		total_card = next(c for c in result["cards"] if c["key"] == "total-stock-value")
		by_group = next(c for c in result["charts"] if c["key"] == "stock-value-by-item-group")
		by_warehouse = next(c for c in result["charts"] if c["key"] == "warehouse-wise-stock-value")
		# Both breakdowns and the headline card share the same actual_qty > 0
		# filter, so they must foot to (approximately) the same total.
		self.assertAlmostEqual(total_card["value"], sum(s["value"] for s in by_group["segments"]), delta=1)
		self.assertAlmostEqual(total_card["value"], sum(b["value"] for b in by_warehouse["bars"]), delta=1)

	def test_operations_dashboard_uses_real_permitted_workload(self):
		result = get_operations_dashboard()
		self.assertEqual(_keys(result["cards"]), OPERATIONS_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), OPERATIONS_CHART_KEYS)
		for card in result["cards"]:
			self.assertIsInstance(card["value"], (int, float))

	def test_admin_dashboard_exposes_safe_aggregate_signals_only(self):
		result = get_admin_dashboard()
		self.assertEqual(_keys(result["cards"]), ADMIN_CARD_KEYS)
		self.assertEqual(_keys(result["charts"]), ADMIN_CHART_KEYS)
		self.assertNotIn("password", str(result).lower())
		self.assertNotIn("secret", str(result).lower())

	def test_guest_cannot_read_module_dashboards(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				get_accounts_dashboard()
			with self.assertRaises(frappe.AuthenticationError):
				get_stock_dashboard()
			with self.assertRaises(frappe.AuthenticationError):
				get_operations_dashboard()
			with self.assertRaises(frappe.AuthenticationError):
				get_admin_dashboard()
		finally:
			frappe.set_user("Administrator")

	def test_module_dashboards_never_use_raw_sql_or_ignore_permissions(self):
		source = (APP_PATH / "my_store_ui" / "module_dashboards.py").read_text()
		self.assertNotIn("ignore_permissions=True", source)
		self.assertNotIn("frappe.db.sql", source)
		self.assertNotIn("frappe.db.count", source)
		self.assertNotIn("frappe.db.get_value", source)

	def test_frontend_wires_standard_and_custom_module_dashboards(self):
		service = (APP_PATH / "frontend/src/services/moduleDashboards.js").read_text()
		page = (APP_PATH / "frontend/src/pages/priority/ModuleDashboardPage.vue").read_text()
		for loader in ("getAccountsDashboard", "getPaymentsDashboard", "getBuyingDashboard", "getCrmDashboard", "getSellingDashboard", "getStockDashboard", "getOperationsDashboard", "getAdminDashboard"):
			self.assertIn(loader, service)
		self.assertIn("MODULE_DASHBOARD_LOADERS", page)
		self.assertIn("MODULE_PRESENTATIONS", page)
		for module in ("sales", "purchases", "finance", "crm", "operations", "admin"):
			self.assertIn(f"{module}:", page)
		self.assertIn("SmjChartCard", page)
		self.assertIn("SmjKpiCard", page)

	def test_registry_credits_all_59_dashboard_chart_and_card_features(self):
		from my_store_ui.audit.parity_registry import DASHBOARD_ANALYTICS_ADAPTERS

		expected_charts = ACCOUNTS_CHART_KEYS | PAYMENTS_CHART_KEYS | BUYING_CHART_KEYS | CRM_CHART_KEYS | SELLING_CHART_KEYS | STOCK_CHART_KEYS
		expected_cards = (ACCOUNTS_CARD_KEYS | PAYMENTS_CARD_KEYS | BUYING_CARD_KEYS | CRM_CARD_KEYS | SELLING_CARD_KEYS | STOCK_CARD_KEYS) - CUSTOM_CARD_KEYS
		self.assertEqual(len(expected_charts), 28)
		self.assertEqual(len(expected_cards), 25)
		credited_dashboards = {name for (ftype, name) in DASHBOARD_ANALYTICS_ADAPTERS if ftype == "dashboard"}
		credited_charts = {name for (ftype, name) in DASHBOARD_ANALYTICS_ADAPTERS if ftype == "dashboard_chart"}
		credited_cards = {name for (ftype, name) in DASHBOARD_ANALYTICS_ADAPTERS if ftype == "number_card"}
		self.assertEqual(len(credited_dashboards), 6)
		self.assertEqual(len(credited_charts), 28)
		self.assertEqual(len(credited_cards), 25)


if __name__ == "__main__":
	unittest.main()
