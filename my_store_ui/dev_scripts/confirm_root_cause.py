"""Voucher-level confirmation of the opening-stock root cause (read-only)."""

from __future__ import annotations

import json

import frappe
from frappe.utils import flt


def run():
	frappe.set_user("Administrator")
	company = frappe.get_all("Company", pluck="name")[0]
	sa = frappe.db.get_value("Company", company, "stock_adjustment_account")

	# Every GL row on Stock Adjustment, with source detail.
	rows = frappe.db.sql(
		"""SELECT gle.voucher_type, gle.voucher_no, gle.posting_date, gle.debit, gle.credit,
		          gle.against, gle.is_opening, gle.creation, gle.owner, gle.is_cancelled
		   FROM `tabGL Entry` gle WHERE gle.account=%s ORDER BY gle.posting_date, gle.voucher_no""",
		sa, as_dict=True)

	# Account metadata for the accounts involved.
	def acct(name):
		return frappe.db.get_value("Account", name, ["root_type", "account_type", "report_type"], as_dict=True) if name else None

	# Check for other potential root causes.
	opening_invoices = frappe.db.count("Sales Invoice", {"is_opening": "Yes", "company": company}) + \
		frappe.db.count("Purchase Invoice", {"is_opening": "Yes", "company": company})
	manual_je_on_sa = [r for r in rows if r["voucher_type"] == "Journal Entry"]
	stock_recos = [r for r in rows if r["voucher_type"] == "Stock Reconciliation"]
	opening_stock_entries = [r for r in rows if r["voucher_type"] == "Stock Entry" and str(r["posting_date"]) <= "2025-07-01"]

	out = {
		"company": company,
		"stock_adjustment_account": sa,
		"stock_adjustment_meta": acct(sa),
		"opening_balance_equity_meta": acct(frappe.db.get_value("Account", {"company": company, "account_name": "Opening Balance Equity"}, "name")),
		"temporary_opening_meta": acct(frappe.db.get_value("Account", {"company": company, "account_name": "Temporary Opening"}, "name")),
		"all_stock_adjustment_gl_rows": rows,
		"opening_stock_entries_count": len(opening_stock_entries),
		"opening_stock_credit_total": round(sum(flt(r["credit"]) - flt(r["debit"]) for r in opening_stock_entries), 2),
		"other_root_cause_checks": {
			"opening_invoices": opening_invoices,
			"manual_je_on_stock_adjustment": len(manual_je_on_sa),
			"stock_reconciliations_on_sa": len(stock_recos),
			"any_is_opening_flag_on_stock_entries": any(r.get("is_opening") == "Yes" for r in opening_stock_entries),
		},
	}
	print("ROOT_CAUSE:", json.dumps(out, default=str))
