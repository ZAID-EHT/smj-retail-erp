from __future__ import annotations

import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

import frappe


BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.universal.api import (
	get_document_actions,
	get_document_list,
	get_doctype_metadata,
	get_list_configuration,
	get_print_formats,
	run_document_action,
)
from my_store_ui.universal.collaboration import add_comment, email_document, get_collaboration_state, remove_attachment, set_tags
from my_store_ui.universal.registry import CUSTOM_OVERRIDES, GENERATED_ALLOWLIST, get_feature


class TestUniversalGeneratedExperience(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
		frappe.connect()
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	@classmethod
	def tearDownClass(cls):
		frappe.destroy()

	def test_all_twenty_features_have_safe_presentation_and_list_configuration(self):
		for doctype in sorted(GENERATED_ALLOWLIST):
			feature = frappe.scrub(doctype).replace("_", "-")
			configuration = get_list_configuration(feature)
			self.assertLessEqual(len(configuration["main_filters"]), 5, doctype)
			self.assertTrue(configuration["presentation"].get("plural"), doctype)
			self.assertTrue(configuration["presentation"].get("description"), doctype)
			self.assertTrue(configuration["default_columns"], doctype)
			self.assertNotIn("owner", configuration["default_columns"], doctype)
			self.assertNotIn("modified_by", configuration["default_columns"], doctype)
			filter_names = {row["fieldname"] for row in configuration["filter_fields"]}
			self.assertEqual(
				filter_names,
				{row["fieldname"] for row in configuration["main_filters"] + configuration["more_filters"]},
				doctype,
			)

	def test_column_selection_is_server_allowlisted_and_bounded(self):
		configuration = get_list_configuration("supplier")
		allowed = [row["fieldname"] for row in configuration["all_columns"][:3]]
		result = get_document_list("supplier", columns=allowed, page_size=1)
		self.assertEqual([row["fieldname"] for row in result["columns"]], allowed)
		with self.assertRaises(frappe.ValidationError):
			get_document_list("supplier", columns=["password"])
		with self.assertRaises(frappe.ValidationError):
			get_document_list("supplier", filters=[["owner", "=", "Administrator"]])
		with self.assertRaises(frappe.ValidationError):
			get_document_list("supplier", sort_field="modified_by")
		with self.assertRaises(frappe.ValidationError):
			get_document_list("supplier", columns=[row["fieldname"] for row in configuration["all_columns"][:13]])

	def test_required_fields_are_not_removed_from_generated_metadata(self):
		for doctype in sorted(GENERATED_ALLOWLIST):
			feature = frappe.scrub(doctype).replace("_", "-")
			metadata = get_doctype_metadata(feature)
			returned = {field["fieldname"] for field in metadata["fields"]}
			readable_levels = set(frappe.get_meta(doctype).get_permlevel_access("read", user=frappe.session.user))
			required = {
				field.fieldname for field in frappe.get_meta(doctype).fields
				if field.reqd and field.fieldtype != "Password" and field.permlevel in readable_levels
			}
			self.assertTrue(required.issubset(returned), f"{doctype}: {required - returned}")

	def test_generated_ux_sources_include_filters_columns_cards_and_grouping(self):
		list_source = (APP_PATH / "frontend/src/pages/generated/UniversalListPage.vue").read_text()
		form_source = (APP_PATH / "frontend/src/pages/generated/UniversalFormPage.vue").read_text()
		detail_source = (APP_PATH / "frontend/src/pages/generated/UniversalDetailPage.vue").read_text()
		styles = (APP_PATH / "frontend/src/design/generated-ux.css").read_text()
		for marker in ("More filters", "activeChips", "Visible columns", 'data-label="column.label"'):
			self.assertIn(marker, list_source)
		for marker in ("primaryFields", "Advanced", "required", "beforeunload"):
			self.assertIn(marker, form_source)
		for marker in ("UniversalCollaborationPanel", "UniversalPrintDialog", "importantFields", "related"):
			self.assertIn(marker, detail_source)
		self.assertIn("overflow-x:auto", styles)
		self.assertIn("@media(max-width:390px)", styles)
		self.assertNotIn("overflow-x: hidden", styles)

	def test_collaboration_state_is_document_permission_filtered(self):
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		state = get_collaboration_state("supplier", name)
		self.assertIn("permissions", state)
		self.assertEqual(state["upload"]["doctype"], "Supplier")
		with patch("my_store_ui.universal.collaboration._context", side_effect=frappe.DoesNotExistError):
			with self.assertRaises(frappe.DoesNotExistError):
				get_collaboration_state("supplier", "RESTRICTED")

	def test_guest_cannot_access_collaboration(self):
		original = frappe.session.user
		try:
			frappe.session.user = "Guest"
			with self.assertRaises(frappe.AuthenticationError):
				get_collaboration_state("supplier", "ANY")
		finally:
			frappe.session.user = original

	def test_attachment_and_email_adapters_recheck_permissions(self):
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		doc = frappe.get_doc("Supplier", name)
		with patch("my_store_ui.universal.collaboration._context", return_value=(get_feature("supplier"), doc)), patch(
			"my_store_ui.universal.collaboration._can", return_value=False
		):
			with self.assertRaises(frappe.PermissionError):
				email_document("supplier", name, ["test@example.com"], "Subject", "Message")
		with patch("my_store_ui.universal.collaboration._context", side_effect=frappe.PermissionError):
			with self.assertRaises(frappe.PermissionError):
				remove_attachment("supplier", name, "restricted-file")

	def test_comment_and_tag_writes_use_standard_document_paths_with_rollback(self):
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		frappe.db.savepoint("universal_collaboration_test")
		try:
			comment = add_comment("supplier", name, "Temporary universal collaboration test")
			self.assertTrue(frappe.db.exists("Comment", comment["name"]))
			result = set_tags("supplier", name, ["universal-test"])
			self.assertEqual(result["tags"], ["universal-test"])
		finally:
			frappe.db.rollback(save_point="universal_collaboration_test")

	def test_print_configuration_is_permission_checked_and_reports_environment(self):
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		result = get_print_formats("supplier", name)
		self.assertIn("Standard", result["formats"])
		self.assertEqual(result["pdf_environment"]["available"], bool(shutil.which("wkhtmltopdf")))
		with patch("my_store_ui.universal.api.frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				get_print_formats("supplier", name)

	def test_action_registry_never_accepts_arbitrary_method_paths(self):
		name = frappe.get_list("Supplier", pluck="name", limit_page_length=1)[0]
		actions = get_document_actions("supplier", name)["actions"]
		self.assertTrue(all("method" not in action for action in actions))
		with self.assertRaises(frappe.PermissionError):
			run_document_action("supplier", name, "erpnext.some.module.method")

	def test_custom_routes_keep_priority_over_generated_routes(self):
		for doctype, route in CUSTOM_OVERRIDES.items():
			feature = get_feature(frappe.scrub(doctype).replace("_", "-"))
			self.assertEqual(feature["implementation_type"], "custom")
			self.assertEqual(feature["route"], route)
		self.assertNotIn("Customer", GENERATED_ALLOWLIST)


if __name__ == "__main__":
	unittest.main()
