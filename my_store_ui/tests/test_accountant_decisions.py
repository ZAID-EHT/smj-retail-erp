"""Accountant Decision Centre: the refusals are the feature.

What is tested here is mostly what the Centre will *not* do — approve without
evidence, reject without a reason, let a preparer approve their own proposal, let a
System Manager stand in for the accountant, or let a decided record be edited. A
decision record that could be filled in freely would be worse than no record at all,
because it would look like approval.

Savepoint + rollback; users created here are removed in tearDownClass.
"""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui.finance.accountant_decisions import (
	AREA_COMMISSION,
	DECISION_DETAIL,
	AREA_OPENING_STOCK,
	CAP_RECORD,
	CAP_SUBMIT_CORRECTION,
	CAPABILITIES,
	CATALOGUE,
	DECISION,
	approved_decision,
	capability_report,
	decision_history,
	get_decision_centre,
	has_capability,
	mark_implemented,
	mark_verified,
	move_to_review,
	prepare_proposal,
	record_decision,
	supersede_decision,
	unresolved_topics,
)

TOPIC_TRIGGER = "Commission: earning trigger"
TOPIC_AMOUNT = "Opening stock correction: amount"


class AccountantDecisionBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.suffix = uuid.uuid4().hex[:6]
		cls.preparer = cls._user("prep", ("System Manager", "Accounts Manager"))
		cls.accountant = cls._user("acct", ("Retail Accountant",))
		# A second accountant, so segregation can be tested without role confusion.
		cls.accountant2 = cls._user("acc2", ("Retail Accountant",))
		cls.verifier = cls._user("veri", ("Retail Finance Verifier",))
		cls.outsider = cls._user("outs", ("Sales User",))

	@classmethod
	def _user(cls, tag, roles):
		email = f"smjdec_{tag}_{cls.suffix}@example.com"
		doc = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": f"Decision {tag}",
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
		for email in (cls.preparer, cls.accountant, cls.accountant2, cls.verifier,
		              cls.outsider):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		frappe.db.commit()

	def setUp(self):
		self.sp = f"dec_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	# -- helpers ------------------------------------------------------

	def _prepare(self, topic=TOPIC_TRIGGER):
		frappe.set_user(self.preparer)
		result = prepare_proposal(topic=topic, company=self.company)
		return result["name"]

	def _approve(self, name, user=None, **over):
		frappe.set_user(user or self.accountant)
		payload = {
			"name": name, "status": "Approved",
			"accountant_decision": "Customer Payment Collection",
			"accountant_name": "R. Perera FCA",
			"evidence_reference": "Board minute 2026/14",
			"effective_date": "2026-09-01",
		}
		payload.update(over)
		return record_decision(**payload)


class TestDecisionCatalogue(AccountantDecisionBase):
	def test_every_catalogue_entry_is_complete(self):
		for entry in CATALOGUE:
			for key in ("area", "topic", "question", "proposal", "why"):
				self.assertTrue((entry.get(key) or "").strip(),
				                f"{entry.get('topic')} is missing {key}")

	def test_catalogue_covers_both_accountant_areas(self):
		areas = {e["area"] for e in CATALOGUE}
		self.assertEqual(areas, {AREA_OPENING_STOCK, AREA_COMMISSION})

	def test_topics_are_unique(self):
		topics = [e["topic"] for e in CATALOGUE]
		self.assertEqual(len(topics), len(set(topics)))

	def test_commission_accounting_questions_are_all_present(self):
		"""The nine choices that decide how commission becomes money."""
		topics = {e["topic"] for e in CATALOGUE if e["area"] == AREA_COMMISSION}
		for required in ("earning trigger", "calculation basis", "expense account",
		                 "payable account", "payee party type", "payout document type",
		                 "payout cycle", "withholding", "tax treatment",
		                 "returns and clawback"):
			self.assertTrue(any(required in t for t in topics),
			                f"no catalogue question covers {required}")

	def test_no_commission_accounting_question_ships_with_a_chosen_answer(self):
		"""Every accounting choice must read as unproposed, not as a default."""
		for entry in CATALOGUE:
			if entry["area"] != AREA_COMMISSION:
				continue
			self.assertIn("Not proposed", entry["proposal"],
			              f"{entry['topic']} ships with an answer the accountant did not give")


