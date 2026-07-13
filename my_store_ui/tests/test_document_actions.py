from __future__ import annotations

import unittest

import frappe

from my_store_ui.document_actions import ENTITY_REGISTRY, _definition


class TestDocumentActionRegistry(unittest.TestCase):
	def test_delivery_note_and_invoice_are_allowlisted(self):
		self.assertEqual(set(ENTITY_REGISTRY), {"delivery_notes", "sales_invoices", "payment_entries"})
		self.assertEqual(ENTITY_REGISTRY["delivery_notes"]["doctype"], "Delivery Note")
		self.assertEqual(ENTITY_REGISTRY["sales_invoices"]["doctype"], "Sales Invoice")

	def test_unknown_entity_is_not_allowlisted(self):
		self.assertNotIn("Journal Entry", ENTITY_REGISTRY)
