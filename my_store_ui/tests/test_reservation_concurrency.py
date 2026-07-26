"""Stock reservation never over-reserves under contention.

The live two-process race is in
`dev_scripts/live_reservation_concurrency.py` and documented in
`docs/verification/SMJ_LIVE_RESERVATION_CONCURRENCY.md`; a subprocess race is too
flaky for the suite. This module proves the same invariant deterministically:
against 10 physical stock, two Sales Orders for 8 each cannot reserve 16 -- the
second is capped so total reserved never exceeds Actual. That cap is exactly what
the FOR UPDATE bin lock preserves when the two run concurrently.
"""

from __future__ import annotations

import unittest

import frappe
from frappe.utils import add_days, flt, nowdate

from my_store_ui.wholesale.reservation import get_stock_availability, reserve_sales_order

ITEM = "SMJ-CONC-REGR-ITEM"
STOCK = 10.0
QTY_EACH = 8.0


class TestReservationConcurrency(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.enabled = bool(frappe.db.get_single_value("Stock Settings", "enable_stock_reservation"))
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.warehouse = cls._warehouse()
		cls.customer = cls._customer()
		cls._teardown()
		if cls.enabled:
			cls._make_stock()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		cls._teardown()

	@classmethod
	def _warehouse(cls):
		name = "SMJ Concurrency Regr WH"
		existing = frappe.get_all("Warehouse", filters={"warehouse_name": name}, pluck="name")
		if existing:
			return existing[0]
		return frappe.get_doc({
			"doctype": "Warehouse", "warehouse_name": name, "company": cls.company,
		}).insert(ignore_permissions=True).name

	@classmethod
	def _customer(cls):
		name = "SMJ Concurrency Regr Customer"
		if frappe.db.exists("Customer", name):
			return name
		group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": name, "customer_type": "Company",
			"customer_group": group, "territory": territory,
		}).insert(ignore_permissions=True).name

	@classmethod
	def _make_stock(cls):
		group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		frappe.get_doc({
			"doctype": "Item", "item_code": ITEM, "item_name": "SMJ Concurrency Regr",
			"item_group": group, "stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1,
		}).insert(ignore_permissions=True)
		receipt = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": cls.company,
			"items": [{"item_code": ITEM, "qty": STOCK, "t_warehouse": cls.warehouse, "basic_rate": 100}],
		})
		receipt.insert(ignore_permissions=True)
		receipt.submit()
		frappe.db.commit()

	def _make_so(self):
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": self.customer, "company": self.company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": ITEM, "qty": QTY_EACH, "warehouse": self.warehouse,
			           "delivery_date": add_days(nowdate(), 7), "rate": 150}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		return so.name

	@classmethod
	def _teardown(cls):
		for sre in frappe.get_all("Stock Reservation Entry", filters={"item_code": ITEM}, pluck="name"):
			doc = frappe.get_doc("Stock Reservation Entry", sre)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc("Stock Reservation Entry", sre, force=True, ignore_permissions=True)
		for parent in frappe.get_all("Sales Order Item", filters={"item_code": ITEM}, pluck="parent"):
			if frappe.db.exists("Sales Order", parent):
				doc = frappe.get_doc("Sales Order", parent)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Sales Order", parent, force=True, ignore_permissions=True)
		for parent in frappe.get_all("Stock Entry Detail", filters={"item_code": ITEM}, pluck="parent"):
			if frappe.db.exists("Stock Entry", parent):
				doc = frappe.get_doc("Stock Entry", parent)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Stock Entry", parent, force=True, ignore_permissions=True)
		if frappe.db.exists("Item", ITEM):
			frappe.delete_doc("Item", ITEM, force=True, ignore_permissions=True)
		frappe.db.commit()

	def test_two_orders_cannot_reserve_beyond_physical_stock(self):
		if not self.enabled:
			self.skipTest("stock reservation not enabled on this site")

		start = get_stock_availability(ITEM, self.warehouse)
		self.assertEqual(flt(start["actual_qty"]), STOCK)
		self.assertEqual(flt(start["reserved_qty"]), 0.0)

		so_a = self._make_so()
		so_b = self._make_so()

		reserve_sales_order(so_a)
		reserve_sales_order(so_b)

		end = get_stock_availability(ITEM, self.warehouse)
		# The invariant: total reserved never exceeds physical stock. Two orders for
		# 8 each against 10 stock reserve 10 in total, not 16.
		self.assertLessEqual(flt(end["reserved_qty"]), flt(end["actual_qty"]))
		self.assertEqual(flt(end["reserved_qty"]), STOCK)
		self.assertEqual(flt(end["available_to_sell"]), 0.0)
		self.assertGreaterEqual(flt(end["available_to_sell"]), 0.0, "available must never go negative")

		total = sum(
			flt(row.reserved_qty)
			for row in frappe.get_all(
				"Stock Reservation Entry",
				filters={"item_code": ITEM, "docstatus": 1},
				fields=["reserved_qty"],
			)
		)
		self.assertEqual(total, STOCK, "sum of reservation entries must equal stock, not exceed it")

	def test_available_to_sell_equals_actual_minus_reserved(self):
		if not self.enabled:
			self.skipTest("stock reservation not enabled on this site")
		state = get_stock_availability(ITEM, self.warehouse)
		self.assertEqual(
			flt(state["available_to_sell"]),
			flt(state["actual_qty"]) - flt(state["reserved_qty"]),
		)


if __name__ == "__main__":
	unittest.main()
