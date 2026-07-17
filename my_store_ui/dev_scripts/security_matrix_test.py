"""
Phase 5 -- real backend permission enforcement test.

Creates one dedicated test user per role (System Manager, Sales User,
Sales Manager, Purchase User, Purchase Manager, Stock User, Stock Manager,
Accounts User, Accounts Manager, and a Restricted user with no elevated
roles), then, impersonating each via frappe.set_user(), tests BOTH
frappe.has_permission() (the real function every ERPNext controller/API
uses) AND at least one genuine write attempt per role so this is proof of
enforcement, not just config reading.
"""
import json

import frappe

TEST_USERS = {
    "smj.sysmgr.test@smjretail.local": ["System Manager"],
    "smj.sales.user.test@smjretail.local": ["Sales User"],
    "smj.sales.mgr.test@smjretail.local": ["Sales Manager"],
    "smj.purchase.user.test@smjretail.local": ["Purchase User"],
    "smj.purchase.mgr.test@smjretail.local": ["Purchase Manager"],
    "smj.stock.user.test@smjretail.local": ["Stock User"],
    "smj.stock.mgr.test@smjretail.local": ["Stock Manager"],
    "smj.accounts.user.test@smjretail.local": ["Accounts User"],
    "smj.accounts.mgr.test@smjretail.local": ["Accounts Manager"],
    "smj.restricted.test@smjretail.local": [],
}

DOCTYPE_MATRIX = [
    "Sales Order", "Sales Invoice", "Purchase Order", "Purchase Invoice",
    "Purchase Receipt", "Stock Entry", "Payment Entry", "Journal Entry",
    "GL Entry", "User", "Role",
]
PTYPES = ["read", "write", "create", "submit", "cancel", "delete"]


def setup_users():
    frappe.set_user("Administrator")
    created = []
    for email, roles in TEST_USERS.items():
        if frappe.db.exists("User", email):
            continue
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": email.split(".test@")[0].replace(".", " ").title(),
            "send_welcome_email": 0,
            "user_type": "System User",
            "roles": [{"role": r} for r in roles],
        })
        user.insert(ignore_permissions=True)
        created.append(email)
    frappe.db.commit()
    print(f"USERS_CREATED {json.dumps(created)}")


def has_permission_matrix():
    frappe.set_user("Administrator")
    results = {}
    for email in TEST_USERS:
        frappe.set_user(email)
        row = {}
        for dt in DOCTYPE_MATRIX:
            row[dt] = {}
            for pt in PTYPES:
                try:
                    row[dt][pt] = bool(frappe.has_permission(dt, pt))
                except Exception as e:
                    row[dt][pt] = f"ERROR:{type(e).__name__}"
        results[email] = row
        frappe.set_user("Administrator")
    print("HAS_PERMISSION_MATRIX_JSON_START")
    print(json.dumps(results, indent=2))
    print("HAS_PERMISSION_MATRIX_JSON_END")


