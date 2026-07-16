from __future__ import annotations

import unittest
from pathlib import Path

import frappe

from my_store_ui.audit.parity_registry import (
	DOCTYPE_SPECIFIC_ACTIONS,
	DOCUMENT_ACTION_OVERRIDES,
	corrected_production_parity_audit,
)
from my_store_ui.universal.api import MAPPED_ACTIONS, _populate_invoice_discounting, get_document_actions


APP_PATH = Path(__file__).resolve().parents[2]


class TestAccountsActionParity(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def _first_record(self, doctype: str):
		names = frappe.get_list(doctype, pluck="name", limit_page_length=1)
		return names[0] if names else None

	def test_source_verified_accounts_actions_are_registered(self):
		expected = {
			"Accounting Dimension": {"show_0"},
			"Bank Account": {"unlink_external_integrations"},
			"Bank Reconciliation Tool": {"upload_bank_statement"},
			"Bank Statement Import": {"export_errored_rows", "export_import_log", "go_to_0_list"},
			"Cheque Print Template": {"create_or_update_cheque_print_format"},
			"Dunning": {"fetch_overdue_payments"},
			"Invoice Discounting": {"accounting_ledger", "close_loan", "create_disbursement_entry", "get_invoices"},
			"Payment Order": {"make_payment_records", "payment_request"},
			"Payment Request": {"make_payment_entry", "resend_payment_email"},
			"Process Statement Of Accounts": {"download", "send_emails"},
			"Share Transfer": {"make_jv_entry"},
			"Shareholder": {"share_balance", "share_ledger"},
			"Subscription": {"cancel_subscription", "fetch_subscription_updates", "force_fetch_subscription_updates", "restart_subscription"},
		}
		for doctype, actions in expected.items():
			self.assertTrue(actions <= DOCTYPE_SPECIFIC_ACTIONS[doctype], f"Missing credits for {doctype}")

	def test_accounts_mappings_use_fixed_symbolic_methods(self):
		expected = {
			"Purchase Invoice": {"make_inter_company_sales_invoice", "make_purchase_receipt", "make_stock_entry"},
			"Journal Entry": {"make_inter_company_journal_entry"},
			"Invoice Discounting": {"create_disbursement_entry", "close_loan"},
			"Payment Request": {"make_payment_entry"},
			"Share Transfer": {"make_jv_entry"},
		}
		for doctype, actions in expected.items():
			for action in actions:
				self.assertIn(action, MAPPED_ACTIONS[doctype])
				self.assertNotIn(".", MAPPED_ACTIONS[doctype][action]["method"])

	def test_misattributed_helpers_have_truthful_routes_or_internal_status(self):
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Journal Entry", "quick_entry")][2], "/retail-erp/finance/journal-entries/new")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Payment Request", "make_payment_order")][2], "/retail-erp/finance/payment-order/new")
		self.assertEqual(DOCUMENT_ACTION_OVERRIDES[("Bank Statement Import", "report_error")][1], "internal")

	def test_live_action_discovery_returns_only_symbolic_actions(self):
		for feature, doctype in {
			"purchase-invoice": "Purchase Invoice",
			"journal-entry": "Journal Entry",
			"payment-request": "Payment Request",
			"subscription": "Subscription",
			"process-statement-of-accounts": "Process Statement Of Accounts",
		}.items():
			name = self._first_record(doctype)
			if not name:
				continue
			for action in get_document_actions(feature, name)["actions"]:
				self.assertNotIn(".", action["action"])
				self.assertFalse(action["action"].startswith("frappe"))

	def test_guest_cannot_discover_accounts_document_actions(self):
		name = self._first_record("Purchase Invoice")
		if not name:
			self.skipTest("No Purchase Invoice exists on site1")
		frappe.set_user("Guest")
		with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
			get_document_actions("purchase-invoice", name)

	def test_invoice_discounting_filters_reject_mass_assignment(self):
		doc = frappe.new_doc("Invoice Discounting")
		with self.assertRaises(frappe.ValidationError):
			_populate_invoice_discounting(doc, '{"customer":"x","owner":"Administrator"}')

	def test_frontend_exposes_bank_statement_upload_without_desk(self):
		page = (APP_PATH / "frontend/src/pages/priority/BankReconciliationPage.vue").read_text()
		self.assertIn("Upload bank statement", page)
		self.assertIn("/finance/bank-statement-import/new", page)
		self.assertNotIn("/app/", page)

	def test_corrected_audit_has_no_accounts_items_left(self):
		keys = corrected_production_parity_audit()["required_but_missing_feature_keys"]
		accounts_doctypes = {
			"accounting-dimension", "bank-account", "bank-reconciliation-tool", "bank-statement-import",
			"cheque-print-template", "dunning", "invoice-discounting", "journal-entry", "party-link",
			"payment-order", "payment-request", "pricing-rule", "process-statement-of-accounts",
			"purchase-invoice", "share-transfer", "shareholder", "subscription", "unreconcile-payment",
		}
		self.assertFalse(any(any(f":document-action:{doctype}:" in key for doctype in accounts_doctypes) for key in keys))


if __name__ == "__main__":
	unittest.main()
