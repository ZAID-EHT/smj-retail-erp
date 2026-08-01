"""Give buying operators the same create rights selling operators already have.

Stock ERPNext v15 treats Supplier and Supplier Group as master data restricted to
`Purchase Master Manager`, while the selling side lets `Sales User` create a
Customer. The result is an asymmetry that breaks the Retail ERP buying workflow:
"+ New Supplier" is hidden from every real operator role, and for Administrator it
leads to a form nobody else can save -- which is exactly the "this button does not
work" report.

This patch mirrors the selling side on the buying side. It is idempotent and safe to
re-run: `add_permission` is a no-op when the rule already exists.
"""

from __future__ import annotations

import frappe
from frappe.permissions import add_permission, update_permission_property

# doctype -> roles that should be able to create and maintain it.
# Purchase User is the operator counterpart of Sales User (who can create a
# Customer); Purchase Manager supervises them.
BUYING_MASTERS = {
	"Supplier": ("Purchase User", "Purchase Manager"),
	"Supplier Group": ("Purchase Manager",),
}

GRANTS = ("read", "write", "create")


def execute():
	for doctype, roles in BUYING_MASTERS.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for role in roles:
			if not frappe.db.exists("Role", role):
				continue
			add_permission(doctype, role, 0)
			for permission in GRANTS:
				update_permission_property(doctype, role, 0, permission, 1)
	frappe.clear_cache()
