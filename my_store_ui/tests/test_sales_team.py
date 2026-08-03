"""Sales Teams, customer assignment and the commission snapshot.

The structural rules are enforced by the controller, so they hold for any caller --
the Retail ERP form, a direct API request, or the Desk. Savepoint + rollback.
"""

from __future__ import annotations

import json
import unittest
import uuid

import frappe
from frappe.utils import flt, nowdate

from my_store_ui.sales_team import (
	assign_customer_sales_team,
	get_customer_sales_assignment,
	get_document_sales_team,
	get_sales_team,
	list_sales_teams,
	save_sales_team,
	search_sales_persons,
	team_payload,
)
from my_store_ui.standalone import authorize_frontend_route

SALES_USER = "steam-sales@example.invalid"
REP_USER = "steam-rep@example.invalid"


class SalesTeamBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"steam_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")
		self.people = [self._person() for _ in range(4)]

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _person(self):
		name = f"SP {uuid.uuid4().hex[:8]}"
		doc = frappe.get_doc({
			"doctype": "Sales Person", "sales_person_name": name, "is_group": 0,
			"parent_sales_person": "",
		})
		doc.insert(ignore_permissions=True)
		return doc.name

	def _members(self, shares=(50, 25, 25), roles=None):
		roles = roles or ["Sales Manager", "Sales Representative", "Sales Representative"]
		return [
			{"sales_person": self.people[i], "team_role": roles[i],
			 "share_percentage": shares[i], "is_active": True}
			for i in range(len(shares))
		]

	def _team(self, **over):
		payload = {
			"team_name": f"Team {uuid.uuid4().hex[:6]}", "commission_rate": 4,
			"effective_from": nowdate(), "is_active": True, "members": self._members(),
		}
		payload.update(over)
		return save_sales_team(payload)

	def _customer(self):
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": f"STCust {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
			"default_price_list": "Wholesale Price List",
		}).insert(ignore_permissions=True).name

	def _user(self, email, roles):
		if not frappe.db.exists("User", email):
			doc = frappe.get_doc({
				"doctype": "User", "email": email, "first_name": "ST",
				"send_welcome_email": 0,
			})
			doc.insert(ignore_permissions=True)
			doc.add_roles(*roles)
		return email


