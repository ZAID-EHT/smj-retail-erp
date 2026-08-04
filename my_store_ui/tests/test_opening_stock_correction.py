"""Guardrails and reconciliation for the opening-stock correction package.

Runs only inspect/dry_run (savepoint-rolled-back) and the refusal paths -- it never
submits or persists a correction, so staging books are untouched by the test.
"""

from __future__ import annotations

import pathlib
import unittest

import frappe

from my_store_ui.finance import opening_stock_correction as osc

PACKAGE = (pathlib.Path(frappe.get_app_path("my_store_ui")).parent
           / "docs" / "finance" / "SMJ_OPENING_STOCK_FINAL_ACCOUNTANT_PACKAGE.md")

# Published in July 2026 documents, correct then, stale now. Kept by name so the
# suite fails loudly if it ever creeps back in as the figure of record.
SUPERSEDED_PROFIT_FIGURE = "4,048,006"


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


class TestAccountantPackageStaysTruthful(unittest.TestCase):
	"""The package an accountant signs must agree with the ledger it describes.

	A correction package is only worth signing if its headline figure still matches
	the books. The July 2026 documents published 4,048,006 and were correct at the
	time; further trading moved profit before anyone noticed, and the number aged
	into something an accountant could have reconciled against and failed. These
	tests make that failure mode loud instead of silent.
	"""

	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.on_staging = frappe.local.site == "staging.local"

	def test_package_exists(self):
		self.assertTrue(PACKAGE.exists(), f"missing accountant package at {PACKAGE}")

	def test_correction_reduces_profit_by_exactly_the_correction_amount(self):
		"""The invariant that holds no matter how the underlying data moves."""
		if not self.on_staging:
			self.skipTest("needs staging.local")
		result = osc.dry_run()
		if result.get("status") == "already_applied":
			self.skipTest("correction already applied")
		delta = round(result["before"]["profit"] - result["after"]["profit"], 2)
		self.assertEqual(delta, osc.EXPECTED_AMOUNT)
		self.assertEqual(result["profit_reduced_by"], osc.EXPECTED_AMOUNT)

	def test_correction_moves_no_stock(self):
		"""A reclassification Journal Entry must never touch the stock ledger."""
		if not self.on_staging:
			self.skipTest("needs staging.local")
		before = frappe.db.count("Stock Ledger Entry", {"is_cancelled": 0})
		result = osc.dry_run()
		if result.get("status") == "already_applied":
			self.skipTest("correction already applied")
		self.assertEqual(frappe.db.count("Stock Ledger Entry", {"is_cancelled": 0}), before)

	def test_package_quotes_the_live_post_correction_profit(self):
		"""If trading moves profit again, this fails and the package gets re-measured."""
		if not self.on_staging:
			self.skipTest("needs staging.local")
		result = osc.dry_run()
		if result.get("status") == "already_applied":
			self.skipTest("correction already applied")
		text = PACKAGE.read_text(encoding="utf-8")
		expected = f"{result['after']['profit']:,.2f}"
		self.assertIn(
			expected, text,
			f"the accountant package no longer quotes the measured post-correction "
			f"profit {expected}; re-measure and reissue it before anyone signs it")

	def test_package_does_not_present_the_superseded_figure_as_current(self):
		"""The old number may be named as superseded, never offered as the answer."""
		text = PACKAGE.read_text(encoding="utf-8")
		if SUPERSEDED_PROFIT_FIGURE not in text:
			return
		self.assertIn(
			"out of date", text.lower(),
			"the package mentions the superseded profit figure without marking it stale")
		self.assertIn("Do not approve against", text)


if __name__ == "__main__":
	unittest.main()
