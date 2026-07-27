"""Guardrails and reconciliation for the opening-stock correction package.

Runs only inspect/dry_run (savepoint-rolled-back) and the refusal paths -- it never
submits or persists a correction, so staging books are untouched by the test.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.finance import opening_stock_correction as osc


class TestOpeningStockCorrection(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.on_staging = frappe.local.site == "staging.local"

	def test_inspect_reports_correctable_situation(self):
		result = osc.inspect()
		self.assertEqual(result["expected_amount"], osc.EXPECTED_AMOUNT)
		if not result["already_submitted"]:
			self.assertTrue(result["correctable"])
			self.assertEqual(result["opening_amount"], osc.EXPECTED_AMOUNT)
			self.assertTrue(set(osc.EXPECTED_SOURCE).issubset(set(result["source_vouchers"])))

	def test_dry_run_reconciles_and_persists_nothing(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		before_je = frappe.db.count("Journal Entry", {"user_remark": ["like", f"%{osc.MARKER}%"]})
		result = osc.dry_run()
		if result.get("status") == "already_applied":
			self.skipTest("correction already applied")
		self.assertEqual(result["status"], "reconciled")
		self.assertEqual(result["profit_reduced_by"], osc.EXPECTED_AMOUNT)
		self.assertTrue(result["balanced_before"])
		self.assertTrue(result["balanced_after"])
		self.assertFalse(result["persisted"])
		# Nothing was persisted.
		after_je = frappe.db.count("Journal Entry", {"user_remark": ["like", f"%{osc.MARKER}%"]})
		self.assertEqual(before_je, after_je)

	def test_apply_without_confirmation_is_refused(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		if osc._applied_je(osc._context(), 1):
			self.skipTest("already applied")
		with self.assertRaises(osc.CorrectionRefused):
			osc.apply(confirm="")
		with self.assertRaises(osc.CorrectionRefused):
			osc.apply(confirm="wrong-token")
		# Still nothing submitted.
		self.assertIsNone(osc._applied_je(osc._context(), 1))

	def test_wrong_site_is_refused(self):
		original = frappe.local.site
		try:
			frappe.local.site = "site1.local"
			with self.assertRaises(osc.CorrectionRefused):
				osc._guard_site()
			frappe.local.site = "some-unknown-prod.local"
			with self.assertRaises(osc.CorrectionRefused):
				osc._guard_site()
		finally:
			frappe.local.site = original

	def test_amount_mismatch_is_refused(self):
		"""If the source amount ever drifts from the expected, validation refuses."""
		original = osc.EXPECTED_AMOUNT
		try:
			osc.EXPECTED_AMOUNT = original + 1  # simulate a drift
			with self.assertRaises(osc.CorrectionRefused):
				osc._validate(osc._context())
		finally:
			osc.EXPECTED_AMOUNT = original


if __name__ == "__main__":
	unittest.main()
