"""Read-only audit of the opening-stock P&L overstatement (staging).

Confirms whether the reported ~11.8M artifact still exists, the exact amount, the
account it hit, whether a Balance-Sheet equity target ("Temporary Opening") exists,
and the current P&L / Balance Sheet totals. Writes nothing.
"""

from __future__ import annotations

import json

import frappe
from frappe.utils import flt


def run():
	frappe.set_user("Administrator")
	company = frappe.get_all("Company", pluck="name")[0]
	out = {"company": company}

	# The opening-stock GL entries against Stock Adjustment.
	sa_account = frappe.db.get_value("Company", company, "stock_adjustment_account")
	out["stock_adjustment_account"] = sa_account
	if sa_account:
		out["stock_adjustment_root_type"] = frappe.db.get_value("Account", sa_account, "root_type")
		rows = frappe.db.sql(
			"""
			SELECT voucher_type, voucher_no, posting_date,
			       ROUND(SUM(debit),2) AS debit, ROUND(SUM(credit),2) AS credit
			FROM `tabGL Entry`
			WHERE account = %s AND is_cancelled = 0
			GROUP BY voucher_type, voucher_no, posting_date
			ORDER BY posting_date, voucher_no
			""",
			sa_account, as_dict=True,
		)
		out["stock_adjustment_entries"] = rows
		out["stock_adjustment_net_credit"] = round(sum(flt(r["credit"]) - flt(r["debit"]) for r in rows), 2)
		# The opening-stock portion: entries dated on/before the opening date.
		opening = [r for r in rows if str(r["posting_date"]) <= "2025-07-01"]
		out["opening_stock_credit"] = round(sum(flt(r["credit"]) - flt(r["debit"]) for r in opening), 2)

	# Does a Balance-Sheet equity target exist to reclassify into?
	temp_opening = frappe.get_all(
		"Account",
		filters={"company": company, "account_name": ["like", "%Temporary Opening%"]},
		fields=["name", "root_type", "account_type"],
	)
	out["temporary_opening_account"] = temp_opening

	# Existing correction Journal Entries (idempotency check).
	out["existing_correction_je"] = frappe.get_all(
		"Journal Entry",
		filters={"company": company, "user_remark": ["like", "%SMJ opening-stock reclassification%"]},
		fields=["name", "docstatus", "total_debit"],
	)

	print(json.dumps(out, indent=1, default=str))
