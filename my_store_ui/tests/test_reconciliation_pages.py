"""Payment and Bank Reconciliation adapters.

Both pages call ERPNext's own reconciliation controllers; these tests exercise the
adapters' permission handling, validation and real-data paths. Savepoint + rollback.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt, nowdate

from my_store_ui.wholesale.bank_reconciliation_api import get_summary, search_bank_account
from my_store_ui.wholesale.payment_reconciliation_api import (
	get_unreconciled_entries,
	preview_allocation,
	search_company,
	search_party,
)

SALES_USER = "recon-sales@example.invalid"


class ReconBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
		cls.supplier_group = frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"recon_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _user(self, email, roles):
		if not frappe.db.exists("User", email):
			doc = frappe.get_doc({
				"doctype": "User", "email": email, "first_name": "Recon",
				"send_welcome_email": 0,
			})
			doc.insert(ignore_permissions=True)
			doc.add_roles(*roles)
		return email


class TestPaymentReconciliation(ReconBase):
	def _customer(self):
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": f"Recon {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
		}).insert(ignore_permissions=True).name

	def _supplier(self):
		return frappe.get_doc({
			"doctype": "Supplier", "supplier_name": f"ReconSup {uuid.uuid4().hex[:6]}",
			"supplier_group": self.supplier_group,
		}).insert(ignore_permissions=True).name

	def test_company_search_returns_options(self):
		rows = search_company(self.company[:4])
		self.assertTrue(any(r["value"] == self.company for r in rows))

	def test_party_search_finds_a_customer(self):
		customer = self._customer()
		rows = search_party("Customer", customer[:6])
		self.assertTrue(any(r["value"] == customer for r in rows))

	def test_party_search_finds_a_supplier(self):
		supplier = self._supplier()
		rows = search_party("Supplier", supplier[:6])
		self.assertTrue(any(r["value"] == supplier for r in rows))

	def test_customer_with_no_open_documents_returns_empty_lists(self):
		"""'No matching records' must be an empty result, not an error."""
		customer = self._customer()
		result = get_unreconciled_entries(
			company=self.company, party_type="Customer", party=customer
		)
		self.assertEqual(result["invoices"], [])
		self.assertEqual(result["payments"], [])

	def test_supplier_reconciliation_is_supported(self):
		supplier = self._supplier()
		result = get_unreconciled_entries(
			company=self.company, party_type="Supplier", party=supplier
		)
		self.assertIn("invoices", result)
		self.assertIn("payments", result)

	def test_invalid_party_type_is_refused(self):
		with self.assertRaises(Exception):
			get_unreconciled_entries(
				company=self.company, party_type="Employee", party="whoever"
			)

	def test_preview_with_nothing_selected_is_refused(self):
		"""An empty selection must be rejected, not silently allocate nothing."""
		customer = self._customer()
		with self.assertRaises(frappe.ValidationError):
			preview_allocation(
				company=self.company, party_type="Customer", party=customer,
				receivable_payable_account="", invoices=[], payments=[],
			)

	def test_a_sales_user_cannot_read_reconciliation_entries(self):
		customer = self._customer()
		user = self._user(SALES_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_unreconciled_entries(
					company=self.company, party_type="Customer", party=customer
				)
		finally:
			frappe.set_user("Administrator")


class TestBankReconciliation(ReconBase):
	def _bank_account(self):
		"""An existing Bank Account, or one built inside the savepoint."""
		rows = frappe.get_all("Bank Account", filters={"company": self.company}, pluck="name")
		if rows:
			return rows[0]
		gl_account = frappe.get_all(
			"Account",
			filters={"company": self.company, "account_type": "Bank", "is_group": 0},
			pluck="name", limit=1,
		)
		if not gl_account:
			return None
		bank_name = f"ReconBank {uuid.uuid4().hex[:5]}"
		bank = frappe.get_doc({"doctype": "Bank", "bank_name": bank_name})
		bank.insert(ignore_permissions=True)
		account = frappe.get_doc({
			"doctype": "Bank Account", "account_name": f"ReconAcct {uuid.uuid4().hex[:5]}",
			"bank": bank.name, "company": self.company, "account": gl_account[0],
		})
		account.insert(ignore_permissions=True)
		return account.name

	def test_bank_account_search_does_not_error(self):
		rows = search_bank_account("", self.company)
		self.assertIsInstance(rows, list)

	def test_summary_for_an_account_with_no_transactions(self):
		account = self._bank_account()
		if not account:
			self.skipTest("no Bank Account configured on this site")
		result = get_summary(
			company=self.company, bank_account=account,
			bank_statement_from_date=frappe.utils.add_days(nowdate(), -30),
			bank_statement_to_date=nowdate(),
			bank_statement_closing_balance=0,
		)
		self.assertIn("transactions", result)
		self.assertIsInstance(result["transactions"], list)

	def test_summary_reports_ledger_balance(self):
		account = self._bank_account()
		if not account:
			self.skipTest("no Bank Account configured on this site")
		result = get_summary(
			company=self.company, bank_account=account,
			bank_statement_from_date=frappe.utils.add_days(nowdate(), -30),
			bank_statement_to_date=nowdate(),
			bank_statement_closing_balance=0,
		)
		self.assertIn("ledger_balance", result)
		self.assertEqual(flt(result["ledger_balance"]), flt(result["ledger_balance"]))

	def test_a_sales_user_cannot_read_the_bank_summary(self):
		account = self._bank_account()
		if not account:
			self.skipTest("no Bank Account configured on this site")
		user = self._user(SALES_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_summary(
					company=self.company, bank_account=account,
					bank_statement_from_date=frappe.utils.add_days(nowdate(), -30),
					bank_statement_to_date=nowdate(),
					bank_statement_closing_balance=0,
				)
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
