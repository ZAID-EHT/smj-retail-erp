from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"

from my_store_ui.route_guard import _mapped_desk_route
from my_store_ui.services.frontend_routes import resolve_frontend_route
from my_store_ui.services.permissions import can_open_standard_desk
from my_store_ui.standalone import authorize_frontend_route, get_landing_route, get_session_bootstrap


class TestStandaloneRetailERP(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")


	def test_registered_clean_routes_resolve_without_double_slashes(self):
		for route in (
			"/retail-erp/home",
			"/retail-erp/sales/orders/new",
			"/retail-erp/sales/invoices/ACC-SINV-2026-00010",
			"/retail-erp/finance/payments/new",
		):
			definition, _params = resolve_frontend_route(route)
			self.assertIsNotNone(definition, route)
			self.assertNotIn("//", route)

	def test_access_control_resolves_with_and_without_a_tab(self):
		"""An optional route group must not 500 when it does not participate.

		`unquote(None)` raises, so a valid URL that simply omitted the optional
		segment returned HTTP 500. Found in a real browser, not by this suite.
		"""
		definition, params = resolve_frontend_route("/retail-erp/admin/access-control")
		self.assertIsNotNone(definition)
		self.assertEqual(definition["name"], "access-control")
		self.assertEqual(params, {}, "an unmatched optional group is an absent parameter")

		for tab in ("access", "restrictions", "roles", "profiles", "email"):
			with self.subTest(tab=tab):
				definition, params = resolve_frontend_route(f"/retail-erp/admin/access-control/{tab}")
				self.assertIsNotNone(definition)
				self.assertEqual(params, {"tab": tab})

		# It is an admin surface, so it must be System Manager gated like /admin.
		self.assertEqual(definition["roles"], ("System Manager",))
		self.assertIsNone(resolve_frontend_route("/retail-erp/admin/access-control/not-a-tab")[0])

	def test_admin_operational_routes_resolve_and_are_gated(self):
		"""System Operations and Data Management must resolve (not dead) and be
		System Manager gated, with their optional tab groups not 500ing."""
		for base in ("/retail-erp/admin/system", "/retail-erp/admin/data"):
			definition, params = resolve_frontend_route(base)
			self.assertIsNotNone(definition, base)
			self.assertEqual(definition["roles"], ("System Manager",))
			self.assertEqual(params, {})
		# Optional tab present.
		definition, params = resolve_frontend_route("/retail-erp/admin/system/health")
		self.assertEqual(params, {"tab": "health"})
		definition, params = resolve_frontend_route("/retail-erp/admin/data/export")
		self.assertEqual(params, {"tab": "export"})

	def test_email_and_setup_routes_resolve(self):
		email, params = resolve_frontend_route("/retail-erp/admin/email")
		self.assertIsNotNone(email)
		self.assertEqual(email["roles"], ("System Manager",))
		self.assertEqual(resolve_frontend_route("/retail-erp/admin/email/templates")[1], {"tab": "templates"})
		# Setup is reachable by any authenticated user (no roles gate); create is
		# gated in the backend, not the route.
		setup, params = resolve_frontend_route("/retail-erp/setup")
		self.assertIsNotNone(setup)
		self.assertNotIn("roles", setup)
		self.assertEqual(resolve_frontend_route("/retail-erp/setup/company")[1], {"step": "company"})

	def test_printing_and_finance_admin_routes_resolve(self):
		# Printing landing is dedicated; finance CRUD is via the generated engine.
		printing, _p = resolve_frontend_route("/retail-erp/admin/printing")
		self.assertIsNotNone(printing)
		self.assertEqual(printing["roles"], ("System Manager",))
		for route in ("/retail-erp/finance/chart-of-accounts", "/retail-erp/finance/fiscal-year",
		              "/retail-erp/finance/cost-centers", "/retail-erp/admin/companies",
		              "/retail-erp/admin/print-format", "/retail-erp/admin/letter-head"):
			definition, _p = resolve_frontend_route(route)
			self.assertIsNotNone(definition, route)

	def test_unknown_route_returns_custom_not_found(self):
		result = authorize_frontend_route("/retail-erp/not-a-registered-feature")
		self.assertEqual(result["outcome"], "not_found")
		self.assertEqual(result["route"], "/retail-erp/not-found")
		definition, _params = resolve_frontend_route("/retail-erp/sales/invoices/%00")
		self.assertIsNone(definition)

	def test_permission_denial_is_server_owned(self):
		with patch("my_store_ui.standalone.route_is_permitted", return_value=False):
			result = authorize_frontend_route("/retail-erp/sales/orders")
		self.assertEqual(result, {"outcome": "denied", "route": "/retail-erp/permission-denied"})

	def test_guest_bootstrap_contains_no_identity_or_permissions(self):
		original = frappe.session.user
		try:
			frappe.session.user = "Guest"
			self.assertEqual(get_session_bootstrap(), {"authenticated": False})
		finally:
			frappe.session.user = original

	def test_role_landing_precedence(self):
		original = frappe.session.user
		try:
			frappe.session.user = "multi-role@example.invalid"
			with patch("my_store_ui.standalone.frappe.get_roles", return_value=["Accounts User", "Sales User"]), patch("my_store_ui.standalone.route_is_permitted", return_value=True):
				self.assertEqual(get_landing_route(), "/retail-erp/smart-sales")
		finally:
			frappe.session.user = original

	def test_desk_routes_map_only_to_retail_frontend(self):
		self.assertEqual(_mapped_desk_route("/app/customer"), "/retail-erp/sales/customers")
		self.assertEqual(_mapped_desk_route("/app/sales-order/SAL-ORD-0001"), "/retail-erp/sales/orders/SAL-ORD-0001")
		self.assertEqual(_mapped_desk_route("/app/retail-erp/finance/payments"), "/retail-erp/finance/payments")
		self.assertTrue(_mapped_desk_route("/app/manufacturing").startswith("/retail-erp/feature-unavailable"))
		self.assertFalse(can_open_standard_desk())

	def test_hashed_assets_and_desk_compatibility_assets_exist(self):
		output = APP_PATH / "my_store_ui" / "public" / "frontend"
		manifest = json.loads((output / ".vite" / "manifest.json").read_text())
		entry = manifest["src/main.js"]
		self.assertRegex(entry["file"], r"assets/retail-erp-[A-Za-z0-9_-]+\.js")
		self.assertTrue((output / entry["file"]).exists())
		self.assertTrue((output / "retail-erp.js").exists())
		self.assertTrue((output / "retail-erp.css").exists())

	def test_login_source_does_not_persist_credentials_or_sessions(self):
		source = (APP_PATH / "frontend" / "src" / "services" / "session.js").read_text()
		self.assertNotIn("localStorage", source)
		self.assertNotIn("sessionStorage", source)
		self.assertIn('fetch("/api/method/login"', source)
		self.assertIn('fetch("/api/method/logout"', source)

	def test_empty_server_navigation_never_falls_back_to_static_modules(self):
		for relative_path in (
			"frontend/src/components/shell/ModuleNavigation.vue",
			"frontend/src/components/navigation/MobileNavigation.vue",
		):
			source = (APP_PATH / relative_path).read_text()
			self.assertIn("session ? session.state.navigation : navigationModules", source)
			self.assertNotIn("navigation?.length", source)

	def test_modal_focus_manager_supports_escape_trapping_and_restoration(self):
		source = (APP_PATH / "frontend" / "src" / "directives" / "focusTrap.js").read_text()
		self.assertIn('event.key === "Escape"', source)
		self.assertIn('event.key !== "Tab"', source)
		self.assertIn("previousFocus.focus()", source)
		self.assertIn("MutationObserver", source)

	def test_raw_website_template_remains_safe_render_compatible(self):
		template = (APP_PATH / "my_store_ui" / "www" / "retail_erp.html").read_text()
		self.assertNotIn(".__", template)
		self.assertIn('id="retail-erp-root"', template)


if __name__ == "__main__":
	unittest.main()
