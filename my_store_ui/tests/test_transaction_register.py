"""Wholesale Transaction Register: statuses, filters and permission filtering.

The register is assembled from standard ERPNext links only. Savepoint + rollback.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.api import create_draft_sales_order
from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.credit import NON_CREDIT_CUSTOMER
from my_store_ui.wholesale.delivery import create_delivery_note
from my_store_ui.wholesale.invoicing import create_sales_invoice
from my_store_ui.wholesale.payments import create_customer_payment
from my_store_ui.wholesale.register import (
	get_transaction_timeline,
	get_wholesale_transactions,
)
from my_store_ui.wholesale.returns import create_sales_return

RATE = 1200.0


class TestTransactionRegister(unittest.TestCase):
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
		self.sp = f"reg_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"Reg {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": RATE,
			"retail_price": 1500,
		})["name"]
		self.customer = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"RegCust {uuid.uuid4().hex[:6]}",
			"custom_credit_type": NON_CREDIT_CUSTOMER, "customer_group": self.customer_group,
			"territory": self.territory, "default_price_list": "Wholesale Price List",
		}).insert(ignore_permissions=True).name
		self._receive(50)

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _receive(self, qty):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": self.item, "qty": qty, "t_warehouse": self.wh, "basic_rate": 1000}],
		})
		se.insert(ignore_permissions=True)
		se.submit()

	def _order(self, qty=5):
		res = create_draft_sales_order({
			"request_id": uuid.uuid4().hex, "customer": self.customer, "company": self.company,
			"warehouse": self.wh, "items": [{"item_code": self.item, "qty": qty}],
		})
		order = frappe.get_doc("Sales Order", res["name"])
		order.submit()
		order.reload()
		return order

	def _pay(self, order, amount):
		create_customer_payment(
			customer=self.customer, amount=amount, company=self.company, submit=1,
			allocations=[{"reference_doctype": "Sales Order", "reference_name": order.name,
			              "allocated_amount": amount}],
			reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex,
		)

	def _row_for(self, order, **filters):
		res = get_wholesale_transactions(filters={"customer": self.customer, **filters})
		return next((r for r in res["rows"] if r["sales_order"] == order.name), None)

	# --- statuses ---

	def test_new_order_shows_not_delivered_and_not_invoiced(self):
		order = self._order()
		row = self._row_for(order)
		self.assertIsNotNone(row)
		self.assertEqual(row["delivery_status"], "Not Delivered")
		self.assertEqual(row["invoice_status"], "Not Invoiced")
		self.assertEqual(row["return_status"], "No Return")
		self.assertEqual(row["payment_status"], "Unpaid")

	def test_transaction_id_is_exposed(self):
		order = self._order()
		row = self._row_for(order)
		self.assertTrue(row["transaction_id"])
		if row["transaction_id"] != order.name:
			self.assertTrue(row["transaction_id"].startswith("TRX-"))

	def test_partial_delivery_shows_partially_delivered(self):
		order = self._order(10)
		self._pay(order, order.grand_total)
		create_delivery_note(order.name, lines=[{"idx": 1, "qty": 4}], submit=1)
		row = self._row_for(order)
		self.assertEqual(row["delivery_status"], "Partially Delivered")

	def test_full_cycle_shows_delivered_invoiced_and_paid(self):
		order = self._order(5)
		self._pay(order, order.grand_total)
		note = create_delivery_note(order.name, submit=1)
		create_sales_invoice(delivery_note=note["name"], submit=1)
		row = self._row_for(order)
		self.assertEqual(row["delivery_status"], "Fully Delivered")
		self.assertEqual(row["invoice_status"], "Fully Invoiced")
		self.assertEqual(row["payment_status"], "Paid")

	def test_return_is_reflected_in_the_register(self):
		order = self._order(10)
		self._pay(order, order.grand_total)
		note = create_delivery_note(order.name, submit=1)
		create_sales_return(note["name"], lines=[{"idx": 1, "qty": 3}], reason="Damaged", submit=1)
		row = self._row_for(order)
		self.assertNotEqual(row["return_status"], "No Return")
		self.assertEqual(len(row["return_notes"]), 1)

	def test_linked_documents_are_listed(self):
		order = self._order(5)
		self._pay(order, order.grand_total)
		note = create_delivery_note(order.name, submit=1)
		invoice = create_sales_invoice(delivery_note=note["name"], submit=1)
		row = self._row_for(order)
		self.assertIn(note["name"], row["delivery_notes"])
		self.assertIn(invoice["name"], row["sales_invoices"])
		self.assertTrue(row["payment_entries"])

	# --- filters ---

	def test_delivery_status_filter_narrows_results(self):
		order = self._order(5)
		self.assertIsNotNone(self._row_for(order, delivery_status="Not Delivered"))
		self.assertIsNone(self._row_for(order, delivery_status="Fully Delivered"))

	def test_invoice_status_filter_narrows_results(self):
		order = self._order(5)
		self.assertIsNotNone(self._row_for(order, invoice_status="Not Invoiced"))
		self.assertIsNone(self._row_for(order, invoice_status="Fully Invoiced"))

	def test_company_filter_applies(self):
		order = self._order(5)
		self.assertIsNotNone(self._row_for(order, company=self.company))

	def test_unsupported_filter_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			get_wholesale_transactions(filters={"drop_table": 1})

	def test_unsupported_sort_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			get_wholesale_transactions(sort_field="grand_total; DROP TABLE")

	def test_page_size_is_capped(self):
		res = get_wholesale_transactions(page_size=100000)
		self.assertLessEqual(res["pagination"]["page_size"], 100)

	# --- timeline ---

	def test_timeline_reports_the_lifecycle(self):
		order = self._order(5)
		self._pay(order, order.grand_total)
		note = create_delivery_note(order.name, submit=1)
		create_sales_invoice(delivery_note=note["name"], submit=1)
		timeline = get_transaction_timeline(order.name)
		self.assertTrue(timeline)


if __name__ == "__main__":
	unittest.main()
