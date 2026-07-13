from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.form_api import get_entity_form, save_entity_form
from my_store_ui.sales_order_actions import (
	create_mapped_document,
	execute_document_action,
	get_document_actions,
	get_mapped_document_preview,
)


class TestSalesOrderLifecycle(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
		frappe.connect()
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	@classmethod
	def tearDownClass(cls):
		frappe.destroy()

	def _draft_order(self):
		customer = frappe.get_list("Customer", filters={"disabled": 0}, pluck="name", limit_page_length=1)[0]
		company = frappe.defaults.get_global_default("company") or frappe.get_list("Company", pluck="name", limit_page_length=1)[0]
		item = frappe.get_list("Item", filters={"disabled": 0, "is_sales_item": 1}, pluck="name", limit_page_length=1)[0]
		warehouse = frappe.get_list("Warehouse", filters={"is_group": 0, "company": company}, pluck="name", limit_page_length=1)
		result = save_entity_form("sales_orders", {"customer": customer, "company": company, "transaction_date": "2026-07-13", "delivery_date": "2026-07-14", "order_type": "Sales", "set_warehouse": warehouse[0] if warehouse else None, "items": [{"item_code": item, "qty": 1, "warehouse": warehouse[0] if warehouse else None}]}, request_id=f"lifecycle-{uuid4().hex}")
		return frappe.get_doc("Sales Order", result["name"])

	def test_submit_rejects_stale_document_and_double_submit(self):
		try:
			doc = self._draft_order()
			with self.assertRaises(frappe.ValidationError):
				execute_document_action(doc.name, "submit", "2000-01-01 00:00:00")
			result = execute_document_action(doc.name, "submit", str(doc.modified))
			self.assertEqual(result["docstatus"], 1)
			with self.assertRaises(frappe.ValidationError):
				execute_document_action(doc.name, "submit", result["modified"])
		finally:
			frappe.db.rollback()

	def test_cancel_amend_and_mapping_use_standard_controller_paths(self):
		try:
			doc = self._draft_order()
			submitted = execute_document_action(doc.name, "submit", str(doc.modified))
			available = get_document_actions(doc.name)
			self.assertIn("cancel", {entry["key"] for entry in available["actions"]})
			preview = get_mapped_document_preview(doc.name, "sales_invoice", expected_modified=submitted["modified"])
			self.assertEqual(preview["target_doctype"], "Sales Invoice")
			mapped = create_mapped_document(doc.name, "sales_invoice", expected_modified=submitted["modified"])
			self.assertEqual(frappe.get_doc("Sales Invoice", mapped["name"]).docstatus, 0)
			delivery_preview = get_mapped_document_preview(doc.name, "delivery_note", expected_modified=submitted["modified"])
			self.assertEqual(delivery_preview["target_doctype"], "Delivery Note")
			delivery = create_mapped_document(doc.name, "delivery_note", expected_modified=submitted["modified"])
			self.assertEqual(frappe.get_doc("Delivery Note", delivery["name"]).docstatus, 0)
			for entity_key, mapped_name in (("sales_invoices", mapped["name"]), ("delivery_notes", delivery["name"])):
				form = get_entity_form(entity_key, mapped_name)
				saved = save_entity_form(entity_key, form["document"], name=mapped_name, request_id=f"mapped-{uuid4().hex}")
				self.assertEqual(saved["name"], mapped_name)
			with self.assertRaises(frappe.ValidationError):
				execute_document_action(doc.name, "cancel", submitted["modified"])
			# Remove the mapped Draft through rollback, then make a second isolated order
			frappe.db.rollback()
			doc = self._draft_order()
			submitted = execute_document_action(doc.name, "submit", str(doc.modified))
			cancelled = execute_document_action(doc.name, "cancel", submitted["modified"], {"reason": "test"})
			self.assertEqual(cancelled["docstatus"], 2)
			amended = execute_document_action(doc.name, "amend", cancelled["modified"])
			new_doc = frappe.get_doc("Sales Order", amended["name"])
			self.assertEqual(new_doc.docstatus, 0)
			self.assertEqual(new_doc.amended_from, doc.name)
		finally:
			frappe.db.rollback()

	def test_unknown_actions_and_permission_denial_are_rejected(self):
		try:
			doc = self._draft_order()
			with self.assertRaises(frappe.ValidationError):
				execute_document_action(doc.name, "arbitrary_method", str(doc.modified))
			with self.assertRaises(frappe.PermissionError):
				get_mapped_document_preview(doc.name, "unapproved_target", expected_modified=str(doc.modified))
			with patch("my_store_ui.sales_order_actions.frappe.has_permission", return_value=False):
				with self.assertRaises(frappe.PermissionError):
					get_document_actions(doc.name)
		finally:
			frappe.db.rollback()

	def test_active_workflow_blocks_direct_submission(self):
		try:
			doc = self._draft_order()
			with patch("my_store_ui.sales_order_actions._active_workflow", return_value="Sales Order Approval"):
				self.assertNotIn("submit", {entry["key"] for entry in get_document_actions(doc.name)["actions"]})
				with self.assertRaises(frappe.PermissionError):
					execute_document_action(doc.name, "submit", str(doc.modified))
		finally:
			frappe.db.rollback()


if __name__ == "__main__":
	unittest.main()
