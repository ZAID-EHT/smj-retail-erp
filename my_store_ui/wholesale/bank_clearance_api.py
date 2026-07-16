"""Permission-aware adapter for ERPNext's Bank Clearance Single DocType."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, getdate


MAX_RESULTS = 50
MAX_PAYMENT_ROWS = 500
ALLOWED_PAYMENT_DOCUMENTS = {"Journal Entry", "Payment Entry", "Purchase Invoice", "Sales Invoice"}
FILTER_FIELDS = {
	"account", "from_date", "to_date", "bank_account",
	"include_reconciled_entries", "include_pos_transactions",
}
ROW_FIELDS = {
	"payment_document", "payment_entry", "against_account", "amount",
	"posting_date", "cheque_number", "cheque_date", "clearance_date",
}


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_access(permission: str = "read") -> None:
	_require_login()
	if not frappe.has_permission("Bank Clearance", permission):
		frappe.throw(_("Bank Clearance is not available."), frappe.PermissionError)


def _visible_link(doctype: str, name: str, filters: dict | None = None) -> bool:
	if not name or not frappe.has_permission(doctype, "read"):
		return False
	query = {"name": name, **(filters or {})}
	return bool(frappe.get_list(doctype, filters=query, pluck="name", limit_page_length=1))


def _parse_filters(filters) -> dict:
	filters = frappe.parse_json(filters) if isinstance(filters, str) else filters
	if not isinstance(filters, dict) or set(filters) - FILTER_FIELDS:
		frappe.throw(_("Unsupported Bank Clearance filter."), frappe.ValidationError)
	values = {key: filters.get(key) for key in FILTER_FIELDS}
	if not values.get("account"):
		frappe.throw(_("Account is required."), frappe.ValidationError)
	if not values.get("from_date") or not values.get("to_date"):
		frappe.throw(_("From Date and To Date are required."), frappe.ValidationError)
	values["from_date"] = str(getdate(values["from_date"]))
	values["to_date"] = str(getdate(values["to_date"]))
	if getdate(values["from_date"]) > getdate(values["to_date"]):
		frappe.throw(_("From Date cannot be after To Date."), frappe.ValidationError)
	if not _visible_link("Account", values["account"], {"is_group": 0, "account_type": ["in", ["Bank", "Cash"]]}):
		frappe.throw(_("A permitted Bank or Cash account is required."), frappe.PermissionError)
	if values.get("bank_account"):
		if not _visible_link("Bank Account", values["bank_account"], {"is_company_account": 1}):
			frappe.throw(_("Bank Account is not available."), frappe.PermissionError)
		linked_account = frappe.db.get_value("Bank Account", values["bank_account"], "account")
		if linked_account and linked_account != values["account"]:
			frappe.throw(_("Bank Account does not match the selected account."), frappe.ValidationError)
	values["include_reconciled_entries"] = cint(values.get("include_reconciled_entries"))
	values["include_pos_transactions"] = cint(values.get("include_pos_transactions"))
	return values


def _tool_doc(filters: dict):
	doc = frappe.get_doc("Bank Clearance", "Bank Clearance")
	for key, value in filters.items():
		doc.set(key, value)
	return doc


def _can_access_payment(row, permission: str) -> bool:
	doctype = row.get("payment_document")
	name = row.get("payment_entry")
	if doctype not in ALLOWED_PAYMENT_DOCUMENTS or not name or not frappe.has_permission(doctype, permission):
		return False
	return bool(frappe.get_list(doctype, filters={"name": name}, pluck="name", limit_page_length=1))


def _serialise_rows(doc) -> list[dict]:
	return [
		{field: row.get(field) for field in ROW_FIELDS}
		for row in doc.get("payment_entries") or []
		if _can_access_payment(row, "read")
	]


@frappe.whitelist(methods=["GET"])
def search_accounts(txt: str = ""):
	_require_access()
	if not frappe.has_permission("Account", "read"):
		return []
	txt = str(txt or "").strip()[:140]
	or_filters = [["name", "like", f"%{txt}%"], ["account_name", "like", f"%{txt}%"]] if txt else []
	rows = frappe.get_list(
		"Account", filters={"is_group": 0, "account_type": ["in", ["Bank", "Cash"]]},
		or_filters=or_filters, fields=["name", "account_name", "account_currency", "company"],
		order_by="name asc", limit_page_length=MAX_RESULTS,
	)
	return [{"value": row.name, "label": row.name, "currency": row.account_currency, "company": row.company} for row in rows]


@frappe.whitelist(methods=["GET"])
def search_bank_accounts(txt: str = "", account: str | None = None):
	_require_access()
	if not frappe.has_permission("Bank Account", "read"):
		return []
	txt = str(txt or "").strip()[:140]
	filters = {"is_company_account": 1}
	if account:
		filters["account"] = account
	or_filters = [["name", "like", f"%{txt}%"], ["bank", "like", f"%{txt}%"]] if txt else []
	rows = frappe.get_list(
		"Bank Account", filters=filters, or_filters=or_filters,
		fields=["name", "bank", "account", "company"], order_by="name asc",
		limit_page_length=MAX_RESULTS,
	)
	return [{"value": row.name, "label": row.name, "account": row.account, "company": row.company} for row in rows]


@frappe.whitelist(methods=["POST"])
def get_payment_entries(filters):
	_require_access()
	values = _parse_filters(filters)
	doc = _tool_doc(values)
	doc.get_payment_entries()
	return {
		"filters": values,
		"account_currency": doc.account_currency,
		"payment_entries": _serialise_rows(doc),
	}


@frappe.whitelist(methods=["POST"])
def update_clearance_dates(filters, payment_entries):
	_require_access("write")
	values = _parse_filters(filters)
	rows = frappe.parse_json(payment_entries) if isinstance(payment_entries, str) else payment_entries
	if not isinstance(rows, list) or not rows or len(rows) > MAX_PAYMENT_ROWS:
		frappe.throw(_("Select at least one valid payment entry."), frappe.ValidationError)

	doc = _tool_doc(values)
	doc.get_payment_entries()
	eligible = {
		(row.payment_document, row.payment_entry): row
		for row in doc.get("payment_entries") or []
		if _can_access_payment(row, "write")
	}
	selected = []
	seen = set()
	for supplied in rows:
		if not isinstance(supplied, dict) or set(supplied) - {"payment_document", "payment_entry", "clearance_date"}:
			frappe.throw(_("Unsupported Bank Clearance row."), frappe.ValidationError)
		key = (supplied.get("payment_document"), supplied.get("payment_entry"))
		if key in seen or key not in eligible:
			frappe.throw(_("Payment entry is unavailable or no longer eligible."), frappe.PermissionError)
		seen.add(key)
		clearance_date = supplied.get("clearance_date")
		if clearance_date:
			clearance_date = str(getdate(clearance_date))
		authoritative = eligible[key]
		row = {field: authoritative.get(field) for field in ROW_FIELDS}
		row["clearance_date"] = clearance_date or None
		selected.append(row)

	doc.set("payment_entries", [])
	for row in selected:
		doc.append("payment_entries", row)
	doc.update_clearance_date()
	return {
		"updated": len(selected),
		"account_currency": doc.account_currency,
		"payment_entries": _serialise_rows(doc),
	}
