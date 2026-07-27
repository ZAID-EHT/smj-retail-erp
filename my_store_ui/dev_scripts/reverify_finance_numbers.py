"""Authoritative, read-only re-verification of the opening-stock finance figures.

Uses ERPNext's official financial-statement report APIs (not documentation) to
derive Profit, expense, Trial Balance and the Stock Adjustment / Opening Balance
Equity positions. Writes nothing.
"""

from __future__ import annotations

import json

import frappe
from frappe.utils import flt


def _fiscal_year(company):
	fy = frappe.get_all("Fiscal Year", fields=["name", "year_start_date", "year_end_date"],
	                    order_by="year_start_date desc", limit_page_length=1)
	return fy[0] if fy else None


def _pnl_profit(company, fy):
	"""Profit for the period from the official Profit and Loss Statement report."""
	from erpnext.accounts.report.profit_and_loss_statement.profit_and_loss_statement import execute
	filters = frappe._dict({
		"company": company, "from_fiscal_year": fy["name"], "to_fiscal_year": fy["name"],
		"periodicity": "Yearly", "filter_based_on": "Fiscal Year", "accumulated_values": 1,
	})
	columns, data, *_rest = execute(filters)
	# The report appends a "Profit for the year" summary row.
	profit_row = next((r for r in data if isinstance(r, dict) and str(r.get("account_name") or r.get("account") or "").lower().startswith("profit")), None)
	# Period key is the fiscal-year label column.
	period_key = None
	for col in columns:
		key = col.get("fieldname") if isinstance(col, dict) else None
		if key and key not in ("account", "account_name", "currency"):
			period_key = key
			break
	profit = flt(profit_row.get(period_key)) if (profit_row and period_key) else None
	return profit, period_key


def _root_totals(company):
	income = frappe.db.sql(
		"""SELECT ROUND(SUM(gle.credit-gle.debit),2) FROM `tabGL Entry` gle
		   JOIN `tabAccount` a ON a.name=gle.account
		   WHERE gle.company=%s AND gle.is_cancelled=0 AND a.root_type='Income'""", company)[0][0] or 0
	expense = frappe.db.sql(
		"""SELECT ROUND(SUM(gle.debit-gle.credit),2) FROM `tabGL Entry` gle
		   JOIN `tabAccount` a ON a.name=gle.account
		   WHERE gle.company=%s AND gle.is_cancelled=0 AND a.root_type='Expense'""", company)[0][0] or 0
	td, tc = frappe.db.sql(
		"""SELECT ROUND(SUM(debit),2), ROUND(SUM(credit),2) FROM `tabGL Entry`
		   WHERE company=%s AND is_cancelled=0""", company)[0]
	return flt(income), flt(expense), flt(td), flt(tc)


def run():
	frappe.set_user("Administrator")
	company = frappe.get_all("Company", pluck="name")[0]
	fy = _fiscal_year(company)
	currency = frappe.db.get_value("Company", company, "default_currency")

	income, expense, td, tc = _root_totals(company)
	gl_profit = round(income - expense, 2)

	sa_account = frappe.db.get_value("Company", company, "stock_adjustment_account")
	opening_credit = frappe.db.sql(
		"""SELECT ROUND(SUM(credit-debit),2) FROM `tabGL Entry`
		   WHERE account=%s AND is_cancelled=0 AND voucher_type='Stock Entry' AND posting_date<=%s""",
		(sa_account, "2025-07-01"))[0][0] or 0
	opening_credit = flt(opening_credit)

	report_profit, period_key = None, None
	try:
		report_profit, period_key = _pnl_profit(company, fy) if fy else (None, None)
	except Exception as exc:
		report_profit = f"report error: {str(exc)[:120]}"

	result = {
		"company": company,
		"currency": currency,
		"fiscal_year": fy["name"] if fy else None,
		"gl_income": income,
		"gl_expense": expense,
		"gl_profit_before_correction": gl_profit,
		"official_pnl_report_profit": report_profit,
		"trial_balance_debit": td,
		"trial_balance_credit": tc,
		"trial_balance_balanced": abs(td - tc) < 0.01,
		"opening_stock_credit_on_stock_adjustment": opening_credit,
		"expected_profit_after_correction": round(gl_profit - opening_credit, 2),
		"expected_expense_after_correction": round(expense + opening_credit, 2),
		"arithmetic_check": f"{gl_profit} - {opening_credit} = {round(gl_profit - opening_credit, 2)}",
	}
	print("FINANCE_REVERIFY:", json.dumps(result, default=str))
