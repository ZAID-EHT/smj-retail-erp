"""Purchasing end to end: PO -> Purchase Receipt -> Purchase Invoice -> payment.

Includes partial receipt, batch creation on receipt, Carton buying and supplier
returns with a debit note. Standard controllers only; savepoint + rollback.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.purchasing import (
	create_purchase_invoice,
	create_purchase_order,
	create_purchase_receipt,
	create_supplier_payment,
	get_purchase_position,
)
from my_store_ui.wholesale.returns import create_debit_note, create_purchase_return
from my_store_ui.wholesale.uom import CARTON_UOM

COST = 1000.0
CARTON_SIZE = 12


class TestPurchaseFlow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name"
		)[0]
		cls.supplier_group = frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"purch_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"Purch {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": COST, "wholesale_price": 1200,
			"retail_price": 1500, "carton_qty": CARTON_SIZE,
		})["name"]
		self.supplier = frappe.get_doc({
			"doctype": "Supplier", "supplier_name": f"PurchSup {uuid.uuid4().hex[:6]}",
			"supplier_group": self.supplier_group,
		}).insert(ignore_permissions=True).name

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _order(self, qty=10, uom=None, submit=True):
		line = {"item_code": self.item, "qty": qty, "rate": COST}
		if uom:
			line["uom"] = uom
		return create_purchase_order(
			supplier=self.supplier, items=[line], company=self.company, warehouse=self.wh,
			submit=1 if submit else 0, request_id=uuid.uuid4().hex,
		)

	def _bin_qty(self):
		return flt(frappe.db.get_value("Bin", {"item_code": self.item, "warehouse": self.wh}, "actual_qty"))

	# --- purchase order ---

	def test_purchase_order_is_created_and_submitted(self):
		res = self._order(10)
		order = frappe.get_doc("Purchase Order", res["name"])
		self.assertEqual(order.docstatus, 1)
		self.assertEqual(flt(order.items[0].qty), 10.0)

	def test_purchase_order_in_cartons_converts_to_stock_units(self):
		res = self._order(3, uom=CARTON_UOM)
		row = frappe.get_doc("Purchase Order", res["name"]).items[0]
		self.assertEqual(row.uom, CARTON_UOM)
		self.assertEqual(flt(row.conversion_factor), float(CARTON_SIZE))
		self.assertEqual(flt(row.stock_qty), 36.0)

	def test_purchase_order_rejects_a_forged_uom(self):
		with self.assertRaises(frappe.ValidationError):
			create_purchase_order(
				supplier=self.supplier, company=self.company, warehouse=self.wh,
				items=[{"item_code": self.item, "qty": 1, "rate": COST, "uom": "Pallet-Forged"}],
				request_id=uuid.uuid4().hex,
			)

	def test_purchase_order_rejects_empty_items(self):
		with self.assertRaises(frappe.ValidationError):
			create_purchase_order(supplier=self.supplier, company=self.company, items=[],
			                      request_id=uuid.uuid4().hex)

	def test_purchase_order_rejects_zero_quantity(self):
		with self.assertRaises(frappe.ValidationError):
			create_purchase_order(
				supplier=self.supplier, company=self.company, warehouse=self.wh,
				items=[{"item_code": self.item, "qty": 0, "rate": COST}],
				request_id=uuid.uuid4().hex,
			)

	# --- receipt ---

	def test_full_receipt_increases_stock_and_creates_a_batch(self):
		res = self._order(10)
		before = self._bin_qty()
		receipt = create_purchase_receipt(res["name"], submit=1)
		self.assertEqual(self._bin_qty() - before, 10.0)
		row = frappe.get_doc("Purchase Receipt", receipt["name"]).items[0]
		self.assertTrue(row.batch_no or row.serial_and_batch_bundle)

	def test_partial_receipt_leaves_the_order_open(self):
		res = self._order(10)
		create_purchase_receipt(res["name"], lines=[{"idx": 1, "qty": 4}], submit=1)
		position = get_purchase_position(res["name"])
		self.assertEqual(flt(position["lines"][0]["received_qty"]), 4.0)
		self.assertEqual(flt(position["lines"][0]["pending_qty"]), 6.0)
		self.assertFalse(position["fully_received"])

	def test_second_receipt_completes_the_order(self):
		res = self._order(10)
		create_purchase_receipt(res["name"], lines=[{"idx": 1, "qty": 4}], submit=1)
		create_purchase_receipt(res["name"], lines=[{"idx": 1, "qty": 6}], submit=1)
		position = get_purchase_position(res["name"])
		self.assertTrue(position["fully_received"])

	def test_over_receipt_is_refused(self):
		res = self._order(10)
		with self.assertRaises(frappe.ValidationError):
			create_purchase_receipt(res["name"], lines=[{"idx": 1, "qty": 15}])

	def test_fully_received_order_cannot_be_received_again(self):
		res = self._order(10)
		create_purchase_receipt(res["name"], submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_purchase_receipt(res["name"])

	def test_draft_order_cannot_be_received(self):
		res = self._order(10, submit=False)
		with self.assertRaises(frappe.ValidationError):
			create_purchase_receipt(res["name"])

	# --- invoice and payment ---

	def test_invoice_from_receipt_and_supplier_payment(self):
		res = self._order(10)
		receipt = create_purchase_receipt(res["name"], submit=1)
		invoice = create_purchase_invoice(purchase_receipt=receipt["name"], submit=1)
		doc = frappe.get_doc("Purchase Invoice", invoice["name"])
		self.assertEqual(doc.docstatus, 1)
		outstanding = flt(doc.outstanding_amount)
		self.assertGreater(outstanding, 0)

		create_supplier_payment(
			supplier=self.supplier, amount=outstanding, company=self.company, submit=1,
			reference_no=uuid.uuid4().hex[:8],
			allocations=[{"reference_doctype": "Purchase Invoice", "reference_name": invoice["name"],
			              "allocated_amount": outstanding}],
			request_id=uuid.uuid4().hex,
		)
		self.assertLessEqual(
			flt(frappe.db.get_value("Purchase Invoice", invoice["name"], "outstanding_amount")), 0.01
		)

	def test_receipt_cannot_be_billed_twice(self):
		res = self._order(10)
		receipt = create_purchase_receipt(res["name"], submit=1)
		create_purchase_invoice(purchase_receipt=receipt["name"], submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_purchase_invoice(purchase_receipt=receipt["name"])

	def test_supplier_payment_to_another_suppliers_invoice_is_refused(self):
		res = self._order(10)
		receipt = create_purchase_receipt(res["name"], submit=1)
		invoice = create_purchase_invoice(purchase_receipt=receipt["name"], submit=1)
		other = frappe.get_doc({
			"doctype": "Supplier", "supplier_name": f"Other {uuid.uuid4().hex[:6]}",
			"supplier_group": self.supplier_group,
		}).insert(ignore_permissions=True).name
		with self.assertRaises(frappe.ValidationError):
			create_supplier_payment(
				supplier=other, amount=100, company=self.company, reference_no=uuid.uuid4().hex[:8],
				allocations=[{"reference_doctype": "Purchase Invoice",
				              "reference_name": invoice["name"], "allocated_amount": 100}],
				request_id=uuid.uuid4().hex,
			)

	# --- supplier returns ---

	def test_purchase_return_reduces_stock(self):
		res = self._order(10)
		receipt = create_purchase_receipt(res["name"], submit=1)
		before = self._bin_qty()
		create_purchase_return(receipt["name"], lines=[{"idx": 1, "qty": 3}], reason="Damaged", submit=1)
		self.assertEqual(before - self._bin_qty(), 3.0)

	def test_purchase_return_above_received_is_refused(self):
		res = self._order(10)
		receipt = create_purchase_receipt(res["name"], submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_purchase_return(receipt["name"], lines=[{"idx": 1, "qty": 12}], reason="Damaged")

	def test_debit_note_reduces_the_payable(self):
		res = self._order(10)
		receipt = create_purchase_receipt(res["name"], submit=1)
		invoice = create_purchase_invoice(purchase_receipt=receipt["name"], submit=1)
		debit = create_debit_note(invoice["name"], submit=1)
		note = frappe.get_doc("Purchase Invoice", debit["name"])
		self.assertTrue(note.is_return)
		self.assertLess(flt(note.grand_total), 0)

	def test_purchase_idempotency_is_database_backed(self):
		rid = uuid.uuid4().hex
		first = create_purchase_order(
			supplier=self.supplier, company=self.company, warehouse=self.wh,
			items=[{"item_code": self.item, "qty": 5, "rate": COST}], request_id=rid,
		)
		frappe.cache.delete_value(f"my_store_ui:idem:Purchase Order:{frappe.session.user}:{rid}")
		second = create_purchase_order(
			supplier=self.supplier, company=self.company, warehouse=self.wh,
			items=[{"item_code": self.item, "qty": 5, "rate": COST}], request_id=rid,
		)
		self.assertEqual(first["name"], second["name"])
		self.assertTrue(second["duplicate"])


if __name__ == "__main__":
	unittest.main()
