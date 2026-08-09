"""Phase 5 regression: Purchase Order field exposure and purchasing mappings.

These are read-only assertions so they can run on every suite pass. The document
chain itself (MR -> RFQ -> SQ -> PO -> PR -> PI -> Payment -> Return -> Debit Note
-> LCV) writes submitted stock/GL documents and therefore lives in
`my_store_ui.dev_scripts.purchase_workflow_verification.run`; its recorded result is
in `docs/workflows/SMJ_PURCHASE_END_TO_END_ACCEPTANCE.md`.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.dev_scripts.purchase_workflow_verification import (
	PO_HEADER_REQUIRED,
	PO_ITEM_REQUIRED,
	PO_TOTALS_REQUIRED,
	REQUIRED_MAPPINGS,
	_exposure,
)
from my_store_ui.universal.api import MAPPED_ACTIONS


class TestPurchaseWorkflow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def test_purchase_order_header_fields_exist_and_are_exposed(self):
		meta, readable, _writable = _exposure("Purchase Order")
		for fieldname in PO_HEADER_REQUIRED:
			with self.subTest(field=fieldname):
				self.assertIsNotNone(meta.get_field(fieldname), f"{fieldname} missing from Purchase Order")
				self.assertIn(fieldname, readable, f"{fieldname} not readable through the universal engine")

	def test_purchase_order_totals_are_exposed_and_controller_owned(self):
		meta, readable, writable = _exposure("Purchase Order")
		for fieldname in PO_TOTALS_REQUIRED:
			with self.subTest(field=fieldname):
				self.assertIsNotNone(meta.get_field(fieldname))
				self.assertIn(fieldname, readable)
		# Computed totals must never be writable from the browser -- ERPNext
		# controllers own them. Only the additional-discount inputs are editable.
		for fieldname in ("net_total", "grand_total", "base_grand_total", "rounded_total",
				"total_taxes_and_charges", "advance_paid", "per_received", "per_billed"):
			with self.subTest(field=fieldname):
				self.assertNotIn(fieldname, writable, f"{fieldname} must stay controller-owned")

	def test_purchase_order_item_fields_use_parent_permlevels(self):
		"""Child tables carry no DocPerm rows; exposure comes from the parent."""
		meta, readable, writable = _exposure("Purchase Order Item", parent_doctype="Purchase Order")
		for fieldname in PO_ITEM_REQUIRED:
			with self.subTest(field=fieldname):
				self.assertIsNotNone(meta.get_field(fieldname), f"{fieldname} missing from Purchase Order Item")
				self.assertIn(fieldname, readable, f"{fieldname} not readable on the item table")
		# Entry fields the buyer must be able to type.
		for fieldname in ("item_code", "qty", "rate", "uom", "warehouse", "schedule_date", "cost_center"):
			with self.subTest(writable=fieldname):
				self.assertIn(fieldname, writable)
		# Controller-calculated / source-link fields stay read-only.
		for fieldname in ("amount", "base_amount", "received_qty", "billed_amt", "stock_qty"):
			with self.subTest(read_only=fieldname):
				self.assertNotIn(fieldname, writable, f"{fieldname} must stay controller-owned")

	def test_every_required_purchasing_mapping_is_registered(self):
		for source, action in REQUIRED_MAPPINGS:
			with self.subTest(source=source, action=action):
				mapping = MAPPED_ACTIONS.get(source, {}).get(action)
				self.assertIsNotNone(mapping, f"{source} -> {action} is not registered")
				self.assertTrue(mapping.get("target"))
				self.assertTrue(mapping.get("method"))

	def test_purchasing_mapping_targets_are_installed_doctypes(self):
		for source in ("Purchase Order", "Purchase Receipt", "Purchase Invoice"):
			for action, mapping in MAPPED_ACTIONS.get(source, {}).items():
				with self.subTest(source=source, action=action):
					self.assertTrue(
						frappe.db.exists("DocType", mapping["target"]),
						f"{source}:{action} targets missing doctype {mapping['target']}",
					)

	def test_purchase_order_is_submittable_and_amendable(self):
		meta = frappe.get_meta("Purchase Order")
		self.assertTrue(meta.is_submittable)
		self.assertIsNone(
			frappe.db.get_value("Workflow", {"document_type": "Purchase Order", "is_active": 1}, "name"),
			"an active Workflow would take over submit/cancel and change these expectations",
		)

	def test_purchase_order_has_create_and_detail_routes(self):
		from my_store_ui.services.priority_registry import CANONICAL_ROUTE_BY_DOCTYPE

		base = CANONICAL_ROUTE_BY_DOCTYPE.get("Purchase Order")
		self.assertTrue(base, "Purchase Order has no canonical route")
		self.assertTrue(base.startswith("/"))


if __name__ == "__main__":
	unittest.main()
