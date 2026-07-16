from __future__ import annotations

import unittest
from pathlib import Path

import frappe

from my_store_ui.audit.parity_registry import DOCTYPE_SPECIFIC_ACTIONS, corrected_production_parity_audit
from my_store_ui.priority_pages import get_priority_route_definition
from my_store_ui.universal.api import get_document_actions, get_document_detail


APP_PATH = Path(__file__).resolve().parents[2]


class TestAdminContactsPrintingParity(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_source_verified_admin_contact_print_actions_are_registered(self):
		expected = {
			"Company": {
				"create_default_tax_template", "create_tax_template", "create_transaction_deletion_request",
				"delete_transactions", "purchase_tax_template", "sales_tax_template",
			},
			"Email Digest": {"send_now", "view_now"},
			"Employee": {"create_user"},
			"Address": {"0_1"},
			"Contact": {"0_1", "call", "invite_as_user"},
			"Print Format": {"edit_format", "make_default", "set_as_default"},
			"Print Style": {"print_settings"},
		}
		for doctype, actions in expected.items():
			self.assertTrue(actions <= DOCTYPE_SPECIFIC_ACTIONS[doctype], f"Missing credits for {doctype}")

	def test_print_settings_single_route_loads_real_metadata(self):
		definition = get_priority_route_definition("/admin/print-settings")
		self.assertEqual(definition["component"], "single")
		self.assertEqual(definition["doctype"], "Print Settings")
		detail = get_document_detail("print-settings", "Print Settings")
		self.assertEqual(detail["document"]["doctype"], "Print Settings")
		self.assertTrue(detail["metadata"]["fields"])

	def test_company_actions_are_allowlisted_and_symbolic(self):
		names = frappe.get_list("Company", pluck="name", limit_page_length=1)
		self.assertTrue(names)
		actions = {item["action"] for item in get_document_actions("company", names[0])["actions"]}
		self.assertIn("create_tax_template", actions)
		self.assertIn("delete_transactions", actions)
		self.assertFalse(any("." in action for action in actions))

	def test_frontend_uses_masked_password_and_stays_on_single_save(self):
		detail_page = (APP_PATH / "frontend/src/pages/generated/UniversalDetailPage.vue").read_text()
		form_page = (APP_PATH / "frontend/src/pages/generated/UniversalFormPage.vue").read_text()
		priority_page = (APP_PATH / "frontend/src/pages/priority/PriorityRoutePage.vue").read_text()
		self.assertIn('input.type = "password"', detail_page)
		self.assertIn('input.autocomplete = "current-password"', detail_page)
		self.assertIn("props.stayOnSave", form_page)
		self.assertIn("stay-on-save", priority_page)

	def test_guest_cannot_load_print_settings(self):
		frappe.set_user("Guest")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			get_document_detail("print-settings", "Print Settings")

	def test_corrected_audit_is_zero_and_classified(self):
		result = corrected_production_parity_audit()
		self.assertEqual(result["required_but_missing"], 0)
		self.assertEqual(result["unclassified"], 0)


if __name__ == "__main__":
	unittest.main()
