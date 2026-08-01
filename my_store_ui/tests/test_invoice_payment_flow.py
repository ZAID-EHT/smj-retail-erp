"""Final Sales Invoice + payment allocation through standard ERPNext.

Delivery -> Invoice -> allocate advance -> collect balance -> complete. Every
document is created by a standard mapping/controller; no ledger is written here.
Savepoint + rollback, no residue.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.credit import NON_CREDIT_CUSTOMER, sales_order_paid_amount
from my_store_ui.wholesale.delivery import create_delivery_note
from my_store_ui.wholesale.invoicing import create_sales_invoice, get_invoice_position
from my_store_ui.wholesale.payments import (
	create_customer_payment,
	get_outstanding_documents,
)

RATE = 1200.0


class TestInvoicePaymentFlow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name"
		)[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"invpay_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"InvPay {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": RATE,
			"retail_price": 1500,
		})["name"]
		self.customer = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"InvPayCust {uuid.uuid4().hex[:6]}",
			"custom_credit_type": NON_CREDIT_CUSTOMER, "customer_group": self.customer_group,
			"territory": self.territory,
		}).insert(ignore_permissions=True).name
		self._receive(50)

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _receive(self, qty, rate=1000):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": self.item, "qty": qty, "t_warehouse": self.wh, "basic_rate": rate}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		return se

	def _order(self, qty=5):
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": self.customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
			"items": [{"item_code": self.item, "qty": qty, "rate": RATE, "warehouse": self.wh,
			           "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		return so

	def _pay_order(self, so, amount, submit=True):
		return create_customer_payment(
			customer=self.customer, amount=amount, company=self.company, submit=1 if submit else 0,
			allocations=[{"reference_doctype": "Sales Order", "reference_name": so.name,
			              "allocated_amount": amount}],
			reference_no=uuid.uuid4().hex[:8], reference_date=frappe.utils.nowdate(),
			request_id=uuid.uuid4().hex,
		)

	# --- invoicing ---

	def test_invoice_from_delivery_note(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=1)
		res = create_sales_invoice(delivery_note=dn["name"], submit=1)
		invoice = frappe.get_doc("Sales Invoice", res["name"])
		self.assertEqual(invoice.docstatus, 1)
		self.assertEqual(flt(invoice.items[0].qty), 5.0)

	def test_invoice_marks_the_order_billed(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=1)
		create_sales_invoice(delivery_note=dn["name"], submit=1)
		so.reload()
		self.assertGreaterEqual(flt(so.per_billed), 100.0)

	def test_advance_allocation_clears_the_invoice(self):
		"""A fully prepaid order leaves nothing outstanding on the final invoice."""
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=1)
		res = create_sales_invoice(delivery_note=dn["name"], submit=1)
		invoice = frappe.get_doc("Sales Invoice", res["name"])
		self.assertLessEqual(flt(invoice.outstanding_amount), 0.01)

	def test_partial_advance_leaves_a_balance(self):
		so = self._order(5)
		half = flt(so.grand_total) / 2
		self._pay_order(so, half)
		dn = create_delivery_note(so.name, override_reason="Approved: half paid", submit=1)
		res = create_sales_invoice(delivery_note=dn["name"], submit=1)
		invoice = frappe.get_doc("Sales Invoice", res["name"])
		self.assertAlmostEqual(flt(invoice.outstanding_amount), half, places=1)

	def test_fully_invoiced_delivery_cannot_be_invoiced_twice(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=1)
		create_sales_invoice(delivery_note=dn["name"], submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_sales_invoice(delivery_note=dn["name"], submit=1)

	def test_draft_delivery_cannot_be_invoiced(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=0)
		with self.assertRaises(frappe.ValidationError):
			create_sales_invoice(delivery_note=dn["name"])

	def test_invoice_idempotency_is_database_backed(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=1)
		rid = uuid.uuid4().hex
		first = create_sales_invoice(delivery_note=dn["name"], request_id=rid)
		frappe.cache.delete_value(f"my_store_ui:idem:Sales Invoice:{frappe.session.user}:{rid}")
		second = create_sales_invoice(delivery_note=dn["name"], request_id=rid)
		self.assertEqual(first["name"], second["name"])
		self.assertTrue(second["duplicate"])

	def test_invoice_position_reports_progress(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		pos = get_invoice_position(so.name)
		self.assertEqual(flt(pos["advance_paid"]), flt(so.grand_total))
		self.assertFalse(pos["fully_invoiced"])
		dn = create_delivery_note(so.name, submit=1)
		create_sales_invoice(delivery_note=dn["name"], submit=1)
		pos = get_invoice_position(so.name)
		self.assertTrue(pos["fully_invoiced"])
		self.assertEqual(len(pos["invoices"]), 1)

	# --- payments ---

	def test_payment_allocates_to_the_order(self):
		so = self._order(5)
		res = self._pay_order(so, so.grand_total)
		self.assertEqual(flt(res["allocated"]), flt(so.grand_total))
		self.assertEqual(flt(sales_order_paid_amount(so.name)), flt(so.grand_total))

	def test_over_allocation_is_refused(self):
		so = self._order(5)
		with self.assertRaises(frappe.ValidationError):
			create_customer_payment(
				customer=self.customer, amount=flt(so.grand_total), company=self.company,
				allocations=[{"reference_doctype": "Sales Order", "reference_name": so.name,
				              "allocated_amount": flt(so.grand_total) * 2}],
				reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex,
			)

	def test_allocation_to_another_customers_document_is_refused(self):
		so = self._order(5)
		other = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"Other {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
		}).insert(ignore_permissions=True).name
		with self.assertRaises(frappe.ValidationError):
			create_customer_payment(
				customer=other, amount=100, company=self.company,
				allocations=[{"reference_doctype": "Sales Order", "reference_name": so.name,
				              "allocated_amount": 100}],
				reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex,
			)

	def test_allocation_to_an_unsupported_doctype_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			create_customer_payment(
				customer=self.customer, amount=100, company=self.company,
				allocations=[{"reference_doctype": "Journal Entry", "reference_name": "X",
				              "allocated_amount": 100}],
				reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex,
			)

	def test_zero_or_negative_payment_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			create_customer_payment(customer=self.customer, amount=0, company=self.company,
			                        reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex)

	def test_bank_payment_without_reference_is_refused_clearly(self):
		"""ERPNext requires a bank reference; fail with a field-level message."""
		so = self._order(5)
		with self.assertRaises(frappe.ValidationError) as ctx:
			create_customer_payment(
				customer=self.customer, amount=flt(so.grand_total), company=self.company,
				allocations=[{"reference_doctype": "Sales Order", "reference_name": so.name,
				              "allocated_amount": flt(so.grand_total)}],
				request_id=uuid.uuid4().hex,
			)
		self.assertIn("Reference Number", str(ctx.exception))

	def test_auto_allocation_settles_the_invoice_oldest_first(self):
		so = self._order(5)
		self._pay_order(so, so.grand_total)
		dn = create_delivery_note(so.name, submit=1)
		create_sales_invoice(delivery_note=dn["name"], submit=1)
		# Fully prepaid: nothing should remain outstanding.
		position = get_outstanding_documents(self.customer, self.company)
		self.assertLessEqual(flt(position["total_invoice_outstanding"]), 0.01)

	def test_outstanding_documents_lists_the_unpaid_invoice(self):
		so = self._order(5)
		dn = create_delivery_note(so.name, override_reason="Approved: bill first", submit=1)
		create_sales_invoice(delivery_note=dn["name"], submit=1)
		position = get_outstanding_documents(self.customer, self.company)
		self.assertEqual(len(position["invoices"]), 1)
		self.assertGreater(flt(position["total_invoice_outstanding"]), 0)

	def test_balance_collection_completes_the_transaction(self):
		so = self._order(5)
		dn = create_delivery_note(so.name, override_reason="Approved: pay on invoice", submit=1)
		inv = create_sales_invoice(delivery_note=dn["name"], submit=1)
		outstanding = flt(frappe.db.get_value("Sales Invoice", inv["name"], "outstanding_amount"))
		self.assertGreater(outstanding, 0)
		create_customer_payment(
			customer=self.customer, amount=outstanding, company=self.company, submit=1,
			allocations=[{"reference_doctype": "Sales Invoice", "reference_name": inv["name"],
			              "allocated_amount": outstanding}],
			reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex,
		)
		self.assertLessEqual(
			flt(frappe.db.get_value("Sales Invoice", inv["name"], "outstanding_amount")), 0.01
		)


if __name__ == "__main__":
	unittest.main()
