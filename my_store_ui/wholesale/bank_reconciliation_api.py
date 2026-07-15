"""Bank Reconciliation Tool adapter for Retail ERP.

`Bank Reconciliation Tool` is a standard ERPNext *virtual* doctype - its
`Document` subclass body is literally `pass`; nothing is ever saved to the
database for it. All real behaviour lives in module-level
`@frappe.whitelist()` functions in `erpnext.accounts.doctype.
bank_reconciliation_tool.bank_reconciliation_tool`, which the Desk client
calls directly by method path with no server-side permission checks of its
own (Desk relies on the page only being reachable by a role with "Bank
Reconciliation Tool" read permission). This module reproduces the same flow
with fixed-purpose whitelisted wrappers - never Frappe's generic,
browser-suppliable `run_doc_method` / method-path RPC - and adds explicit
company/bank-account/doctype permission checks on every operation, matching
(and exceeding) what the standard Desk tool enforces.

Every write operation ultimately calls ERPNext's own controller functions
(`create_payment_entry_bts`, `create_journal_entry_bts`, `reconcile_vouchers`,
`auto_reconcile_vouchers`, `Bank Transaction.remove_payment_entries`,
`update_bank_transaction`) - this module never writes a GL Entry, Payment
Ledger Entry, Bank Transaction allocation or clearance date directly.
"""
from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

MAX_SEARCH_RESULTS = 20

# Exact "Journal Entry Type" options offered by ERPNext's own Bank
# Reconciliation Tool dialog (erpnext/public/js/bank_reconciliation_tool/
# dialog_manager.js). Kept as an explicit allowlist rather than trusting the
# browser-supplied voucher_type string.
ALLOWED_JOURNAL_ENTRY_TYPES = {
    "Journal Entry", "Inter Company Journal Entry", "Bank Entry", "Cash Entry",
    "Credit Card Entry", "Debit Note", "Credit Note", "Contra Entry", "Excise Entry",
    "Write Off Entry", "Opening Entry", "Depreciation Entry",
    "Exchange Rate Revaluation", "Deferred Revenue", "Deferred Expense",
}

PE_PREVIEW_FIELDS = (
    "doctype", "payment_type", "company", "party_type", "party",
    "paid_from", "paid_to", "paid_from_account_currency", "paid_to_account_currency",
    "paid_amount", "received_amount", "reference_no", "reference_date",
    "posting_date", "mode_of_payment", "project", "cost_center",
)
JE_PREVIEW_FIELDS = (
    "doctype", "voucher_type", "company", "posting_date", "cheque_date",
    "cheque_no", "mode_of_payment", "multi_currency",
)

ALLOWED_MATCH_DOCUMENT_TYPES = {
    "payment_entry", "journal_entry", "sales_invoice", "purchase_invoice",
    "bank_transaction", "exact_match",
}
ALLOWED_VOUCHER_DOCTYPES = {"Payment Entry", "Journal Entry", "Sales Invoice", "Purchase Invoice", "Bank Transaction"}


def _require_login() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_tool_access() -> None:
    """Gate on the same DocType permission the real ERPNext Desk tool uses."""
    if not frappe.has_permission("Bank Reconciliation Tool", "read"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)


def _bank_account_company(bank_account: str) -> str | None:
    return frappe.db.get_value("Bank Account", bank_account, "company")


def _check_account_access(company: str, bank_account: str | None = None, *, write: bool = False) -> None:
    _require_tool_access()
    if not company or not frappe.has_permission("Company", "read", doc=company):
        frappe.throw(_("Not permitted for this company."), frappe.PermissionError)
    if bank_account:
        if not frappe.has_permission("Bank Account", "read", doc=bank_account):
            frappe.throw(_("Not permitted."), frappe.PermissionError)
        if _bank_account_company(bank_account) != company:
            frappe.throw(_("Bank account does not belong to the selected company."), frappe.ValidationError)
    if not frappe.has_permission("Bank Transaction", "write" if write else "read"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)


def _bank_transaction_context(bank_transaction_name: str) -> tuple[str, str]:
    bank_account_name = frappe.db.get_value("Bank Transaction", bank_transaction_name, "bank_account")
    if not bank_account_name:
        frappe.throw(_("Bank transaction not found."), frappe.DoesNotExistError)
    company = _bank_account_company(bank_account_name)
    return bank_account_name, company


