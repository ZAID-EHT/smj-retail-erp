"""The commission register, team performance and customer history.

Every figure must come from the frozen snapshot, and a user who is not a manager
must never see another person's earnings. Savepoint + rollback.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt, nowdate

from my_store_ui.commission import (
	get_customer_commission_history,
	get_team_performance,
	list_commissions,
	sales_persons_for_user,
)
from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team
from my_store_ui.standalone import authorize_frontend_route

REGISTER_USER = "commreg-user@example.invalid"


class CommissionBase(unittest.TestCase):
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
		self.sp = f"comm_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _person(self, employee=None):
		doc = frappe.get_doc({
			"doctype": "Sales Person", "sales_person_name": f"CP {uuid.uuid4().hex[:8]}",
			"is_group": 0, "parent_sales_person": "", "employee": employee,
		})
		doc.insert(ignore_permissions=True)
		return doc.name

	def _team(self, people, rate=2, shares=(50, 25, 25)):
		roles = ["Sales Manager"] + ["Sales Representative"] * (len(shares) - 1)
		return save_sales_team({
			"team_name": f"CTeam {uuid.uuid4().hex[:6]}", "commission_rate": rate,
			"effective_from": nowdate(), "is_active": True,
			"members": [
				{"sales_person": people[i], "team_role": roles[i],
				 "share_percentage": shares[i], "is_active": True}
				for i in range(len(shares))
			],
		})["name"]

	def _customer(self):
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": f"CCust {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
		}).insert(ignore_permissions=True).name

	def _item(self):
		from my_store_ui.quick_entry.product import create_product

		name = create_product({
			"product_name": f"CItem {uuid.uuid4().hex[:5]}", "category": self.item_group,
			"stock_location_1": self.warehouse, "cost_price": 500,
			"wholesale_price": 1000, "retail_price": 1200,
		})["name"]
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
			"company": self.company,
			"items": [{"item_code": name, "qty": 500, "t_warehouse": self.warehouse,
			           "basic_rate": 500}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		return name

	def _invoiced(self, customer, qty=100, rate=1000):
		"""A submitted order, delivery and invoice for this customer."""
		from my_store_ui.wholesale.delivery import create_delivery_note
		from my_store_ui.wholesale.invoicing import create_sales_invoice

		item = self._item()
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": qty, "rate": rate, "warehouse": self.warehouse,
			           "delivery_date": frappe.utils.add_days(nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		so.submit()
		note = create_delivery_note(so.name, override_reason="Commission test", submit=1)
		invoice = create_sales_invoice(note["name"], submit=1)
		return so, frappe.get_doc("Sales Invoice", invoice["name"])


class TestCommissionRegister(CommissionBase):
	def test_route_resolves(self):
		self.assertEqual(
			authorize_frontend_route("/sales/commissions")["outcome"], "allowed")

	def test_one_line_per_member_per_invoice(self):
		people = [self._person() for _ in range(3)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team(people))
		_so, invoice = self._invoiced(customer)

		rows = [r for r in list_commissions()["rows"] if r["sales_invoice"] == invoice.name]
		self.assertEqual(len(rows), 3)
		self.assertEqual(
			sorted(flt(r["net_commission"]) for r in rows), [500.0, 500.0, 1000.0])

	def test_the_register_reports_the_whole_chain(self):
		people = [self._person() for _ in range(3)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team(people))
		_so, invoice = self._invoiced(customer)

		row = next(r for r in list_commissions()["rows"]
		           if r["sales_invoice"] == invoice.name and r["role"] == "Sales Manager")
		self.assertEqual(flt(row["commission_base"]), 100000.0)
		self.assertEqual(flt(row["commission_rate"]), 2.0)
		self.assertEqual(flt(row["commission_pool"]), 2000.0)
		self.assertEqual(flt(row["allocation_percentage"]), 50.0)
		self.assertEqual(flt(row["gross_commission"]), 1000.0)
		self.assertEqual(flt(row["return_reversal"]), 0.0)
		self.assertEqual(flt(row["net_commission"]), 1000.0)
		self.assertEqual(row["commission_status"], "Earned")

	def test_a_credit_note_shows_as_a_reversal_and_nets_off(self):
		from my_store_ui.wholesale.returns import create_credit_note

		people = [self._person() for _ in range(3)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team(people))
		_so, invoice = self._invoiced(customer)
		credit = create_credit_note(invoice.name, submit=1)

		rows = [r for r in list_commissions()["rows"]
		        if r["sales_invoice"] in (invoice.name, credit["name"])]
		reversals = [r for r in rows if r["is_return"]]
		self.assertEqual(len(reversals), 3)
		self.assertTrue(all(flt(r["return_reversal"]) < 0 for r in reversals))
		self.assertTrue(all(r["commission_status"] == "Reversed" for r in reversals))
		# A full return nets the whole pool back to zero.
		self.assertEqual(round(sum(flt(r["net_commission"]) for r in rows), 2), 0.0)

	def test_filters_narrow_the_register(self):
		people = [self._person() for _ in range(3)]
		customer = self._customer()
		team = self._team(people)
		assign_customer_sales_team(customer, team)
		_so, invoice = self._invoiced(customer)

		self.assertTrue(list_commissions(team=team)["rows"])
		self.assertTrue(list_commissions(customer=customer)["rows"])
		self.assertTrue(list_commissions(sales_invoice=invoice.name)["rows"])
		self.assertEqual(len(list_commissions(sales_person=people[0],
		                                      sales_invoice=invoice.name)["rows"]), 1)
		self.assertFalse(list_commissions(customer="does-not-exist")["rows"])

	def test_a_blank_filter_never_errors(self):
		"""Cleared filters are sent as empty strings and must mean "all"."""
		data = list_commissions(from_date="", to_date="", team="", sales_person="",
		                        customer="", sales_order="", sales_invoice="",
		                        payment_status="", status="")
		self.assertIn("rows", data)

	def test_totals_reconcile_with_the_rows(self):
		people = [self._person() for _ in range(3)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team(people))
		self._invoiced(customer)
		data = list_commissions()
		self.assertEqual(
			data["totals"]["net_commission"],
			round(sum(flt(r["net_commission"]) for r in data["rows"]), 2),
		)

	def test_an_order_with_no_team_never_reaches_the_register(self):
		customer = self._customer()
		_so, invoice = self._invoiced(customer)
		self.assertFalse(
			[r for r in list_commissions()["rows"] if r["sales_invoice"] == invoice.name])


class TestCommissionPermissions(CommissionBase):
	def _employee_user(self):
		email = f"comm-{uuid.uuid4().hex[:8]}@example.invalid"
		frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "Comm",
			"send_welcome_email": 0,
		# Sales User alone has no Sales Invoice read in ERPNext v15, and the register
		# reports invoice data -- so an ordinary counter user needs Accounts User to
		# see even their own line. Recorded in the permission matrix.
		}).insert(ignore_permissions=True).add_roles("Sales User", "Accounts User")
		# Employee requires a gender, but the Gender table is empty on this site, so
		# one is created inside the savepoint rather than assuming "Other" exists.
		gender = frappe.get_all("Gender", limit=1, pluck="name")
		if not gender:
			gender = [frappe.get_doc({
				"doctype": "Gender", "gender": "Prefer not to say",
			}).insert(ignore_permissions=True).name]
		employee = frappe.get_doc({
			"doctype": "Employee", "first_name": "Comm", "user_id": email,
			"company": self.company, "date_of_birth": "1990-01-01",
			"date_of_joining": "2020-01-01", "status": "Active",
			"gender": gender[0],
		}).insert(ignore_permissions=True)
		return email, employee.name

	def test_a_sales_user_sees_only_their_own_lines(self):
		email, employee = self._employee_user()
		mine = self._person(employee=employee)
		theirs = [self._person() for _ in range(2)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team([mine] + theirs))
		_so, invoice = self._invoiced(customer)

		frappe.set_user(email)
		try:
			data = list_commissions(sales_invoice=invoice.name)
			self.assertFalse(data["can_see_everyone"])
			self.assertEqual(len(data["rows"]), 1)
			self.assertEqual(data["rows"][0]["sales_person"], mine)
		finally:
			frappe.set_user("Administrator")

	def test_a_user_with_no_sales_person_sees_an_empty_register(self):
		email = f"comm-{uuid.uuid4().hex[:8]}@example.invalid"
		frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "Comm",
			"send_welcome_email": 0,
		}).insert(ignore_permissions=True).add_roles("Sales User", "Accounts User")
		people = [self._person() for _ in range(3)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team(people))
		self._invoiced(customer)

		frappe.set_user(email)
		try:
			data = list_commissions()
			self.assertEqual(data["rows"], [])
			self.assertFalse(data["can_see_everyone"])
		finally:
			frappe.set_user("Administrator")

	def test_a_sales_manager_sees_the_whole_register(self):
		email = f"comm-mgr-{uuid.uuid4().hex[:6]}@example.invalid"
		frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "CommMgr",
			"send_welcome_email": 0,
		}).insert(ignore_permissions=True).add_roles("Sales Manager", "Accounts User")
		people = [self._person() for _ in range(3)]
		customer = self._customer()
		assign_customer_sales_team(customer, self._team(people))
		_so, invoice = self._invoiced(customer)

		frappe.set_user(email)
		try:
			data = list_commissions(sales_invoice=invoice.name)
			self.assertTrue(data["can_see_everyone"])
			self.assertEqual(len(data["rows"]), 3)
		finally:
			frappe.set_user("Administrator")

	def test_a_user_without_invoice_read_is_refused_outright(self):
		"""The register reports invoice data, so it requires the same permission the
		data does. Sales User alone does not have it in ERPNext v15."""
		email = f"comm-noinv-{uuid.uuid4().hex[:6]}@example.invalid"
		frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "NoInv",
			"send_welcome_email": 0,
		}).insert(ignore_permissions=True).add_roles("Sales User")
		frappe.set_user(email)
		try:
			with self.assertRaises(frappe.PermissionError):
				list_commissions()
		finally:
			frappe.set_user("Administrator")

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				list_commissions()
		finally:
			frappe.set_user("Administrator")

	def test_sales_person_lookup_is_empty_for_an_unlinked_user(self):
		self.assertEqual(sales_persons_for_user("Administrator"), [])


class TestTeamPerformanceAndHistory(CommissionBase):
	def test_performance_counts_customers_and_commission(self):
		people = [self._person() for _ in range(3)]
		team = self._team(people)
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		self._invoiced(customer)

		data = get_team_performance(team)
		self.assertEqual(data["assigned_customers"], 1)
		self.assertEqual(data["active_customers"], 1)
		self.assertEqual(data["orders"], 1)
		self.assertEqual(flt(data["invoiced_sales"]), 100000.0)
		self.assertEqual(flt(data["earned_commission"]), 2000.0)
		self.assertEqual(flt(data["net_commission"]), 2000.0)

	def test_performance_nets_off_a_return(self):
		from my_store_ui.wholesale.returns import create_credit_note

		people = [self._person() for _ in range(3)]
		team = self._team(people)
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		_so, invoice = self._invoiced(customer)
		create_credit_note(invoice.name, submit=1)

		data = get_team_performance(team)
		self.assertEqual(flt(data["earned_commission"]), 2000.0)
		self.assertEqual(flt(data["reversed_commission"]), -2000.0)
		self.assertEqual(flt(data["net_commission"]), 0.0)

	def test_customer_history_shows_the_team_each_order_was_raised_with(self):
		people = [self._person() for _ in range(3)]
		first = self._team(people)
		customer = self._customer()
		assign_customer_sales_team(customer, first)
		self._invoiced(customer)

		second = self._team([self._person() for _ in range(3)])
		assign_customer_sales_team(customer, second)
		self._invoiced(customer)

		history = get_customer_commission_history(customer)
		teams = {row["team"] for row in history["transactions"]}
		self.assertEqual(teams, {first, second},
		                 "each order keeps the team it was raised with")

	def test_customer_history_records_the_reassignment(self):
		"""Frappe sets `ignore_version = frappe.flags.in_test` on every save, so the
		test runner writes no Version rows at all. The flag is cleared here so the
		production path is the one under test -- otherwise this would pass on a
		feature that never runs."""
		people = [self._person() for _ in range(3)]
		first = self._team(people)
		second = self._team([self._person() for _ in range(3)])
		customer = self._customer()

		was_in_test = frappe.flags.in_test
		frappe.flags.in_test = False
		try:
			assign_customer_sales_team(customer, first)
			assign_customer_sales_team(customer, second)
		finally:
			frappe.flags.in_test = was_in_test

		history = get_customer_commission_history(customer)["assignment_history"]
		self.assertTrue(history, "the Version trail must record the change")
		self.assertEqual(history[0]["new_team"], second)
		self.assertEqual(history[0]["previous_team"], first)

	def test_history_for_a_customer_with_nothing_is_empty_not_broken(self):
		data = get_customer_commission_history(self._customer())
		self.assertEqual(data["transactions"], [])
		self.assertEqual(data["assignment_history"], [])


if __name__ == "__main__":
	unittest.main()
