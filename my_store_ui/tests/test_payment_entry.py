from __future__ import annotations

import unittest
from pathlib import Path
from uuid import uuid4

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.document_actions import execute_document_action, get_document_actions
from my_store_ui.form_api import get_entity_form, save_entity_form


class TestPaymentEntryLifecycle(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		pass

	def setUp(self):
		frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
		frappe.connect()
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def _draft(self):
		company = frappe.get_all("Company", pluck="name", limit=1)[0]
		accounts = frappe.get_all("Account", filters={"company": company, "is_group": 0, "disabled": 0}, pluck="name", limit=2)
		self.assertGreaterEqual(len(accounts), 2)
		values = get_entity_form("payment_entries")["document"]
		values.update({"payment_type": "Internal Transfer", "company": company, "paid_from": accounts[0], "paid_to": accounts[1], "paid_amount": 10, "received_amount": 10, "source_exchange_rate": 1, "target_exchange_rate": 1})
		return save_entity_form("payment_entries", values, request_id=f"payment-{uuid4().hex}")

	def tearDown(self):
		frappe.db.rollback()
		frappe.destroy()

	def test_internal_transfer_submit_cancel_and_amend(self):
		draft = self._draft()
		submitted = execute_document_action("payment_entries", draft["name"], "submit")
		self.assertEqual(submitted["docstatus"], 1)
		cancelled = execute_document_action("payment_entries", draft["name"], "cancel", expected_modified=submitted["modified"])
		self.assertEqual(cancelled["docstatus"], 2)
		amended = execute_document_action("payment_entries", draft["name"], "amend", expected_modified=cancelled["modified"])
		self.assertEqual(amended["docstatus"], 0)

	def test_actions_are_state_aware(self):
		draft = self._draft()
		self.assertIn("submit", {row["key"] for row in get_document_actions("payment_entries", draft["name"])["actions"]})

	def test_invalid_reference_is_rejected_before_save(self):
		company = frappe.get_all("Company", pluck="name", limit=1)[0]
		values = get_entity_form("payment_entries")["document"]
		values.update({"payment_type": "Internal Transfer", "company": company, "paid_amount": 10, "received_amount": 10, "references": [{"reference_doctype": "Sales Invoice", "reference_name": "NOT-A-REAL-INVOICE", "allocated_amount": 10}]})
		with self.assertRaises(frappe.ValidationError):
			save_entity_form("payment_entries", values, request_id="payment-invalid-12345678")
