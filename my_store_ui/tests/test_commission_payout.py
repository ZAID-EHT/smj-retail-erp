"""Commission policy, periods, adjustments, statements, approval and payout.

The rules that matter most here are the refusals: an incomplete policy cannot pay,
a blocking exception cannot be approved past, a preparer cannot approve their own
work, and no payout can ever reach Posted. Savepoint + rollback.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import add_days, flt, nowdate

from my_store_ui.commission_payout import (
	get_commission_statement,
	list_commission_statements,
	post_commission_payout,
	prepare_commission_payout,
	validate_commission_payout,
)
from my_store_ui.commission_period import (
	approve_commission_adjustment,
	approve_commission_period,
	cancel_commission_period,
	create_commission_period,
	get_commission_period,
	get_period_approval_checks,
	prepare_commission_period,
	reject_commission_adjustment,
	reopen_commission_period,
	request_commission_adjustment,
	resolve_commission_exception,
	review_commission_period,
	submit_period_for_review,
)
from my_store_ui.commission_policy import (
	approve_commission_policy,
	get_commission_policy,
	get_commission_policy_status,
	inspect_commission_policy,
	save_commission_policy,
	simulate_commission_policy,
	validate_commission_policy,
)
from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team


class CommissionPayoutBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
		cls.warehouse = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0},
			pluck="name")[0]
		cls.item_group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"cpay_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	# -- fixtures -----------------------------------------------------

	def _policy(self, approve=True, **over):
		payload = {
			"policy_name": f"CP {uuid.uuid4().hex[:8]}", "company": self.company,
			"effective_from": nowdate(), "enabled": 1,
			"earning_trigger": "Sales Invoice Submission",
			"commission_basis": "Net Total After Discount",
			"rate_source": "Sales Team Rate",
			"payout_cycle": "Monthly",
			"withholding_mode": "No Withholding",
			"returns_rule": "Reverse Before Payout",
		}
		payload.update(over)
		result = save_commission_policy(payload)
		if approve:
			result = approve_commission_policy(result["name"])
		return result["name"]

	def _person(self):
		return frappe.get_doc({
			"doctype": "Sales Person", "sales_person_name": f"CP {uuid.uuid4().hex[:8]}",
			"is_group": 0, "parent_sales_person": "",
		}).insert(ignore_permissions=True).name

	def _team(self, rate=2):
		people = [self._person() for _ in range(3)]
		name = save_sales_team({
			"team_name": f"CPTeam {uuid.uuid4().hex[:6]}", "commission_rate": rate,
			"effective_from": nowdate(), "is_active": True,
			"members": [
				{"sales_person": people[0], "team_role": "Sales Manager",
				 "share_percentage": 50, "is_active": True},
				{"sales_person": people[1], "team_role": "Sales Representative",
				 "share_percentage": 25, "is_active": True},
				{"sales_person": people[2], "team_role": "Sales Representative",
				 "share_percentage": 25, "is_active": True},
			],
		})["name"]
		return name, people

	def _customer(self, team=None):
		name = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"CPCust {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
			"default_price_list": "Wholesale Price List",
		}).insert(ignore_permissions=True).name
		if team:
			assign_customer_sales_team(name, team)
		return name

	def _invoice(self, customer, qty=100, rate=1000):
		"""A submitted order -> delivery -> invoice chain for this customer."""
		from my_store_ui.quick_entry.product import create_product
		from my_store_ui.wholesale.delivery import create_delivery_note
		from my_store_ui.wholesale.invoicing import create_sales_invoice

		item = create_product({
			"product_name": f"CPItem {uuid.uuid4().hex[:5]}", "category": self.item_group,
			"stock_location_1": self.warehouse, "cost_price": 500,
			"wholesale_price": 1000, "retail_price": 1200,
		})["name"]
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
			"company": self.company,
			"items": [{"item_code": item, "qty": qty * 3, "t_warehouse": self.warehouse,
			           "basic_rate": 500}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": self.company,
			"delivery_date": add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": qty, "rate": rate,
			           "warehouse": self.warehouse,
			           "delivery_date": add_days(nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		note = create_delivery_note(so.name, override_reason="Payout test", submit=1)
		return frappe.get_doc(
			"Sales Invoice", create_sales_invoice(note["name"], submit=1)["name"])

	def _period(self, policy, prepare=True):
		result = create_commission_period(
			company=self.company, policy=policy,
			from_date=add_days(nowdate(), -30), to_date=add_days(nowdate(), 1))
		if prepare:
			prepare_commission_period(result["name"])
		return result["name"]

	def _user(self, roles, prefix="cp"):
		email = f"{prefix}-{uuid.uuid4().hex[:8]}@example.invalid"
		frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "CP",
			"send_welcome_email": 0,
		}).insert(ignore_permissions=True).add_roles(*roles)
		return email


class TestCommissionPolicy(CommissionPayoutBase):
	def test_a_new_policy_has_no_defaults_at_all(self):
		data = get_commission_policy("")
		policy = data["policy"]
		for field in ("earning_trigger", "commission_basis", "rate_source", "payout_cycle",
		              "withholding_mode", "returns_rule"):
			self.assertEqual(policy[field], "", f"{field} must not be defaulted")
		self.assertFalse(policy["may_post"])

	def test_an_empty_policy_is_draft_and_cannot_calculate(self):
		name = save_commission_policy({
			"policy_name": f"CP {uuid.uuid4().hex[:8]}", "company": self.company,
			"effective_from": nowdate(),
		})["name"]
		doc = frappe.get_doc("Retail Commission Policy", name)
		self.assertEqual(doc.status, "Draft")
		self.assertFalse(doc.is_complete_for_calculation())
		self.assertFalse(doc.may_post())

	def test_a_partly_filled_policy_is_incomplete(self):
		name = save_commission_policy({
			"policy_name": f"CP {uuid.uuid4().hex[:8]}", "company": self.company,
			"effective_from": nowdate(), "earning_trigger": "Sales Invoice Submission",
		})["name"]
		self.assertEqual(frappe.db.get_value("Retail Commission Policy", name, "status"),
		                 "Incomplete")

	def test_a_complete_policy_is_ready_then_active_once_approved(self):
		name = self._policy(approve=False)
		self.assertEqual(frappe.db.get_value("Retail Commission Policy", name, "status"),
		                 "Ready for Review")
		approve_commission_policy(name)
		self.assertEqual(frappe.db.get_value("Retail Commission Policy", name, "status"),
		                 "Active")

	def test_an_active_policy_still_cannot_post(self):
		"""Calculation completeness is not posting completeness."""
		doc = frappe.get_doc("Retail Commission Policy", self._policy())
		self.assertTrue(doc.is_active())
		self.assertFalse(doc.may_post())
		self.assertIn("Commission Expense Account", doc.missing_for_posting())

	def test_an_incomplete_policy_cannot_be_approved(self):
		name = save_commission_policy({
			"policy_name": f"CP {uuid.uuid4().hex[:8]}", "company": self.company,
			"effective_from": nowdate(),
		})["name"]
		with self.assertRaises(frappe.ValidationError):
			approve_commission_policy(name)

	def test_changing_the_terms_withdraws_the_approval(self):
		name = self._policy()
		self.assertTrue(frappe.db.get_value("Retail Commission Policy", name, "approved_by"))
		save_commission_policy({"rate_source": "Fixed Policy Rate", "fixed_rate": 3}, name=name)
		self.assertFalse(frappe.db.get_value("Retail Commission Policy", name, "approved_by"),
		                 "a rate change must not keep an approval given for something else")

	def test_a_payload_cannot_set_its_own_approval(self):
		name = save_commission_policy({
			"policy_name": f"CP {uuid.uuid4().hex[:8]}", "company": self.company,
			"effective_from": nowdate(), "approved_by": "Administrator",
			"status": "Active",
		})["name"]
		doc = frappe.get_doc("Retail Commission Policy", name)
		self.assertFalse(doc.approved_by)
		self.assertEqual(doc.status, "Draft")

	def test_fixed_withholding_needs_an_approved_percentage(self):
		with self.assertRaises(frappe.ValidationError):
			self._policy(withholding_mode="Fixed Percentage", withholding_percentage=0)

	def test_a_custom_rule_needs_its_approved_wording(self):
		with self.assertRaises(frappe.ValidationError):
			self._policy(earning_trigger="Approved Custom Rule")

	def test_effective_to_before_from_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._policy(effective_to=add_days(nowdate(), -5))

	def test_validation_lists_what_is_missing_for_posting(self):
		result = validate_commission_policy(self._policy())
		self.assertTrue(result["valid_for_calculation"])
		self.assertFalse(result["valid_for_posting"])
		self.assertTrue(any(i["severity"] == "Blocking for posting" for i in result["issues"]))

	def test_status_endpoint_reports_no_policy_honestly(self):
		result = get_commission_policy_status(company=self.company)
		self.assertIn("may_post", result)
		self.assertFalse(result["may_post"])

	def test_inspect_without_a_policy_does_not_error(self):
		result = inspect_commission_policy(name="", company="")
		self.assertIn("found", result)


class TestPolicySimulation(CommissionPayoutBase):
	def test_simulation_persists_nothing(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		policy = self._policy()
		before = frappe.db.count("Retail Commission Period")
		result = simulate_commission_policy(policy)
		self.assertFalse(result["persisted"])
		self.assertEqual(frappe.db.count("Retail Commission Period"), before)
		self.assertTrue(result["totals"]["lines"] >= 3)

	def test_simulation_reproduces_the_frozen_calculation(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		result = simulate_commission_policy(self._policy())
		self.assertTrue(result["matches_current_calculation"], result["differences"])

	def test_a_rate_source_with_no_data_blocks_rather_than_substituting(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		result = simulate_commission_policy(self._policy(rate_source="Customer Rate"))
		blocking = [e for e in result["exceptions"] if e["severity"] == "Blocking"]
		self.assertTrue(blocking, "an unconfigured rate source must block")
		self.assertEqual(result["totals"]["gross_commission"], 0.0,
		                 "it must not fall back to the team rate")

	def test_withholding_reduces_the_net_but_not_the_gross(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		result = simulate_commission_policy(self._policy(
			withholding_mode="Fixed Percentage", withholding_percentage=10))
		self.assertGreater(result["totals"]["withholding"], 0)
		self.assertAlmostEqual(
			result["totals"]["net_commission"],
			result["totals"]["gross_commission"] - result["totals"]["withholding"], places=2)


class TestCommissionPeriods(CommissionPayoutBase):
	def test_a_period_gets_a_dated_identifier(self):
		name = self._period(self._policy(), prepare=False)
		self.assertTrue(name.startswith("COM-PER-"), name)

	def test_dates_the_wrong_way_round_are_rejected(self):
		policy = self._policy()
		with self.assertRaises(frappe.ValidationError):
			create_commission_period(company=self.company, policy=policy,
			                         from_date=nowdate(), to_date=add_days(nowdate(), -5))

	def test_overlapping_periods_are_refused(self):
		policy = self._policy()
		self._period(policy, prepare=False)
		with self.assertRaises(frappe.ValidationError):
			create_commission_period(
				company=self.company, policy=policy,
				from_date=add_days(nowdate(), -10), to_date=nowdate())

	def test_a_period_needs_an_active_policy(self):
		policy = self._policy(approve=False)
		with self.assertRaises(frappe.ValidationError):
			create_commission_period(company=self.company, policy=policy,
			                         from_date=add_days(nowdate(), -30), to_date=nowdate())

	def test_preparation_builds_rows_from_the_frozen_snapshot(self):
		team, people = self._team()
		invoice = self._invoice(self._customer(team))
		period = self._period(self._policy())
		data = get_commission_period(period)
		rows = [r for r in data["period"]["details"] if r["sales_invoice"] == invoice.name]
		self.assertEqual(len(rows), 3)
		self.assertEqual(sorted(flt(r["gross_commission"]) for r in rows),
		                 [500.0, 500.0, 1000.0])
		self.assertEqual({r["sales_person"] for r in rows}, set(people))

	def test_preparing_twice_does_not_duplicate(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		policy = self._policy()
		period = self._period(policy)
		first = len(get_commission_period(period)["period"]["details"])
		prepare_commission_period(period)
		self.assertEqual(len(get_commission_period(period)["period"]["details"]), first)

	def test_totals_reconcile_with_the_rows(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		data = get_commission_period(period)["period"]
		self.assertAlmostEqual(
			data["net_payable"],
			round(sum(flt(r["net_commission"]) for r in data["details"]), 2), places=2)

	def test_paid_stays_zero_and_outstanding_is_the_whole_amount(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		data = get_commission_period(self._period(self._policy()))["period"]
		self.assertEqual(flt(data["paid_amount"]), 0.0)
		self.assertEqual(flt(data["outstanding"]), flt(data["net_payable"]))

	def test_a_credit_note_before_preparation_reduces_the_net(self):
		from my_store_ui.wholesale.returns import create_credit_note

		team, _people = self._team()
		invoice = self._invoice(self._customer(team))
		policy = self._policy()
		before = get_commission_period(self._period(policy))["period"]["net_payable"]

		create_credit_note(invoice.name, submit=1)
		frappe.db.set_value("Retail Commission Period",
		                    frappe.get_all("Retail Commission Period", limit=1, pluck="name")[0],
		                    "status", "Draft")
		period = frappe.get_all("Retail Commission Period", limit=1, pluck="name")[0]
		prepare_commission_period(period)
		after = get_commission_period(period)["period"]["net_payable"]
		self.assertLess(after, before, "a return must reduce what is owed")

	def test_a_cancelled_invoice_never_reaches_a_period(self):
		team, _people = self._team()
		invoice = self._invoice(self._customer(team))
		invoice.cancel()
		period = self._period(self._policy())
		rows = [r for r in get_commission_period(period)["period"]["details"]
		        if r["sales_invoice"] == invoice.name]
		self.assertEqual(rows, [])

	def test_a_row_already_in_another_period_is_not_claimed_twice(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		policy = self._policy()
		first = self._period(policy)
		self.assertTrue(get_commission_period(first)["period"]["details"])

		# A second period over the same dates needs a different policy: overlap is
		# refused per company and policy, so reusing the first would test nothing.
		second = create_commission_period(
			company=self.company, policy=self._policy(),
			from_date=add_days(nowdate(), -30), to_date=add_days(nowdate(), 1))["name"]
		prepare_commission_period(second)
		data = get_commission_period(second)["period"]
		self.assertEqual(data["details"], [], "the same invoice must not be paid twice")
		self.assertTrue(any(e["exception_type"] == "Already in another period"
		                    for e in data["exceptions"]))


class TestExceptionsAndApproval(CommissionPayoutBase):
	def test_a_blocking_exception_prevents_approval(self):
		team, _people = self._team(rate=0)
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		data = get_commission_period(period)
		self.assertTrue(data["blocking_exceptions"])

		submit_period_for_review(period)
		review_commission_period(period)
		with self.assertRaises(frappe.ValidationError):
			approve_commission_period(period)

	def test_an_exception_can_be_waived_only_with_a_reason(self):
		team, _people = self._team(rate=0)
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		with self.assertRaises(frappe.ValidationError):
			resolve_commission_exception(period, idx=1, resolution="Waived", note="")
		resolve_commission_exception(period, idx=1, resolution="Waived", note="Known, agreed")
		self.assertEqual(get_commission_period(period)["blocking_exceptions"], 0)

	def test_a_resolution_survives_re_preparation(self):
		team, _people = self._team(rate=0)
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		resolve_commission_exception(period, idx=1, resolution="Waived", note="Agreed")
		prepare_commission_period(period)
		rows = get_commission_period(period)["period"]["exceptions"]
		self.assertTrue(any(r["resolution_status"] == "Waived" for r in rows))

	def test_the_full_approval_sequence(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		self.assertEqual(get_commission_period(period)["period"]["status"], "Prepared")
		submit_period_for_review(period)
		self.assertEqual(get_commission_period(period)["period"]["status"], "Under Review")
		review_commission_period(period, comment="Checked")
		approve_commission_period(period, comment="Agreed")
		data = get_commission_period(period)["period"]
		self.assertEqual(data["status"], "Approved")
		self.assertTrue(data["approved_by"])
		self.assertEqual(len(data["decision_log"]), 4)

	def test_an_unprepared_period_cannot_go_for_review(self):
		with self.assertRaises(frappe.ValidationError):
			submit_period_for_review(self._period(self._policy(), prepare=False))

	def test_approval_checks_are_reported_before_approving(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		result = get_period_approval_checks(period)
		self.assertTrue(result["checks"])
		self.assertEqual(result["failed"], [])

	def test_an_approved_period_cannot_be_re_prepared(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		submit_period_for_review(period)
		review_commission_period(period)
		approve_commission_period(period)
		with self.assertRaises(frappe.ValidationError):
			prepare_commission_period(period)

	def test_reopening_needs_a_reason_and_clears_the_approval(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		submit_period_for_review(period)
		review_commission_period(period)
		approve_commission_period(period)
		with self.assertRaises(frappe.ValidationError):
			reopen_commission_period(period, reason="")
		reopen_commission_period(period, reason="Late credit note")
		data = get_commission_period(period)["period"]
		self.assertEqual(data["status"], "Reopened")
		self.assertFalse(data["approved_by"])

	def test_cancelling_needs_a_reason(self):
		period = self._period(self._policy(), prepare=False)
		with self.assertRaises(frappe.ValidationError):
			cancel_commission_period(period, reason="")
		cancel_commission_period(period, reason="Opened by mistake")
		self.assertEqual(get_commission_period(period)["period"]["status"], "Cancelled")


class TestAdjustments(CommissionPayoutBase):
	def _prepared(self):
		team, people = self._team()
		self._invoice(self._customer(team))
		return self._period(self._policy()), people

	def test_an_adjustment_changes_the_period_total(self):
		period, people = self._prepared()
		before = get_commission_period(period)["period"]["net_payable"]
		adjustment = request_commission_adjustment(
			period=period, sales_person=people[0], adjustment_type="Bonus",
			amount=250, reason="Agreed bonus")["name"]
		approve_commission_adjustment(adjustment)
		after = get_commission_period(period)["period"]["net_payable"]
		self.assertAlmostEqual(after, before + 250, places=2)

	def test_an_adjustment_needs_a_reason_and_an_amount(self):
		period, people = self._prepared()
		with self.assertRaises(frappe.ValidationError):
			request_commission_adjustment(period=period, sales_person=people[0],
			                              adjustment_type="Bonus", amount=0, reason="x")
		with self.assertRaises(frappe.ValidationError):
			request_commission_adjustment(period=period, sales_person=people[0],
			                              adjustment_type="Bonus", amount=10, reason="")

	def test_an_adjustment_must_name_someone_the_period_pays(self):
		period, _people = self._prepared()
		with self.assertRaises(frappe.ValidationError):
			request_commission_adjustment(
				period=period, sales_person=self._person(), adjustment_type="Bonus",
				amount=10, reason="Not in this period")

	def test_a_rejected_adjustment_changes_nothing(self):
		period, people = self._prepared()
		before = get_commission_period(period)["period"]["net_payable"]
		adjustment = request_commission_adjustment(
			period=period, sales_person=people[0], adjustment_type="Bonus",
			amount=500, reason="Requested")["name"]
		reject_commission_adjustment(adjustment, note="Not agreed")
		self.assertAlmostEqual(
			get_commission_period(period)["period"]["net_payable"], before, places=2)

	def test_rejecting_needs_a_note(self):
		period, people = self._prepared()
		adjustment = request_commission_adjustment(
			period=period, sales_person=people[0], adjustment_type="Bonus",
			amount=50, reason="Requested")["name"]
		with self.assertRaises(frappe.ValidationError):
			reject_commission_adjustment(adjustment, note="")

	def test_a_requester_cannot_approve_their_own_adjustment(self):
		period, people = self._prepared()
		requester = self._user(["Sales Manager", "Accounts Manager", "Accounts User"])
		frappe.set_user(requester)
		try:
			adjustment = request_commission_adjustment(
				period=period, sales_person=people[0], adjustment_type="Bonus",
				amount=100, reason="Mine")["name"]
			with self.assertRaises(frappe.PermissionError):
				approve_commission_adjustment(adjustment)
		finally:
			frappe.set_user("Administrator")

	def test_an_adjustment_awaiting_approval_blocks_period_approval(self):
		period, people = self._prepared()
		request_commission_adjustment(
			period=period, sales_person=people[0], adjustment_type="Bonus",
			amount=100, reason="Pending")
		submit_period_for_review(period)
		review_commission_period(period)
		with self.assertRaises(frappe.ValidationError):
			approve_commission_period(period)

	def test_an_adjustment_never_touches_the_invoice(self):
		period, people = self._prepared()
		row = get_commission_period(period)["period"]["details"][0]
		invoice_before = frappe.db.get_value(
			"Sales Invoice", row["sales_invoice"], ["total_commission", "grand_total"],
			as_dict=True)
		adjustment = request_commission_adjustment(
			period=period, sales_person=people[0], adjustment_type="Deduction",
			amount=-100, reason="Correction")["name"]
		approve_commission_adjustment(adjustment)
		invoice_after = frappe.db.get_value(
			"Sales Invoice", row["sales_invoice"], ["total_commission", "grand_total"],
			as_dict=True)
		self.assertEqual(invoice_before, invoice_after)


class TestStatements(CommissionPayoutBase):
	def _prepared(self):
		team, people = self._team()
		self._invoice(self._customer(team))
		return self._period(self._policy()), people

	def test_a_statement_shows_the_members_own_figures(self):
		period, people = self._prepared()
		data = get_commission_statement(period, sales_person=people[0])
		entry = data["statements"][0]
		self.assertEqual(entry["sales_person"], people[0])
		self.assertEqual(flt(entry["gross_commission"]), 1000.0)
		self.assertEqual(flt(entry["net_payable"]), 1000.0)
		self.assertEqual(len(entry["transactions"]), 1)

	def test_every_statement_is_listed_for_a_manager(self):
		period, _people = self._prepared()
		data = list_commission_statements(period)
		self.assertGreaterEqual(len(data["statements"]), 3)
		self.assertFalse(data["restricted"])

	def test_a_member_cannot_read_another_members_statement(self):
		period, people = self._prepared()
		email = self._user(["Sales User", "Accounts User"])
		employee = self._employee(email)
		frappe.db.set_value("Sales Person", people[0], "employee", employee)
		frappe.set_user(email)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_commission_statement(period, sales_person=people[1])
			own = get_commission_statement(period, sales_person=people[0])
			self.assertTrue(own["restricted"])
			self.assertEqual(own["statements"][0]["sales_person"], people[0])
		finally:
			frappe.set_user("Administrator")

	def test_a_user_with_no_sales_person_sees_nothing(self):
		period, _people = self._prepared()
		email = self._user(["Sales User", "Accounts User"])
		frappe.set_user(email)
		try:
			self.assertEqual(list_commission_statements(period)["statements"], [])
		finally:
			frappe.set_user("Administrator")

	def _employee(self, email):
		gender = frappe.get_all("Gender", limit=1, pluck="name")
		if not gender:
			gender = [frappe.get_doc({
				"doctype": "Gender", "gender": "Prefer not to say",
			}).insert(ignore_permissions=True).name]
		return frappe.get_doc({
			"doctype": "Employee", "first_name": "CP", "user_id": email,
			"company": self.company, "date_of_birth": "1990-01-01",
			"date_of_joining": "2020-01-01", "status": "Active", "gender": gender[0],
		}).insert(ignore_permissions=True).name


class TestPayoutPreparation(CommissionPayoutBase):
	def _approved(self, **policy_over):
		team, people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy(**policy_over))
		submit_period_for_review(period)
		review_commission_period(period)
		approve_commission_period(period)
		return period, people

	def test_only_an_approved_period_can_be_paid(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		with self.assertRaises(frappe.ValidationError):
			prepare_commission_payout(self._period(self._policy()))

	def test_a_payout_groups_by_member(self):
		period, people = self._approved()
		payout = prepare_commission_payout(period)["payout"]
		# The period covers a date range, so staging's own invoices are legitimately
		# in it too. Assert on the members this test created.
		mine = [l for l in payout["lines"] if l["sales_person"] in people]
		self.assertEqual(len(mine), 3)
		self.assertEqual(sorted(flt(l["net_payable"]) for l in mine), [500.0, 500.0, 1000.0])
		self.assertEqual(len({l["sales_person"] for l in payout["lines"]}),
		                 len(payout["lines"]), "one line per member")

	def test_every_line_is_blocked_without_accounting_configuration(self):
		period, people = self._approved()
		payout = prepare_commission_payout(period)["payout"]
		self.assertTrue(all(l["validation_status"] == "Blocked" for l in payout["lines"]))
		self.assertTrue(all("payee" in l["validation_note"].lower()
		                    for l in payout["lines"]))

	def test_preparing_a_payout_twice_reuses_the_same_record(self):
		period, _people = self._approved()
		first = prepare_commission_payout(period)["name"]
		second = prepare_commission_payout(period)["name"]
		self.assertEqual(first, second)

	def test_the_accounting_preview_proposes_without_posting(self):
		period, _people = self._approved()
		payout = prepare_commission_payout(period)["payout"]
		preview = payout["accounting_preview"]
		self.assertFalse(preview["would_post"])
		self.assertTrue(preview["blocked_because"])
		self.assertEqual(preview["entry_count"],
		                 len([l for l in payout["lines"] if flt(l["net_payable"]) > 0]))
		self.assertEqual(frappe.db.count("GL Entry", {"voucher_no": payout["name"]}), 0)

	def test_a_payout_can_never_reach_ready_for_posting(self):
		period, _people = self._approved()
		payout = prepare_commission_payout(period)["name"]
		result = validate_commission_payout(payout)
		self.assertNotEqual(result["payout"]["status"], "Ready for Posting")

	def test_posting_always_refuses_and_says_why(self):
		period, _people = self._approved()
		payout = prepare_commission_payout(period)["name"]
		with self.assertRaises(frappe.ValidationError) as caught:
			post_commission_payout(payout, confirmation="yes")
		message = str(caught.exception)
		self.assertIn("not enabled", message)
		self.assertIn("accountant", message.lower())

	def test_a_posted_status_cannot_be_forced_onto_the_record(self):
		period, _people = self._approved()
		doc = frappe.get_doc("Retail Commission Payout", prepare_commission_payout(period)["name"])
		doc.status = "Posted"
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_a_balance_below_the_minimum_is_carried_not_lost(self):
		period, people = self._approved(minimum_payout_amount=100000)
		payout = prepare_commission_payout(period)["payout"]
		mine = [l for l in payout["lines"] if l["sales_person"] in people]
		self.assertTrue(mine)
		self.assertTrue(all(flt(l["net_payable"]) == 0 for l in mine))
		self.assertTrue(all(flt(l["carry_forward_out"]) > 0 for l in mine),
		                "a balance below the minimum is carried, never lost")

	def test_no_gl_entry_is_ever_created(self):
		period, _people = self._approved()
		before = frappe.db.count("GL Entry")
		payout = prepare_commission_payout(period)["name"]
		validate_commission_payout(payout)
		self.assertEqual(frappe.db.count("GL Entry"), before)


class TestCommissionPermissions(CommissionPayoutBase):
	def test_a_sales_user_cannot_change_policy(self):
		email = self._user(["Sales User"])
		frappe.set_user(email)
		try:
			with self.assertRaises(frappe.PermissionError):
				save_commission_policy({"policy_name": "Nope", "company": self.company,
				                        "effective_from": nowdate()})
		finally:
			frappe.set_user("Administrator")

	def test_a_sales_manager_cannot_approve_a_policy(self):
		name = self._policy(approve=False)
		email = self._user(["Sales Manager", "Sales User"])
		frappe.set_user(email)
		try:
			with self.assertRaises(frappe.PermissionError):
				approve_commission_policy(name)
		finally:
			frappe.set_user("Administrator")

	def test_a_sales_manager_cannot_approve_a_period(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		submit_period_for_review(period)
		email = self._user(["Sales Manager", "Sales User", "Accounts User"])
		frappe.set_user(email)
		try:
			review_commission_period(period)
			with self.assertRaises(frappe.PermissionError):
				approve_commission_period(period)
		finally:
			frappe.set_user("Administrator")

	def test_a_sales_manager_cannot_prepare_a_payout(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		period = self._period(self._policy())
		submit_period_for_review(period)
		review_commission_period(period)
		approve_commission_period(period)
		email = self._user(["Sales Manager", "Sales User"])
		frappe.set_user(email)
		try:
			with self.assertRaises(frappe.PermissionError):
				prepare_commission_payout(period)
		finally:
			frappe.set_user("Administrator")

	def test_the_preparer_cannot_review_or_approve_their_own_period(self):
		team, _people = self._team()
		self._invoice(self._customer(team))
		email = self._user(["Sales Manager", "Accounts Manager", "Accounts User"])
		frappe.set_user(email)
		try:
			period = self._period(self._policy_as_admin())
			submit_period_for_review(period)
			with self.assertRaises(frappe.PermissionError):
				review_commission_period(period)
		finally:
			frappe.set_user("Administrator")

	def _policy_as_admin(self):
		current = frappe.session.user
		frappe.set_user("Administrator")
		try:
			return self._policy()
		finally:
			frappe.set_user(current)

	def test_guest_is_rejected_everywhere(self):
		frappe.set_user("Guest")
		try:
			for call in (
				lambda: get_commission_policy_status(),
				lambda: get_commission_statement("x", "y"),
			):
				with self.assertRaises((frappe.AuthenticationError, frappe.PermissionError)):
					call()
		finally:
			frappe.set_user("Administrator")

	def test_a_period_cannot_be_opened_for_another_companys_policy(self):
		other = frappe.get_doc({
			"doctype": "Company", "company_name": f"CPCo {uuid.uuid4().hex[:6]}",
			"default_currency": "LKR", "country": "Sri Lanka",
		}).insert(ignore_permissions=True)
		policy = self._policy()
		with self.assertRaises(frappe.ValidationError):
			create_commission_period(company=other.name, policy=policy,
			                         from_date=add_days(nowdate(), -30), to_date=nowdate())


class TestHistoricalReviewAndDashboard(CommissionPayoutBase):
	def test_the_review_list_never_suggests_the_customers_current_team(self):
		from my_store_ui.commission_payout import list_historical_commission_review

		data = list_historical_commission_review()
		self.assertIn("note", data)
		for row in data["rows"]:
			if not row["has_reliable_evidence"]:
				self.assertFalse(row["suggested_team"],
				                 "a team must never be suggested without evidence")

	def test_a_team_cannot_be_assigned_without_evidence_on_the_document(self):
		"""The customer's current team is not proof of the historical one."""
		from my_store_ui.commission_payout import (
			list_historical_commission_review, record_historical_commission_decision,
		)

		rows = [r for r in list_historical_commission_review()["rows"]
		        if not r["has_reliable_evidence"]]
		if not rows:
			self.skipTest("no evidence-free historical document on this site")
		row = rows[0]
		team, _people = self._team()
		with self.assertRaises(frappe.ValidationError):
			record_historical_commission_decision(
				source_doctype=row["source_doctype"], source_name=row["source_name"],
				status="Assigned", reason="Customer has this team now", team=team)

	def test_a_decision_needs_a_reason(self):
		from my_store_ui.commission_payout import (
			list_historical_commission_review, record_historical_commission_decision,
		)

		rows = list_historical_commission_review()["rows"]
		if not rows:
			self.skipTest("nothing to review on this site")
		with self.assertRaises(frappe.ValidationError):
			record_historical_commission_decision(
				source_doctype=rows[0]["source_doctype"], source_name=rows[0]["source_name"],
				status="Excluded", reason="")

	def test_excluding_records_the_decision_without_editing_the_document(self):
		from my_store_ui.commission_payout import (
			list_historical_commission_review, record_historical_commission_decision,
		)

		rows = list_historical_commission_review()["rows"]
		if not rows:
			self.skipTest("nothing to review on this site")
		row = rows[0]
		before = frappe.db.get_value(
			row["source_doctype"], row["source_name"], ["grand_total", "docstatus"], as_dict=True)
		record_historical_commission_decision(
			source_doctype=row["source_doctype"], source_name=row["source_name"],
			status="Excluded", reason="Predates the feature; no evidence exists")
		after = frappe.db.get_value(
			row["source_doctype"], row["source_name"], ["grand_total", "docstatus"], as_dict=True)
		self.assertEqual(before, after, "the submitted document must not be edited")

	def test_an_unsupported_status_is_refused(self):
		from my_store_ui.commission_payout import record_historical_commission_decision

		with self.assertRaises(frappe.ValidationError):
			record_historical_commission_decision(
				source_doctype="Sales Invoice", source_name="x", status="Paid", reason="no")

	def test_the_dashboard_never_reports_a_payout_as_possible(self):
		from my_store_ui.commission_payout import get_commission_dashboard

		data = get_commission_dashboard(company=self.company)
		self.assertIn("periods", data)
		if data.get("accounts"):
			self.assertFalse(data["accounts"]["posting_enabled"])

	def test_a_member_sees_only_their_own_dashboard_figures(self):
		from my_store_ui.commission_payout import get_commission_dashboard

		team, people = self._team()
		self._invoice(self._customer(team))
		self._period(self._policy())
		email = self._user(["Sales User", "Accounts User"])
		gender = frappe.get_all("Gender", limit=1, pluck="name")
		if not gender:
			gender = [frappe.get_doc({
				"doctype": "Gender", "gender": "Prefer not to say",
			}).insert(ignore_permissions=True).name]
		employee = frappe.get_doc({
			"doctype": "Employee", "first_name": "CP", "user_id": email,
			"company": self.company, "date_of_birth": "1990-01-01",
			"date_of_joining": "2020-01-01", "status": "Active", "gender": gender[0],
		}).insert(ignore_permissions=True).name
		frappe.db.set_value("Sales Person", people[0], "employee", employee)

		frappe.set_user(email)
		try:
			data = get_commission_dashboard(company=self.company)
			self.assertFalse(data["is_manager"])
			self.assertIsNone(data["sales"], "a member must not see team-wide figures")
			self.assertIsNotNone(data["own"])
			self.assertEqual(flt(data["own"]["paid"]), 0.0)
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
