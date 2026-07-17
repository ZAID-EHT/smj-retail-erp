from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"

from my_store_ui.priority_pages import (
	get_module_dashboard,
	get_priority_report_definition,
	get_priority_route_definition,
	get_report_hub,
	get_special_page,
	get_tree_nodes,
	run_priority_report,
)
from my_store_ui.search import SEARCH_REGISTRY
from my_store_ui.services.frontend_routes import get_permitted_navigation, resolve_frontend_route, route_is_permitted
from my_store_ui.services.priority_registry import ENTITY_ROUTES, FORM_VARIANTS, REPORT_GROUPS, SPECIAL_ROUTES
from my_store_ui.universal.api import MAPPED_ACTIONS


class TestPriorityPageCoverage(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")


	def test_every_clean_entity_route_has_list_new_detail_and_edit_resolution(self):
		for base_path, spec in ENTITY_ROUTES.items():
			definition, _ = resolve_frontend_route(f"/retail-erp{base_path}")
			self.assertEqual(definition["doctype"], spec["doctype"], base_path)
			self.assertEqual(definition["permission"], "read", base_path)
			if spec.get("view") == "tree":
				self.assertEqual(definition["component"], "tree", base_path)
				continue
			for suffix, permission in (("/new", "create"), ("/TEST-NAME", "read"), ("/TEST-NAME/edit", "write")):
				resolved, params = resolve_frontend_route(f"/retail-erp{base_path}{suffix}")
				self.assertEqual(resolved["doctype"], spec["doctype"], f"{base_path}{suffix}")
				self.assertEqual(resolved["permission"], permission, f"{base_path}{suffix}")
				if suffix.startswith("/TEST"):
					self.assertEqual(params["name"], "TEST-NAME")

	def test_stock_purpose_variants_are_server_owned(self):
		for path, spec in FORM_VARIANTS.items():
			definition = get_priority_route_definition(f"/retail-erp{path}")
			self.assertEqual(definition["doctype"], "Stock Entry")
			self.assertEqual(definition["defaults"], spec["defaults"])

	def test_handcrafted_routes_win_and_generated_aliases_remain(self):
		custom, _ = resolve_frontend_route("/retail-erp/sales/orders")
		generated, _ = resolve_frontend_route("/retail-erp/generated/supplier")
		clean, _ = resolve_frontend_route("/retail-erp/purchases/suppliers")
		self.assertEqual(custom["name"], "sales-order-list")
		self.assertEqual(generated["doctype"], "Supplier")
		self.assertEqual(clean["doctype"], "Supplier")
		self.assertEqual(clean["component"], "entity")

	def test_header_navigation_contains_only_explicit_clean_permitted_links(self):
		navigation = get_permitted_navigation()
		names = {module["name"] for module in navigation}
		self.assertTrue({"home", "sales", "purchases", "inventory", "finance", "crm", "operations", "reports", "pos", "admin"} <= names)
		links = [link for module in navigation for link in module["links"]]
		self.assertTrue(links)
		self.assertTrue(all(link.get("path", "").startswith("/") for link in links))
		self.assertFalse(any(link["path"].startswith("/generated/") for link in links))
		self.assertFalse(any("feature-unavailable" in link["path"] for link in links))

	def test_guest_cannot_authorise_priority_routes_or_load_dashboards(self):
		original = frappe.session.user
		try:
			frappe.session.user = "Guest"
			definition, _ = resolve_frontend_route("/retail-erp/purchases/orders")
			self.assertFalse(route_is_permitted(definition))
			with self.assertRaises(frappe.AuthenticationError):
				get_module_dashboard("purchases")
		finally:
			frappe.session.user = original

	def test_module_dashboards_use_real_permission_filtered_sources(self):
		for module in ("home", "sales", "purchases", "inventory", "finance", "crm", "operations", "admin"):
			result = get_module_dashboard(module)
			self.assertEqual(result["module"], module)
			self.assertTrue(all(isinstance(metric["value"], int) for metric in result["metrics"]))
			self.assertTrue(all(record["path"].startswith("/") for record in result["recent"]))
			self.assertTrue(all("/app/" not in link["path"] for link in result["links"]))

	def test_report_hub_is_allowlisted_and_permission_checked(self):
		hub = get_report_hub("finance")
		self.assertEqual(hub["selected_group"], "finance")
		self.assertTrue(all(report["name"] in REPORT_GROUPS["finance"] for group in hub["groups"] for report in group["reports"]))
		definition = get_priority_report_definition("General Ledger")
		self.assertEqual(definition["name"], "General Ledger")
		with self.assertRaises(frappe.PermissionError):
			get_priority_report_definition("Definitely Not Allowlisted")

	def test_report_runner_rejects_unapproved_filters_and_uses_standard_adapter(self):
		with self.assertRaises(frappe.ValidationError):
			run_priority_report("General Ledger", {"company": frappe.defaults.get_global_default("company"), "password": "secret"})
		with patch("frappe.desk.query_report.run", return_value={"columns": [], "result": []}) as runner:
			result = run_priority_report("General Ledger", {"company": frappe.defaults.get_global_default("company")})
			runner.assert_called_once()
			self.assertEqual(result["retail_links"], {})

	def test_tree_adapter_is_allowlisted_and_permission_aware(self):
		result = get_tree_nodes("/retail-erp/finance/chart-of-accounts")
		self.assertEqual(result["doctype"], "Account")
		self.assertTrue(all(set(node) == {"name", "label", "expandable"} for node in result["nodes"]))
		with self.assertRaises(frappe.ValidationError):
			get_tree_nodes("/retail-erp/purchases/orders")

	def test_admin_routes_require_server_side_system_manager_role(self):
		definition, _ = resolve_frontend_route("/retail-erp/admin/users")
		original = frappe.session.user
		try:
			frappe.session.user = "ordinary@example.com"
			with patch("my_store_ui.services.frontend_routes.frappe.get_roles", return_value=["Sales User"]):
				self.assertFalse(route_is_permitted(definition))
		finally:
			frappe.session.user = original

	def test_admin_permission_matrix_is_read_only_metadata(self):
		result = get_special_page("/retail-erp/admin/permissions")
		self.assertEqual(result["classification"], "read_only")
		self.assertTrue(result["permission_matrix"])
		self.assertTrue(all(set(row) == {"doctype", "role", "read", "create", "write", "delete", "submit", "cancel", "print", "email", "import", "export"} for row in result["permission_matrix"]))

	def test_pos_launcher_is_hidden_without_an_assigned_profile(self):
		with patch("posawesome.posawesome.api.utils.get_active_pos_profile", return_value=None):
			result = get_special_page("/retail-erp/pos")
			self.assertIsNone(result["launch_url"])
			self.assertEqual(result["profiles"], [])

	def test_special_routes_are_registered_without_arbitrary_desk_targets(self):
		for path in SPECIAL_ROUTES:
			definition, _ = resolve_frontend_route(f"/retail-erp{path}")
			self.assertIsNotNone(definition, path)
			self.assertTrue(definition["implemented"], path)
			self.assertNotIn("method", definition)

	def test_mapping_registry_contains_only_fixed_server_methods(self):
		expected = {
			("Quotation", "make_sales_order"), ("Quotation", "make_sales_invoice"),
			("Material Request", "make_request_for_quotation"), ("Material Request", "make_purchase_order"),
			("Supplier Quotation", "make_purchase_order"), ("Purchase Order", "make_purchase_receipt"),
			("Purchase Order", "make_purchase_invoice"), ("Purchase Receipt", "make_purchase_invoice"),
			("Purchase Invoice", "make_payment_entry"), ("Opportunity", "make_quotation"),
		}
		registered = {(doctype, action) for doctype, actions in MAPPED_ACTIONS.items() for action in actions}
		self.assertTrue(expected <= registered)
		for actions in MAPPED_ACTIONS.values():
			for spec in actions.values():
				self.assertNotIn(".", spec["method"])
				self.assertIn("target", spec)

	def test_global_search_uses_clean_registered_routes(self):
		self.assertTrue(any(row["doctype"] == "Purchase Order" for row in SEARCH_REGISTRY))
		self.assertTrue(any(row["doctype"] == "Journal Entry" for row in SEARCH_REGISTRY))
		self.assertTrue(all(row["route"].startswith("/") and "/app/" not in row["route"] for row in SEARCH_REGISTRY))

	def test_frontend_registers_priority_pages_and_live_header_search(self):
		routes = (APP_PATH / "frontend/src/router/routes.js").read_text()
		header = (APP_PATH / "frontend/src/components/shell/AppHeader.vue").read_text()
		navigation = (APP_PATH / "frontend/src/components/shell/ModuleNavigation.vue").read_text()
		search = (APP_PATH / "frontend/src/components/shell/GlobalSearch.vue").read_text()
		styles = (APP_PATH / "frontend/src/design/priority-pages.css").read_text()
		form = (APP_PATH / "frontend/src/pages/generated/UniversalFormPage.vue").read_text()
		self.assertIn("priorityRoutes", routes)
		self.assertIn("PriorityRoutePage.vue", routes)
		self.assertIn("SmartSalesPage", routes)
		self.assertIn("ModuleNavigation", header)
		self.assertIn("GlobalSearch", header)
		self.assertIn("session.state.navigation", navigation)
		self.assertIn("searchRetailERP", search)
		self.assertIn("@media(max-width:560px)", styles)
		self.assertIn("containsRequiredInput", form)
		self.assertIn("SmjNotification", header)
		self.assertIn('/feature-unavailable?feature=Notifications', header)


if __name__ == "__main__":
	unittest.main()
