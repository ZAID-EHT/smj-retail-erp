"""Payment Reconciliation adapter for Retail ERP.

`Payment Reconciliation` is a standard ERPNext *virtual* doctype (never saved
to the database - `Document.save()` is a no-op on it). The Desk client keeps
the whole doc in browser memory across a 3-step flow and resubmits it on
every RPC call. This module reproduces that flow with three fixed-purpose
whitelisted functions instead of exposing the generic, browser-suppliable
`run_doc_method` RPC - only these three named operations can ever run, never
an arbitrary method path.

All three delegate to the exact same standard `erpnext.accounts.doctype.
payment_reconciliation.payment_reconciliation.PaymentReconciliation` methods
the Desk UI itself calls (`get_unreconciled_entries`, `allocate_entries`,
`reconcile`). No GL Entry, Payment Ledger Entry or outstanding balance is
written or computed by this module directly - `reconcile()` is ERPNext's own
official reconciliation posting path.
"""
from __future__ import annotations

import frappe
from frappe import _

PARTY_TYPES = {"Customer", "Supplier"}


def _require_login() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


MAX_SEARCH_RESULTS = 20


@frappe.whitelist(methods=["GET"])
def search_company(txt: str = ""):
    """Permission-aware Company search for the reconciliation filter form."""
    _require_login()
    if not frappe.has_permission("Company", "read"):
        return []
    filters = {"name": ["like", f"%{txt}%"]} if txt else {}
    rows = frappe.get_list("Company", filters=filters, fields=["name"], limit_page_length=MAX_SEARCH_RESULTS)
    return [{"value": r.name, "label": r.name} for r in rows]


@frappe.whitelist(methods=["GET"])
def search_party(party_type: str, txt: str = ""):
    """Permission-aware Customer/Supplier search for the reconciliation filter form."""
    _require_login()
    if party_type not in PARTY_TYPES or not frappe.has_permission(party_type, "read"):
        return []
    title_field = "customer_name" if party_type == "Customer" else "supplier_name"
    fields = ["name", title_field]
    or_filters = [["name", "like", f"%{txt}%"], [title_field, "like", f"%{txt}%"]] if txt else []
    rows = frappe.get_list(party_type, or_filters=or_filters, fields=fields, limit_page_length=MAX_SEARCH_RESULTS)
    return [{"value": r.name, "label": f"{r.name} — {r.get(title_field)}" if r.get(title_field) else r.name} for r in rows]


def _invoice_doctype(party_type: str) -> str:
    return "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"


def _check_permissions(party_type: str, party: str, *, write: bool = False) -> None:
    if party_type not in PARTY_TYPES:
        frappe.throw(_("Party type must be Customer or Supplier."), frappe.ValidationError)
    if not frappe.has_permission(party_type, "read", doc=party):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    if not frappe.has_permission("Payment Entry", "write" if write else "read"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    if not frappe.has_permission(_invoice_doctype(party_type), "write" if write else "read"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)


def _new_reconciliation_doc(company: str, party_type: str, party: str, receivable_payable_account: str | None):
    from erpnext.accounts.party import get_party_account

    account = receivable_payable_account or get_party_account(party_type, party, company)
    doc = frappe.get_doc({
        "doctype": "Payment Reconciliation",
        "company": company,
        "party_type": party_type,
        "party": party,
        "receivable_payable_account": account,
        "invoice_limit": 100,
        "payment_limit": 100,
    })
    return doc


def _row_dicts(rows) -> list[dict]:
    return [row.as_dict() if hasattr(row, "as_dict") else dict(row) for row in (rows or [])]


@frappe.whitelist(methods=["POST"])
def get_unreconciled_entries(company: str, party_type: str, party: str, receivable_payable_account: str | None = None):
    """Step 1 (read-only): list this party's unreconciled invoices and payments."""
    _require_login()
    _check_permissions(party_type, party, write=False)

    doc = _new_reconciliation_doc(company, party_type, party, receivable_payable_account)
    doc.get_unreconciled_entries()
    return {
        "company": doc.company,
        "party_type": doc.party_type,
        "party": doc.party,
        "receivable_payable_account": doc.receivable_payable_account,
        "invoices": _row_dicts(doc.get("invoices")),
        "payments": _row_dicts(doc.get("payments")),
    }


@frappe.whitelist(methods=["POST"])
def preview_allocation(
    company: str, party_type: str, party: str, receivable_payable_account: str,
    invoices: list | str, payments: list | str,
):
    """Step 2 (read-only): compute proposed allocation + difference amounts.

    `invoices`/`payments` must be the exact row objects returned by
    get_unreconciled_entries for this same party/account - the frontend
    round-trips them unmodified except for which rows are selected, matching
    the shape ERPNext's own reconciliation engine expects.
    """
    _require_login()
    _check_permissions(party_type, party, write=False)

    invoices = frappe.parse_json(invoices) if isinstance(invoices, str) else invoices
    payments = frappe.parse_json(payments) if isinstance(payments, str) else payments
    if not invoices or not payments:
        frappe.throw(_("Select at least one invoice and one payment to allocate."), frappe.ValidationError)

    doc = _new_reconciliation_doc(company, party_type, party, receivable_payable_account)
    doc.allocate_entries({"invoices": invoices, "payments": payments})
    return {"allocation": _row_dicts(doc.get("allocation"))}


@frappe.whitelist(methods=["POST"])
def reconcile(
    company: str, party_type: str, party: str, receivable_payable_account: str,
    allocation: list | str,
):
    """Step 3 (writes): post the reconciliation via ERPNext's standard engine.

    `allocation` must be the exact rows returned by preview_allocation for
    this same party/account.
    """
    _require_login()
    _check_permissions(party_type, party, write=True)

    allocation = frappe.parse_json(allocation) if isinstance(allocation, str) else allocation
    if not allocation:
        frappe.throw(_("Nothing to reconcile - run allocation preview first."), frappe.ValidationError)

    doc = _new_reconciliation_doc(company, party_type, party, receivable_payable_account)
    doc.set("allocation", [])
    for row in allocation:
        doc.append("allocation", row)
    doc.reconcile()
    return {
        "reconciled_count": len(allocation),
        "company": doc.company,
        "party_type": doc.party_type,
        "party": doc.party,
    }
