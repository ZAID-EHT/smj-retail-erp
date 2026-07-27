"""Phase 8: printing overview + preview are gated and permission-safe."""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.printing_admin import (
	PRINTABLE_DOCTYPES,
	get_preview_candidates,
	get_printing_overview,
	preview_document,
)

SALES_USER = "smj-print-sales@example.com"


class TestPrintingAdmin(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			doc = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "SMJ Print",
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

	def test_overview_is_manager_only(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			get_printing_overview()

	def test_overview_lists_formats_for_wholesale_documents(self):
		overview = get_printing_overview()
		doctypes = {row["doctype"] for row in overview["formats_by_doctype"]}
		self.assertIn("Sales Invoice", doctypes)
		self.assertIn("Purchase Order", doctypes)
		for row in overview["formats_by_doctype"]:
			self.assertIn(row["doctype"], PRINTABLE_DOCTYPES)

	def test_preview_rejects_non_printable_doctype(self):
		with self.assertRaises(frappe.ValidationError):
			preview_document(doctype="User", name="Administrator")

	def test_preview_rejects_missing_document(self):
		with self.assertRaises(frappe.DoesNotExistError):
			preview_document(doctype="Sales Invoice", name="NO-SUCH-INVOICE-XYZ")

	def test_preview_renders_when_a_document_exists(self):
		candidate = frappe.get_all("Sales Invoice", pluck="name", limit_page_length=1)
		if not candidate:
			self.skipTest("no Sales Invoice on this site to preview")
		result = preview_document(doctype="Sales Invoice", name=candidate[0])
		self.assertIn("html", result)
		self.assertTrue(result["html"])

	def test_preview_candidates_are_manager_only(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			get_preview_candidates(doctype="Sales Invoice")


if __name__ == "__main__":
	unittest.main()
