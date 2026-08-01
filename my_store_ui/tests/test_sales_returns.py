"""Sales returns: Return Delivery Note, Credit Note, stock restoration.

All return documents come from ERPNext's own return mappings, so stock goes back
through the standard Stock Ledger and the receivable is reduced by the standard
accounting controller. Savepoint + rollback, no residue.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.credit import NON_CREDIT_CUSTOMER
from my_store_ui.wholesale.delivery import create_delivery_note
from my_store_ui.wholesale.invoicing import create_sales_invoice
from my_store_ui.wholesale.payments import create_customer_payment
from my_store_ui.wholesale.returns import (
	create_credit_note,
	create_sales_return,
	get_return_position,
)

RATE = 1200.0


class TestSalesReturns(unittest.TestCase):
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
		self.sp = f"ret_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"Ret {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": RATE,
			"retail_price": 1500,
		})["name"]
		self.customer = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"RetCust {uuid.uuid4().hex[:6]}",
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

	def _delivered(self, qty=10):
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": self.customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
			"items": [{"item_code": self.item, "qty": qty, "rate": RATE, "warehouse": self.wh,
			           "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		create_customer_payment(
			customer=self.customer, amount=so.grand_total, company=self.company, submit=1,
			allocations=[{"reference_doctype": "Sales Order", "reference_name": so.name,
			              "allocated_amount": so.grand_total}],
			reference_no=uuid.uuid4().hex[:8], request_id=uuid.uuid4().hex,
		)
		dn = create_delivery_note(so.name, submit=1)
		return so, dn["name"]

	def _bin_qty(self):
		return flt(frappe.db.get_value("Bin", {"item_code": self.item, "warehouse": self.wh}, "actual_qty"))

	# --- position ---

	def test_return_position_lists_returnable_quantity(self):
		_, dn = self._delivered(10)
		position = get_return_position(dn)
		self.assertEqual(flt(position["lines"][0]["returnable_qty"]), 10.0)
		self.assertFalse(position["fully_returned"])

	def test_draft_delivery_cannot_be_returned(self):
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": self.customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
			"items": [{"item_code": self.item, "qty": 3, "rate": RATE, "warehouse": self.wh,
			           "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		dn = create_delivery_note(so.name, override_reason="test", submit=0)
		with self.assertRaises(frappe.ValidationError):
			get_return_position(dn["name"])

	# --- full and partial returns ---

	def test_full_return_restores_stock(self):
		_, dn = self._delivered(10)
		before = self._bin_qty()
		create_sales_return(dn, reason="Damaged", submit=1)
		self.assertEqual(self._bin_qty() - before, 10.0)

	def test_partial_return_leaves_the_rest_returnable(self):
		_, dn = self._delivered(10)
		create_sales_return(dn, lines=[{"idx": 1, "qty": 4}], reason="Quality Issue", submit=1)
		position = get_return_position(dn)
		self.assertEqual(flt(position["lines"][0]["returned_qty"]), 4.0)
		self.assertEqual(flt(position["lines"][0]["returnable_qty"]), 6.0)

	def test_return_document_has_negative_quantities(self):
		_, dn = self._delivered(10)
		res = create_sales_return(dn, lines=[{"idx": 1, "qty": 4}], reason="Damaged", submit=1)
		ret = frappe.get_doc("Delivery Note", res["name"])
		self.assertTrue(ret.is_return)
		self.assertEqual(flt(ret.items[0].qty), -4.0)
		self.assertEqual(ret.return_against, dn)

	def test_return_above_delivered_quantity_is_refused(self):
		_, dn = self._delivered(10)
		with self.assertRaises(frappe.ValidationError):
			create_sales_return(dn, lines=[{"idx": 1, "qty": 11}], reason="Damaged")

	def test_second_return_cannot_exceed_the_remainder(self):
		_, dn = self._delivered(10)
		create_sales_return(dn, lines=[{"idx": 1, "qty": 7}], reason="Damaged", submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_sales_return(dn, lines=[{"idx": 1, "qty": 4}], reason="Damaged")

	def test_fully_returned_delivery_cannot_be_returned_again(self):
		_, dn = self._delivered(10)
		create_sales_return(dn, reason="Customer Cancelled", submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_sales_return(dn, reason="Damaged")

	# --- reason and condition ---

	def test_reason_is_required(self):
		_, dn = self._delivered(10)
		with self.assertRaises(frappe.ValidationError):
			create_sales_return(dn, reason="   ")

	def test_invalid_reason_is_refused(self):
		_, dn = self._delivered(10)
		with self.assertRaises(frappe.ValidationError):
			create_sales_return(dn, reason="Because I said so")

	def test_reason_and_condition_are_recorded(self):
		_, dn = self._delivered(10)
		res = create_sales_return(dn, lines=[{"idx": 1, "qty": 2}], reason="Damaged",
		                          condition="Two cartons crushed", submit=1)
		# Delivery Note has no `remarks` field in ERPNext v15 -- the reason is written
		# to whichever narrative field the doctype actually has.
		from my_store_ui.wholesale.returns import _narrative_field

		field = _narrative_field("Delivery Note")
		self.assertEqual(field, "instructions")
		text = frappe.db.get_value("Delivery Note", res["name"], field) or ""
		self.assertIn("Damaged", text)
		self.assertIn("Two cartons crushed", text)

	def test_return_to_an_invalid_warehouse_is_refused(self):
		_, dn = self._delivered(10)
		with self.assertRaises(frappe.ValidationError):
			create_sales_return(dn, reason="Damaged", warehouse="No-Such-Warehouse-XYZ")

	# --- credit note ---

	def test_credit_note_reduces_the_receivable(self):
		so, dn = self._delivered(10)
		inv = create_sales_invoice(delivery_note=dn, submit=1)
		ret = create_sales_return(dn, reason="Damaged", submit=1)
		self.assertTrue(ret["name"])
		credit = create_credit_note(inv["name"], submit=1)
		note = frappe.get_doc("Sales Invoice", credit["name"])
		self.assertTrue(note.is_return)
		self.assertLess(flt(note.grand_total), 0)
		self.assertEqual(note.return_against, inv["name"])

	def test_credit_note_cannot_be_credited_again(self):
		so, dn = self._delivered(10)
		inv = create_sales_invoice(delivery_note=dn, submit=1)
		credit = create_credit_note(inv["name"], submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_credit_note(credit["name"])

	def test_credit_note_against_draft_invoice_is_refused(self):
		so, dn = self._delivered(10)
		inv = create_sales_invoice(delivery_note=dn, submit=0)
		with self.assertRaises(frappe.ValidationError):
			create_credit_note(inv["name"])

	def test_return_idempotency_is_database_backed(self):
		_, dn = self._delivered(10)
		rid = uuid.uuid4().hex
		first = create_sales_return(dn, lines=[{"idx": 1, "qty": 2}], reason="Damaged", request_id=rid)
		frappe.cache.delete_value(f"my_store_ui:idem:Delivery Note:{frappe.session.user}:{rid}")
		second = create_sales_return(dn, lines=[{"idx": 1, "qty": 2}], reason="Damaged", request_id=rid)
		self.assertEqual(first["name"], second["name"])
		self.assertTrue(second["duplicate"])


if __name__ == "__main__":
	unittest.main()
