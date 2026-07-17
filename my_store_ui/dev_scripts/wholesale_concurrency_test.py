"""
Real two-session concurrent stock reservation test, per
docs/full-parity/VERIFICATION_MATRIX.md's own acceptance criterion:
"two sessions, 10 available, two 8-unit reservations -> never 16".

Run as two separate OS processes (real concurrency, not simulated) each
calling reserve_one() against the SAME item/warehouse with only 10 units
available. Setup creates the item + two Sales Orders (8 units each) first;
reserve_one(sales_order_name) is what each process calls independently.
"""
import sys
import time

import frappe

COMPANY = "SMJ Retail ERP"
ITEM_CODE = "CONC-TEST-001"
WAREHOUSE = None  # resolved in setup()


def setup():
    global WAREHOUSE
    WAREHOUSE = frappe.db.get_value("Warehouse", {"company": COMPANY, "warehouse_name": "Main Warehouse"}, "name")
    cc = frappe.db.get_value("Company", COMPANY, "cost_center")

    if not frappe.db.exists("Item", ITEM_CODE):
        frappe.get_doc({
            "doctype": "Item", "item_code": ITEM_CODE, "item_name": "Concurrency Test Rug",
            "item_group": "Rugs", "stock_uom": "Nos", "is_stock_item": 1,
        }).insert(ignore_permissions=True)

    # Reset to exactly 10 units on hand via Stock Reconciliation (idempotent,
    # safe to re-run -- this is a dedicated test item, not real demo data).
    existing_qty = frappe.db.get_value("Bin", {"item_code": ITEM_CODE, "warehouse": WAREHOUSE}, "actual_qty") or 0
    if existing_qty != 10:
        sr = frappe.get_doc({
            "doctype": "Stock Reconciliation", "company": COMPANY,
            "posting_date": frappe.utils.nowdate(), "set_posting_time": 1,
            "purpose": "Stock Reconciliation",
            "items": [{"item_code": ITEM_CODE, "warehouse": WAREHOUSE, "qty": 10, "valuation_rate": 1000}],
        })
        sr.insert(ignore_permissions=True)
        sr.submit()
        frappe.db.commit()

    so_names = []
    for i in range(2):
        so = frappe.get_doc({
            "doctype": "Sales Order", "customer": "ABC Traders", "company": COMPANY,
            "transaction_date": frappe.utils.nowdate(), "delivery_date": frappe.utils.nowdate(),
            "cost_center": cc,
            "items": [{"item_code": ITEM_CODE, "qty": 8, "rate": 1500, "warehouse": WAREHOUSE,
                       "delivery_date": frappe.utils.nowdate()}],
        })
        so.insert(ignore_permissions=True)
        so.submit()
        so_names.append(so.name)
    frappe.db.commit()

    print(f"SETUP_OK warehouse={WAREHOUSE} so1={so_names[0]} so2={so_names[1]}")
    return so_names


def reserve_one(so_name, delay=0.0):
    global WAREHOUSE
    if WAREHOUSE is None:
        WAREHOUSE = frappe.db.get_value("Warehouse", {"company": COMPANY, "warehouse_name": "Main Warehouse"}, "name")
    so = frappe.get_doc("Sales Order", so_name)
    if delay:
        time.sleep(delay)
    try:
        items_details = [
            {"sales_order_item": row.name, "warehouse": row.warehouse, "qty_to_reserve": row.qty}
            for row in so.items
        ]
        so.create_stock_reservation_entries(items_details=items_details, notify=False)
        frappe.db.commit()
        reserved = frappe.db.get_value(
            "Stock Reservation Entry", {"voucher_no": so_name, "docstatus": 1}, "reserved_qty"
        ) or 0
        print(f"RESERVE_RESULT so={so_name} reserved_qty={reserved}")
    except Exception as e:
        frappe.db.rollback()
        print(f"RESERVE_RESULT so={so_name} reserved_qty=0 error={type(e).__name__}: {e}")


def check_final_state():
    global WAREHOUSE
    if WAREHOUSE is None:
        WAREHOUSE = frappe.db.get_value("Warehouse", {"company": COMPANY, "warehouse_name": "Main Warehouse"}, "name")
    total_reserved = frappe.db.sql("""
        select coalesce(sum(reserved_qty), 0) from `tabStock Reservation Entry`
        where item_code=%s and warehouse=%s and docstatus=1
    """, (ITEM_CODE, WAREHOUSE))[0][0]
    actual_qty = frappe.db.get_value("Bin", {"item_code": ITEM_CODE, "warehouse": WAREHOUSE}, "actual_qty")
    print(f"FINAL_STATE total_reserved={total_reserved} actual_qty={actual_qty} "
          f"over_reserved={total_reserved > 10}")


def cleanup():
    """Release reservations and remove test Sales Orders so this is re-runnable and
    doesn't pollute the real demo dataset's document counts."""
    sres = frappe.get_all("Stock Reservation Entry", filters={"item_code": ITEM_CODE}, pluck="name")
    for name in sres:
        doc = frappe.get_doc("Stock Reservation Entry", name)
        if doc.docstatus == 1:
            doc.cancel()
    sos = frappe.get_all("Sales Order", filters={"items.item_code": ITEM_CODE}, pluck="name", distinct=True)
    for name in sos:
        so = frappe.get_doc("Sales Order", name)
        if so.docstatus == 1:
            so.cancel()
        frappe.delete_doc("Sales Order", name, ignore_permissions=True, force=True)
    frappe.db.commit()
    print(f"CLEANUP_OK cancelled_sres={len(sres)} removed_sos={len(sos)}")