def _validate_posting_date(posting_date: str | None) -> None:
    if not posting_date:
        frappe.throw(_("Posting date is required."), frappe.ValidationError)
    try:
        getdate(posting_date)
    except Exception:
        frappe.throw(_("Posting date is invalid."), frappe.ValidationError)


def _validate_party(party_type: str, party: str) -> None:
    if not party_type or not party:
        frappe.throw(_("Party Type and Party are required."), frappe.ValidationError)
    if not frappe.db.exists("Party Type", party_type):
        frappe.throw(_("Unsupported party type."), frappe.ValidationError)
    if not frappe.has_permission(party_type, "read", doc=party):
        frappe.throw(_("Not permitted."), frappe.PermissionError)


def _serialise(doc, fields: tuple[str, ...]) -> dict:
    return {field: doc.get(field) for field in fields}


@frappe.whitelist(methods=["GET"])
def search_bank_account(txt: str = "", company: str | None = None):
    """Permission-aware Bank Account search for the reconciliation filter form."""
    _require_login()
    _require_tool_access()
    if not frappe.has_permission("Bank Account", "read"):
        return []
    filters = {}
    if company:
        filters["company"] = company
    or_filters = [["name", "like", f"%{txt}%"], ["account", "like", f"%{txt}%"]] if txt else []
    rows = frappe.get_list(
        "Bank Account", filters=filters, or_filters=or_filters,
        fields=["name", "account", "company"], limit_page_length=MAX_SEARCH_RESULTS,
    )
    return [{"value": r.name, "label": f"{r.name} ({r.company})" if r.company else r.name} for r in rows]


PARTY_TYPES = {"Customer", "Supplier", "Employee"}


@frappe.whitelist(methods=["GET"])
def search_party(party_type: str, txt: str = ""):
    """Permission-aware party search for Journal/Payment Entry creation."""
    _require_login()
    if party_type not in PARTY_TYPES or not frappe.has_permission(party_type, "read"):
        return []
    title_field = {"Customer": "customer_name", "Supplier": "supplier_name", "Employee": "employee_name"}[party_type]
    fields = ["name", title_field]
    or_filters = [["name", "like", f"%{txt}%"], [title_field, "like", f"%{txt}%"]] if txt else []
    rows = frappe.get_list(party_type, or_filters=or_filters, fields=fields, limit_page_length=MAX_SEARCH_RESULTS)
    return [{"value": r.name, "label": f"{r.name} — {r.get(title_field)}" if r.get(title_field) else r.name} for r in rows]


@frappe.whitelist(methods=["GET"])
def search_account(txt: str = "", company: str | None = None):
    """Permission-aware, non-group Account search for the Journal Entry second account."""
    _require_login()
    if not frappe.has_permission("Account", "read"):
        return []
    filters = {"is_group": 0}
    if company:
        filters["company"] = company
    or_filters = [["name", "like", f"%{txt}%"], ["account_name", "like", f"%{txt}%"]] if txt else []
    rows = frappe.get_list(
        "Account", filters=filters, or_filters=or_filters,
        fields=["name", "account_name"], limit_page_length=MAX_SEARCH_RESULTS,
    )
    return [{"value": r.name, "label": r.name} for r in rows]


@frappe.whitelist(methods=["GET"])
def search_mode_of_payment(txt: str = ""):
    """Permission-aware Mode of Payment search."""
    _require_login()
    if not frappe.has_permission("Mode of Payment", "read"):
        return []
    filters = {"name": ["like", f"%{txt}%"]} if txt else {}
    rows = frappe.get_list("Mode of Payment", filters=filters, fields=["name"], limit_page_length=MAX_SEARCH_RESULTS)
    return [{"value": r.name, "label": r.name} for r in rows]