class TestSalesTeamMaster(SalesTeamBase):
	def test_route_resolves(self):
		self.assertEqual(authorize_frontend_route("/sales/teams")["outcome"], "allowed")

	def test_new_record_contract_holds_however_it_is_called(self):
		"""Regression: the frontend helper once dropped name="" and the endpoint ran
		with no argument, returning HTTP 500 and a blank form body. Every form of the
		new-record call must return the new-team shape."""
		for call in (lambda: get_sales_team(), lambda: get_sales_team(""),
		             lambda: get_sales_team(name="")):
			data = call()
			self.assertTrue(data["is_new"])
			self.assertEqual(len(data["team"]["members"]), 3)

	def test_no_retail_erp_endpoint_requires_an_argument_the_ui_may_blank(self):
		"""Any whitelisted endpoint the UI calls with a possibly-empty value must
		declare a default, or the same 500 returns on a different page."""
		import inspect

		import my_store_ui.sales_team as module

		for attr in ("get_sales_team", "list_sales_teams", "search_sales_persons"):
			fn = getattr(module, attr)
			sig = inspect.signature(getattr(fn, "__wrapped__", fn))
			required = [
				p.name for p in sig.parameters.values()
				if p.default is inspect.Parameter.empty
				and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
			]
			self.assertFalse(required, f"{attr} would break on a blank value: {required}")

	def test_default_new_team_is_50_25_25(self):
		data = get_sales_team("")
		members = data["team"]["members"]
		self.assertEqual([m["share_percentage"] for m in members], [50.0, 25.0, 25.0])
		self.assertEqual(members[0]["team_role"], "Sales Manager")
		self.assertEqual(
			[m["team_role"] for m in members[1:]],
			["Sales Representative", "Sales Representative"],
		)
		self.assertTrue(data["is_new"])

	def test_create_a_team_with_the_default_split(self):
		res = self._team()
		doc = frappe.get_doc("Retail Sales Team", res["name"])
		self.assertEqual(len(doc.members), 3)
		self.assertEqual(doc.sales_manager, self.people[0])
		self.assertTrue(doc.name.startswith("STM-"), doc.name)

	def test_team_code_is_generated(self):
		res = self._team()
		self.assertEqual(get_sales_team(res["name"])["team"]["team_code"], res["name"])

	def test_shares_totalling_90_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(members=self._members(shares=(50, 25, 15)))

	def test_shares_totalling_110_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(members=self._members(shares=(60, 25, 25)))

	def test_exactly_100_is_accepted(self):
		res = self._team(members=self._members(shares=(40, 30, 30)))
		self.assertTrue(res["name"])

	def test_more_than_two_representatives_is_supported(self):
		members = self._members(
			shares=(40, 20, 20),
			roles=["Sales Manager", "Sales Representative", "Sales Representative"],
		)
		members.append({"sales_person": self.people[3], "team_role": "Sales Representative",
		                "share_percentage": 20, "is_active": True})
		res = self._team(members=members)
		self.assertEqual(len(frappe.get_doc("Retail Sales Team", res["name"]).members), 4)

	def test_duplicate_person_is_rejected(self):
		members = self._members()
		members[2]["sales_person"] = members[1]["sales_person"]
		with self.assertRaises(frappe.ValidationError):
			self._team(members=members)

	def test_a_team_needs_an_active_manager(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(members=self._members(
				roles=["Sales Representative"] * 3, shares=(50, 25, 25)))

	def test_two_managers_are_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(members=self._members(
				roles=["Sales Manager", "Sales Manager", "Sales Representative"]))

	def test_negative_share_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(members=self._members(shares=(120, -10, -10)))

	def test_inactive_members_are_excluded_from_the_total(self):
		members = self._members()
		members.append({"sales_person": self.people[3], "team_role": "Sales Representative",
		                "share_percentage": 40, "is_active": False})
		res = self._team(members=members)          # active still totals 100
		payload = team_payload(res["name"])
		self.assertEqual(len(payload["members"]), 3)
		self.assertEqual(flt(payload["total_share"]), 100.0)

	def test_effective_to_before_from_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(effective_from=nowdate(),
			           effective_to=frappe.utils.add_days(nowdate(), -3))

	def test_commission_rate_out_of_range_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self._team(commission_rate=140)

	def test_editing_a_team_updates_it(self):
		res = self._team()
		save_sales_team({
			"team_name": "Renamed Team " + uuid.uuid4().hex[:4], "commission_rate": 6,
			"effective_from": nowdate(), "is_active": True,
			"members": self._members(shares=(60, 20, 20)),
		}, name=res["name"])
		doc = frappe.get_doc("Retail Sales Team", res["name"])
		self.assertEqual(flt(doc.commission_rate), 6.0)
		self.assertEqual(flt(doc.members[0].share_percentage), 60.0)

	def test_list_filters_and_paginates(self):
		self._team()
		result = list_sales_teams(is_active="1", page_size=5)
		self.assertIn("rows", result)
		self.assertLessEqual(len(result["rows"]), 5)
		self.assertIn("pagination", result)
		self.assertTrue(result["can_manage"])

	def test_list_rejects_an_unsupported_sort(self):
		with self.assertRaises(frappe.ValidationError):
			list_sales_teams(sort_field="commission_rate; DROP TABLE")

	def test_search_sales_persons_returns_options(self):
		rows = search_sales_persons(self.people[0][:6])
		self.assertTrue(any(r["value"] == self.people[0] for r in rows))


class TestCustomerAssignment(SalesTeamBase):
	def test_assign_and_read_back(self):
		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		data = get_customer_sales_assignment(customer)
		self.assertTrue(data["assigned"])
		self.assertEqual(data["assignment"]["team"], team)
		self.assertEqual(len(data["assignment"]["members"]), 3)
		self.assertEqual(flt(data["assignment"]["total_share"]), 100.0)

	def test_assignment_projects_onto_erpnext_sales_team_rows(self):
		"""Standard ERPNext reporting must keep working, not be replaced."""
		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		rows = frappe.get_doc("Customer", customer).get("sales_team") or []
		self.assertEqual(len(rows), 3)
		self.assertEqual(flt(sum(flt(r.allocated_percentage) for r in rows)), 100.0)

	def test_unassigned_customer_reports_no_team(self):
		data = get_customer_sales_assignment(self._customer())
		self.assertFalse(data["assigned"])
		self.assertIsNone(data["assignment"])

	def test_assignment_can_be_cleared(self):
		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		assign_customer_sales_team(customer, "")
		self.assertFalse(get_customer_sales_assignment(customer)["assigned"])

	def test_invalid_team_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			assign_customer_sales_team(self._customer(), "STM-NOPE")

	def test_inactive_team_cannot_be_assigned(self):
		team = self._team(is_active=False)["name"]
		with self.assertRaises(frappe.ValidationError):
			assign_customer_sales_team(self._customer(), team)


class TestSalesOrderSnapshot(SalesTeamBase):
	def _item(self):
		from my_store_ui.quick_entry.product import create_product

		group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": self.company, "disabled": 0},
			pluck="name")[0]
		return create_product({
			"product_name": f"STItem {uuid.uuid4().hex[:5]}", "category": group,
			"stock_location_1": wh, "cost_price": 1000, "wholesale_price": 1200,
			"retail_price": 1500,
		})["name"], wh

	def _receive(self, item, wh, qty=50):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
			"company": self.company,
			"items": [{"item_code": item, "qty": qty, "t_warehouse": wh, "basic_rate": 1000}],
		})
		se.insert(ignore_permissions=True)
		se.submit()

	def _order(self, customer, with_stock=False):
		item, wh = self._item()
		if with_stock:
			self._receive(item, wh)
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": 2, "rate": 1200, "warehouse": wh,
			           "delivery_date": frappe.utils.add_days(nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		return so

	def test_order_stores_a_snapshot(self):
		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		so = self._order(customer)
		self.assertEqual(so.custom_sales_team, team)
		self.assertTrue(so.custom_sales_team_snapshot)
		snapshot = json.loads(so.custom_sales_team_snapshot)
		self.assertEqual(len(snapshot["members"]), 3)
		self.assertEqual(flt(snapshot["commission_rate"]), 4.0)
		self.assertEqual(snapshot["source_customer"], customer)

	def test_reassigning_the_customer_does_not_change_the_old_order(self):
		"""The whole point of the snapshot."""
		first = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, first)
		so = self._order(customer)
		original = json.loads(so.custom_sales_team_snapshot)

		second = self._team(members=self._members(shares=(70, 30), roles=[
			"Sales Manager", "Sales Representative"]))["name"]
		assign_customer_sales_team(customer, second)

		so.reload()
		self.assertEqual(so.custom_sales_team, first, "the old order must keep its team")
		self.assertEqual(json.loads(so.custom_sales_team_snapshot), original)

		later = self._order(customer)
		self.assertEqual(later.custom_sales_team, second, "a new order uses the new team")

	def test_editing_the_team_master_does_not_change_the_old_order(self):
		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		so = self._order(customer)
		before = json.loads(so.custom_sales_team_snapshot)

		save_sales_team({
			"team_name": frappe.db.get_value("Retail Sales Team", team, "team_name"),
			"commission_rate": 9, "effective_from": nowdate(), "is_active": True,
			"members": self._members(shares=(80, 10, 10)),
		}, name=team)

		so.reload()
		self.assertEqual(json.loads(so.custom_sales_team_snapshot), before)
		self.assertEqual(flt(so.custom_team_commission_rate), 4.0)

	def test_customer_without_a_team_leaves_the_snapshot_empty(self):
		so = self._order(self._customer())
		self.assertFalse(so.get("custom_sales_team_snapshot"))

	def test_delivery_note_inherits_the_orders_snapshot(self):
		from my_store_ui.wholesale.delivery import create_delivery_note

		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		so = self._order(customer, with_stock=True)
		so.submit()

		note = create_delivery_note(so.name, override_reason="Snapshot test", submit=0)
		doc = frappe.get_doc("Delivery Note", note["name"])
		self.assertEqual(doc.custom_sales_team, team)
		self.assertEqual(
			json.loads(doc.custom_sales_team_snapshot),
			json.loads(so.custom_sales_team_snapshot),
		)

	def test_get_document_sales_team_reads_the_snapshot(self):
		team = self._team()["name"]
		customer = self._customer()
		assign_customer_sales_team(customer, team)
		so = self._order(customer)
		data = get_document_sales_team("Sales Order", so.name)
		self.assertTrue(data["assigned"])
		self.assertEqual(data["assignment"]["team"], team)

	def test_unsupported_doctype_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			get_document_sales_team("Customer", "whatever")


class TestSalesTeamPermissions(SalesTeamBase):
	def test_a_sales_user_can_read_but_not_change_a_team(self):
		team = self._team()["name"]
		user = self._user(SALES_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			self.assertTrue(list_sales_teams()["rows"] is not None)
			self.assertFalse(list_sales_teams()["can_manage"])
			with self.assertRaises(frappe.PermissionError):
				save_sales_team({"team_name": "Nope", "effective_from": nowdate(),
				                 "members": self._members()})
			with self.assertRaises(frappe.PermissionError):
				assign_customer_sales_team(self._customer(), team)
		finally:
			frappe.set_user("Administrator")

	def test_a_sales_manager_can_manage_teams(self):
		user = self._user("steam-mgr@example.invalid", ["Sales Manager", "Sales User"])
		frappe.set_user(user)
		try:
			self.assertTrue(list_sales_teams()["can_manage"])
		finally:
			frappe.set_user("Administrator")

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				list_sales_teams()
		finally:
			frappe.set_user("Administrator")


if __name__ == "__main__":
	unittest.main()
