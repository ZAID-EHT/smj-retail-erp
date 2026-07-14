"""Integration tests for the wholesale core: reservation, transaction id and the
register. These require a site with `enable_stock_reservation` on and the
my_store_ui custom fields applied (the approved staging/test site), plus
`allow_tests`. They follow standard ERPNext test helpers and never write ledgers
directly.

Run on staging:
    bench --site <staging> run-tests --app my_store_ui \
        --module my_store_ui.tests.test_wholesale_integration
"""
import unittest

import frappe
from frappe.utils import flt

from my_store_ui.wholesale import register, reservation, transaction_id


def _reservation_ready() -> bool:
    return bool(frappe.db.get_single_value("Stock Settings", "enable_stock_reservation")) and bool(
        frappe.get_meta("Sales Order").get_field("custom_wholesale_transaction_id")
    )


@unittest.skipUnless(_reservation_ready(), "needs staging: reservation on + custom fields applied")
class TestWholesaleIntegration(unittest.TestCase):
    """These tests assume ERPNext demo/test masters exist. They create their own
    Sales Orders against an item/warehouse with known available-to-sell."""

    def _make_so(self, customer, item_code, warehouse, qty, rate=100):
        so = frappe.get_doc({
            "doctype": "Sales Order", "customer": customer, "company": frappe.defaults.get_user_default("Company"),
            "transaction_date": frappe.utils.nowdate(), "delivery_date": frappe.utils.nowdate(),
            "items": [{"item_code": item_code, "qty": qty, "rate": rate, "warehouse": warehouse}],
        })
        so.insert()
        so.submit()
        return so

    def test_transaction_id_assigned_on_sales_order(self):
        cust = frappe.get_all("Customer", limit=1, pluck="name")[0]
        item = frappe.get_all("Item", filters={"is_stock_item": 1}, limit=1, pluck="name")[0]
        wh = frappe.get_all("Warehouse", filters={"is_group": 0}, limit=1, pluck="name")[0]
        so = self._make_so(cust, item, wh, 1)
        self.assertTrue(so.get("custom_wholesale_transaction_id"))
        self.assertTrue(so.get("custom_wholesale_transaction_id").startswith("TRX-"))
        frappe.db.rollback()

    def test_reserve_does_not_reduce_actual_but_reduces_available(self):
        item = frappe.get_all("Item", filters={"is_stock_item": 1}, limit=1, pluck="name")[0]
        wh = frappe.get_all("Warehouse", filters={"is_group": 0}, limit=1, pluck="name")[0]
        cust = frappe.get_all("Customer", limit=1, pluck="name")[0]
        before = reservation.get_stock_availability(item, wh)
        if before["available_to_sell"] < 2:
            self.skipTest("insufficient available stock for reservation test")
        so = self._make_so(cust, item, wh, 1)
        reservation.reserve_sales_order(so.name)
        after = reservation.get_stock_availability(item, wh)
        self.assertEqual(flt(after["actual_qty"]), flt(before["actual_qty"]))  # actual unchanged
        self.assertEqual(flt(after["reserved_qty"]), flt(before["reserved_qty"]) + 1)  # reserved +1
        self.assertEqual(flt(after["available_to_sell"]), flt(before["available_to_sell"]) - 1)
        frappe.db.rollback()

    def test_cannot_over_reserve(self):
        """Available 10, reserve 8, then reserve 8 again -> total never 16."""
        item = frappe.get_all("Item", filters={"is_stock_item": 1}, limit=1, pluck="name")[0]
        wh = frappe.get_all("Warehouse", filters={"is_group": 0}, limit=1, pluck="name")[0]
        cust = frappe.get_all("Customer", limit=1, pluck="name")[0]
        avail = reservation.get_stock_availability(item, wh)["available_to_sell"]
        if avail < 10:
            self.skipTest("need >=10 available for over-reservation test")
        so1 = self._make_so(cust, item, wh, 8)
        reservation.reserve_sales_order(so1.name)
        so2 = self._make_so(cust, item, wh, 8)
        with self.assertRaises(frappe.ValidationError):
            reservation.reserve_sales_order(so2.name)
        total_reserved = reservation.get_stock_availability(item, wh)["reserved_qty"]
        self.assertLessEqual(flt(total_reserved), flt(avail))  # never exceeds available
        frappe.db.rollback()

    def test_cancel_releases_reservation(self):
        item = frappe.get_all("Item", filters={"is_stock_item": 1}, limit=1, pluck="name")[0]
        wh = frappe.get_all("Warehouse", filters={"is_group": 0}, limit=1, pluck="name")[0]
        cust = frappe.get_all("Customer", limit=1, pluck="name")[0]
        if reservation.get_stock_availability(item, wh)["available_to_sell"] < 2:
            self.skipTest("insufficient stock")
        before = reservation.get_stock_availability(item, wh)["reserved_qty"]
        so = self._make_so(cust, item, wh, 1)
        reservation.reserve_sales_order(so.name)
        reservation.unreserve_sales_order(so.name)
        after = reservation.get_stock_availability(item, wh)["reserved_qty"]
        self.assertEqual(flt(after), flt(before))
        frappe.db.rollback()

    def test_register_lists_transaction(self):
        cust = frappe.get_all("Customer", limit=1, pluck="name")[0]
        item = frappe.get_all("Item", filters={"is_stock_item": 1}, limit=1, pluck="name")[0]
        wh = frappe.get_all("Warehouse", filters={"is_group": 0}, limit=1, pluck="name")[0]
        so = self._make_so(cust, item, wh, 1)
        result = register.get_wholesale_transactions(filters={"customer": cust})
        names = [r["sales_order"] for r in result["rows"]]
        self.assertIn(so.name, names)
        row = next(r for r in result["rows"] if r["sales_order"] == so.name)
        self.assertTrue(row["transaction_id"].startswith("TRX-"))
        frappe.db.rollback()


if __name__ == "__main__":
    unittest.main()
