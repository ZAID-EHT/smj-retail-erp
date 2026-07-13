"""Permission-aware Payment Entry helpers backed by ERPNext controllers."""
from __future__ import annotations

import json
import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.entity_api import _require_login


@frappe.whitelist()
def get_outstanding_references(args):
	_require_login()
	if isinstance(args, str):
		args = json.loads(args)
	if not isinstance(args, dict):
		frappe.throw(_("Invalid outstanding reference request."), frappe.ValidationError)
	party_type = args.get("party_type")
	party = args.get("party")
	company = args.get("company")
	if not party_type or not party or not company:
		frappe.throw(_("Party Type, Party and Company are required."), frappe.ValidationError)
	if not frappe.has_permission("Payment Entry", "read"):
		frappe.throw(_("You do not have permission to read Payment Entries."), frappe.PermissionError)
	if party_type not in {"Customer", "Supplier", "Employee", "Shareholder"}:
		frappe.throw(_("Unsupported Party Type."), frappe.ValidationError)
	if not frappe.db.exists(party_type, party) or not frappe.has_permission(party_type, "read", doc=party):
		frappe.throw(_("Party not found or unavailable."), frappe.DoesNotExistError)
	if not frappe.db.exists("Company", company) or not frappe.has_permission("Company", "read", doc=company):
		frappe.throw(_("Company not found or unavailable."), frappe.DoesNotExistError)
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_outstanding_reference_documents

	request = {
		"party_type": party_type, "party": party, "company": company,
		"reference_type": args.get("reference_type"), "payment_type": args.get("payment_type") or "Receive",
		"get_outstanding_invoices": cint(args.get("get_outstanding_invoices", 1)),
		"get_orders_to_be_billed": cint(args.get("get_orders_to_be_billed", 0)),
	}
	return get_outstanding_reference_documents(request)


@frappe.whitelist()
def get_account_options(company, payment_type="Receive"):
	_require_login()
	if not frappe.has_permission("Account", "read"):
		frappe.throw(_("You do not have permission to read accounts."), frappe.PermissionError)
	if not frappe.db.exists("Company", company) or not frappe.has_permission("Company", "read", doc=company):
		frappe.throw(_("Company not found or unavailable."), frappe.DoesNotExistError)
	filters = {"company": company, "is_group": 0, "disabled": 0}
	return frappe.get_list("Account", filters=filters, fields=["name", "account_currency", "account_type"], order_by="name asc", limit_page_length=200)