def real_write_attempts():
    """Not just has_permission() -- actually try to create/submit documents
    as each restricted persona and confirm the ORM itself blocks it."""
    frappe.set_user("Administrator")
    company = "SMJ Retail ERP"
    customer = frappe.db.get_value("Customer", {"company": company}, "name") or \
        frappe.get_all("Customer", limit=1, pluck="name")[0]
    supplier = frappe.get_all("Supplier", limit=1, pluck="name")[0]
    item = frappe.get_all("Item", filters={"disabled": 0, "is_stock_item": 1}, limit=1, pluck="name")[0]
    warehouse = frappe.db.get_value("Warehouse", {"company": company, "warehouse_name": "Main Warehouse"}, "name")

    outcomes = {}

    def attempt(label, fn):
        frappe.set_user("Administrator")
        try:
            fn()
            outcomes[label] = "SUCCEEDED"
        except frappe.PermissionError as e:
            outcomes[label] = f"BLOCKED (PermissionError): {e}"
        except Exception as e:
            outcomes[label] = f"BLOCKED (other: {type(e).__name__}): {e}"
        finally:
            frappe.set_user("Administrator")

    # Restricted user must NOT be able to create a Sales Order.
    def restricted_tries_sales_order():
        frappe.set_user("smj.restricted.test@smjretail.local")
        doc = frappe.get_doc({
            "doctype": "Sales Order", "customer": customer, "company": company,
            "transaction_date": frappe.utils.nowdate(), "delivery_date": frappe.utils.nowdate(),
            "items": [{"item_code": item, "qty": 1, "rate": 100, "delivery_date": frappe.utils.nowdate()}],
        })
        doc.insert()

    attempt("restricted_user_create_sales_order", restricted_tries_sales_order)

    # Sales User must NOT be able to create a Purchase Order (cross-department boundary).
    def sales_user_tries_purchase_order():
        frappe.set_user("smj.sales.user.test@smjretail.local")
        doc = frappe.get_doc({
            "doctype": "Purchase Order", "supplier": supplier, "company": company,
            "transaction_date": frappe.utils.nowdate(),
            "items": [{"item_code": item, "qty": 1, "rate": 100, "schedule_date": frappe.utils.nowdate(),
                       "warehouse": warehouse}],
        })
        doc.insert()

    attempt("sales_user_create_purchase_order", sales_user_tries_purchase_order)

    # Sales User (not Manager) creating a Sales Order they own should be ALLOWED.
    def sales_user_creates_sales_order():
        frappe.set_user("smj.sales.user.test@smjretail.local")
        doc = frappe.get_doc({
            "doctype": "Sales Order", "customer": customer, "company": company,
            "transaction_date": frappe.utils.nowdate(), "delivery_date": frappe.utils.nowdate(),
            "items": [{"item_code": item, "qty": 1, "rate": 100, "delivery_date": frappe.utils.nowdate()}],
        })
        doc.insert()
        frappe.set_user("Administrator")
        frappe.delete_doc("Sales Order", doc.name, ignore_permissions=True, force=True)
        frappe.db.commit()

    attempt("sales_user_create_own_sales_order", sales_user_creates_sales_order)

    # Purchase User must NOT be able to create a Payment Entry (Accounts territory).
    def purchase_user_tries_payment_entry():
        frappe.set_user("smj.purchase.user.test@smjretail.local")
        doc = frappe.get_doc({
            "doctype": "Payment Entry", "payment_type": "Pay", "party_type": "Supplier",
            "party": supplier, "company": company, "paid_amount": 100, "received_amount": 100,
        })
        doc.insert()

    attempt("purchase_user_create_payment_entry", purchase_user_tries_payment_entry)

    # Restricted user must NOT be able to read the User list / create a new User.
    def restricted_tries_create_user():
        frappe.set_user("smj.restricted.test@smjretail.local")
        doc = frappe.get_doc({
            "doctype": "User", "email": "should.never.exist@smjretail.local",
            "first_name": "Should Not Exist", "user_type": "System User",
        })
        doc.insert()

    attempt("restricted_user_create_user", restricted_tries_create_user)

    # Stock User must NOT be able to directly post a Journal Entry (Accounts territory).
    def stock_user_tries_journal_entry():
        frappe.set_user("smj.stock.user.test@smjretail.local")
        doc = frappe.get_doc({
            "doctype": "Journal Entry", "company": company, "posting_date": frappe.utils.nowdate(),
            "accounts": [],
        })
        doc.insert()

    attempt("stock_user_create_journal_entry", stock_user_tries_journal_entry)

    frappe.set_user("Administrator")
    print("REAL_WRITE_ATTEMPTS_JSON_START")
    print(json.dumps(outcomes, indent=2))
    print("REAL_WRITE_ATTEMPTS_JSON_END")


def cleanup_users():
    frappe.set_user("Administrator")
    removed = []
    for email in TEST_USERS:
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, ignore_permissions=True, force=True)
            removed.append(email)
    frappe.db.commit()
    print(f"USERS_REMOVED {json.dumps(removed)}")
