"""Create/remove a throwaway System Manager for browser verification.

The password is generated per run and printed to stdout only -- it is never
written into a document, a doc file or the repository. Staging only.

    bench --site staging.local execute my_store_ui.dev_scripts.browser_check_user.create
    bench --site staging.local execute my_store_ui.dev_scripts.browser_check_user.remove
"""

import secrets

import frappe

BROWSER_USER = "smj-browser-check@example.com"


def create():
	frappe.set_user("Administrator")
	if frappe.local.site != "staging.local":
		raise RuntimeError(f"refusing to run on {frappe.local.site!r}; staging.local only")
	remove()
	password = f"Smj!{secrets.token_urlsafe(18)}"
	doc = frappe.get_doc({
		"doctype": "User", "email": BROWSER_USER, "first_name": "SMJ Browser Check",
		"send_welcome_email": 0, "enabled": 1, "new_password": password,
	})
	doc.insert(ignore_permissions=True)
	# System Manager is a Frappe role and carries no ERPNext selling/buying rights --
	# a browser check with only that role sees permission-denied everywhere and proves
	# nothing. Give the throwaway user the roles a real operator has.
	for role in ("System Manager", "Sales Manager", "Sales User", "Accounts Manager",
	             "Stock Manager", "Stock User", "Purchase Manager", "Purchase User",
	             "Item Manager"):
		if frappe.db.exists("Role", role):
			doc.append("roles", {"role": role})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	# stdout only, so the browser harness can pick it up without persisting it
	print(f"BROWSER_USER={BROWSER_USER}")
	print(f"BROWSER_PW={password}")


def remove():
	frappe.set_user("Administrator")
	if frappe.db.exists("User", BROWSER_USER):
		frappe.delete_doc("User", BROWSER_USER, force=True, ignore_permissions=True)
		frappe.db.commit()
