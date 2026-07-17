"""
Phase 10 -- load/concurrency test using REAL separate OS processes (the
same proven pattern as Phase 4's reservation race test), since Frappe's
frappe.local context is not safe to share across Python threads in one
process -- real Frappe web workers are separate OS processes too, so this
is the correct way to simulate concurrent users, not a workaround.
"""
import time

import frappe
from frappe.utils import flt


COMPANY = "SMJ Retail ERP"


def one_read(worker_id):
    start = time.monotonic()
    rows = frappe.get_all("Sales Order", filters={"docstatus": 1}, limit=50, fields=["name", "grand_total"])
    elapsed = time.monotonic() - start
    print(f"READ_RESULT worker={worker_id} rows={len(rows)} elapsed_ms={round(elapsed * 1000, 1)}")


def one_gl_query(worker_id):
    start = time.monotonic()
    total = frappe.db.sql(
        "select sum(debit), sum(credit) from `tabGL Entry` where company=%s", (COMPANY,)
    )
    elapsed = time.monotonic() - start
    print(f"GL_RESULT worker={worker_id} debit={flt(total[0][0])} credit={flt(total[0][1])} "
          f"elapsed_ms={round(elapsed * 1000, 1)}")


def one_write(worker_id):
    """Concurrent write test: each worker creates and submits a tiny,
    uniquely-tagged Journal Entry to prove writes survive concurrent load
    without corruption or lock timeouts under normal (non-adversarial)
    concurrency."""
    cash = frappe.db.get_value("Account", {"company": COMPANY, "account_name": "Petty Cash"}, "name")
    misc = frappe.db.get_value("Account", {"company": COMPANY, "account_name": "Miscellaneous Expenses"}, "name")
    start = time.monotonic()
    try:
        je = frappe.get_doc({
            "doctype": "Journal Entry", "company": COMPANY, "posting_date": frappe.utils.nowdate(),
            "user_remark": f"SMJ_LOAD_TEST_WORKER_{worker_id}",
            "accounts": [
                {"account": misc, "debit_in_account_currency": 1, "credit_in_account_currency": 0},
                {"account": cash, "debit_in_account_currency": 0, "credit_in_account_currency": 1},
            ],
        })
        je.insert(ignore_permissions=True)
        je.submit()
        frappe.db.commit()
        elapsed = time.monotonic() - start
        print(f"WRITE_RESULT worker={worker_id} name={je.name} elapsed_ms={round(elapsed * 1000, 1)}")
    except Exception as e:
        frappe.db.rollback()
        elapsed = time.monotonic() - start
        print(f"WRITE_RESULT worker={worker_id} name=FAILED error={type(e).__name__}:{e} elapsed_ms={round(elapsed * 1000, 1)}")


def cleanup_load_test_writes():
    frappe.set_user("Administrator")
    names = frappe.get_all("Journal Entry", filters={"user_remark": ["like", "SMJ_LOAD_TEST_WORKER_%"]}, pluck="name")
    for name in names:
        doc = frappe.get_doc("Journal Entry", name)
        if doc.docstatus == 1:
            doc.cancel()
        frappe.delete_doc("Journal Entry", name, ignore_permissions=True, force=True)
    frappe.db.commit()
    print(f"CLEANUP_OK removed={len(names)}")
