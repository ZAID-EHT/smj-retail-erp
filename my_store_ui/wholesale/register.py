"""Wholesale Transaction Register.

One row per wholesale transaction, anchored on the Sales Order and assembled from
standard ERPNext links (Delivery Note Item.against_sales_order, Sales Invoice
Item.sales_order, Payment Entry Reference). All figures come from ERPNext; there
is no shadow ledger. The shared Transaction ID is read from the custom field
`custom_wholesale_transaction_id` when present, otherwise the Sales Order name is
used as the interim anchor so the register works before the fixture is applied.

Read-only and permission-aware: Sales Orders are fetched with frappe.get_list so
User Permissions / company / warehouse restrictions apply.
"""
from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

TRANSACTION_ID_FIELD = "custom_wholesale_transaction_id"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
FINANCIAL_ROLES = ("Accounts User", "Accounts Manager", "Sales Manager")

SAFE_FILTERS = {"customer", "status", "from_date", "to_date", "credit_type"}


def _has_txn_field() -> bool:
    return bool(frappe.get_meta("Sales Order").get_field(TRANSACTION_ID_FIELD))


def _can_see_financials() -> bool:
    roles = set(frappe.get_roles(frappe.session.user))
    return "System Manager" in roles or bool(roles & set(FINANCIAL_ROLES))


def _delivery_status(per_delivered: float) -> str:
    if per_delivered <= 0:
        return "Not Delivered"
    if per_delivered >= 100:
        return "Fully Delivered"
    return "Partially Delivered"


def _payment_status(outstanding: float, grand_total: float, paid: float) -> str:
    if grand_total and paid <= 0:
        return "Unpaid"
    if outstanding <= 0.01:
        return "Paid"
    return "Partially Paid"


