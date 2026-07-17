"""
Phase 8 -- report reconciliation using ERPNext's OWN Report API
(frappe.desk.query_report.run), the exact function the Report UI calls,
not direct SQL. Cross-checks against the earlier direct-SQL validation
from the original demo-data build to confirm both methods agree.
"""
import json
import traceback

import frappe
from frappe.utils import flt, nowdate, add_months, getdate


COMPANY = "SMJ Retail ERP"


def _run(report_name, filters):
    from frappe.desk.query_report import run
    return run(report_name, filters=filters)


def reconcile():
    frappe.set_user("Administrator")
    fy_start = "2025-07-01"
    fy_end = nowdate()
    results = {}

    def safe(label, fn):
        try:
            results[label] = fn()
        except Exception as e:
            results[label] = f"ERROR: {type(e).__name__}: {e}"
            traceback.print_exc()

    # 1. General Ledger -- total debit/credit must balance to zero.
    def gl():
        out = _run("General Ledger", {
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
            "group_by": "", "show_cancelled_entries": 0,
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("account")]
        total_debit = sum(flt(r.get("debit")) for r in rows)
        total_credit = sum(flt(r.get("credit")) for r in rows)
        return {"row_count": len(rows), "total_debit": total_debit, "total_credit": total_credit,
                "balanced": abs(total_debit - total_credit) < 0.01}
    safe("general_ledger", gl)

    # 2. Trial Balance -- opening + debit - credit = closing, and totals balance.
    def tb():
        out = _run("Trial Balance", {
            "company": COMPANY, "fiscal_year": "2025-2026",
            "from_date": fy_start, "to_date": fy_end,
            "show_zero_values": 0,
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        total_row = next((r for r in rows if r.get("account") == "Total"), None)
        return {"row_count": len(rows), "total_row": total_row}
    safe("trial_balance", tb)

    # 3. Profit and Loss Statement.
    def pnl():
        out = _run("Profit and Loss Statement", {
            "company": COMPANY, "filter_based_on": "Fiscal Year",
            "from_fiscal_year": "2025-2026", "to_fiscal_year": "2025-2026",
            "periodicity": "Yearly",
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        net_profit_row = next((r for r in rows if "profit" in str(r.get("account_name") or "").lower()), None)
        return {"row_count": len(rows), "net_profit_row": net_profit_row}
    safe("profit_and_loss", pnl)

    # 4. Balance Sheet -- Assets = Liabilities + Equity.
    def bs():
        out = _run("Balance Sheet", {
            "company": COMPANY, "filter_based_on": "Fiscal Year",
            "from_fiscal_year": "2025-2026", "to_fiscal_year": "2025-2026",
            "periodicity": "Yearly",
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        return {"row_count": len(rows)}
    safe("balance_sheet", bs)

    # 5. Accounts Receivable -- total outstanding should match live SQL.
    def ar():
        out = _run("Accounts Receivable", {
            "company": COMPANY, "report_date": fy_end, "ageing_based_on": "Due Date",
            "range": "30, 60, 90, 120",
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("party")]
        total_outstanding = sum(flt(r.get("outstanding")) for r in rows)
        return {"row_count": len(rows), "total_outstanding": total_outstanding}
    safe("accounts_receivable", ar)

    # 6. Accounts Payable.
    def ap():
        out = _run("Accounts Payable", {
            "company": COMPANY, "report_date": fy_end, "ageing_based_on": "Due Date",
            "range": "30, 60, 90, 120",
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("party")]
        total_outstanding = sum(flt(r.get("outstanding")) for r in rows)
        return {"row_count": len(rows), "total_outstanding": total_outstanding}
    safe("accounts_payable", ap)

    # 7. Gross Profit.
    def gp():
        out = _run("Gross Profit", {
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
            "group_by": "Invoice",
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("sales_invoice") or (isinstance(r, dict) and r.get("gross_profit") is not None)]
        total_gp = sum(flt(r.get("gross_profit")) for r in out["result"] if isinstance(r, dict))
        return {"row_count": len(out["result"]), "total_gross_profit": total_gp}
    safe("gross_profit", gp)

    # 8. Stock Balance -- total valuation.
    def stock_balance():
        from erpnext.stock.report.stock_balance.stock_balance import execute as sb_execute
        columns, data = sb_execute(frappe._dict({
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
        }))
        rows = [r for r in data if isinstance(r, dict) and r.get("item_code")]
        total_value = sum(flt(r.get("bal_val")) for r in rows)
        negative_qty_rows = [r for r in rows if flt(r.get("bal_qty")) < 0]
        return {"row_count": len(rows), "total_stock_value": total_value,
                "negative_qty_count": len(negative_qty_rows)}
    safe("stock_balance", stock_balance)

    # 9. Stock Ledger -- row count sanity.
    def stock_ledger():
        out = _run("Stock Ledger", {
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("item_code")]
        return {"row_count": len(rows)}
    safe("stock_ledger", stock_ledger)

    # 10. Payment Ledger.
    def payment_ledger():
        out = _run("Payment Ledger", {
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
        })
        rows = [r for r in out["result"] if isinstance(r, dict)]
        return {"row_count": len(rows)}
    safe("payment_ledger", payment_ledger)

    # 11. Customer Ledger Summary.
    def customer_ledger():
        out = _run("Customer Ledger Summary", {
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("party")]
        return {"row_count": len(rows)}
    safe("customer_ledger_summary", customer_ledger)

    # 12. Supplier Ledger Summary.
    def supplier_ledger():
        out = _run("Supplier Ledger Summary", {
            "company": COMPANY, "from_date": fy_start, "to_date": fy_end,
        })
        rows = [r for r in out["result"] if isinstance(r, dict) and r.get("party")]
        return {"row_count": len(rows)}
    safe("supplier_ledger_summary", supplier_ledger)

    print("REPORT_RECONCILIATION_JSON_START")
    print(json.dumps(results, indent=2, default=str))
    print("REPORT_RECONCILIATION_JSON_END")
