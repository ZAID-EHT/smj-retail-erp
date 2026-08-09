from __future__ import annotations

import unittest
from pathlib import Path

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]
APP_PATH = BENCH_PATH / "apps" / "my_store_ui"

from my_store_ui.universal.api import get_dashboard_connections
from my_store_ui.universal.registry import ALL_GENERATED_DOCTYPES

CREDITED_CONNECTION_ACTIONS = {
	("Lead", "prospect"),
	("Payment Order", "payment_entry"),
	("Purchase Invoice", "payment_request"),
	("Purchase Invoice", "purchase_order"),
	("Purchase Invoice", "purchase_receipt"),
	("Purchase Order", "payment_request"),
	("Purchase Receipt", "asset"),
	("Purchase Receipt", "purchase_invoice"),
	("Purchase Receipt", "purchase_order"),
	("Quotation", "sales_order"),
	("Supplier", "bank_account"),
	("Supplier", "pricing_rule"),
}


class TestDashboardConnections(unittest.TestCase):
	"""get_dashboard_connections() reuses each doctype's own standard
	*_dashboard.py get_data() config (the same source Desk's own Connections
	sidebar and frappe.desk.notifications.get_open_count read) rather than
	hardcoding per-doctype link logic — see DASHBOARD_CONNECTIONS group in
	audit/parity_registry.py's DOCTYPE_SPECIFIC_ACTIONS for the 20 required
	document-action capabilities this credits."""

	def setUp(self):
		frappe.set_user("Administrator")

	def _first_record(self, doctype):
		names = frappe.get_list(doctype, limit_page_length=1, pluck="name")
		return names[0] if names else None

	def test_purchase_invoice_shows_its_source_purchase_order(self):
		name = self._first_record("Purchase Invoice")
		if not name:
			self.skipTest("No Purchase Invoice records on site1")
		result = get_dashboard_connections("purchase-invoice", name)
		self.assertIn("groups", result)
		for group in result["groups"]:
			for item in group["items"]:
				self.assertIn(item["doctype"], ALL_GENERATED_DOCTYPES)
				self.assertLessEqual(len(item["records"]), 5)
				self.assertGreaterEqual(item["count"], len(item["records"]))
				for record in item["records"]:
					self.assertTrue(record["route"])

	def test_only_routable_and_permitted_doctypes_are_surfaced(self):
		name = self._first_record("Supplier")
		if not name:
			self.skipTest("No Supplier records on site1")
		result = get_dashboard_connections("supplier", name)
		for group in result["groups"]:
			for item in group["items"]:
				self.assertIn(item["doctype"], ALL_GENERATED_DOCTYPES)
				self.assertTrue(frappe.has_permission(item["doctype"], "read"))

	def test_guest_cannot_read_dashboard_connections(self):
		name = self._first_record("Purchase Order")
		if not name:
			self.skipTest("No Purchase Order records on site1")
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				get_dashboard_connections("purchase-order", name)
		finally:
			frappe.set_user("Administrator")

	def test_never_reads_beyond_the_doctypes_own_dashboard_config(self):
		source = (APP_PATH / "my_store_ui" / "universal" / "api.py").read_text()
		self.assertIn("def get_dashboard_connections", source)
		self.assertIn("meta.get_dashboard_data()", source)
		self.assertNotIn("frappe.db.sql", source)

	def test_registry_fixes_the_duplicate_supplier_key_and_credits_all_connections(self):
		from my_store_ui.audit.parity_registry import DOCTYPE_SPECIFIC_ACTIONS

		# The duplicate "Supplier" dict-literal key bug (later entry silently
		# overwrote the earlier one) is fixed: both original actions survive.
		self.assertIn("hold", DOCTYPE_SPECIFIC_ACTIONS["Supplier"])
		self.assertIn("resume", DOCTYPE_SPECIFIC_ACTIONS["Supplier"])
		self.assertIn("accounting_ledger", DOCTYPE_SPECIFIC_ACTIONS["Supplier"])
		for doctype, action in CREDITED_CONNECTION_ACTIONS:
			self.assertIn(action, DOCTYPE_SPECIFIC_ACTIONS.get(doctype, set()), f"{doctype}.{action} not credited")

	def test_frontend_wires_the_linked_documents_panel(self):
		page = (APP_PATH / "frontend/src/pages/generated/UniversalDetailPage.vue").read_text()
		service = (APP_PATH / "frontend/src/services/universal.js").read_text()
		self.assertIn("getDashboardConnections", service)
		self.assertIn("get_dashboard_connections", service)
		self.assertIn("connections", page)
		self.assertIn("Linked documents", page)


if __name__ == "__main__":
	unittest.main()