@frappe.whitelist(methods=["GET"])
def get_wholesale_transactions(filters=None, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                               sort_field: str = "transaction_date", sort_order: str = "desc"):
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
    if not frappe.has_permission("Sales Order", "read"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
    if not isinstance(filters, dict) or (set(filters) - SAFE_FILTERS):
        frappe.throw(_("Unsupported filter."), frappe.ValidationError)

    so_filters = {"docstatus": 1}
    if filters.get("customer"):
        so_filters["customer"] = filters["customer"]
    if filters.get("status"):
        so_filters["status"] = filters["status"]
    if filters.get("from_date") and filters.get("to_date"):
        so_filters["transaction_date"] = ["between", [filters["from_date"], filters["to_date"]]]

    if sort_field not in {"transaction_date", "customer", "grand_total", "name"} or str(sort_order).lower() not in {"asc", "desc"}:
        frappe.throw(_("Unsupported sort."), frappe.ValidationError)
    page = max(int(page or 1), 1)
    page_size = min(max(int(page_size or DEFAULT_PAGE_SIZE), 1), MAX_PAGE_SIZE)

    has_txn = _has_txn_field()
    so_fields = ["name", "customer", "customer_name", "company", "transaction_date", "grand_total",
                 "advance_paid", "per_delivered", "per_billed", "status"]
    if has_txn:
        so_fields.append(TRANSACTION_ID_FIELD)

    total = len(frappe.get_list("Sales Order", filters=so_filters, fields=["name"], limit_page_length=0, ignore_permissions=False))
    orders = frappe.get_list("Sales Order", filters=so_filters, fields=so_fields,
                             order_by=f"{sort_field} {sort_order}",
                             limit_start=(page - 1) * page_size, limit_page_length=page_size)
    so_names = [o["name"] for o in orders]
    show_financials = _can_see_financials()

    # Batch links for this page.
    dn_map, si_map, pe_map = {}, {}, {}
    si_outstanding = {}
    if so_names:
        for r in frappe.get_all("Delivery Note Item", filters={"against_sales_order": ["in", so_names], "docstatus": 1},
                                fields=["against_sales_order as so", "parent"], distinct=True):
            dn_map.setdefault(r["so"], set()).add(r["parent"])
        for r in frappe.get_all("Sales Invoice Item", filters={"sales_order": ["in", so_names], "docstatus": 1},
                                fields=["sales_order as so", "parent"], distinct=True):
            si_map.setdefault(r["so"], set()).add(r["parent"])
        all_si = sorted({p for s in si_map.values() for p in s})
        if all_si:
            for r in frappe.get_all("Sales Invoice", filters={"name": ["in", all_si]},
                                    fields=["name", "outstanding_amount", "grand_total"]):
                si_outstanding[r["name"]] = r
            # Payment Entries referencing these invoices or the sales orders.
            refs = frappe.get_all("Payment Entry Reference",
                                  filters={"docstatus": 1, "reference_doctype": ["in", ["Sales Invoice", "Sales Order"]],
                                           "reference_name": ["in", all_si + so_names]},
                                  fields=["parent", "reference_name", "allocated_amount"])
            for r in refs:
                # attribute payment to the SO directly, or via its invoice
                so_for_ref = r["reference_name"] if r["reference_name"] in so_names else None
                if not so_for_ref:
                    for so, sis in si_map.items():
                        if r["reference_name"] in sis:
                            so_for_ref = so
                            break
                if so_for_ref:
                    pe_map.setdefault(so_for_ref, {"entries": set(), "paid": 0.0})
                    pe_map[so_for_ref]["entries"].add(r["parent"])
                    pe_map[so_for_ref]["paid"] += flt(r["allocated_amount"])

    rows = []
    for o in orders:
        so = o["name"]
        sis = sorted(si_map.get(so, []))
        outstanding = flt(sum(flt(si_outstanding.get(s, {}).get("outstanding_amount", 0)) for s in sis))
        paid = flt(pe_map.get(so, {}).get("paid", 0.0)) or flt(o.get("advance_paid"))
        grand_total = flt(o.get("grand_total"))
        txn_id = (o.get(TRANSACTION_ID_FIELD) if has_txn else None) or so
        row = {
            "transaction_id": txn_id,
            "sales_order": so,
            "customer": o["customer"],
            "customer_name": o.get("customer_name"),
            "customer_type": frappe.db.get_value("Customer", o["customer"], "custom_credit_type") if frappe.get_meta("Customer").get_field("custom_credit_type") else None,
            "transaction_date": o.get("transaction_date"),
            "delivery_notes": sorted(dn_map.get(so, [])),
            "sales_invoices": sis,
            "payment_entries": sorted(pe_map.get(so, {}).get("entries", [])),
            "delivery_status": _delivery_status(flt(o.get("per_delivered"))),
            "overall_status": o.get("status"),
        }
        if show_financials:
            row.update({
                "grand_total": grand_total,
                "paid_amount": paid,
                "outstanding_amount": outstanding,
                "payment_status": _payment_status(outstanding, grand_total, paid),
            })
        else:
            row["payment_status"] = _payment_status(outstanding, grand_total, paid)
        rows.append(row)

    return {
        "rows": rows,
        "pagination": {"page": page, "page_size": page_size, "total": total,
                       "pages": max((total + page_size - 1) // page_size, 1)},
        "shows_financials": show_financials,
        "transaction_id_field_present": has_txn,
        "columns": _register_columns(show_financials),
    }


def _register_columns(show_financials: bool) -> list[dict]:
    cols = [
        {"fieldname": "transaction_id", "label": _("Transaction"), "fieldtype": "Data"},
        {"fieldname": "customer_name", "label": _("Customer"), "fieldtype": "Data"},
        {"fieldname": "customer_type", "label": _("Type"), "fieldtype": "Data"},
        {"fieldname": "transaction_date", "label": _("Date"), "fieldtype": "Date"},
        {"fieldname": "sales_order", "label": _("Sales Order"), "fieldtype": "Link"},
        {"fieldname": "delivery_status", "label": _("Delivery"), "fieldtype": "Data"},
        {"fieldname": "payment_status", "label": _("Payment"), "fieldtype": "Data"},
        {"fieldname": "overall_status", "label": _("Status"), "fieldtype": "Data"},
    ]
    if show_financials:
        cols[5:5] = [
            {"fieldname": "grand_total", "label": _("Total"), "fieldtype": "Currency"},
            {"fieldname": "paid_amount", "label": _("Paid"), "fieldtype": "Currency"},
            {"fieldname": "outstanding_amount", "label": _("Outstanding"), "fieldtype": "Currency"},
        ]
    return cols


@frappe.whitelist(methods=["GET"])
def get_transaction_timeline(sales_order: str):
    """Full document timeline for one wholesale transaction."""
    if not frappe.has_permission("Sales Order", "read", doc=sales_order):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    events = []
    so = frappe.db.get_value("Sales Order", sales_order, ["transaction_date", "customer", "status"], as_dict=True)
    events.append({"doctype": "Sales Order", "name": sales_order, "date": so.transaction_date, "label": _("Sales Order created")})
    for r in frappe.get_all("Stock Reservation Entry", filters={"voucher_type": "Sales Order", "voucher_no": sales_order, "docstatus": 1},
                            fields=["name", "creation", "status", "reserved_qty"]):
        events.append({"doctype": "Stock Reservation Entry", "name": r["name"], "date": r["creation"], "label": _("Stock reserved ({0})").format(r["status"])})
    for r in frappe.get_all("Delivery Note Item", filters={"against_sales_order": sales_order, "docstatus": 1}, fields=["parent"], distinct=True):
        events.append({"doctype": "Delivery Note", "name": r["parent"], "date": frappe.db.get_value("Delivery Note", r["parent"], "posting_date"), "label": _("Delivered")})
    for r in frappe.get_all("Sales Invoice Item", filters={"sales_order": sales_order, "docstatus": 1}, fields=["parent"], distinct=True):
        events.append({"doctype": "Sales Invoice", "name": r["parent"], "date": frappe.db.get_value("Sales Invoice", r["parent"], "posting_date"), "label": _("Invoiced")})
    events.sort(key=lambda e: str(e.get("date") or ""))
    return {"sales_order": sales_order, "events": events}
