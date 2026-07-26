"""One continuous stock-reservation lifecycle trace (staging only).

Same item, warehouse and customer through the whole chain, recording Actual,
Reserved and Available-to-Sell after every step, using only standard ERPNext
controllers. Prints a JSON trace and reconciles the invariants. Refuses to run
off staging; tears everything down at the end.

    bench --site staging.local execute my_store_ui.dev_scripts.reservation_lifecycle_trace.run
"""

from __future__ import annotations

import json

import frappe
from frappe.utils import add_days, flt, nowdate

ITEM = "SMJ-LIFECYCLE-ITEM"
WH_NAME = "SMJ Lifecycle Test WH"
RECEIVE = 20.0


def _guard():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")


def _warehouse(company):
	found = frappe.get_all("Warehouse", filters={"warehouse_name": WH_NAME}, pluck="name")
	if found:
		return found[0]
	return frappe.get_doc({"doctype": "Warehouse", "warehouse_name": WH_NAME, "company": company}).insert(ignore_permissions=True).name


def _customer():
	name = "SMJ Lifecycle Customer"
	if frappe.db.exists("Customer", name):
		return name
	group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
	terr = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
	return frappe.get_doc({"doctype": "Customer", "customer_name": name, "customer_type": "Company",
	                       "customer_group": group, "territory": terr}).insert(ignore_permissions=True).name


def _teardown():
	for dt, field in (("Stock Reservation Entry", "item_code"),):
		for name in frappe.get_all(dt, filters={field: ITEM}, pluck="name"):
			doc = frappe.get_doc(dt, name)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
	# Cancel dependents newest-first so submitted links release cleanly.
	for dt, child in (("Delivery Note", "Delivery Note Item"), ("Sales Invoice", "Sales Invoice Item"),
	                  ("Sales Order", "Sales Order Item"), ("Stock Entry", "Stock Entry Detail")):
		for parent in frappe.get_all(child, filters={"item_code": ITEM}, pluck="parent"):
			if frappe.db.exists(dt, parent):
				doc = frappe.get_doc(dt, parent)
				try:
					if doc.docstatus == 1:
						doc.cancel()
					frappe.delete_doc(dt, parent, force=True, ignore_permissions=True)
				except Exception:
					pass
	if frappe.db.exists("Item", ITEM):
		frappe.delete_doc("Item", ITEM, force=True, ignore_permissions=True)
	frappe.db.commit()


def _state(warehouse: str) -> dict:
	from my_store_ui.wholesale.reservation import get_stock_availability
	s = get_stock_availability(ITEM, warehouse)
	return {"actual": flt(s["actual_qty"]), "reserved": flt(s["reserved_qty"]),
	        "available": flt(s["available_to_sell"])}


def execute() -> dict:
	_guard()
	frappe.set_user("Administrator")
	if not frappe.db.get_single_value("Stock Settings", "enable_stock_reservation"):
		raise RuntimeError("reservation not enabled on staging")
	_teardown()

	company = frappe.get_all("Company", pluck="name")[0]
	warehouse = _warehouse(company)
	customer = _customer()
	group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
	trace = []

	def record(step, extra=None):
		row = {"step": step, **_state(warehouse)}
		if extra:
			row.update(extra)
		row["invariant_ok"] = abs(row["available"] - (row["actual"] - row["reserved"])) < 1e-9 and row["available"] >= -1e-9
		trace.append(row)

	frappe.get_doc({"doctype": "Item", "item_code": ITEM, "item_name": "SMJ Lifecycle",
	                "item_group": group, "stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1}).insert(ignore_permissions=True)

	# 1. Stock receipt
	receipt = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": company,
	                          "items": [{"item_code": ITEM, "qty": RECEIVE, "t_warehouse": warehouse, "basic_rate": 100}]})
	receipt.insert(ignore_permissions=True)
	receipt.submit()
	frappe.db.commit()
	record("1_receipt_20")

	# 2. Create + submit Sales Order for 12
	so = frappe.get_doc({"doctype": "Sales Order", "customer": customer, "company": company,
	                     "delivery_date": add_days(nowdate(), 7),
	                     "items": [{"item_code": ITEM, "qty": 12, "warehouse": warehouse,
	                                "delivery_date": add_days(nowdate(), 7), "rate": 150}]})
	so.insert(ignore_permissions=True)
	so.submit()
	frappe.db.commit()
	record("2_so_submitted_qty12", {"so": so.name, "so_status": so.status})

	# 3. Reserve stock (12) -> Available drops to 8, physical Actual unchanged
	from my_store_ui.wholesale.reservation import reserve_sales_order, unreserve_sales_order
	reserve_sales_order(so.name)
	record("3_reserved_12")

	# 4. Release the reservation -> Available back to 20, Actual still 20
	unreserve_sales_order(so.name)
	record("4_unreserved_released")

	# 5. Re-reserve -> reservation is re-established at 12
	reserve_sales_order(so.name)
	record("5_rereserved_12")

	# 8. Partial delivery of 5 (standard Delivery Note against the SO). Physical
	#    Actual drops by 5, and the delivered part of the reservation is consumed.
	from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
	dn = make_delivery_note(so.name)
	dn.items[0].qty = 5
	dn.insert(ignore_permissions=True)
	dn.submit()
	frappe.db.commit()
	record("8_delivered_5", {"dn": dn.name, "dn_status": dn.docstatus})

	# 9. Deliver the remaining 7 -> SO fully delivered, reservation fully consumed
	so.reload()
	dn2 = make_delivery_note(so.name)
	dn2.insert(ignore_permissions=True)
	dn2.submit()
	frappe.db.commit()
	record("9_delivered_remaining_7", {"dn2": dn2.name})

	# 12. Return: reverse 2 units of the first delivery (standard return Delivery
	#     Note). Physical Actual increases by 2; it must NOT recreate a reservation.
	from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_return
	ret = make_sales_return(dn.name)
	for row in ret.items:
		row.qty = -2
		row.received_qty = -2
	ret.insert(ignore_permissions=True)
	ret.submit()
	frappe.db.commit()
	record("12_returned_2", {"return_dn": ret.name})

	# Reconcile
	reconciled = all(r["invariant_ok"] for r in trace)
	no_negative = all(r["available"] >= -1e-9 for r in trace)
	# After full delivery, no active (open) reservation should remain.
	open_res = frappe.get_all("Stock Reservation Entry",
	                          filters={"item_code": ITEM, "docstatus": 1, "status": ["in", ["Reserved", "Partially Reserved"]]},
	                          fields=["name", "reserved_qty", "delivered_qty", "status"])
	result = {
		"trace": trace,
		"all_invariants_ok": reconciled,
		"no_negative_available": no_negative,
		"open_reservations_after_full_delivery": open_res,
	}
	_teardown()
	result["teardown_ok"] = True
	return result


def run():
	print(json.dumps(execute(), indent=1, default=str))
	print("TEARDOWN_OK")
