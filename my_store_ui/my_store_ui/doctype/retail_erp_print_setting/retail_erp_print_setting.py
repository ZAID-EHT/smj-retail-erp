"""Retail ERP print defaults (Single).

Stores only which Print Format Retail ERP should use per document type. ERPNext
Standard formats are never modified -- the selection lives here instead.
"""

from __future__ import annotations

from frappe.model.document import Document


class RetailERPPrintSetting(Document):
	pass
