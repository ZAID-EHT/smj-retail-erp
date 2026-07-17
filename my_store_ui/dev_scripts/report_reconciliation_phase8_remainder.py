"""Phase 8 remainder: Balance Sheet re-balance, Cash Flow, bank reconciliation."""
import json
import traceback

import frappe
from frappe.utils import flt, nowdate

COMPANY = "SMJ Retail ERP"


def _run(report_name, filters):
    from frappe.desk.query_report import run
    return run(report_name, filters=filters)


def check():
    frappe.set_user("Administrator")
    results = {}

    def safe(label, fn):
        try:
            results[label] = fn()
        except Exception as e:
            results[label] = f"ERROR: {type(e).__name__}: {e}"
            traceback.print_exc()

    def balance_sheet():
        out = _run("Balance Sheet", {
            "company": COMPANY, "filter_based_on": "Fiscal Year",
            "from_fiscal_year": "2025-2026", "to_fiscal_year": "2025-2026",
            "periodicity": "Yearly",
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        summary = [{"account_name": r.get("account_name"), "total": r.get("total")} for r in rows]
        assets = next((r.get("total") for r in rows if r.get("account_name") == "'Total Assets'"), None)
        liab = next((r.get("total") for r in rows if r.get("account_name") == "'Total Liabilities'"), None)
        eq = next((r.get("total") for r in rows if r.get("account_name") == "'Total Equity'"), None)
        return {"row_count": len(rows), "all_rows_summary": summary,
                "total_assets": assets, "total_liabilities": liab, "total_equity": eq}
    safe("balance_sheet", balance_sheet)

    def cash_flow():
        out = _run("Cash Flow", {
            "company": COMPANY, "filter_based_on": "Fiscal Year",
            "from_fiscal_year": "2025-2026", "to_fiscal_year": "2025-2026",
            "periodicity": "Yearly",
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        summary = [{"account_name": r.get("account_name"), "total": r.get("total")} for r in rows]
        return {"row_count": len(rows), "all_rows_summary": summary}
    safe("cash_flow", cash_flow)

    def bank_reconciliation_statement():
        bank_account = frappe.db.get_value(
            "Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name"
        )
        out = _run("Bank Reconciliation Statement", {
            "company": COMPANY, "account": bank_account, "report_date": nowdate(),
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        return {"bank_account": bank_account, "row_count": len(rows), "rows": rows[:5]}
    safe("bank_reconciliation_statement", bank_reconciliation_statement)

    def bank_clearance_summary():
        out = _run("Bank Clearance Summary", {
            "company": COMPANY, "from_date": "2025-07-01", "to_date": nowdate(),
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        return {"row_count": len(rows)}
    safe("bank_clearance_summary", bank_clearance_summary)

    print("PHASE8_REMAINDER_JSON_START")
    print(json.dumps(results, indent=2, default=str))
    print("PHASE8_REMAINDER_JSON_END")
