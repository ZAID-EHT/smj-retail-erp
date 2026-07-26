"""Live two-process stock-reservation concurrency verification (staging only).

Two genuinely independent `bench execute` processes race to reserve the same
stock. This is real cross-process/cross-connection concurrency, not two threads
and not one transaction. The FOR UPDATE bin lock in
`wholesale.reservation.reserve_sales_order` must serialise them so the total
reserved never exceeds physical stock.

Scenario: one item, 10 in a fresh warehouse; two submitted Sales Orders each for
8; both reserved at once. Exactly one fully reserves 8; the other cannot take
another 8. Total active reservation stays <= 10.

Refuses to run on any site other than staging.local. All fixtures are removed by
`teardown`.

    # setup returns the two SO names on stdout as SO_A=... SO_B=...
    bench --site staging.local execute my_store_ui.dev_scripts.live_reservation_concurrency.setup
    # a worker reserves one SO and writes its result JSON to the given path
    bench --site staging.local execute my_store_ui.dev_scripts.live_reservation_concurrency.worker --kwargs '{"sales_order":"SO-xxxx","out":"/path/a.json"}'
    bench --site staging.local execute my_store_ui.dev_scripts.live_reservation_concurrency.teardown
"""

from __future__ import annotations

import json
import time

import frappe
from frappe.utils import flt, nowdate, add_days

ITEM = "SMJ-CONC-TEST-ITEM"
QTY_EACH = 8.0
STOCK = 10.0
MARKER = "smj-conc-test"


def _guard_site() -> None:
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")


def _warehouse() -> str:
	# A dedicated, fresh warehouse so no pre-existing stock or reservation interferes.
	name = "SMJ Concurrency Test WH"
	existing = frappe.get_all("Warehouse", filters={"warehouse_name": name}, pluck="name")
	if existing:
		return existing[0]
	company = frappe.get_all("Company", pluck="name")[0]
	doc = frappe.get_doc({
		"doctype": "Warehouse", "warehouse_name": name, "company": company,
	}).insert(ignore_permissions=True)
	return doc.name


def _customer() -> str:
	name = "SMJ Concurrency Test Customer"
	if frappe.db.exists("Customer", name):
		return name
	group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
	territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
	frappe.get_doc({
		"doctype": "Customer", "customer_name": name, "customer_type": "Company",
		"customer_group": group, "territory": territory,
	}).insert(ignore_permissions=True)
	return name


def setup() -> None:
	"""Create the item, receive exactly 10, and submit two SOs for 8 each."""
	_guard_site()
	frappe.set_user("Administrator")
	if not frappe.db.get_single_value("Stock Settings", "enable_stock_reservation"):
		raise RuntimeError("stock reservation is not enabled on staging")
	teardown()

	company = frappe.get_all("Company", pluck="name")[0]
	warehouse = _warehouse()
	customer = _customer()
	group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]

	frappe.get_doc({
		"doctype": "Item", "item_code": ITEM, "item_name": "SMJ Concurrency Test",
		"item_group": group, "stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1,
		"description": MARKER,
	}).insert(ignore_permissions=True)

	# Receive exactly 10 via a standard Stock Entry (Material Receipt).
	receipt = frappe.get_doc({
		"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": company,
		"items": [{"item_code": ITEM, "qty": STOCK, "t_warehouse": warehouse, "basic_rate": 100}],
	})
	receipt.insert(ignore_permissions=True)
	receipt.submit()

	so_names = []
	for _ in range(2):
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": ITEM, "qty": QTY_EACH, "warehouse": warehouse,
			           "delivery_date": add_days(nowdate(), 7), "rate": 150}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		so_names.append(so.name)

	frappe.db.commit()
	bin_row = frappe.db.get_value(
		"Bin", {"item_code": ITEM, "warehouse": warehouse},
		["actual_qty", "reserved_stock"], as_dict=True,
	)
	print(f"SO_A={so_names[0]}")
	print(f"SO_B={so_names[1]}")
	print(f"WAREHOUSE={warehouse}")
	print(f"START_ACTUAL={flt(bin_row.actual_qty)}")
	print(f"START_RESERVED={flt(bin_row.reserved_stock)}")


def worker(sales_order: str, out: str, barrier_until: float | None = None) -> None:
	"""Reserve one SO and write a structured result. Runs as its own process."""
	_guard_site()
	frappe.set_user("Administrator")
	from my_store_ui.wholesale.reservation import reserve_sales_order

	# Optional wall-clock barrier so both processes hit the lock at nearly the same
	# instant, maximising the real contention window.
	if barrier_until:
		while time.time() < float(barrier_until):
			time.sleep(0.001)

	result = {"sales_order": sales_order, "pid": frappe.utils.cint(__import__("os").getpid())}
	t0 = time.time()
	try:
		res = reserve_sales_order(sales_order)
		result.update({"outcome": "reserved", "attempts": res.get("attempts"),
		               "reservations": res.get("reservations")})
	except frappe.ValidationError as exc:
		frappe.db.rollback()
		result.update({"outcome": "rejected", "error_type": "ValidationError", "message": str(exc)})
	except Exception as exc:  # noqa: BLE001 - record any raw failure for the report
		frappe.db.rollback()
		result.update({"outcome": "error", "error_type": type(exc).__name__, "message": str(exc)[:400]})
	result["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
	with open(out, "w") as handle:
		json.dump(result, handle)
	print(json.dumps(result))


def report() -> None:
	"""Print the ending Actual/Reserved/Available for the test item."""
	_guard_site()
	frappe.set_user("Administrator")
	warehouse = _warehouse()
	bin_row = frappe.db.get_value(
		"Bin", {"item_code": ITEM, "warehouse": warehouse},
		["actual_qty", "reserved_stock"], as_dict=True,
	) or frappe._dict()
	actual = flt(bin_row.get("actual_qty"))
	reserved = flt(bin_row.get("reserved_stock"))
	sres = frappe.get_all(
		"Stock Reservation Entry",
		filters={"item_code": ITEM, "docstatus": 1},
		fields=["name", "voucher_no", "reserved_qty", "status"],
	)
	print(json.dumps({
		"end_actual": actual, "end_reserved": reserved, "end_available": actual - reserved,
		"over_reserved": reserved > actual,
		"active_reservations": sres,
	}))


def teardown() -> None:
	"""Remove every fixture created by this harness."""
	_guard_site()
	frappe.set_user("Administrator")
	for sre in frappe.get_all("Stock Reservation Entry", filters={"item_code": ITEM}, pluck="name"):
		doc = frappe.get_doc("Stock Reservation Entry", sre)
		if doc.docstatus == 1:
			doc.cancel()
		frappe.delete_doc("Stock Reservation Entry", sre, force=True, ignore_permissions=True)
	for so in frappe.get_all("Sales Order", filters={"item_code": ITEM}, pluck="name") if False else \
			frappe.get_all("Sales Order Item", filters={"item_code": ITEM}, pluck="parent"):
		if frappe.db.exists("Sales Order", so):
			doc = frappe.get_doc("Sales Order", so)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc("Sales Order", so, force=True, ignore_permissions=True)
	for se in frappe.get_all("Stock Entry Detail", filters={"item_code": ITEM}, pluck="parent"):
		if frappe.db.exists("Stock Entry", se):
			doc = frappe.get_doc("Stock Entry", se)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc("Stock Entry", se, force=True, ignore_permissions=True)
	if frappe.db.exists("Item", ITEM):
		frappe.delete_doc("Item", ITEM, force=True, ignore_permissions=True)
	frappe.db.commit()
	print("teardown complete")
