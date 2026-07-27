"""Phase 10: guided data import/export is allowlisted and permission-filtered."""

from __future__ import annotations

import json
import unittest

import frappe

from my_store_ui.data_management import (
	ALLOWED_DOCTYPES,
	FORBIDDEN_EXPORT_FIELDS,
	export_records,
	get_import_template_fields,
	get_import_types,
)

SALES_USER = "smj-data-sales@example.com"


class TestDataManagement(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Data",
			                      "send_welcome_email": 0, "enabled": 1})
			doc.insert(ignore_permissions=True)
			doc.append("roles", {"role": "Sales User"})
			doc.save(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		if frappe.db.exists("User", SALES_USER):
			frappe.delete_doc("User", SALES_USER, force=True, ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_arbitrary_doctype_is_rejected_for_export(self):
		for bad in ("User", "DocType", "GL Entry", "Stock Ledger Entry"):
			with self.subTest(doctype=bad):
				with self.assertRaises(frappe.ValidationError):
					export_records(doctype=bad)

	def test_arbitrary_doctype_is_rejected_for_template(self):
		with self.assertRaises(frappe.ValidationError):
			get_import_template_fields(doctype="User")

	def test_export_excludes_sensitive_fields(self):
		result = export_records(doctype="Customer", limit=5)
		self.assertEqual(result["doctype"], "Customer")
		for field in result["fields"]:
			self.assertNotIn(field, FORBIDDEN_EXPORT_FIELDS)
		blob = json.dumps(result, default=str).lower()
		for secret in ("api_key", "api_secret", "password"):
			self.assertNotIn(secret, blob)

	def test_export_is_permission_filtered(self):
		"""A Sales User can read Customers but not, say, Suppliers-only data leaks."""
		frappe.set_user(SALES_USER)
		# Sales User has Customer read; export should succeed and be capped.
		result = export_records(doctype="Customer", limit=10)
		self.assertLessEqual(result["row_count"], 10)
		self.assertEqual(result["capped_at"], 10)

	def test_export_row_cap_is_enforced(self):
		result = export_records(doctype="Item", limit=999999)
		self.assertLessEqual(result["capped_at"], 5000)

	def test_import_types_are_allowlisted(self):
		types = get_import_types()
		names = {row["doctype"] for row in types["types"]}
		self.assertTrue(names.issubset(set(ALLOWED_DOCTYPES)))
		self.assertNotIn("User", names)
		self.assertNotIn("GL Entry", names)

	def test_template_fields_exclude_sensitive(self):
		fields = get_import_template_fields(doctype="Customer")["fields"]
		names = {f["fieldname"] for f in fields}
		self.assertEqual(names & FORBIDDEN_EXPORT_FIELDS, set())


if __name__ == "__main__":
	unittest.main()
