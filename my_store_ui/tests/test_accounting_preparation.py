"""The guarded accounting preparation service: what it refuses to do.

This service exists to be told "no". A general "prepare any accounting" function
that could also submit would be the most dangerous thing in the application, so
the tests that matter are the ones proving it cannot: no submit mode exists, the
protected site is refused even if the allowlist is edited, commission preparation
refuses even when every accountant decision is recorded, and nothing it does
writes a ledger row.

Savepoint + rollback throughout. No document is submitted by any test here.
"""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui.finance import accounting_preparation as prep
from my_store_ui.finance import accountant_decisions as decisions


class PreparationBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.on_staging = frappe.local.site == "staging.local"
		cls.suffix = uuid.uuid4().hex[:6]
		cls.preparer = cls._user("prep", ("System Manager", "Accounts Manager"))
		cls.accountant = cls._user("acct", ("Retail Accountant",))
		cls.outsider = cls._user("outs", ("Sales User",))

	@classmethod
	def _user(cls, tag, roles):
		email = f"smjprep_{tag}_{cls.suffix}@example.com"
		doc = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": f"Prep {tag}",
			"send_welcome_email": 0, "enabled": 1,
		}).insert(ignore_permissions=True)
		for role in roles:
			if frappe.db.exists("Role", role):
				doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)
		return email

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for email in (cls.preparer, cls.accountant, cls.outsider):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		frappe.db.commit()

	def setUp(self):
		self.sp = f"prep_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		# Rollback first: it undoes everything still uncommitted. Cleanup after,
		# because committing before the rollback destroys the savepoint.
		#
		# A mid-test commit (prepare_draft) discards the savepoint entirely, so the
		# rollback itself can fail with "SAVEPOINT does not exist". That is expected
		# for those tests and must not mask the cleanup that follows it.
		try:
			frappe.db.rollback(save_point=self.sp)
		except Exception:
			frappe.db.rollback()
		self._remove_committed_residue()

	@staticmethod
	def _remove_committed_residue():
		"""Delete what a mid-test commit made permanent.

		`osc.prepare_draft()` calls `frappe.db.commit()`. That commit does not only
		persist the draft -- it ends the transaction, so every accountant decision
		the test approved moments earlier is committed too and survives the
		rollback. The first runs of this file left a real draft Journal Entry and
		eighteen Approved decisions on staging that way.

		Approved opening-stock decisions are the more dangerous residue of the two:
		left behind, they would satisfy the preparation guard for real work later.
		"""
		from my_store_ui.finance import opening_stock_correction as osc

		drafts = frappe.get_all(
			"Journal Entry",
			filters={"user_remark": ["like", f"%{osc.MARKER}%"], "docstatus": 0},
			pluck="name",
		)
		leaked = frappe.get_all("Retail Accountant Decision", pluck="name")
		if not drafts and not leaked:
			return
		for name in drafts:
			frappe.delete_doc("Journal Entry", name, force=True, ignore_permissions=True)
		for name in leaked:
			frappe.delete_doc("Retail Accountant Decision", name, force=True,
			                  ignore_permissions=True)
		frappe.db.commit()

	def _record_decisions(self, topics):
		"""Record positively-decided entries with proper segregation."""
		made = []
		for topic in topics:
			frappe.set_user(self.preparer)
			name = decisions.prepare_proposal(topic=topic, company=self.company)["name"]
			frappe.set_user(self.accountant)
			decisions.record_decision(
				name=name, status="Approved", accountant_decision="Approved value",
				accountant_name="R. Perera FCA", evidence_reference="Minute 2026/14")
			made.append(name)
		frappe.set_user("Administrator")
		return made


class TestServiceShape(PreparationBase):
	def test_there_is_no_submit_mode(self):
		"""The single most important assertion in this file."""
		self.assertNotIn("submit", prep.MODES)
		self.assertNotIn("apply", prep.MODES)
		self.assertNotIn("post", prep.MODES)

	def test_modes_are_exactly_the_five_documented_ones(self):
		self.assertEqual(
			set(prep.MODES),
			{"inspect", "dry_run", "prepare_draft", "verify_draft", "cancel_draft"})

	def test_all_three_proposal_types_are_supported(self):
		self.assertEqual(
			set(prep.PROPOSAL_TYPES),
			{prep.OPENING_STOCK, prep.COMMISSION_RECOGNITION, prep.COMMISSION_PAYOUT})

	def test_unknown_proposal_type_is_refused(self):
		with self.assertRaises(prep.PreparationRefused):
			prep.run("Whatever Accounting", prep.INSPECT, company=self.company)

	def test_unknown_mode_is_refused(self):
		with self.assertRaises(prep.PreparationRefused):
			prep.run(prep.OPENING_STOCK, "submit", company=self.company)

	def test_every_proposal_type_declares_required_decisions(self):
		for proposal_type in prep.PROPOSAL_TYPES:
			self.assertTrue(prep.REQUIRED_DECISIONS[proposal_type],
			                f"{proposal_type} requires no accountant decision")

	def test_status_reports_submission_as_unavailable(self):
		frappe.set_user(self.preparer)
		status = prep.preparation_status(company=self.company)
		self.assertFalse(status["submission_available"])
		self.assertIn("no submit mode", status["boundary"])


