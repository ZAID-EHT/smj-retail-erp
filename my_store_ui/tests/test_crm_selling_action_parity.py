from __future__ import annotations

import unittest

import frappe

from my_store_ui.audit.parity_registry import DOCTYPE_SPECIFIC_ACTIONS, DOCUMENT_ACTION_OVERRIDES, corrected_production_parity_audit
from my_store_ui.services.priority_registry import CANONICAL_ROUTE_BY_DOCTYPE
from my_store_ui.universal.api import MAPPED_ACTIONS, get_document_actions


class TestCrmSellingActionParity(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_source_verified_actions_are_registered(self):
		expected = {
			"Campaign": {"view_leads"},
			"Delivery Trip": {"delivery_note", "delivery_notes", "notify_customers_via_email"},
			"Installation Note": {"from_delivery_note"},
			"Lead": {"add_to_prospect", "create_prospect_and_contact"},
			"Opportunity": {"fetch_latest_exchange_rate"},
			"Prospect": {"customer", "make_customer", "make_opportunity", "opportunity"},
			"Quotation": {"opportunity", "update_items"},
			"Maintenance Schedule": {"sales_order"},
			"Maintenance Visit": {"sales_order"},
		}
		for doctype, actions in expected.items():
			self.assertTrue(actions <= DOCTYPE_SPECIFIC_ACTIONS[doctype], f"Missing credits for {doctype}")

	def test_prospect_mappings_use_symbolic_allowlist(self):
		for action in {"make_customer", "make_opportunity"}:
			self.assertIn(action, MAPPED_ACTIONS["Prospect"])
			self.assertNotIn(".", MAPPED_ACTIONS["Prospect"][action]["method"])

	def test_communication_helpers_are_not_misattributed_buttons(self):
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Lead", "make_lead_from_communication")][1], "internal")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Opportunity", "make_opportunity_from_communication")][1], "internal")

	def test_new_transaction_routes_are_registered(self):
		self.assertEqual(CANONICAL_ROUTE_BY_DOCTYPE["Blanket Order"], "/sales/blanket-orders")
		self.assertEqual(CANONICAL_ROUTE_BY_DOCTYPE["Maintenance Schedule"], "/operations/maintenance-schedules")
		self.assertEqual(CANONICAL_ROUTE_BY_DOCTYPE["Maintenance Visit"], "/operations/maintenance-visits")

	def test_live_quotation_actions_remain_symbolic(self):
		names = frappe.get_list("Quotation", pluck="name", limit_page_length=1)
		if not names:
			self.skipTest("No Quotation exists on site1")
		for action in get_document_actions("quotation", names[0])["actions"]:
			self.assertNotIn(".", action["action"])

	def test_corrected_audit_has_no_crm_selling_items_left(self):
		keys = corrected_production_parity_audit()["required_but_missing_feature_keys"]
		parents = {
			"blanket-order", "campaign", "delivery-trip", "installation-note", "lead",
			"maintenance-schedule", "maintenance-visit", "opportunity", "prospect", "quotation",
		}
		self.assertFalse(any(any(f":document-action:{parent}:" in key for parent in parents) for key in keys))


if __name__ == "__main__":
	unittest.main()