@frappe.whitelist(methods=["POST"])
def get_summary(
    company: str, bank_account: str,
    bank_statement_from_date: str | None = None, bank_statement_to_date: str | None = None,
    bank_statement_closing_balance: float = 0,
):
    """Read-only: account currency, ERP ledger balance and unreconciled bank transactions."""
    _require_login()
    _check_account_access(company, bank_account, write=False)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import (
        get_account_balance,
        get_bank_transactions,
    )

    till_date = bank_statement_to_date or nowdate()
    account = frappe.db.get_value("Bank Account", bank_account, "account")
    account_currency = frappe.db.get_value("Account", account, "account_currency") if account else None

    ledger_balance = flt(get_account_balance(bank_account, till_date, company))
    transactions = get_bank_transactions(bank_account, bank_statement_from_date, bank_statement_to_date)
    closing_balance = flt(bank_statement_closing_balance)

    return {
        "company": company, "bank_account": bank_account, "account": account,
        "account_currency": account_currency,
        "ledger_balance": ledger_balance,
        "bank_statement_closing_balance": closing_balance,
        "difference": flt(closing_balance - ledger_balance),
        "transactions": transactions,
    }


@frappe.whitelist(methods=["POST"])
def get_matches(
    bank_transaction_name: str, document_types: list | str,
    from_date: str | None = None, to_date: str | None = None,
    filter_by_reference_date: int = 0, from_reference_date: str | None = None, to_reference_date: str | None = None,
):
    """Read-only: candidate Payment Entry / Journal Entry / Invoice / Bank Transaction matches."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=False)

    document_types = frappe.parse_json(document_types) if isinstance(document_types, str) else document_types
    if not document_types or set(document_types) - ALLOWED_MATCH_DOCUMENT_TYPES:
        frappe.throw(_("Unsupported document type filter."), frappe.ValidationError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import get_linked_payments
    return get_linked_payments(
        bank_transaction_name, document_types, from_date, to_date,
        filter_by_reference_date, from_reference_date, to_reference_date,
    )


@frappe.whitelist(methods=["POST"])
def update_transaction_reference(
    bank_transaction_name: str, reference_number: str | None = None,
    party_type: str | None = None, party: str | None = None,
):
    """Writes: update a bank transaction's reference number / party before matching."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=True)
    if party_type:
        _validate_party(party_type, party)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import update_bank_transaction
    return update_bank_transaction(bank_transaction_name, reference_number, party_type, party)


