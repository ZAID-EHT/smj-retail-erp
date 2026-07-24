"""Stock reservation and Available-to-Sell.

Delegates entirely to standard ERPNext: Sales Order.create_stock_reservation_entries /
cancel_stock_reservation_entries and the Stock Reservation Entry helpers. Vue never
writes Bin or Stock Ledger Entry. Reserving does not reduce Actual Warehouse Stock;
Delivery Note submission does (standard controller behaviour).

Concurrency: before creating reservations we take a row lock on each affected Bin
(SELECT ... FOR UPDATE), so two parallel reservations of the same item/warehouse
serialise and the second sees the updated reserved qty — the 10/8/8 case can never
reserve 16.

Expiry: reservations older than the configurable window (default 3 days) that are
still open are released by a scheduled job. The window is read from site config
(`wholesale_reservation_expiry_days`) so it is configurable without a schema change.
"""
from __future__ import annotations

import time

import frappe
from frappe import _
from frappe.utils import add_days, flt, now_datetime, get_datetime

DEFAULT_EXPIRY_DAYS = 3
RESERVE_MAX_ATTEMPTS = 3
RESERVE_BACKOFF_SECONDS = 0.15


def _is_lock_conflict(exc: Exception) -> bool:
	"""True for a MariaDB deadlock (1213) or lock-wait timeout (1205)."""
	if isinstance(exc, (getattr(frappe, "QueryDeadlockError", ()), getattr(frappe, "QueryTimeoutError", ()))):
		return True
	code = getattr(exc, "args", [None])[0]
	return code in (1213, 1205)


def reservation_expiry_days() -> int:
    return int(frappe.conf.get("wholesale_reservation_expiry_days") or DEFAULT_EXPIRY_DAYS)


def _reservation_enabled() -> bool:
    return bool(frappe.db.get_single_value("Stock Settings", "enable_stock_reservation"))


