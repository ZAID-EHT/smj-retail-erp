"""Custom fields linking Customers and Sales Orders to a Retail Sales Team.

The transaction fields are a historical snapshot: they are written once, when the
document is raised, and never re-read from the master. Reassigning a customer to a
different team later therefore cannot rewrite an order that already exists.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOMER_FIELDS = [
	{"fieldname": "custom_sales_section", "label": "Sales Assignment", "fieldtype": "Section Break",
	 "insert_after": "custom_credit_days"},
	{"fieldname": "custom_sales_team", "label": "Assigned Sales Team", "fieldtype": "Link",
	 "options": "Retail Sales Team", "insert_after": "custom_sales_section",
	 "in_standard_filter": 1,
	 "description": "Drives the sales team and commission split used on new transactions."},
]

SNAPSHOT_FIELDS = [
	{"fieldname": "custom_sales_team_section", "label": "Sales Team and Commission",
	 "fieldtype": "Section Break", "insert_after": "sales_team"},
	{"fieldname": "custom_sales_team", "label": "Sales Team", "fieldtype": "Link",
	 "options": "Retail Sales Team", "insert_after": "custom_sales_team_section",
	 "read_only": 1},
	{"fieldname": "custom_sales_team_name", "label": "Sales Team Name", "fieldtype": "Data",
	 "insert_after": "custom_sales_team", "read_only": 1},
	{"fieldname": "custom_sales_manager", "label": "Sales Manager", "fieldtype": "Link",
	 "options": "Sales Person", "insert_after": "custom_sales_team_name", "read_only": 1},
	{"fieldname": "custom_team_commission_rate", "label": "Team Commission Rate",
	 "fieldtype": "Percent", "insert_after": "custom_sales_manager", "read_only": 1},
	{"fieldname": "custom_sales_team_snapshot", "label": "Sales Team Snapshot",
	 "fieldtype": "Long Text", "insert_after": "custom_team_commission_rate",
	 "read_only": 1, "print_hide": 1,
	 "description": "Immutable copy of the team and split at the time this document was raised."},
]

SNAPSHOT_DOCTYPES = ("Sales Order", "Delivery Note", "Sales Invoice")


def execute():
	fields = {"Customer": CUSTOMER_FIELDS}
	for doctype in SNAPSHOT_DOCTYPES:
		if frappe.db.exists("DocType", doctype):
			fields[doctype] = [dict(f) for f in SNAPSHOT_FIELDS]
	create_custom_fields(fields, ignore_validate=True)
	frappe.clear_cache()