@frappe.whitelist(methods=["POST"])
def reconcile_transaction(bank_transaction_name: str, vouchers: list | str):
    """Writes: reconcile the bank transaction against selected existing vouchers."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=True)

    vouchers = frappe.parse_json(vouchers) if isinstance(vouchers, str) else vouchers
    if not vouchers:
        frappe.throw(_("Select at least one voucher to reconcile."), frappe.ValidationError)
    for voucher in vouchers:
        doctype = voucher.get("payment_doctype")
        if doctype not in ALLOWED_VOUCHER_DOCTYPES:
            frappe.throw(_("Unsupported voucher type."), frappe.ValidationError)
        if not frappe.has_permission(doctype, "write", doc=voucher.get("payment_name")):
            frappe.throw(_("Not permitted."), frappe.PermissionError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import reconcile_vouchers
    transaction = reconcile_vouchers(bank_transaction_name, frappe.as_json(vouchers))
    return transaction.as_dict()


@frappe.whitelist(methods=["POST"])
def unreconcile_transaction(bank_transaction_name: str):
    """Writes: remove existing payment links from a bank transaction (ERPNext's own undo path)."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=True)

    doc = frappe.get_doc("Bank Transaction", bank_transaction_name)
    if not doc.has_permission("write"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    doc.remove_payment_entries()
    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def preview_payment_entry(
    bank_transaction_name: str, party_type: str, party: str,
    reference_number: str | None = None, reference_date: str | None = None,
    posting_date: str | None = None, mode_of_payment: str | None = None,
    project: str | None = None, cost_center: str | None = None, company_bank_account: str | None = None,
):
    """Read-only: build the Payment Entry ERPNext would create, without saving it."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=False)
    _validate_party(party_type, party)
    _validate_posting_date(posting_date)
    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import create_payment_entry_bts
    doc = create_payment_entry_bts(
        bank_transaction_name, reference_number, reference_date, party_type, party,
        posting_date, mode_of_payment, project, cost_center, allow_edit=1,
        company_bank_account=company_bank_account,
    )
    return _serialise(doc, PE_PREVIEW_FIELDS)


@frappe.whitelist(methods=["POST"])
def confirm_payment_entry(
    bank_transaction_name: str, party_type: str, party: str,
    reference_number: str | None = None, reference_date: str | None = None,
    posting_date: str | None = None, mode_of_payment: str | None = None,
    project: str | None = None, cost_center: str | None = None, company_bank_account: str | None = None,
):
    """Writes: insert + submit the Payment Entry, then reconcile it against the bank transaction."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=True)
    _validate_party(party_type, party)
    _validate_posting_date(posting_date)
    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import create_payment_entry_bts
    transaction = create_payment_entry_bts(
        bank_transaction_name, reference_number, reference_date, party_type, party,
        posting_date, mode_of_payment, project, cost_center, allow_edit=0,
        company_bank_account=company_bank_account,
    )
    return transaction.as_dict()


@frappe.whitelist(methods=["POST"])
def preview_journal_entry(
    bank_transaction_name: str, second_account: str, entry_type: str,
    reference_number: str | None = None, reference_date: str | None = None,
    posting_date: str | None = None, mode_of_payment: str | None = None,
    party_type: str | None = None, party: str | None = None,
):
    """Read-only: build the Journal Entry ERPNext would create, without saving it.

    Note (matches ERPNext's own Desk behaviour): unlike the Payment Entry
    preview, `create_journal_entry_bts` does not call `.validate()` before
    returning the unsaved doc, so debit/credit imbalance and other
    controller-level checks only surface at `confirm_journal_entry`.
    """
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=False)
    _validate_posting_date(posting_date)
    if entry_type not in ALLOWED_JOURNAL_ENTRY_TYPES:
        frappe.throw(_("Unsupported journal entry type."), frappe.ValidationError)
    if party_type:
        _validate_party(party_type, party)
    if not frappe.has_permission("Journal Entry", "create"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    if not frappe.has_permission("Account", "read", doc=second_account):
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import create_journal_entry_bts
    doc = create_journal_entry_bts(
        bank_transaction_name, reference_number, reference_date, posting_date, entry_type,
        second_account, mode_of_payment, party_type, party, allow_edit=1,
    )
    result = _serialise(doc, JE_PREVIEW_FIELDS)
    result["accounts"] = [row.as_dict() for row in (doc.get("accounts") or [])]
    return result


@frappe.whitelist(methods=["POST"])
def confirm_journal_entry(
    bank_transaction_name: str, second_account: str, entry_type: str,
    reference_number: str | None = None, reference_date: str | None = None,
    posting_date: str | None = None, mode_of_payment: str | None = None,
    party_type: str | None = None, party: str | None = None,
):
    """Writes: insert + submit the Journal Entry, then reconcile it against the bank transaction."""
    _require_login()
    bank_account_name, company = _bank_transaction_context(bank_transaction_name)
    _check_account_access(company, bank_account_name, write=True)
    _validate_posting_date(posting_date)
    if entry_type not in ALLOWED_JOURNAL_ENTRY_TYPES:
        frappe.throw(_("Unsupported journal entry type."), frappe.ValidationError)
    if party_type:
        _validate_party(party_type, party)
    if not frappe.has_permission("Journal Entry", "create"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)
    if not frappe.has_permission("Account", "read", doc=second_account):
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import create_journal_entry_bts
    transaction = create_journal_entry_bts(
        bank_transaction_name, reference_number, reference_date, posting_date, entry_type,
        second_account, mode_of_payment, party_type, party, allow_edit=0,
    )
    return transaction.as_dict()


@frappe.whitelist(methods=["POST"])
def auto_reconcile(
    company: str, bank_account: str, from_date: str | None = None, to_date: str | None = None,
    filter_by_reference_date: int = 0, from_reference_date: str | None = None, to_reference_date: str | None = None,
):
    """Writes: ERPNext's own best-match auto reconciliation across all unreconciled transactions."""
    _require_login()
    _check_account_access(company, bank_account, write=True)
    if not frappe.has_permission("Payment Entry", "write") or not frappe.has_permission("Journal Entry", "write"):
        frappe.throw(_("Not permitted."), frappe.PermissionError)

    from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import auto_reconcile_vouchers
    auto_reconcile_vouchers(
        bank_account, from_date, to_date, filter_by_reference_date, from_reference_date, to_reference_date,
    )
    return {"started": True}
