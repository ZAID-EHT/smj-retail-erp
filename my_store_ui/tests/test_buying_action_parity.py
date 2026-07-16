from __future__ import annotations

import unittest
from pathlib import Path

import frappe

from my_store_ui.audit.parity_registry import (
	DOCTYPE_SPECIFIC_ACTIONS,
	DOCUMENT_ACTION_OVERRIDES,
	corrected_production_parity_audit,
)
from my_store_ui.universal.api import MAPPED_ACTIONS, _update_transaction_items, get_document_actions


APP_PATH = Path(__file__).resolve().parents[2]


class TestBuyingActionParity(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def _first_record(self, doctype: str):
		names = frappe.get_list(doctype, pluck="name", limit_page_length=1)
		return names[0] if names else None

	def test_source_verified_buying_actions_are_registered(self):
		expected = {
			"Purchase Order": {
				"delivered", "link_to_material_request", "make_inter_company_sales_order",
				"make_subcontracting_order", "material_to_supplier", "return_of_components",
				"update_items", "update_rate_as_per_last_purchase", "update_status",
			},
			"Request for Quotation": {
				"download_pdf", "get_suppliers", "link_to_material_requests",
				"material_request", "opportunity", "possible_supplier",
			},
			"Supplier Quotation": {"make_purchase_invoice", "link_to_material_requests", "update_items"},
			"Supplier": {"get_supplier_group_details", "link_with_customer"},
		}
		for doctype, actions in expected.items():
			self.assertTrue(actions <= DOCTYPE_SPECIFIC_ACTIONS[doctype], f"Missing credits for {doctype}")

	def test_new_mappings_use_fixed_symbolic_methods(self):
		self.assertEqual(MAPPED_ACTIONS["Supplier Quotation"]["make_purchase_invoice"]["target"], "Purchase Invoice")
		for action in {
			"make_inter_company_sales_order", "make_subcontracting_order",
			"material_to_supplier", "return_of_components",
		}:
			self.assertIn(action, MAPPED_ACTIONS["Purchase Order"])
			self.assertNotIn(".", MAPPED_ACTIONS["Purchase Order"][action]["method"])

	def test_portal_and_scheduler_actions_are_not_fake_staff_buttons(self):
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Purchase Order", "make_purchase_invoice_from_portal")][0], "external_app_adapter")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Request for Quotation", "create_supplier_quotation")][0], "external_app_adapter")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Supplier Scorecard", "make_all_scorecards")][0], "internal")

	def test_live_action_discovery_returns_only_allowlisted_actions(self):
		for feature, doctype in {
			"purchase-order": "Purchase Order",
			"request-for-quotation": "Request for Quotation",
			"supplier-quotation": "Supplier Quotation",
			"supplier": "Supplier",
		}.items():
			name = self._first_record(doctype)
			if not name:
				continue
			result = get_document_actions(feature, name)
			for action in result["actions"]:
				self.assertNotIn(".", action["action"])
				self.assertFalse(action["action"].startswith("frappe"))

	def test_guest_cannot_discover_buying_document_actions(self):
		name = self._first_record("Supplier")
		if not name:
			self.skipTest("No Supplier exists on site1")
		frappe.set_user("Guest")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			get_document_actions("supplier", name)

	def test_item_update_rejects_mass_assignment_before_controller_call(self):
		name = self._first_record("Purchase Order")
		if not name:
			self.skipTest("No Purchase Order exists on site1")
		doc = frappe.get_doc("Purchase Order", name)
		with self.assertRaises(frappe.ValidationError):
			_update_transaction_items(doc, '[{"docname":"row","qty":1,"parent":"forbidden"}]')

	def test_frontend_supports_item_payloads_and_download_responses(self):
		page = (APP_PATH / "frontend/src/pages/generated/UniversalDetailPage.vue").read_text()
		self.assertIn('field === "items_json"', page)
		self.assertIn("result.download_url", page)
		self.assertIn("window.location.assign", page)

	def test_corrected_audit_has_no_buying_items_left(self):
		result = corrected_production_parity_audit()
		keys = result["required_but_missing_feature_keys"]
		self.assertFalse(any(":document-action:purchase-order:" in key for key in keys))
		self.assertFalse(any(":document-action:request-for-quotation:" in key for key in keys))
		self.assertFalse(any(":document-action:supplier-quotation:" in key for key in keys))
		self.assertFalse(any(":document-action:supplier-scorecard:" in key for key in keys))


if __name__ == "__main__":
	unittest.main()
