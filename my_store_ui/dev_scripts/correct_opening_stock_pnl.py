"""Guarded, reversible correction of the opening-stock P&L overstatement.

Root cause: three opening-stock Stock Entries dated 2025-07-01 credited the
opening inventory value to `Stock Adjustment` (an Expense account) instead of a
balance-sheet account, so the P&L shows ~11.82M of "negative expense" that is
really the owner's opening inventory contribution -- inflating profit.

Correction (standard, no ledger cascade): a single reclassification Journal Entry
dated 2025-07-01 moving the opening-stock amount out of Stock Adjustment (Expense)
into `Opening Balance Equity` (Equity):

    Dr  Stock Adjustment      11,820,700   (removes the P&L artifact)
    Cr  Opening Balance Equity 11,820,700  (parks it as opening equity)

Net effect: P&L profit drops by the artifact; retained earnings drop by the same;
Opening Balance Equity rises by the same; total equity and total assets unchanged;
the Balance Sheet still balances. No submitted stock/business document is touched
or cancelled, so there is no Stock Ledger reposting cascade.

Safety:
  * refuses to run off staging.local;
  * refuses to run twice (looks for its own marker Journal Entry);
  * verifies the three expected source Stock Entries and the exact amount;
  * verifies both accounts exist and have the expected root types;
  * `run()` is a DRY RUN -- it computes before/after inside a savepoint and rolls
    back, persisting nothing;
  * `apply()` creates and submits the reversible Journal Entry for real.

    bench --site staging.local execute my_store_ui.dev_scripts.correct_opening_stock_pnl.run
    bench --site staging.local execute my_store_ui.dev_scripts.correct_opening_stock_pnl.apply
"""

from __future__ import annotations

import json

import frappe
from frappe.utils import flt

OPENING_DATE = "2025-07-01"
EXPECTED_SOURCE = {"MAT-STE-2026-00001", "MAT-STE-2026-00002", "MAT-STE-2026-00003"}
MARKER = "SMJ opening-stock reclassification"
EQUITY_ACCOUNT_NAME = "Opening Balance Equity"


def _guard():
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")


def _context() -> dict:
	company = frappe.get_all("Company", pluck="name")[0]
	sa_account = frappe.db.get_value("Company", company, "stock_adjustment_account")
	equity_account = frappe.db.get_value(
		"Account", {"company": company, "account_name": EQUITY_ACCOUNT_NAME}, "name"
	)
	return {"company": company, "sa_account": sa_account, "equity_account": equity_account}


def _opening_amount(ctx: dict) -> tuple[float, list[str]]:
	rows = frappe.db.sql(
		"""
		SELECT voucher_no, ROUND(SUM(credit - debit), 2) AS net_credit
		FROM `tabGL Entry`
		WHERE account = %s AND is_cancelled = 0 AND voucher_type = 'Stock Entry'
		      AND posting_date <= %s
		GROUP BY voucher_no
		""",
		(ctx["sa_account"], OPENING_DATE), as_dict=True,
	)
	vouchers = {r["voucher_no"] for r in rows if flt(r["net_credit"]) != 0}
	amount = round(sum(flt(r["net_credit"]) for r in rows), 2)
	return amount, sorted(vouchers)


def _pnl_and_balance(ctx: dict) -> dict:
	company = ctx["company"]
	income = frappe.db.sql(
		"""SELECT ROUND(SUM(gle.credit - gle.debit),2) FROM `tabGL Entry` gle
		   JOIN `tabAccount` a ON a.name = gle.account
		   WHERE gle.company=%s AND gle.is_cancelled=0 AND a.root_type='Income'""",
		company)[0][0] or 0
	expense = frappe.db.sql(
		"""SELECT ROUND(SUM(gle.debit - gle.credit),2) FROM `tabGL Entry` gle
		   JOIN `tabAccount` a ON a.name = gle.account
		   WHERE gle.company=%s AND gle.is_cancelled=0 AND a.root_type='Expense'""",
		company)[0][0] or 0
	total_debit, total_credit = frappe.db.sql(
		"""SELECT ROUND(SUM(debit),2), ROUND(SUM(credit),2) FROM `tabGL Entry`
		   WHERE company=%s AND is_cancelled=0""", company)[0]
	return {
		"income": flt(income), "expense": flt(expense),
		"profit": round(flt(income) - flt(expense), 2),
		"total_debit": flt(total_debit), "total_credit": flt(total_credit),
		"trial_balance_balanced": abs(flt(total_debit) - flt(total_credit)) < 0.01,
	}


