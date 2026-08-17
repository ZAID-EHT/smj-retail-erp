from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"

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
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def _configured_custom_role(self, prefix="Universal Custom Role"):
		name = f"{prefix} {frappe.generate_hash(length=8)}"
		frappe.get_doc({
			"doctype": "Role", "role_name": name, "disabled": 0,
			"desk_access": 1, "is_custom": 1,
		}).insert(ignore_permissions=True)
		access = frappe.get_doc({"doctype": "Retail Role Page Access", "role": name})
		access.append("pages", {"path": "/home", "label": "Dashboard"})
		access.insert(ignore_permissions=True)
		return name


	def test_custom_overrides_always_win(self):
		for doctype in CUSTOM_OVERRIDES:
			record = get_feature(frappe.scrub(doctype).replace("_", "-"))
			self.assertEqual(record["implementation_type"], "custom")
			with self.assertRaises(frappe.PermissionError):
				get_generated_feature(frappe.scrub(doctype).replace("_", "-"))

	def test_generated_allowlist_is_provisional(self):
		self.assertGreaterEqual(len(GENERATED_ALLOWLIST), 20)
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
		# The only Password input exposed is the controlled, write-only new_password;
		# no other sensitive password field is surfaced on the User form.
		password_fields = [field["fieldname"] for field in user["fields"] if field["fieldtype"] == "Password"]
		self.assertEqual(password_fields, ["new_password"])
		new_password = next(field for field in user["fields"] if field["fieldname"] == "new_password")
		self.assertFalse(new_password["read_only"])
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
		frappe.db.savepoint("custom_role_link_test")
		try:
			custom_role = self._configured_custom_role("Searchable Custom Role")
			all_roles = get_link_options("user", "role", "", parent_fieldname="roles")
			self.assertIn(custom_role, {row["value"] for row in all_roles["results"]})
			self.assertNotIn("Customer", {row["value"] for row in all_roles["results"]})
			roles = get_link_options("user", "role", "Searchable", parent_fieldname="roles")
			self.assertEqual([row["value"] for row in roles["results"]], [custom_role])
		finally:
			frappe.db.rollback(save_point="custom_role_link_test")
		with self.assertRaises(frappe.PermissionError):
			get_link_options("supplier", "owner", "Administrator")

	def test_generated_user_role_controls_are_searchable_and_explained(self):
		metadata = get_doctype_metadata("user")
		fields = {field["fieldname"]: field for field in metadata["fields"]}
		self.assertEqual(fields["role_profile_name"]["label"], "Role Profile (optional)")
		self.assertIn("individual roles", fields["role_profile_name"]["description"])
		self.assertEqual(fields["roles"]["label"], "Custom Role")
		self.assertTrue(fields["roles"]["simple_create_single"])
		self.assertFalse(fields["roles"]["read_only"])
		self.assertEqual(fields["roles"]["child_fields"][0]["options"], "Role")

	def test_user_manager_can_set_password_create_disabled_and_reset(self):
		from frappe.utils.password import check_password

		metadata = get_doctype_metadata("user")
		fields = {field["fieldname"]: field for field in metadata["fields"]}
		# new_password is surfaced as a write-only Password input on the form.
		self.assertIn("new_password", fields)
		self.assertEqual(fields["new_password"]["fieldtype"], "Password")
		self.assertFalse(fields["new_password"]["read_only"])
		# enabled is re-exposed as writable so managers can revoke/restore access.
		self.assertFalse(fields["enabled"]["read_only"])

		frappe.db.savepoint("user_password_test")
		try:
			custom_role = self._configured_custom_role()
			email = f"universal_pw_{frappe.generate_hash(length=8)}@example.com"
			password = "Xq7!vTn2@Lp9zK"
			created = create_document("user", {
				"email": email, "first_name": "Universal Password",
				"send_welcome_email": 0, "enabled": 0,
				"new_password": password, "roles": [{"role": custom_role}],
			})
			# The password set on create yields working login credentials.
			self.assertEqual(check_password(email, password), email)
			# ...and the account was created disabled, as requested.
			self.assertEqual(frappe.db.get_value("User", email, "enabled"), 0)
			# The password is never echoed back on the read path.
			detail = get_document_detail("user", created["name"])
			self.assertNotIn("new_password", detail["document"])

			doc = frappe.get_doc("User", email)
			reset = "Zt3#Mw8&Qr1yB"
			update_document("user", email, {"enabled": 1, "new_password": reset}, str(doc.modified))
			self.assertEqual(check_password(email, reset), email)
			self.assertEqual(frappe.db.get_value("User", email, "enabled"), 1)
		finally:
			frappe.db.rollback(save_point="user_password_test")

	def test_password_and_enable_overrides_require_privilege(self):
		from my_store_ui.universal.api import _writable_fields, _write_only_inputs

		meta = frappe.get_meta("User")
		frappe.db.savepoint("user_priv_test")
		try:
			email = f"universal_restricted_{frappe.generate_hash(length=8)}@example.com"
			frappe.get_doc({
				"doctype": "User", "email": email, "first_name": "Restricted",
				"send_welcome_email": 0, "roles": [{"role": "Sales User"}],
			}).insert(ignore_permissions=True)
			original = frappe.session.user
			try:
				frappe.set_user(email)
				writable = {field.fieldname for field in _writable_fields(meta)}
				self.assertEqual(_write_only_inputs(meta), [])
				self.assertNotIn("new_password", writable)
				self.assertNotIn("enabled", writable)
			finally:
				frappe.set_user(original)
		finally:
			frappe.db.rollback(save_point="user_priv_test")

	def test_add_user_form_is_curated_to_essentials(self):
		metadata = get_doctype_metadata("user")
		self.assertEqual(
			metadata["simple_create_fields"],
			["username", "new_password", "enabled", "roles"],
		)
		# Username, password and role are the only mandatory inputs on the add form.
		self.assertEqual(metadata["simple_create_required"], ["username", "new_password", "roles"])
		# The full field set is still returned so the edit form stays complete.
		all_names = {field["fieldname"] for field in metadata["fields"]}
		self.assertTrue(set(metadata["simple_create_fields"]).issubset(all_names))
		self.assertGreater(len(metadata["fields"]), len(metadata["simple_create_fields"]))
		# A doctype with no curated config is unaffected (falls through to []).
		# Warehouse used to be the example here, but it now has a curated add form of
		# its own (see SIMPLE_CREATE_FIELDS), so use one that is still uncurated.
		self.assertEqual(get_doctype_metadata("contact")["simple_create_fields"], [])
		self.assertEqual(get_doctype_metadata("contact")["simple_create_required"], [])
		# Warehouse is curated now, and must stay that way.
		self.assertTrue(get_doctype_metadata("warehouse")["simple_create_fields"])

	def test_supplier_has_a_curated_universal_add_form(self):
		# Supplier flows through the universal generated engine.
		metadata = get_doctype_metadata("supplier")
		simple = metadata["simple_create_fields"]
		all_names = {field["fieldname"] for field in metadata["fields"]}
		self.assertIn("supplier_name", simple)
		self.assertTrue(set(simple).issubset(all_names))
		self.assertGreater(len(metadata["fields"]), len(simple))
		# ERPNext-required fields stay required on the add form.
		for field in ("supplier_name", "supplier_group"):
			self.assertIn(field, metadata["simple_create_required"])
			self.assertIn(field, simple)

	def test_custom_entry_forms_are_curated_into_progressive_sections(self):
		# Customer and Item use the custom form engine, already curated + sectioned.
		from my_store_ui.services.form_schemas import FORM_SCHEMAS

		customer = FORM_SCHEMAS["customers"]
		customer_sections = {key for key, _label in customer["sections"]}
		self.assertTrue({"basic", "contact", "sales"}.issubset(customer_sections))
		customer_fields = {f["fieldname"]: f for f in customer["fields"]}
		for field in ("customer_name", "customer_group", "territory"):
			self.assertIn(field, customer_fields)
			self.assertTrue(customer_fields[field]["required"], field)
		# Less-used fields sit outside Basic Information (progressive disclosure).
		self.assertEqual(customer_fields["default_price_list"]["section"], "sales")

		item = FORM_SCHEMAS["items"]
		item_sections = {key for key, _label in item["sections"]}
		self.assertTrue({"basic", "pricing"}.issubset(item_sections))
		item_fields = {f["fieldname"]: f for f in item["fields"]}
		for field in ("item_code", "item_group", "stock_uom"):
			self.assertIn(field, item_fields)

	def test_add_user_by_username_synthesises_optional_email_and_name(self):
		from frappe.utils.password import check_password

		frappe.db.savepoint("user_username_test")
		try:
			custom_role = self._configured_custom_role()
			username = f"universal_uname_{frappe.generate_hash(length=8)}"
			password = "Xq7!vTn2@Lp9zK"
			created = create_document("user", {
				"username": username, "new_password": password, "roles": [{"role": custom_role}],
			})
			doc = frappe.get_doc("User", created["name"])
			# Email is synthesised from the username; first_name defaults to it too.
			self.assertEqual(doc.email, f"{username}@{frappe.local.site}")
			self.assertEqual(created["name"], doc.email)
			self.assertEqual(doc.first_name, username)
			self.assertEqual(frappe.db.get_value("User", {"username": username}, "name"), created["name"])
			self.assertEqual(check_password(doc.email, password), doc.name)
			# Creating with neither a username nor an email is rejected clearly.
			with self.assertRaises(frappe.ValidationError):
				create_document("user", {"new_password": password, "roles": [{"role": custom_role}]})
		finally:
			frappe.db.rollback(save_point="user_username_test")

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
		link_field = (APP_PATH / "frontend/src/components/generated/UniversalField.vue").read_text()
		self.assertIn('aria-autocomplete="list"', link_field)
		self.assertIn("function openLink()", link_field)
		self.assertIn("No matching Role Profiles", link_field)
		self.assertIn("ArrowDown", link_field)


if __name__ == "__main__":
	unittest.main()
