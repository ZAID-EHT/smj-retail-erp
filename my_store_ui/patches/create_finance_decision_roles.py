"""Create the finance-decision roles before any DocType references them.

`Retail Accountant` and `Retail Finance Verifier` exist so that "the accountant" is a
real, grantable identity. Without them the only way to express "an accountant approved
this" is to let a System Manager assert it, which is precisely the segregation failure
the decision workflow is meant to prevent.

Runs in `pre_model_sync` because `Retail Accountant Decision` lists both roles in its
permissions, and a DocPerm row cannot link to a Role that does not exist yet.

Idempotent: an existing role is left exactly as the site configured it.
"""

from __future__ import annotations

import frappe

# desk_access=0 keeps these out of the Frappe desk. They are permission identities
# for the Retail ERP frontend, not a second admin UI.
ROLES = (
	{
		"role_name": "Retail Accountant",
		"desk_access": 0,
	},
	{
		"role_name": "Retail Finance Verifier",
		"desk_access": 0,
	},
)


def execute():
	for spec in ROLES:
		if frappe.db.exists("Role", spec["role_name"]):
			continue
		doc = frappe.new_doc("Role")
		doc.role_name = spec["role_name"]
		doc.desk_access = spec["desk_access"]
		doc.insert(ignore_permissions=True)
	frappe.clear_cache()
