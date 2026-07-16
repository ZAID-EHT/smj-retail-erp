from __future__ import annotations

import unittest
from pathlib import Path

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"
frappe.init(site="site1.local", sites_path=str(BENCH_PATH / "sites"))
frappe.connect()

from my_store_ui.audit.parity_registry import (
	BUILT_ADAPTER_ACTION_ROUTE,
	BUILT_ADAPTER_ACTIONS_BY_PARENT,
	BUILT_ADAPTER_DOCTYPE_NAMES,
)
from my_store_ui.priority_pages import get_priority_route_definition
from my_store_ui.universal.api import get_document_detail, get_doctype_metadata
from my_store_ui.universal.registry import GENERATED_ALLOWLIST
from my_store_ui.wholesale.bank_clearance_api import get_payment_entries, search_accounts


class TestSingleFinanceTools(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_clean_routes_dispatch_to_dedicated_single_pages(self):
		bank = get_priority_route_definition("/finance/bank-clearance")
		pegged = get_priority_route_definition("/finance/pegged-currencies")
		self.assertEqual(bank["component"], "bank_clearance")
		self.assertEqual(bank["doctype"], "Bank Clearance")
		self.assertEqual(pegged["component"], "pegged_currencies")
		self.assertEqual(pegged["doctype"], "Pegged Currencies")

	def test_guest_cannot_resolve_or_use_finance_tools(self):
		frappe.set_user("Guest")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			get_priority_route_definition("/finance/bank-clearance")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			search_accounts()

	def test_bank_clearance_preview_uses_real_controller_without_saving_tool(self):
		accounts = search_accounts()
		if not accounts:
			self.skipTest("No permitted Bank or Cash Account exists on site1")
		stored_before = frappe.db.get_singles_dict("Bank Clearance")
		result = get_payment_entries({
			"account": accounts[0]["value"],
			"from_date": "2020-01-01",
			"to_date": "2035-12-31",
			"include_reconciled_entries": 1,
			"include_pos_transactions": 0,
		})
		self.assertIn("payment_entries", result)
		self.assertEqual(frappe.db.get_singles_dict("Bank Clearance"), stored_before)
		for row in result["payment_entries"]:
			self.assertIn(row["payment_document"], {"Journal Entry", "Payment Entry", "Purchase Invoice", "Sales Invoice"})
			self.assertTrue(frappe.has_permission(row["payment_document"], "read"))

	def test_bank_clearance_rejects_unavailable_account(self):
		with self.assertRaises((frappe.PermissionError, frappe.ValidationError)):
			get_payment_entries({
				"account": "not-a-permitted-bank-account",
				"from_date": "2026-01-01",
				"to_date": "2026-12-31",
			})

	def test_pegged_currencies_metadata_and_single_detail_are_available(self):
		self.assertIn("Pegged Currencies", GENERATED_ALLOWLIST)
		metadata = get_doctype_metadata("pegged-currencies")
		self.assertTrue(metadata["is_single"])
		self.assertTrue(metadata["permissions"]["can_read"])
		field = next(item for item in metadata["fields"] if item["fieldname"] == "pegged_currency_item")
		self.assertEqual(field["fieldtype"], "Table")
		self.assertEqual({item["fieldname"] for item in field["child_fields"]}, {"source_currency", "pegged_against", "pegged_exchange_rate"})
		detail = get_document_detail("pegged-currencies", "Pegged Currencies")
		self.assertEqual(detail["document"]["name"], "Pegged Currencies")
		self.assertIsInstance(detail["document"]["pegged_currency_item"], list)

	def test_adapter_credit_and_frontend_wiring_are_explicit(self):
		self.assertIn("Bank Clearance", BUILT_ADAPTER_DOCTYPE_NAMES)
		self.assertIn("Pegged Currencies", BUILT_ADAPTER_DOCTYPE_NAMES)
		self.assertEqual(
			BUILT_ADAPTER_ACTIONS_BY_PARENT["Bank Clearance"],
			{"get_payment_entries", "update_clearance_date"},
		)
		self.assertEqual(BUILT_ADAPTER_ACTION_ROUTE["Bank Clearance"], "/retail-erp/finance/bank-clearance")
		route_page = (APP_PATH / "frontend/src/pages/priority/PriorityRoutePage.vue").read_text()
		self.assertIn("BankClearancePage", route_page)
		self.assertIn("PeggedCurrenciesPage", route_page)

	def test_adapter_has_no_permission_bypass_or_direct_sql(self):
		source = (APP_PATH / "my_store_ui/wholesale/bank_clearance_api.py").read_text()
		self.assertNotIn("ignore_permissions", source)
		self.assertNotIn("frappe.db.sql", source)
		self.assertIn("doc.get_payment_entries()", source)
		self.assertIn("doc.update_clearance_date()", source)


if __name__ == "__main__":
	unittest.main()