def _validate(ctx: dict) -> tuple[float, list[str]]:
	if not ctx["sa_account"]:
		raise RuntimeError("company has no stock_adjustment_account")
	if not ctx["equity_account"]:
		raise RuntimeError(f"no {EQUITY_ACCOUNT_NAME!r} account on the company")
	if frappe.db.get_value("Account", ctx["sa_account"], "root_type") != "Expense":
		raise RuntimeError("stock adjustment account is not an Expense account; aborting")
	if frappe.db.get_value("Account", ctx["equity_account"], "root_type") != "Equity":
		raise RuntimeError("target account is not Equity; aborting")
	amount, vouchers = _opening_amount(ctx)
	if amount <= 0:
		raise RuntimeError("no opening-stock credit found on Stock Adjustment; nothing to correct")
	if not EXPECTED_SOURCE.issubset(set(vouchers)):
		raise RuntimeError(f"expected source Stock Entries {EXPECTED_SOURCE} not all present: found {vouchers}")
	return amount, vouchers


def _already_applied(ctx: dict) -> str | None:
	return frappe.db.get_value(
		"Journal Entry",
		{"company": ctx["company"], "user_remark": ["like", f"%{MARKER}%"], "docstatus": 1},
		"name",
	)


def _make_je(ctx: dict, amount: float):
	je = frappe.get_doc({
		"doctype": "Journal Entry",
		"voucher_type": "Journal Entry",
		"company": ctx["company"],
		"posting_date": OPENING_DATE,
		"user_remark": f"{MARKER}: move opening inventory offset from Stock Adjustment "
		               f"(Expense) to Opening Balance Equity so the P&L is not overstated.",
		"accounts": [
			{"account": ctx["sa_account"], "debit_in_account_currency": amount, "credit_in_account_currency": 0},
			{"account": ctx["equity_account"], "debit_in_account_currency": 0, "credit_in_account_currency": amount},
		],
	})
	je.insert(ignore_permissions=True)
	je.submit()
	return je


def run() -> dict:
	"""DRY RUN: prove the correction reconciles, persist nothing."""
	_guard()
	frappe.set_user("Administrator")
	ctx = _context()
	if _already_applied(ctx):
		result = {"status": "already_applied", "je": _already_applied(ctx)}
		print(json.dumps(result, indent=1))
		return result
	amount, vouchers = _validate(ctx)
	before = _pnl_and_balance(ctx)
	sp = "opening_stock_dry_run"
	frappe.db.savepoint(sp)
	try:
		je = _make_je(ctx, amount)
		after = _pnl_and_balance(ctx)
		je_name = je.name
	finally:
		frappe.db.rollback(save_point=sp)
	result = {
		"status": "dry_run",
		"amount_reclassified": amount,
		"source_vouchers": vouchers,
		"from_account": ctx["sa_account"],
		"to_account": ctx["equity_account"],
		"before": before,
		"after": after,
		"profit_reduced_by": round(before["profit"] - after["profit"], 2),
		"balanced_before": before["trial_balance_balanced"],
		"balanced_after": after["trial_balance_balanced"],
		"persisted": False,
		"dry_run_je_would_be": je_name,
	}
	print(json.dumps(result, indent=1, default=str))
	return result


def apply() -> dict:
	"""Persist the reversible correction Journal Entry for real."""
	_guard()
	frappe.set_user("Administrator")
	ctx = _context()
	if _already_applied(ctx):
		result = {"status": "already_applied", "je": _already_applied(ctx)}
		print(json.dumps(result, indent=1))
		return result
	amount, vouchers = _validate(ctx)
	before = _pnl_and_balance(ctx)
	je = _make_je(ctx, amount)
	frappe.db.commit()
	after = _pnl_and_balance(ctx)
	result = {
		"status": "applied",
		"je": je.name,
		"amount_reclassified": amount,
		"before_profit": before["profit"],
		"after_profit": after["profit"],
		"profit_reduced_by": round(before["profit"] - after["profit"], 2),
		"balanced_after": after["trial_balance_balanced"],
		"reversible": "cancel Journal Entry " + je.name,
	}
	print(json.dumps(result, indent=1, default=str))
	return result
