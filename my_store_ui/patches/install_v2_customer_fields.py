"""Customer fields added by the second round of form changes.

VAT No sits beside BR No as another registration number the customer is known by.
Assigned Sales Person names the individual behind the customer, next to the sales
manager who identifies the commission-carrying team -- the person is who the
customer deals with, the manager is who the split is paid through.

Idempotent: `create_custom_fields` upserts, so re-running this patch is safe.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOMER_FIELDS = [
	{
		"fieldname": "custom_vat_no", "label": "VAT No", "fieldtype": "Data",
		"insert_after": "custom_br_no", "in_standard_filter": 1,
		"description": "The customer's VAT registration number.",
	},
	{
		"fieldname": "custom_assigned_sales_person", "label": "Assigned Sales Person",
		"fieldtype": "Link", "options": "Sales Person",
		"insert_after": "custom_commission_rate", "in_standard_filter": 1,
		"description": "The sales person who handles this customer. Assigned by a Sales "
		               "Manager or System Manager only.",
	},
]


def execute() -> None:
	create_custom_fields({"Customer": CUSTOMER_FIELDS}, ignore_validate=True)
	frappe.clear_cache()
