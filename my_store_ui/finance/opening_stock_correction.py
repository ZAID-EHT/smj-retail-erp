"""Guarded opening-stock P&L correction package.

Root cause (confirmed): three Material Receipt Stock Entries credited the opening
inventory value to the Expense account `Stock Adjustment`, inflating profit. The
correction is a single reclassification Journal Entry moving the amount to
`Opening Balance Equity` (Equity):

    Dr  Stock Adjustment        <amount>   (removes the P&L artifact)
    Cr  Opening Balance Equity  <amount>   (records opening equity)

No stock document is cancelled, so there is no Stock Ledger reposting cascade.

Modes (call the matching function):
  inspect        -- read-only: report the situation and whether it is correctable
  dry_run        -- build + submit the JE inside a rolled-back savepoint; nothing persists
  prepare_draft  -- create a real DRAFT (docstatus 0) JE for accountant review; not submitted
  verify_after   -- read-only reconciliation after a correction has been applied
  apply          -- submit the correction; REQUIRES confirm="<amount>:APPROVED"

Guardrails (all modes that write): allowlisted sites only, never site1.local, wrong
company / wrong source vouchers / wrong amount / already-applied / unbalanced-TB all
refuse. Standard Journal Entry controller only; no raw SQL ledger writes; no
credentials printed.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt

OPENING_DATE = "2025-07-01"
EXPECTED_SOURCE = {"MAT-STE-2026-00001", "MAT-STE-2026-00002", "MAT-STE-2026-00003"}
EXPECTED_AMOUNT = 11820700.0
MARKER = "SMJ opening-stock reclassification"
DRAFT_TITLE = "Opening Stock Account Reclassification — Accountant Approval Required"
EQUITY_ACCOUNT_NAME = "Opening Balance Equity"
ALLOWED_SITES = {"staging.local", "financeqa.local", "freshrelease.local"}


class CorrectionRefused(Exception):
	pass


def _guard_site():
	site = frappe.local.site
	if site == "site1.local":
		raise CorrectionRefused("refusing: site1.local is protected")
	if site not in ALLOWED_SITES:
		raise CorrectionRefused(f"refusing: {site!r} is not an allowlisted correction site {sorted(ALLOWED_SITES)}")


def _context() -> dict:
	company = frappe.get_all("Company", pluck="name")[0]
	return {
		"company": company,
		"sa_account": frappe.db.get_value("Company", company, "stock_adjustment_account"),
		"equity_account": frappe.db.get_value(
			"Account", {"company": company, "account_name": EQUITY_ACCOUNT_NAME}, "name"),
	}


def _opening_amount(ctx) -> tuple[float, list[str]]:
	rows = frappe.db.sql(
		"""SELECT voucher_no, ROUND(SUM(credit-debit),2) AS net FROM `tabGL Entry`
		   WHERE account=%s AND is_cancelled=0 AND voucher_type='Stock Entry' AND posting_date<=%s
		   GROUP BY voucher_no""", (ctx["sa_account"], OPENING_DATE), as_dict=True)
	vouchers = sorted({r["voucher_no"] for r in rows if flt(r["net"]) != 0})
	return round(sum(flt(r["net"]) for r in rows), 2), vouchers


def _totals(company) -> dict:
	income = frappe.db.sql("""SELECT ROUND(SUM(gle.credit-gle.debit),2) FROM `tabGL Entry` gle
		JOIN `tabAccount` a ON a.name=gle.account WHERE gle.company=%s AND gle.is_cancelled=0 AND a.root_type='Income'""", company)[0][0] or 0
	expense = frappe.db.sql("""SELECT ROUND(SUM(gle.debit-gle.credit),2) FROM `tabGL Entry` gle
		JOIN `tabAccount` a ON a.name=gle.account WHERE gle.company=%s AND gle.is_cancelled=0 AND a.root_type='Expense'""", company)[0][0] or 0
	td, tc = frappe.db.sql("""SELECT ROUND(SUM(debit),2),ROUND(SUM(credit),2) FROM `tabGL Entry`
		WHERE company=%s AND is_cancelled=0""", company)[0]
	return {"income": flt(income), "expense": flt(expense), "profit": round(flt(income) - flt(expense), 2),
	        "trial_debit": flt(td), "trial_credit": flt(tc), "balanced": abs(flt(td) - flt(tc)) < 0.01}


def _applied_je(ctx, docstatus=1) -> str | None:
	return frappe.db.get_value("Journal Entry",
		{"company": ctx["company"], "user_remark": ["like", f"%{MARKER}%"], "docstatus": docstatus}, "name")


def _validate(ctx, require_amount=True) -> tuple[float, list[str]]:
	if not ctx["sa_account"] or not ctx["equity_account"]:
		raise CorrectionRefused("required accounts missing")
	if frappe.db.get_value("Account", ctx["sa_account"], "root_type") != "Expense":
		raise CorrectionRefused("stock adjustment account is not Expense")
	if frappe.db.get_value("Account", ctx["equity_account"], "root_type") != "Equity":
		raise CorrectionRefused("target account is not Equity")
	amount, vouchers = _opening_amount(ctx)
	if amount <= 0:
		raise CorrectionRefused("no opening-stock credit found; nothing to correct")
	if not EXPECTED_SOURCE.issubset(set(vouchers)):
		raise CorrectionRefused(f"expected source vouchers {sorted(EXPECTED_SOURCE)} not all present: {vouchers}")
	if require_amount and abs(amount - EXPECTED_AMOUNT) > 0.01:
		raise CorrectionRefused(f"amount {amount} != expected {EXPECTED_AMOUNT}; refusing")
	before = _totals(ctx["company"])
	if not before["balanced"]:
		raise CorrectionRefused("Trial Balance is not balanced before correction; refusing")
	return amount, vouchers


def _build_je(ctx, amount, submit: bool):
	je = frappe.get_doc({
		"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": ctx["company"],
		"posting_date": OPENING_DATE, "title": DRAFT_TITLE,
		"user_remark": f"{MARKER}: move opening inventory offset from Stock Adjustment (Expense) "
		               f"to Opening Balance Equity so the P&L is not overstated. Accountant approval required.",
		"accounts": [
			{"account": ctx["sa_account"], "debit_in_account_currency": amount, "credit_in_account_currency": 0},
			{"account": ctx["equity_account"], "debit_in_account_currency": 0, "credit_in_account_currency": amount},
		],
	})
	je.insert(ignore_permissions=True)
	if submit:
		je.submit()
	return je


def inspect() -> dict:
	frappe.set_user("Administrator")
	ctx = _context()
	amount, vouchers = _opening_amount(ctx)
	result = {
		"mode": "inspect", "site": frappe.local.site, "company": ctx["company"],
		"from_account": ctx["sa_account"], "to_account": ctx["equity_account"],
		"opening_amount": amount, "expected_amount": EXPECTED_AMOUNT, "source_vouchers": vouchers,
		"already_submitted": _applied_je(ctx, 1), "existing_draft": _applied_je(ctx, 0),
		"totals": _totals(ctx["company"]),
		"correctable": bool(amount > 0 and EXPECTED_SOURCE.issubset(set(vouchers)) and not _applied_je(ctx, 1)),
	}
	print(json.dumps(result, indent=1, default=str))
	return result


def dry_run() -> dict:
	frappe.set_user("Administrator")
	_guard_site()
	ctx = _context()
	if _applied_je(ctx, 1):
		return _print({"mode": "dry_run", "status": "already_applied", "je": _applied_je(ctx, 1)})
	amount, vouchers = _validate(ctx)
	before = _totals(ctx["company"])
	sp = "osc_dry_run"
	frappe.db.savepoint(sp)
	try:
		je = _build_je(ctx, amount, submit=True)
		after = _totals(ctx["company"])
		je_name = je.name
	finally:
		frappe.db.rollback(save_point=sp)
	return _print({
		"mode": "dry_run", "status": "reconciled", "amount": amount, "source_vouchers": vouchers,
		"before": before, "after": after, "profit_reduced_by": round(before["profit"] - after["profit"], 2),
		"balanced_before": before["balanced"], "balanced_after": after["balanced"],
		"persisted": False, "would_be_je": je_name,
	})


def prepare_draft() -> dict:
	"""Create a real DRAFT Journal Entry for accountant review. Not submitted."""
	frappe.set_user("Administrator")
	_guard_site()
	ctx = _context()
	if _applied_je(ctx, 1):
		return _print({"mode": "prepare_draft", "status": "already_applied", "je": _applied_je(ctx, 1)})
	existing = _applied_je(ctx, 0)
	if existing:
		return _print({"mode": "prepare_draft", "status": "draft_exists", "je": existing})
	amount, vouchers = _validate(ctx)
	je = _build_je(ctx, amount, submit=False)
	frappe.db.commit()
	return _print({
		"mode": "prepare_draft", "status": "draft_created", "je": je.name, "docstatus": je.docstatus,
		"amount": amount, "title": DRAFT_TITLE,
		"note": "Draft only -- an accountant must review and submit it (or run apply with confirmation).",
	})


def verify_after() -> dict:
	frappe.set_user("Administrator")
	ctx = _context()
	je = _applied_je(ctx, 1)
	totals = _totals(ctx["company"])
	amount, _v = _opening_amount(ctx)
	return _print({
		"mode": "verify_after", "submitted_je": je, "totals": totals,
		"residual_opening_credit_on_stock_adjustment": amount,
		"reconciled": bool(je) and totals["balanced"] and abs(amount) < 0.01,
	})


def apply(confirm: str = "") -> dict:
	"""Submit the correction. REQUIRES confirm='<amount>:APPROVED' (accountant sign-off)."""
	frappe.set_user("Administrator")
	_guard_site()
	ctx = _context()
	if _applied_je(ctx, 1):
		return _print({"mode": "apply", "status": "already_applied", "je": _applied_je(ctx, 1)})
	amount, vouchers = _validate(ctx)
	expected_token = f"{int(amount)}:APPROVED"
	if confirm != expected_token:
		raise CorrectionRefused(
			f"apply requires accountant sign-off. Re-run with confirm='{expected_token}' "
			f"only after the accountant has approved the reclassification.")
	before = _totals(ctx["company"])
	# Reuse an existing draft if present, else build+submit.
	draft = _applied_je(ctx, 0)
	if draft:
		je = frappe.get_doc("Journal Entry", draft)
		je.submit()
	else:
		je = _build_je(ctx, amount, submit=True)
	frappe.db.commit()
	after = _totals(ctx["company"])
	return _print({
		"mode": "apply", "status": "applied", "je": je.name, "amount": amount,
		"before_profit": before["profit"], "after_profit": after["profit"],
		"profit_reduced_by": round(before["profit"] - after["profit"], 2),
		"balanced_after": after["balanced"], "reversal": f"cancel Journal Entry {je.name}",
	})


def _print(result: dict) -> dict:
	print(json.dumps(result, indent=1, default=str))
	return result
