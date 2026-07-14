"""Shared Wholesale Transaction ID (TRX-YYYY-000001).

Each ERPNext document keeps its own naming series; the transaction id is a shared
reference stamped on the Sales Order and propagated to documents mapped from it.
The id is generated with frappe's atomic naming counter (tabSeries), so parallel
submits never collide.

Every hook is a no-op when the custom field is absent (e.g. before the fixture is
applied), so these events are safe on any site.
"""
from __future__ import annotations

import frappe
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, getdate

FIELD = "custom_wholesale_transaction_id"


def _field_present(doctype: str) -> bool:
    return bool(frappe.get_meta(doctype).get_field(FIELD))


def generate_transaction_id() -> str:
    year = getdate(nowdate()).year
    return make_autoname(f"TRX-{year}-.######")


def assign_to_sales_order(doc, method=None):
    """Stamp a new transaction id on a Sales Order if it has none."""
    if not _field_present(doc.doctype):
        return
    if not doc.get(FIELD):
        doc.set(FIELD, generate_transaction_id())


def _txn_from_sales_orders(so_names: list[str]) -> str | None:
    for name in so_names:
        if not name:
            continue
        value = frappe.db.get_value("Sales Order", name, FIELD)
        if value:
            return value
    return None


def propagate_from_source(doc, method=None):
    """Copy the transaction id onto a Delivery Note / Sales Invoice from its
    source Sales Orders (via child rows). Return documents inherit from the
    original because they share the same DocType and copied rows."""
    if not _field_present(doc.doctype) or doc.get(FIELD):
        return
    so_names = []
    for row in doc.get("items") or []:
        for fieldname in ("against_sales_order", "sales_order"):
            value = row.get(fieldname)
            if value:
                so_names.append(value)
    txn = _txn_from_sales_orders(list(dict.fromkeys(so_names)))
    if txn:
        doc.set(FIELD, txn)


def propagate_payment_entry(doc, method=None):
    """Copy the transaction id onto a Payment Entry from its references."""
    if not _field_present(doc.doctype) or doc.get(FIELD):
        return
    so_names, si_names = [], []
    for ref in doc.get("references") or []:
        if ref.reference_doctype == "Sales Order":
            so_names.append(ref.reference_name)
        elif ref.reference_doctype == "Sales Invoice":
            si_names.append(ref.reference_name)
    txn = _txn_from_sales_orders(so_names)
    if not txn and si_names:
        for si in si_names:
            value = frappe.db.get_value("Sales Invoice", si, FIELD)
            if value:
                txn = value
                break
    if txn:
        doc.set(FIELD, txn)
