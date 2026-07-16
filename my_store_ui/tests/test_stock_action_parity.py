from __future__ import annotations

import unittest

import frappe

from my_store_ui.audit.parity_registry import (
	DOCTYPE_SPECIFIC_ACTIONS,
	DOCUMENT_ACTION_OVERRIDES,
	corrected_production_parity_audit,
)
from my_store_ui.universal.api import MAPPED_ACTIONS, _replace_stock_entry_alternatives, get_document_actions


class TestStockActionParity(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def _first_record(self, doctype: str):
		names = frappe.get_list(doctype, pluck="name", limit_page_length=1)
		return names[0] if names else None

	def test_source_verified_stock_actions_are_registered(self):
		expected = {
			"Material Request": {"bill_of_materials", "make_purchase_order_based_on_supplier", "subcontracted_purchase_order"},
			"Pick List": {"create_delivery_note", "create_dn_for_pick_lists", "create_stock_entry", "get_items"},
			"Purchase Receipt": {
				"asset_movement", "delivery_note", "make_inter_company_delivery_note",
				"make_purchase_return_against_rejected_warehouse", "make_stock_entry", "retention_stock_entry",
			},
			"Stock Entry": {
				"alternate_item", "bill_of_materials", "create_sample_retention_stock_entry", "disassemble",
				"expired_batches", "material_request", "purchase_invoice", "quality_inspection_s",
				"received_stock_entries", "transit_entry",
			},
			"Serial and Batch Bundle": {"create_serial_nos", "make_0"},
			"Stock Reconciliation": {"fetch_items_from_warehouse"},
		}
		for doctype, actions in expected.items():
			self.assertTrue(actions <= DOCTYPE_SPECIFIC_ACTIONS[doctype], f"Missing credits for {doctype}")

	def test_stock_mappings_use_fixed_symbolic_methods(self):
		expected = {
			"Material Request": {"make_purchase_order_based_on_supplier"},
			"Pick List": {"create_delivery_note", "create_stock_entry"},
			"Purchase Receipt": {
				"make_inter_company_delivery_note", "make_purchase_return_against_rejected_warehouse", "make_stock_entry",
			},
			"Stock Entry": {"create_sample_retention_stock_entry", "disassemble"},
			"BOM": {"make_quality_inspection"},
		}
		for doctype, actions in expected.items():
			for action in actions:
				self.assertIn(action, MAPPED_ACTIONS[doctype])
				self.assertNotIn(".", MAPPED_ACTIONS[doctype][action]["method"])

	def test_regional_and_helper_actions_have_truthful_classification(self):
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Stock Entry", "excise_invoice")][1], "not_required")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Stock Entry", "make_stock_entry")][1], "internal")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Quality Inspection", "make_quality_inspection")][2], "/retail-erp/operations/manufacturing/boms")

	def test_live_action_discovery_returns_only_symbolic_actions(self):
		for feature, doctype in {
			"material-request": "Material Request",
			"pick-list": "Pick List",
			"purchase-receipt": "Purchase Receipt",
			"stock-entry": "Stock Entry",
			"stock-reconciliation": "Stock Reconciliation",
		}.items():
			name = self._first_record(doctype)
			if not name:
				continue
			for action in get_document_actions(feature, name)["actions"]:
				self.assertNotIn(".", action["action"])
				self.assertFalse(action["action"].startswith("frappe"))

	def test_guest_cannot_discover_stock_document_actions(self):
		name = self._first_record("Stock Entry")
		if not name:
			self.skipTest("No Stock Entry exists on site1")
		frappe.set_user("Guest")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			get_document_actions("stock-entry", name)

	def test_alternate_item_payload_rejects_mass_assignment(self):
		doc = frappe.new_doc("Stock Entry")
		with self.assertRaises(frappe.ValidationError):
			_replace_stock_entry_alternatives(doc, '[{"docname":"row","alternate_item":"x","owner":"Administrator"}]')

	def test_corrected_audit_has_no_stock_action_items_left(self):
		keys = corrected_production_parity_audit()["required_but_missing_feature_keys"]
		stock_doctypes = {
			"inventory-dimension", "material-request", "pick-list", "price-list", "purchase-receipt",
			"quality-inspection", "serial-and-batch-bundle", "stock-entry", "stock-reconciliation",
		}
		self.assertFalse(any(any(f":document-action:{doctype}:" in key for doctype in stock_doctypes) for key in keys))


if __name__ == "__main__":
	unittest.main()
