"""Batch tracking + FIFO valuation on a quick-entry Product.

Proves standard ERPNext FIFO through real Stock Entries (no direct ledger writes):
receive Batch A (10@1000) + Batch B (10@1200), issue 12 -> outgoing 12,400,
remaining 8 @ 1200 = 9,600. Runs in a savepoint and rolls back.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product

SUFFIX = uuid.uuid4().hex[:6]


class TestBatchFifo(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all("Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name")[0]
		cls.valuation_fifo = frappe.db.get_single_value("Stock Settings", "valuation_method") == "FIFO"

	def _receive(self, item, qty, rate):
		se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
		                     "items": [{"item_code": item, "qty": qty, "t_warehouse": self.wh, "basic_rate": rate}]})
		se.insert(ignore_permissions=True)
		se.submit()
		return se

	def test_new_product_is_batch_managed_and_fifo_valuation(self):
		sp = f"batch_fifo_{SUFFIX}"
		frappe.db.savepoint(sp)
		try:
			res = create_product({"product_name": f"FIFO Test {SUFFIX}", "category": self.group,
			                      "stock_location_1": self.wh, "cost_price": 1000, "wholesale_price": 1200,
			                      "retail_price": 1500, "department_price": 1350})
			item = res["name"]
			it = frappe.get_doc("Item", item)
			# Force FIFO on the item so the test is deterministic regardless of the site default.
			it.valuation_method = "FIFO"
			it.save(ignore_permissions=True)
			self.assertTrue(it.has_batch_no)

			self._receive(item, 10, 1000)   # Batch A
			self._receive(item, 10, 1200)   # Batch B
			frappe.db.commit  # no-op reference; standard controllers already posted SLE

			# Issue 12 via Material Issue -> FIFO consumes 10@1000 + 2@1200.
			issue = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Issue",
			                        "company": self.company,
			                        "items": [{"item_code": item, "qty": 12, "s_warehouse": self.wh}]})
			issue.insert(ignore_permissions=True)
			issue.submit()

			# Outgoing valuation from the standard Stock Ledger.
			outgoing = frappe.db.sql(
				"""SELECT ROUND(ABS(SUM(stock_value_difference)),2) FROM `tabStock Ledger Entry`
				   WHERE item_code=%s AND voucher_no=%s AND is_cancelled=0""",
				(item, issue.name))[0][0]
			self.assertEqual(flt(outgoing), 12400.0)

			# Remaining stock value = 8 @ 1200 = 9,600.
			remaining_qty, remaining_val = frappe.db.sql(
				"""SELECT qty_after_transaction, stock_value FROM `tabStock Ledger Entry`
				   WHERE item_code=%s AND warehouse=%s AND is_cancelled=0
				   ORDER BY posting_date DESC, posting_time DESC, creation DESC LIMIT 1""",
				(item, self.wh))[0]
			self.assertEqual(flt(remaining_qty), 8.0)
			self.assertEqual(flt(remaining_val), 9600.0)

			# Two batches were created.
			batches = frappe.get_all("Batch", filters={"item": item})
			self.assertGreaterEqual(len(batches), 2)
		finally:
			frappe.db.rollback(save_point=sp)


if __name__ == "__main__":
	unittest.main()