class TestSiteGuards(PreparationBase):
	def test_protected_site_is_refused(self):
		original = frappe.local.site
		try:
			frappe.local.site = "site1.local"
			with self.assertRaises(prep.PreparationRefused):
				prep._guard_site()
		finally:
			frappe.local.site = original

	def test_protected_site_is_refused_even_if_allowlisted_by_mistake(self):
		"""Belt and braces: the protected check runs before the allowlist check."""
		original_site = frappe.local.site
		original_allowed = set(prep.ALLOWED_SITES)
		try:
			prep.ALLOWED_SITES.add("site1.local")
			frappe.local.site = "site1.local"
			with self.assertRaises(prep.PreparationRefused):
				prep._guard_site()
		finally:
			frappe.local.site = original_site
			prep.ALLOWED_SITES.clear()
			prep.ALLOWED_SITES.update(original_allowed)

	def test_unknown_production_site_is_refused(self):
		original = frappe.local.site
		try:
			frappe.local.site = "smj-production.example"
			with self.assertRaises(prep.PreparationRefused):
				prep._guard_site()
		finally:
			frappe.local.site = original


class TestPermissionGuards(PreparationBase):
	def test_outsider_cannot_inspect(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(prep.PreparationRefused):
			prep.run(prep.OPENING_STOCK, prep.INSPECT, company=self.company)

	def test_outsider_cannot_prepare_a_draft(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(prep.PreparationRefused):
			prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)

	def test_accountant_alone_cannot_prepare_a_draft(self):
		"""Preparing is a preparer's job; deciding is the accountant's."""
		frappe.set_user(self.accountant)
		with self.assertRaises(prep.PreparationRefused):
			prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)

	def test_preparer_may_inspect(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		frappe.set_user(self.preparer)
		result = prep.run(prep.OPENING_STOCK, prep.INSPECT, company=self.company)
		self.assertEqual(result["mode"], "inspect")
		self.assertFalse(result["submitted"])


class TestDecisionGuards(PreparationBase):
	def test_preparation_is_refused_without_recorded_decisions(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		frappe.set_user(self.preparer)
		with self.assertRaises(prep.PreparationRefused) as caught:
			prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)
		self.assertIn("no accountant decision", str(caught.exception))

	def test_inspect_reports_which_decisions_are_missing(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		frappe.set_user(self.preparer)
		result = prep.run(prep.OPENING_STOCK, prep.INSPECT, company=self.company)
		self.assertFalse(result["decisions"]["complete"])
		self.assertTrue(result["decisions"]["missing"])

	def test_a_rejected_decision_does_not_satisfy_the_guard(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		topic = "Opening stock correction: amount"
		frappe.set_user(self.preparer)
		name = decisions.prepare_proposal(topic=topic, company=self.company)["name"]
		frappe.set_user(self.accountant)
		decisions.record_decision(name=name, status="Rejected",
		                          rejection_reason="needs re-measuring")
		frappe.set_user(self.preparer)
		state = prep._decision_state(prep.OPENING_STOCK, self.company)
		self.assertIn(topic, state["missing"])

	def test_decisions_complete_when_all_are_recorded(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		state = prep._decision_state(prep.OPENING_STOCK, self.company)
		self.assertTrue(state["complete"], state["missing"])
		self.assertEqual(len(state["recorded"]),
		                 len(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK]))


class TestCommissionStaysRefused(PreparationBase):
	"""Recording decisions does not write the code that would post."""

	def test_commission_recognition_is_refused_even_with_every_decision_recorded(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.COMMISSION_RECOGNITION])
		frappe.set_user(self.preparer)
		with self.assertRaises(prep.PreparationRefused) as caught:
			prep.run(prep.COMMISSION_RECOGNITION, prep.PREPARE_DRAFT,
			         company=self.company)
		self.assertIn("not implemented", str(caught.exception))

	def test_commission_payout_is_refused_even_with_every_decision_recorded(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.COMMISSION_PAYOUT])
		frappe.set_user(self.preparer)
		with self.assertRaises(prep.PreparationRefused):
			prep.run(prep.COMMISSION_PAYOUT, prep.PREPARE_DRAFT, company=self.company)

	def test_commission_inspect_reports_posting_as_disabled(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		frappe.set_user(self.preparer)
		result = prep.run(prep.COMMISSION_PAYOUT, prep.INSPECT, company=self.company)
		self.assertFalse(result["position"]["posting_enabled"])
		self.assertFalse(result["position"]["preparable"])


class TestDryRunAndDraft(PreparationBase):
	def test_dry_run_persists_nothing(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		before = frappe.db.count("Journal Entry")
		frappe.set_user(self.preparer)
		result = prep.run(prep.OPENING_STOCK, prep.DRY_RUN, company=self.company)
		self.assertFalse(result["persisted"])
		self.assertFalse(result["submitted"])
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.count("Journal Entry"), before)

	def test_dry_run_writes_no_ledger_row(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		gl_before = frappe.db.count("GL Entry")
		sle_before = frappe.db.count("Stock Ledger Entry")
		frappe.set_user(self.preparer)
		prep.run(prep.OPENING_STOCK, prep.DRY_RUN, company=self.company)
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.count("GL Entry"), gl_before)
		self.assertEqual(frappe.db.count("Stock Ledger Entry"), sle_before)

	def test_draft_is_created_unsubmitted_then_cancelled(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		from my_store_ui.finance import opening_stock_correction as osc
		if osc._applied_je(osc._context(), 1):
			self.skipTest("correction already submitted on this site")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		frappe.set_user(self.preparer)
		result = prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)
		self.assertEqual(result["draft"]["status"], "draft_created")
		name = result["draft"]["je"]
		self.assertTrue(name)
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.get_value("Journal Entry", name, "docstatus"), 0)

		frappe.set_user(self.preparer)
		cancelled = prep.run(prep.OPENING_STOCK, prep.CANCEL_DRAFT,
		                     company=self.company, draft=name)
		self.assertEqual(cancelled["cancelled"], name)
		frappe.set_user("Administrator")
		self.assertFalse(frappe.db.exists("Journal Entry", name))

	def test_a_second_draft_is_refused(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		from my_store_ui.finance import opening_stock_correction as osc
		if osc._applied_je(osc._context(), 1):
			self.skipTest("correction already submitted on this site")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		frappe.set_user(self.preparer)
		prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)
		with self.assertRaises(prep.PreparationRefused) as caught:
			prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)
		self.assertIn("already exists", str(caught.exception))

	def test_verify_draft_checks_the_amount_against_the_ledger(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		from my_store_ui.finance import opening_stock_correction as osc
		if osc._applied_je(osc._context(), 1):
			self.skipTest("correction already submitted on this site")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		frappe.set_user(self.preparer)
		prep.run(prep.OPENING_STOCK, prep.PREPARE_DRAFT, company=self.company)
		verified = prep.run(prep.OPENING_STOCK, prep.VERIFY_DRAFT, company=self.company)
		self.assertTrue(verified["amount_agrees_with_ledger"])

	def test_cancel_refuses_when_there_is_no_draft(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		self._record_decisions(prep.REQUIRED_DECISIONS[prep.OPENING_STOCK])
		frappe.set_user(self.preparer)
		with self.assertRaises(prep.PreparationRefused):
			prep.run(prep.OPENING_STOCK, prep.CANCEL_DRAFT, company=self.company,
			         draft="")


class TestBackupGuard(PreparationBase):
	def test_backup_age_is_measured(self):
		if not self.on_staging:
			self.skipTest("needs staging.local")
		age = prep._latest_backup_age_hours()
		self.assertIsNotNone(age, "no backup found; the guard cannot be evaluated")
		self.assertGreaterEqual(age, 0)

	def test_a_stale_backup_is_refused(self):
		original = prep.BACKUP_MAX_AGE_HOURS
		try:
			prep.BACKUP_MAX_AGE_HOURS = -1  # every backup is now "too old"
			with self.assertRaises(prep.PreparationRefused) as caught:
				prep._guard_backup()
			self.assertIn("older than", str(caught.exception))
		finally:
			prep.BACKUP_MAX_AGE_HOURS = original


class TestNoCredentialLeak(PreparationBase):
	def test_refusals_do_not_carry_credentials(self):
		"""A refusal reason is read by users; it must not quote the site config."""
		messages = []
		original = frappe.local.site
		try:
			frappe.local.site = "site1.local"
			try:
				prep._guard_site()
			except prep.PreparationRefused as refused:
				messages.append(str(refused))
		finally:
			frappe.local.site = original
		for message in messages:
			for forbidden in ("password", "db_password", "secret", "token",
			                  "encryption_key"):
				self.assertNotIn(forbidden, message.lower())


if __name__ == "__main__":
	unittest.main()
