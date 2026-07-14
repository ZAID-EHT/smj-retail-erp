"""Server-side customer credit status and delivery gate.

Official balances come from standard ERPNext (get_customer_outstanding /
get_credit_limit). Vue never computes official receivables. The Credit vs
Non-Credit type is read from the custom field `custom_credit_type` when present
(added via fixtures); the code degrades gracefully when it is absent so it is
testable before the fixture is applied.
"""
from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

CREDIT_TYPE_FIELD = "custom_credit_type"
CREDIT_CUSTOMER = "Credit Customer"
NON_CREDIT_CUSTOMER = "Non-Credit Customer"


def _has_credit_type_field() -> bool:
    return bool(frappe.get_meta("Customer").get_field(CREDIT_TYPE_FIELD))


def get_customer_credit_type(customer: str) -> str | None:
    if not _has_credit_type_field():
        return None
    return frappe.db.get_value("Customer", customer, CREDIT_TYPE_FIELD) or None


def _overdue_amount(customer: str, company: str | None) -> float:
    filters = {"customer": customer, "docstatus": 1, "outstanding_amount": [">", 0], "due_date": ["<", nowdate()]}
    if company:
        filters["company"] = company
    rows = frappe.get_all("Sales Invoice", filters=filters, fields=["outstanding_amount"])
    return flt(sum(flt(r.outstanding_amount) for r in rows))


@frappe.whitelist()
def get_customer_credit_status(customer: str, company: str | None = None):
    """Permission-aware credit snapshot for a customer.

    Read-only; safe to call before any schema change. Returns standard ERPNext
    outstanding/credit-limit plus overdue and available credit.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
    if not frappe.has_permission("Customer", "read", doc=customer):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    if not company:
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_default("company")

    from erpnext.selling.doctype.customer.customer import get_credit_limit, get_customer_outstanding

    credit_type = get_customer_credit_type(customer)
    credit_limit = flt(get_credit_limit(customer, company)) if company else 0.0
    outstanding = flt(get_customer_outstanding(customer, company)) if company else 0.0
    overdue = _overdue_amount(customer, company)
    available = (credit_limit - outstanding) if credit_limit else None
    return {
        "customer": customer,
        "company": company,
        "credit_type": credit_type,
        "is_credit_customer": credit_type == CREDIT_CUSTOMER,
        "credit_limit": credit_limit,
        "current_outstanding": outstanding,
        "available_credit": available,
        "overdue_amount": overdue,
        "has_overdue": overdue > 0,
        "credit_type_field_present": _has_credit_type_field(),
    }


def decide_delivery_gate(credit_type: str | None, has_overdue: bool, credit_limit: float,
                         current_outstanding: float, incremental_amount: float = 0.0,
                         field_present: bool = True) -> dict:
    """Pure decision for the delivery-before-payment gate (no DB access).

    Rules (approved):
    - Type unset: a manager must classify the customer.
    - Non-Credit: dispatch requires full payment (not allowed on credit here).
    - Credit + overdue: requires manager approval.
    - Credit + would exceed limit: requires manager approval.
    - Credit within limit and not overdue: allowed.
    """
    if not field_present or credit_type is None:
        return {"allowed": False, "requires_manager_approval": True,
                "reason": _("Customer credit type is not set; a manager must classify the customer.")}
    if credit_type == NON_CREDIT_CUSTOMER:
        return {"allowed": False, "requires_manager_approval": False,
                "reason": _("Non-Credit customer: full payment is required before dispatch.")}
    if has_overdue:
        return {"allowed": False, "requires_manager_approval": True,
                "reason": _("Customer has overdue invoices; a manager must approve credit delivery.")}
    projected = flt(current_outstanding) + flt(incremental_amount)
    if credit_limit and projected > credit_limit:
        return {"allowed": False, "requires_manager_approval": True,
                "reason": _("This delivery would exceed the credit limit; a manager must approve.")}
    return {"allowed": True, "requires_manager_approval": False,
            "reason": _("Within credit limit and not overdue.")}


def evaluate_delivery_gate(customer: str, company: str | None, incremental_amount: float = 0.0) -> dict:
    """Authoritative server-side delivery gate for a customer (reads real balances)."""
    status = get_customer_credit_status(customer, company)
    decision = decide_delivery_gate(
        credit_type=status["credit_type"], has_overdue=status["has_overdue"],
        credit_limit=flt(status["credit_limit"]), current_outstanding=flt(status["current_outstanding"]),
        incremental_amount=incremental_amount, field_present=status["credit_type_field_present"],
    )
    decision["status"] = status
    return decision


MANAGER_ROLES = ("Sales Manager", "Accounts Manager", "Credit Manager")


def require_manager() -> None:
    roles = set(frappe.get_roles(frappe.session.user))
    if not (roles & set(MANAGER_ROLES)) and "System Manager" not in roles:
        frappe.throw(_("Only an authorised manager can approve this credit override."), frappe.PermissionError)
