from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.services.frontend_routes import get_permitted_navigation, resolve_frontend_route
from my_store_ui.standalone import authorize_frontend_route
from my_store_ui.universal.api import (
	_clean_payload,
	create_document,
	get_doctype_metadata,
	get_document_detail,
	get_document_list,
	get_feature_registry,
	get_list_configuration,
	get_link_options,
	get_report_definition,
	run_document_action,
	update_document,
)
from my_store_ui.universal.registry import ALL_GENERATED_DOCTYPES, CUSTOM_OVERRIDES, GENERATED_ALLOWLIST, feature_is_permitted, get_feature, get_generated_feature


class TestUniversalFrontendFoundation(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
		frappe.connect()
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	@classmethod
	def tearDownClass(cls):
		frappe.destroy()

	def test_custom_overrides_always_win(self):
		for doctype in CUSTOM_OVERRIDES:
			record = get_feature(frappe.scrub(doctype).replace("_", "-"))
			self.assertEqual(record["implementation_type"], "custom")
			with self.assertRaises(frappe.PermissionError):
				get_generated_feature(frappe.scrub(doctype).replace("_", "-"))

	def test_exact_generated_allowlist_is_provisional(self):
		self.assertEqual(len(GENERATED_ALLOWLIST), 20)
		for doctype in GENERATED_ALLOWLIST:
			record = get_generated_feature(frappe.scrub(doctype).replace("_", "-"))
			self.assertEqual(record["implementation_type"], "generated_provisional")
			self.assertEqual(record["doctype"], doctype)

	def test_unknown_or_unclassified_feature_is_not_generated(self):
		with self.assertRaises(frappe.DoesNotExistError):
			get_feature("definitely-not-installed")
		with self.assertRaises(frappe.PermissionError):
			get_generated_feature("gl-entry")

	def test_registry_is_paginated_and_does_not_ship_inventory(self):
		result = get_feature_registry(implementation_type="generated_provisional", page_length=5)
		self.assertEqual(len(result["records"]), 5)
		# The registry contains only installed, user-facing inventory records. A
		# priority allowlist entry can legitimately be absent from that inventory.
		self.assertGreaterEqual(result["total"], len(GENERATED_ALLOWLIST))
		self.assertLessEqual(result["total"], len(ALL_GENERATED_DOCTYPES))
		self.assertTrue(all("required_permissions" not in row for row in result["records"]))

	def test_metadata_filters_fields_and_marks_client_behaviour(self):
		result = get_doctype_metadata("supplier")
		self.assertEqual(result["doctype"], "Supplier")
		self.assertEqual(result["client_script_policy"], "not_executed")
		self.assertTrue(result["fields"])
		self.assertTrue(all(field["fieldtype"] != "Password" for field in result["fields"]))
		self.assertTrue(all("permlevel" in field for field in result["fields"]))

	def test_user_and_role_forms_expose_only_controlled_administration_fields(self):
		user = get_doctype_metadata("user")
		roles = next(field for field in user["fields"] if field["fieldname"] == "roles")
		self.assertFalse(roles["hidden"])
		self.assertFalse(roles["read_only"])
		self.assertEqual([field["fieldname"] for field in roles["child_fields"]], ["role"])
		self.assertFalse(any(field["fieldtype"] == "Password" for field in user["fields"]))
		clean = _clean_payload(
			frappe.get_meta("User"),
			{"email": "dry-run@example.invalid", "first_name": "Dry Run", "roles": [{"role": "Sales User"}]},
		)
		self.assertEqual(clean["roles"], [{"role": "Sales User"}])
		self.assertFalse(frappe.db.exists("User", "dry-run@example.invalid"))

		role = get_doctype_metadata("role")
		role_name = next(field for field in role["fields"] if field["fieldname"] == "role_name")
		self.assertTrue(role_name["required"])
		self.assertFalse(role_name["read_only"])

	def test_user_and_role_generated_aliases_keep_system_manager_boundary(self):
		original = frappe.session.user
		try:
			frappe.session.user = "ordinary@example.com"
			with (
				patch("my_store_ui.universal.registry.frappe.get_roles", return_value=["Sales User"]),
				patch("my_store_ui.universal.registry.frappe.has_permission", return_value=True),
			):
				self.assertFalse(feature_is_permitted(get_feature("user")))
				self.assertFalse(feature_is_permitted(get_feature("role")))
		finally:
			frappe.session.user = original

	def test_list_pagination_search_filter_and_sort(self):
		configuration = get_list_configuration("supplier")
		result = get_document_list("supplier", page_size=2, sort_field="modified", sort_order="desc")
		self.assertLessEqual(len(result["records"]), 2)
		self.assertEqual(result["pagination"]["page_size"], 2)
		self.assertTrue(configuration["columns"])
		if result["records"]:
			searched = get_document_list("supplier", search=result["records"][0]["name"], page_size=20)
			self.assertIn(result["records"][0]["name"], {row.name for row in searched["records"]})
		with self.assertRaises(frappe.ValidationError):
			get_document_list("supplier", filters=[["password", "=", "secret"]])
		with self.assertRaises(frappe.ValidationError):
			get_document_list("supplier", sort_field="password")

	def test_detail_is_permission_filtered_and_existence_safe(self):
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		result = get_document_detail("supplier", name)
		self.assertEqual(result["document"]["name"], name)
		self.assertTrue(result["route"].startswith("/purchases/suppliers/"))
		with self.assertRaises(frappe.DoesNotExistError):
			get_document_detail("supplier", "DOES-NOT-EXIST-UNIVERSAL")
		with patch("my_store_ui.universal.api.frappe.get_list", return_value=[]), patch("my_store_ui.universal.api.frappe.get_doc") as get_doc:
			with self.assertRaises(frappe.DoesNotExistError):
				get_document_detail("supplier", "restricted")
			get_doc.assert_not_called()

	def test_mass_assignment_and_unapproved_action_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			_clean_payload(frappe.get_meta("Supplier"), {"owner": "Guest"})
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		with self.assertRaises(frappe.PermissionError):
			run_document_action("supplier", name, "arbitrary.python.method")

	def test_standard_create_and_update_use_document_controller_with_rollback(self):
		frappe.db.savepoint("universal_write_test")
		try:
			created = create_document("designation", {"designation_name": "Universal Test Designation", "description": "Temporary rollback record"})
			self.assertTrue(frappe.db.exists("Designation", created["name"]))
			doc = frappe.get_doc("Designation", created["name"])
			updated = update_document("designation", doc.name, {"description": "Updated safely"}, str(doc.modified))
			self.assertEqual(frappe.db.get_value("Designation", doc.name, "description"), "Updated safely")
			self.assertEqual(updated["name"], doc.name)
			with self.assertRaises(frappe.TimestampMismatchError):
				update_document("designation", doc.name, {"description": "stale"}, "2000-01-01 00:00:00")
		finally:
			frappe.db.rollback(save_point="universal_write_test")

	def test_report_definition_uses_standard_report_permission_check(self):
		definition = get_report_definition("report:sales-analytics")
		self.assertEqual(definition["name"], "Sales Analytics")
		self.assertEqual(definition["client_filter_policy"], "not_executed")

	def test_link_search_is_server_allowlisted(self):
		result = get_link_options("supplier", "supplier_group", "")
		self.assertLessEqual(len(result["results"]), 20)
		roles = get_link_options("user", "role", "Sales", parent_fieldname="roles")
		self.assertTrue(roles["results"])
		self.assertTrue(all("sales" in row["value"].lower() for row in roles["results"]))
		with self.assertRaises(frappe.PermissionError):
			get_link_options("supplier", "owner", "Administrator")

	def test_guest_cannot_read_registry_or_metadata(self):
		original = frappe.session.user
		try:
			frappe.session.user = "Guest"
			with self.assertRaises(frappe.AuthenticationError):
				get_feature_registry()
			with self.assertRaises(frappe.AuthenticationError):
				get_doctype_metadata("supplier")
		finally:
			frappe.session.user = original

	def test_generated_routes_are_server_authorized_and_custom_routes_preserved(self):
		definition, _params = resolve_frontend_route("/retail-erp/generated/supplier")
		self.assertEqual(definition["doctype"], "Supplier")
		self.assertEqual(authorize_frontend_route("/retail-erp/generated/supplier")["outcome"], "allowed")
		self.assertEqual(authorize_frontend_route("/retail-erp/generated/customer")["outcome"], "not_found")
		custom, _params = resolve_frontend_route("/retail-erp/sales/customers")
		self.assertEqual(custom["name"], "customer-list")

	def test_navigation_promotes_clean_priority_routes(self):
		navigation = get_permitted_navigation()
		paths = {link["path"] for module in navigation for link in module["links"]}
		self.assertIn("/purchases/suppliers", paths)
		self.assertIn("/inventory/warehouses", paths)
		self.assertIn("/inventory/stock-entries", paths)
		self.assertFalse(any(path.startswith("/generated/") for path in paths))

	def test_frontend_contains_lazy_generated_routes_and_no_desk_links(self):
		routes = (APP_PATH / "frontend/src/router/routes.js").read_text()
		service = (APP_PATH / "frontend/src/services/universal.js").read_text()
		self.assertIn('path: "/generated/:feature"', routes)
		self.assertIn('import("@/pages/generated/UniversalListPage.vue")', routes)
		self.assertNotIn("/app/", service)
		self.assertNotIn("ignore_permissions", (APP_PATH / "my_store_ui/universal/api.py").read_text())
		self.assertIn(':read-only="table.read_only"', (APP_PATH / "frontend/src/pages/generated/UniversalFormPage.vue").read_text())


if __name__ == "__main__":
	unittest.main()