@frappe.whitelist(methods=["GET"])
def get_stock_availability(item_code: str, warehouse: str, company: str | None = None):
    """Actual / Reserved / Available-to-Sell / Incoming / Projected for an item.

    Read-only; works whether or not reservation is enabled (reserved is 0 when it
    is off). Available to Sell = Actual - Reserved.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
    if not frappe.has_permission("Bin", "read"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    bin_row = frappe.db.get_value(
        "Bin", {"item_code": item_code, "warehouse": warehouse},
        ["actual_qty", "reserved_stock", "projected_qty", "ordered_qty", "indented_qty"],
        as_dict=True,
    ) or frappe._dict()
    actual = flt(bin_row.get("actual_qty"))
    reserved = flt(bin_row.get("reserved_stock"))
    available = actual - reserved
    return {
        "item_code": item_code,
        "warehouse": warehouse,
        "actual_qty": actual,
        "reserved_qty": reserved,
        "available_to_sell": available,
        "incoming_qty": flt(bin_row.get("ordered_qty")) + flt(bin_row.get("indented_qty")),
        "projected_qty": flt(bin_row.get("projected_qty")),
        "reservation_enabled": _reservation_enabled(),
    }


def _lock_bins(items: list[tuple[str, str]]) -> None:
    """Take a row lock on each (item, warehouse) Bin to serialise reservations."""
    for item_code, warehouse in {(i, w) for i, w in items if i and w}:
        # get_or_make_bin ensures the row exists, then lock it FOR UPDATE.
        from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import get_or_make_bin
        bin_name = get_or_make_bin(item_code, warehouse)
        frappe.qb.from_("Bin").select("name").where(frappe.qb.Field("name") == bin_name).for_update().run()


@frappe.whitelist(methods=["POST"])
def reserve_sales_order(sales_order: str):
    """Create stock reservations for a submitted Sales Order (standard engine)."""
    if not _reservation_enabled():
        frappe.throw(_("Stock reservation is not enabled for this site."), frappe.ValidationError)
    doc = frappe.get_doc("Sales Order", sales_order)
    if not frappe.has_permission("Sales Order", "submit", doc=doc):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    if doc.docstatus != 1:
        frappe.throw(_("Only a submitted Sales Order can reserve stock."), frappe.ValidationError)

    # Concurrency: lock the affected bins so parallel reservations serialise, then
    # let the standard engine validate available qty (it never over-reserves). A
    # lock conflict (deadlock / lock-wait timeout) is retried a bounded number of
    # times with a short backoff; a persistent conflict returns a friendly message
    # instead of a raw 500 database traceback.
    bins = [(row.item_code, row.warehouse) for row in doc.items if row.get("warehouse")]
    last_error: Exception | None = None
    for attempt in range(RESERVE_MAX_ATTEMPTS):
        try:
            _lock_bins(bins)
            doc.create_stock_reservation_entries()
            frappe.db.commit()
            return {"sales_order": sales_order, "reserved": True, "attempts": attempt + 1,
                    "reservations": _reservations_for(sales_order)}
        except Exception as exc:  # noqa: BLE001 - classified below; non-lock errors re-raised
            frappe.db.rollback()
            if not _is_lock_conflict(exc):
                raise
            last_error = exc
            doc.reload()
            if attempt < RESERVE_MAX_ATTEMPTS - 1:
                time.sleep(RESERVE_BACKOFF_SECONDS * (attempt + 1))

    frappe.log_error(title="Stock reservation lock conflict", message=str(last_error))
    frappe.throw(
        _("This stock is being reserved by another order right now. Please try again in a moment."),
        frappe.ValidationError,
    )


@frappe.whitelist(methods=["POST"])
def unreserve_sales_order(sales_order: str, item_code: str | None = None):
    """Release reservations for a Sales Order (standard engine)."""
    doc = frappe.get_doc("Sales Order", sales_order)
    if not frappe.has_permission("Sales Order", "submit", doc=doc):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    kwargs = {"sre_list": None}
    if item_code:
        sres = frappe.get_all("Stock Reservation Entry",
                              filters={"voucher_type": "Sales Order", "voucher_no": sales_order,
                                       "item_code": item_code, "docstatus": 1, "status": ["!=", "Delivered"]},
                              pluck="name")
        doc.cancel_stock_reservation_entries(sre_list=sres)
    else:
        doc.cancel_stock_reservation_entries()
    frappe.db.commit()
    return {"sales_order": sales_order, "released": True}


def _reservations_for(sales_order: str) -> list[dict]:
    return frappe.get_all(
        "Stock Reservation Entry",
        filters={"voucher_type": "Sales Order", "voucher_no": sales_order, "docstatus": 1},
        fields=["name", "item_code", "warehouse", "reserved_qty", "delivered_qty", "status", "creation"],
    )


def release_expired_reservations() -> dict:
    """Scheduled job: cancel open reservations past the expiry window.

    Only releases reservations that are still open (not delivered). Uses the
    standard cancel path so Bin.reserved_stock is corrected by ERPNext.
    """
    if not _reservation_enabled():
        return {"released": 0, "reason": "reservation disabled"}
    cutoff = add_days(now_datetime(), -reservation_expiry_days())
    stale = frappe.get_all(
        "Stock Reservation Entry",
        filters={"voucher_type": "Sales Order", "docstatus": 1,
                 "status": ["in", ["Reserved", "Partially Reserved"]],
                 "creation": ["<", cutoff]},
        fields=["name", "voucher_no"],
    )
    released = 0
    for group in {row["voucher_no"] for row in stale}:
        try:
            doc = frappe.get_doc("Sales Order", group)
            names = [r["name"] for r in stale if r["voucher_no"] == group]
            doc.cancel_stock_reservation_entries(sre_list=names)
            released += len(names)
        except Exception:
            frappe.log_error(title="Reservation expiry release failed", message=frappe.get_traceback())
    frappe.db.commit()
    return {"released": released, "expiry_days": reservation_expiry_days()}
