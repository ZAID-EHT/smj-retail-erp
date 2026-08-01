"""Landed Cost Voucher raises item valuation through standard ERPNext.

Freight/customs charges are distributed by the standard voucher; valuation rates
are never written directly. Savepoint + rollback, no residue.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.landed_cost import create_landed_cost_voucher, get_landed_costs
from my_store_ui.wholesale.purchasing import create_purchase_order, create_purchase_receipt

COST = 1000.0
QTY = 10


class TestLandedCost(unittest.TestCase):
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
		self.sp = f"lcv_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"LCV {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": COST, "wholesale_price": 1200,
			"retail_price": 1500,
		})["name"]
		self.supplier = frappe.get_doc({
			"doctype": "Supplier", "supplier_name": f"LCVSup {uuid.uuid4().hex[:6]}",
			"supplier_group": self.supplier_group,
		}).insert(ignore_permissions=True).name
		order = create_purchase_order(
			supplier=self.supplier, company=self.company, warehouse=self.wh,
			items=[{"item_code": self.item, "qty": QTY, "rate": COST}], submit=1,
			request_id=uuid.uuid4().hex,
		)
		self.receipt = create_purchase_receipt(order["name"], submit=1)["name"]

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _stock_value(self):
		row = frappe.db.sql(
			"""SELECT stock_value FROM `tabStock Ledger Entry`
			   WHERE item_code=%s AND warehouse=%s AND is_cancelled=0
			   ORDER BY posting_date DESC, posting_time DESC, creation DESC LIMIT 1""",
			(self.item, self.wh),
		)
		return flt(row[0][0]) if row else 0.0

	def test_landed_cost_raises_stock_value(self):
		before = self._stock_value()
		create_landed_cost_voucher(
			purchase_receipts=[self.receipt],
			charges=[{"description": "Freight", "amount": 2000}],
			company=self.company, submit=1, request_id=uuid.uuid4().hex,
		)
		self.assertAlmostEqual(self._stock_value() - before, 2000.0, places=1)

	def test_multiple_charges_are_all_applied(self):
		before = self._stock_value()
		res = create_landed_cost_voucher(
			purchase_receipts=[self.receipt],
			charges=[{"description": "Freight", "amount": 1500},
			         {"description": "Customs Duty", "amount": 2500}],
			company=self.company, submit=1, request_id=uuid.uuid4().hex,
		)
		self.assertEqual(flt(res["total_taxes_and_charges"]), 4000.0)
		self.assertAlmostEqual(self._stock_value() - before, 4000.0, places=1)

	def test_voucher_is_linked_to_the_receipt(self):
		create_landed_cost_voucher(
			purchase_receipts=[self.receipt],
			charges=[{"description": "Clearing Charges", "amount": 800}],
			company=self.company, submit=1, request_id=uuid.uuid4().hex,
		)
		applied = get_landed_costs(self.receipt)
		self.assertEqual(len(applied["vouchers"]), 1)
		self.assertEqual(flt(applied["total_applied"]), 800.0)

	def test_charge_must_be_positive(self):
		with self.assertRaises(frappe.ValidationError):
			create_landed_cost_voucher(
				purchase_receipts=[self.receipt],
				charges=[{"description": "Freight", "amount": 0}],
				company=self.company, request_id=uuid.uuid4().hex,
			)

	def test_charge_needs_a_description(self):
		with self.assertRaises(frappe.ValidationError):
			create_landed_cost_voucher(
				purchase_receipts=[self.receipt],
				charges=[{"description": "  ", "amount": 500}],
				company=self.company, request_id=uuid.uuid4().hex,
			)

	def test_no_charges_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			create_landed_cost_voucher(
				purchase_receipts=[self.receipt], charges=[], company=self.company,
				request_id=uuid.uuid4().hex,
			)

	def test_unsubmitted_receipt_is_refused(self):
		order = create_purchase_order(
			supplier=self.supplier, company=self.company, warehouse=self.wh,
			items=[{"item_code": self.item, "qty": 5, "rate": COST}], submit=1,
			request_id=uuid.uuid4().hex,
		)
		draft = create_purchase_receipt(order["name"], submit=0)["name"]
		with self.assertRaises(frappe.ValidationError):
			create_landed_cost_voucher(
				purchase_receipts=[draft],
				charges=[{"description": "Freight", "amount": 100}],
				company=self.company, request_id=uuid.uuid4().hex,
			)

	def test_invalid_distribution_method_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			create_landed_cost_voucher(
				purchase_receipts=[self.receipt],
				charges=[{"description": "Freight", "amount": 100}],
				company=self.company, distribute_on="Vibes", request_id=uuid.uuid4().hex,
			)


if __name__ == "__main__":
	unittest.main()
