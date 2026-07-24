"""Controlled FIFO valuation verification (staging-only).

Creates a fresh FIFO-valued test item, receives two layers at different rates via
standard Material Receipt Stock Entries, issues across both layers via a Material
Issue, then reads the resulting Stock Ledger Entries. No Bin / SLE / GL is written
directly — everything goes through standard ERPNext stock controllers.

FIFO expectation:
  Receipt 1: 10 @ 1,000
  Receipt 2: 10 @ 1,200
  Issue    : 12  -> 10 @ 1,000 + 2 @ 1,200 = 12,400 outgoing value
  Remaining: 8 @ 1,200 = 9,600

Run:
  bench --site staging.local execute my_store_ui.dev_scripts.fifo_verification.run
"""
from __future__ import annotations

import frappe
from frappe.utils import flt

COMPANY = "SMJ Retail ERP"
WAREHOUSE = "Main Warehouse - SMJ"
ITEM = "SMJ-FIFO-TEST-ITEM"


def _receipt(qty: float, rate: float) -> str:
	se = frappe.get_doc({
		"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": COMPANY,
		"items": [{"item_code": ITEM, "qty": qty, "t_warehouse": WAREHOUSE, "basic_rate": rate, "uom": "Nos"}],
	})
	se.insert(ignore_permissions=True)
	se.submit()
	return se.name


def _issue(qty: float) -> str:
	se = frappe.get_doc({
		"doctype": "Stock Entry", "stock_entry_type": "Material Issue", "company": COMPANY,
		"items": [{"item_code": ITEM, "qty": qty, "s_warehouse": WAREHOUSE, "uom": "Nos"}],
	})
	se.insert(ignore_permissions=True)
	se.submit()
	return se.name


def _cleanup(vouchers: list[str]) -> None:
	for name in reversed(vouchers):
		if name and frappe.db.exists("Stock Entry", name):
			doc = frappe.get_doc("Stock Entry", name)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc("Stock Entry", name, force=True, ignore_permissions=True)
	if frappe.db.exists("Item", ITEM):
		frappe.delete_doc("Item", ITEM, force=True, ignore_permissions=True)
	frappe.db.commit()


def run():
	frappe.set_user("Administrator")
	vouchers: list[str] = []
	try:
		if frappe.db.exists("Item", ITEM):
			_cleanup([])
		frappe.get_doc({
			"doctype": "Item", "item_code": ITEM, "item_name": "SMJ FIFO Test Item",
			"item_group": frappe.db.get_value("Item Group", {"is_group": 0}, "name"),
			"stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1, "valuation_method": "FIFO",
		}).insert(ignore_permissions=True)

		r1 = _receipt(10, 1000); vouchers.append(r1)
		r2 = _receipt(10, 1200); vouchers.append(r2)
		issue = _issue(12); vouchers.append(issue)

		# Outgoing valuation of the issue (standard SLE, FIFO consumption).
		issue_sle = frappe.get_all(
			"Stock Ledger Entry",
			filters={"voucher_no": issue, "item_code": ITEM, "is_cancelled": 0},
			fields=["actual_qty", "stock_value_difference", "qty_after_transaction", "stock_value"],
		)
		outgoing_value = -sum(flt(r.stock_value_difference) for r in issue_sle)
		remaining_qty = flt(issue_sle[-1].qty_after_transaction) if issue_sle else None
		remaining_value = flt(issue_sle[-1].stock_value) if issue_sle else None

		result = {
			"item": ITEM, "valuation_method": "FIFO", "warehouse": WAREHOUSE,
			"receipt_1": {"voucher": r1, "qty": 10, "rate": 1000},
			"receipt_2": {"voucher": r2, "qty": 10, "rate": 1200},
			"issue": {"voucher": issue, "qty": 12},
			"expected_outgoing_value": 12400.0,
			"actual_outgoing_value": outgoing_value,
			"outgoing_matches": abs(outgoing_value - 12400.0) < 0.01,
			"expected_remaining_qty": 8.0,
			"actual_remaining_qty": remaining_qty,
			"expected_remaining_value": 9600.0,
			"actual_remaining_value": remaining_value,
			"remaining_value_matches": remaining_value is not None and abs(remaining_value - 9600.0) < 0.01,
		}
		return result
	finally:
		_cleanup(vouchers)