class TestCapabilityMatrix(AccountantDecisionBase):
	def test_system_manager_cannot_record_an_accountant_decision(self):
		"""An administrator must not be able to manufacture finance approval."""
		self.assertNotIn("System Manager", CAPABILITIES[CAP_RECORD])
		frappe.set_user(self.preparer)
		self.assertFalse(has_capability(CAP_RECORD))

	def test_nobody_may_submit_an_accounting_correction(self):
		self.assertEqual(CAPABILITIES[CAP_SUBMIT_CORRECTION], ())
		for user in (self.preparer, self.accountant, self.verifier):
			frappe.set_user(user)
			self.assertFalse(has_capability(CAP_SUBMIT_CORRECTION))

	def test_accountant_holds_the_record_capability(self):
		frappe.set_user(self.accountant)
		self.assertTrue(has_capability(CAP_RECORD))

	def test_capability_report_covers_every_capability(self):
		frappe.set_user(self.accountant)
		self.assertEqual(set(capability_report()), set(CAPABILITIES))

	def test_outsider_cannot_read_the_centre(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(frappe.PermissionError):
			get_decision_centre(company=self.company)

	def test_outsider_cannot_prepare_a_proposal(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(frappe.PermissionError):
			prepare_proposal(topic=TOPIC_TRIGGER, company=self.company)


class TestProposalPreparation(AccountantDecisionBase):
	def test_prepared_proposal_starts_unreviewed(self):
		name = self._prepare()
		doc = frappe.get_doc(DECISION, name)
		self.assertEqual(doc.status, "Not Reviewed")
		self.assertEqual(doc.prepared_by, self.preparer)
		self.assertFalse(doc.accountant_decision)
		self.assertFalse(doc.recorded_by)

	def test_preparing_twice_reuses_the_open_proposal(self):
		first = self._prepare()
		frappe.set_user(self.preparer)
		again = prepare_proposal(topic=TOPIC_TRIGGER, company=self.company)
		self.assertFalse(again["created"])
		self.assertEqual(again["name"], first)

	def test_unknown_topic_is_refused(self):
		frappe.set_user(self.preparer)
		with self.assertRaises(frappe.ValidationError):
			prepare_proposal(topic="Whatever the system feels like",
			                 company=self.company)

	def test_review_stages_are_reachable_before_a_decision(self):
		name = self._prepare()
		frappe.set_user(self.preparer)
		self.assertEqual(
			move_to_review(name, "Under Accountant Review")["status"],
			"Under Accountant Review")
		self.assertEqual(
			move_to_review(name, "Information Required", comment="Need the tax ruling")["status"],
			"Information Required")

	def test_a_decision_status_cannot_be_reached_through_the_review_route(self):
		name = self._prepare()
		frappe.set_user(self.preparer)
		with self.assertRaises(frappe.ValidationError):
			move_to_review(name, "Approved")


class TestRecordingDecisions(AccountantDecisionBase):
	def test_accountant_can_approve_with_evidence(self):
		name = self._prepare()
		self._approve(name)
		doc = frappe.get_doc(DECISION, name)
		self.assertEqual(doc.status, "Approved")
		self.assertEqual(doc.accountant_name, "R. Perera FCA")
		self.assertEqual(doc.recorded_by, self.accountant)
		self.assertTrue(doc.recorded_on)

	def test_approval_without_evidence_is_refused(self):
		name = self._prepare()
		with self.assertRaises(frappe.ValidationError):
			self._approve(name, evidence_reference="")

	def test_approval_without_an_accountant_name_is_refused(self):
		name = self._prepare()
		with self.assertRaises(frappe.ValidationError):
			self._approve(name, accountant_name="")

	def test_rejection_without_a_reason_is_refused(self):
		name = self._prepare()
		frappe.set_user(self.accountant)
		with self.assertRaises(frappe.ValidationError):
			record_decision(name=name, status="Rejected", rejection_reason="")

	def test_rejection_with_a_reason_is_recorded(self):
		name = self._prepare()
		frappe.set_user(self.accountant)
		record_decision(name=name, status="Rejected",
		                rejection_reason="Collection basis needs the tax ruling first")
		doc = frappe.get_doc(DECISION, name)
		self.assertEqual(doc.status, "Rejected")
		self.assertIn("tax ruling", doc.rejection_reason)

	def test_preparer_cannot_record_the_decision_on_their_own_proposal(self):
		"""Segregation of duties, enforced server-side rather than by hiding a button."""
		name = self._prepare()
		frappe.set_user(self.preparer)
		with self.assertRaises((frappe.PermissionError, frappe.ValidationError)):
			record_decision(name=name, status="Approved",
			                accountant_decision="Sales Invoice Submission",
			                accountant_name="Self", evidence_reference="none")

	def test_an_accountant_who_prepared_the_proposal_cannot_also_decide_it(self):
		"""The same person holding both roles is still refused on the same record."""
		frappe.set_user("Administrator")
		doc = frappe.new_doc(DECISION)
		doc.company = self.company
		doc.topic_area = AREA_COMMISSION
		doc.topic = TOPIC_TRIGGER
		doc.status = "Not Reviewed"
		doc.prepared_by = self.accountant
		doc.version_no = 1
		doc.insert(ignore_permissions=True)

		frappe.set_user(self.accountant)
		with self.assertRaises(frappe.ValidationError):
			record_decision(name=doc.name, status="Approved",
			                accountant_decision="Sales Invoice Submission",
			                accountant_name="Same Person",
			                evidence_reference="minute 1")

	def test_a_decided_proposal_cannot_be_decided_again(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.accountant2)
		with self.assertRaises(frappe.ValidationError):
			record_decision(name=name, status="Rejected",
			                rejection_reason="changed my mind")

	def test_a_decided_record_is_frozen_against_direct_edits(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user("Administrator")
		doc = frappe.get_doc(DECISION, name)
		doc.accountant_decision = "Something else entirely"
		with self.assertRaises(frappe.ValidationError):
			doc.save(ignore_permissions=True)


class TestSupersedingAndLifecycle(AccountantDecisionBase):
	def test_superseding_keeps_the_original_intact(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.preparer)
		result = supersede_decision(name, reason="Accountant revised the trigger")

		old = frappe.get_doc(DECISION, name)
		new = frappe.get_doc(DECISION, result["name"])
		self.assertEqual(old.status, "Approved")
		self.assertEqual(old.accountant_decision, "Customer Payment Collection")
		self.assertEqual(old.superseded_by, new.name)
		self.assertEqual(new.status, "Not Reviewed")
		self.assertEqual(new.version_no, 2)

	def test_a_superseded_record_cannot_be_superseded_twice(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.preparer)
		supersede_decision(name, reason="first")
		with self.assertRaises(frappe.ValidationError):
			supersede_decision(name, reason="second")

	def test_implementation_requires_an_approved_decision(self):
		name = self._prepare()
		frappe.set_user(self.accountant)
		with self.assertRaises(frappe.ValidationError):
			mark_implemented(name)

	def test_verification_requires_implementation_first(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.verifier)
		with self.assertRaises(frappe.ValidationError):
			mark_verified(name)

	def test_full_lifecycle_reaches_verified(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.accountant)
		mark_implemented(name, implementation_reference="Policy CP-0001")
		frappe.set_user(self.verifier)
		mark_verified(name, verification_note="Trial balance agrees")

		doc = frappe.get_doc(DECISION, name)
		self.assertEqual(doc.status, "Verified")
		self.assertEqual(doc.implemented_by, self.accountant)
		self.assertEqual(doc.verified_by, self.verifier)
		self.assertEqual(doc.implementation_reference, "Policy CP-0001")

	def test_history_records_every_version(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.preparer)
		supersede_decision(name, reason="revised")
		frappe.set_user(self.accountant)
		rows = decision_history(topic=TOPIC_TRIGGER, company=self.company)
		self.assertGreaterEqual(len(rows), 2)
		self.assertEqual([r["version_no"] for r in rows][:2], [1, 2])


class TestDownstreamQuestions(AccountantDecisionBase):
	def test_no_approved_decision_before_one_is_recorded(self):
		self._prepare()
		frappe.set_user("Administrator")
		self.assertIsNone(approved_decision(TOPIC_TRIGGER, self.company))

	def test_approved_decision_is_visible_downstream(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user("Administrator")
		found = approved_decision(TOPIC_TRIGGER, self.company)
		self.assertIsNotNone(found)
		self.assertEqual(found["accountant_decision"], "Customer Payment Collection")

	def test_a_superseded_approval_no_longer_counts(self):
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.preparer)
		supersede_decision(name, reason="revised")
		frappe.set_user("Administrator")
		self.assertIsNone(approved_decision(TOPIC_TRIGGER, self.company))

	def test_commission_topics_start_unresolved(self):
		frappe.set_user("Administrator")
		unresolved = unresolved_topics(AREA_COMMISSION, self.company)
		self.assertIn(TOPIC_TRIGGER, unresolved)

	def test_rejected_decision_does_not_authorise_anything(self):
		name = self._prepare()
		frappe.set_user(self.accountant)
		record_decision(name=name, status="Rejected", rejection_reason="not yet")
		frappe.set_user("Administrator")
		self.assertIsNone(approved_decision(TOPIC_TRIGGER, self.company))


class TestDecisionCentreView(AccountantDecisionBase):
	def test_centre_lists_every_catalogue_question(self):
		frappe.set_user(self.accountant)
		data = get_decision_centre(company=self.company)
		self.assertEqual(data["total"], len(CATALOGUE))
		self.assertEqual({i["topic"] for i in data["items"]},
		                 {e["topic"] for e in CATALOGUE})

	def test_centre_separates_the_two_areas(self):
		frappe.set_user(self.accountant)
		data = get_decision_centre(company=self.company)
		self.assertEqual(set(data["by_area"]), {AREA_OPENING_STOCK, AREA_COMMISSION})

	def test_centre_reports_commission_posting_as_disabled(self):
		frappe.set_user(self.accountant)
		data = get_decision_centre(company=self.company)
		self.assertFalse(data["commission"]["posting_enabled"])
		self.assertIn("always refuses", data["commission"]["posting_boundary"])

	def test_centre_reports_the_opening_stock_correction_as_unsubmitted(self):
		frappe.set_user(self.accountant)
		data = get_decision_centre(company=self.company)
		self.assertEqual(data["opening_stock"]["posting_status"], "Not submitted")
		self.assertEqual(data["opening_stock"]["stock_quantity_impact"][:4], "None")

	def test_centre_carries_the_worked_commission_example(self):
		frappe.set_user(self.accountant)
		example = get_decision_centre(company=self.company)["commission"]["worked_example"]
		self.assertEqual(example["eligible_base"], 100000.0)
		self.assertEqual(example["rate_percent"], 2.0)
		self.assertEqual(example["pool"], 2000.0)
		self.assertEqual(
			example["manager"] + example["representative_1"] + example["representative_2"],
			example["pool"])

	def test_outstanding_count_drops_when_a_decision_is_recorded(self):
		frappe.set_user(self.accountant)
		before = get_decision_centre(company=self.company)["outstanding"]
		name = self._prepare()
		self._approve(name)
		frappe.set_user(self.accountant)
		after = get_decision_centre(company=self.company)["outstanding"]
		self.assertEqual(after, before - 1)


class TestDecisionCentreRoute(AccountantDecisionBase):
	"""The route must resolve, be gated, and have a page behind it.

	A route registered server-side with no component in the SPA resolves fine here
	and still lands the user on a blank screen, so the frontend side is asserted
	too rather than assumed.
	"""

	def test_route_resolves_to_the_decision_centre(self):
		from my_store_ui.standalone import resolve_frontend_route

		definition, params = resolve_frontend_route("/retail-erp/admin/finance/decisions")
		self.assertIsNotNone(definition, "the decision centre route does not resolve")
		self.assertEqual(definition["name"], "accountant-decisions")
		self.assertEqual(params, {})

	def test_route_is_not_open_to_every_role(self):
		from my_store_ui.services.frontend_routes import ROUTE_REGISTRY

		entry = next(r for r in ROUTE_REGISTRY if r["name"] == "accountant-decisions")
		self.assertTrue(entry.get("roles"), "the decision centre route is ungated")
		self.assertNotIn("Sales User", entry["roles"])
		self.assertIn("Retail Accountant", entry["roles"])

	def test_every_registered_route_has_a_page_in_the_spa(self):
		"""Guards against registering a route nobody built a screen for."""
		import pathlib
		import re

		from my_store_ui.services.frontend_routes import ROUTE_REGISTRY

		routes_js = (pathlib.Path(frappe.get_app_path("my_store_ui")).parent
		             / "frontend" / "src" / "router" / "routes.js")
		if not routes_js.exists():
			self.skipTest("frontend sources are not present in this checkout")
		declared = set(re.findall(r'name:\s*"([a-z0-9-]+)"', routes_js.read_text(encoding="utf-8")))

		# Entity and report routes are generated from the registry at build time and
		# are covered by their own coverage tests; only bespoke pages are checked here.
		bespoke = {"accountant-decisions", "external-actions", "launch-readiness",
		           "system-operations", "data-management", "email-admin",
		           "printing-admin", "access-control", "scheduled-reports"}
		for entry in ROUTE_REGISTRY:
			if entry["name"] not in bespoke:
				continue
			self.assertIn(
				entry["name"], declared,
				f"route {entry['name']} is registered server-side but no SPA page "
				f"declares it; that is a dead route")


class TestCommissionDecisionPackage(AccountantDecisionBase):
	"""Phase 5: every commission choice must be presented, never made.

	The danger with a decision screen is not that it refuses -- it is that it
	quietly shows a value that came from a draft policy and lets a reader take it
	for an answer. These tests hold the line between "current value" and
	"decision".
	"""

	COMMISSION_FIELDS = (
		"earning_trigger", "commission_basis", "commission_expense_account",
		"commission_payable_account", "payee_party_type",
		"accounting_document_type", "payout_cycle", "withholding_mode",
		"returns_rule",
	)

	def test_every_catalogue_topic_has_structured_detail(self):
		for entry in CATALOGUE:
			detail = DECISION_DETAIL.get(entry["topic"])
			self.assertIsNotNone(detail, f"{entry['topic']} has no structured detail")
			self.assertTrue(detail.get("options"), f"{entry['topic']} lists no options")
			self.assertTrue((detail.get("impact") or "").strip(),
			                f"{entry['topic']} states no accounting impact")
			self.assertTrue((detail.get("risk") or "").strip(),
			                f"{entry['topic']} states no risk")

	def test_all_ten_commission_decisions_map_to_a_policy_field_or_are_explained(self):
		commission = [e for e in CATALOGUE if e["area"] == AREA_COMMISSION]
		self.assertEqual(len(commission), 10)
		mapped = {DECISION_DETAIL[e["topic"]].get("field") for e in commission}
		for field in self.COMMISSION_FIELDS:
			self.assertIn(field, mapped, f"no decision maps to policy field {field}")

	def test_payout_document_options_cover_every_candidate(self):
		options = DECISION_DETAIL["Commission: payout document type"]["options"]
		for candidate in ("Journal Entry", "Payment Entry", "Expense Claim",
		                  "Payroll Component"):
			self.assertIn(candidate, options)

	def test_centre_exposes_options_impact_and_risk(self):
		frappe.set_user(self.accountant)
		items = get_decision_centre(company=self.company)["items"]
		for item in items:
			self.assertTrue(item["options"], f"{item['topic']} exposes no options")
			self.assertTrue(item["accounting_impact"])
			self.assertTrue(item["risk"])

	def test_a_current_policy_value_is_never_reported_as_a_decision(self):
		"""The distinction the whole screen depends on."""
		frappe.set_user(self.accountant)
		for item in get_decision_centre(company=self.company)["items"]:
			self.assertFalse(item["current_value_is_a_decision"])
			if not item["answered"]:
				self.assertIsNone(item["accountant_answer"],
				                  f"{item['topic']} shows an answer without a decision")

	def test_verification_state_tracks_the_lifecycle(self):
		name = self._prepare()
		frappe.set_user(self.accountant)
		self.assertEqual(
			next(i for i in get_decision_centre(company=self.company)["items"]
			     if i["topic"] == TOPIC_TRIGGER)["verification_state"],
			"Not verified")
		self._approve(name)
		frappe.set_user(self.accountant)
		self.assertEqual(
			next(i for i in get_decision_centre(company=self.company)["items"]
			     if i["topic"] == TOPIC_TRIGGER)["verification_state"],
			"Decided, not yet implemented")
		mark_implemented(name, implementation_reference="CP-1")
		frappe.set_user(self.verifier)
		mark_verified(name, verification_note="checked")
		frappe.set_user(self.accountant)
		self.assertEqual(
			next(i for i in get_decision_centre(company=self.company)["items"]
			     if i["topic"] == TOPIC_TRIGGER)["verification_state"],
			"Verified")

	def test_worked_example_allocation_matches_the_documented_split(self):
		frappe.set_user(self.accountant)
		ex = get_decision_centre(company=self.company)["commission"]["worked_example"]
		self.assertEqual(ex["eligible_base"] * ex["rate_percent"] / 100, ex["pool"])
		self.assertEqual(ex["manager"], ex["pool"] * 0.5)
		self.assertEqual(ex["representative_1"], ex["pool"] * 0.25)
		self.assertEqual(ex["representative_2"], ex["pool"] * 0.25)
