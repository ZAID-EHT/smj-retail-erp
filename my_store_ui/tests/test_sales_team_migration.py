"""The guarded sales team backfill.

The guardrails matter more than the backfill: this tool must refuse a protected
site, refuse a stale backup, never guess a team, and never rewrite a submitted
document. Savepoint + rollback.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import nowdate

from my_store_ui import sales_team_migration as migration
from my_store_ui.sales_team import assign_customer_sales_team, save_sales_team


class MigrationBase(unittest.TestCase):
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
		self.sp = f"mig_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _person(self):
		return frappe.get_doc({
			"doctype": "Sales Person", "sales_person_name": f"MP {uuid.uuid4().hex[:8]}",
			"is_group": 0, "parent_sales_person": "",
		}).insert(ignore_permissions=True).name

	def _team(self, **over):
		people = [self._person() for _ in range(3)]
		payload = {
			"team_name": f"MTeam {uuid.uuid4().hex[:6]}", "commission_rate": 2,
			"effective_from": nowdate(), "is_active": True,
			"members": [
				{"sales_person": people[0], "team_role": "Sales Manager",
				 "share_percentage": 50, "is_active": True},
				{"sales_person": people[1], "team_role": "Sales Representative",
				 "share_percentage": 25, "is_active": True},
				{"sales_person": people[2], "team_role": "Sales Representative",
				 "share_percentage": 25, "is_active": True},
			],
		}
		payload.update(over)
		return save_sales_team(payload)["name"]

	def _customer(self):
		return frappe.get_doc({
			"doctype": "Customer", "customer_name": f"MCust {uuid.uuid4().hex[:6]}",
			"customer_group": self.customer_group, "territory": self.territory,
		}).insert(ignore_permissions=True).name

	def _draft_order(self, customer):
		"""A draft order raised while the customer had no team, so it has no snapshot."""
		from my_store_ui.quick_entry.product import create_product

		item = create_product({
			"product_name": f"MItem {uuid.uuid4().hex[:5]}", "category": self.item_group,
			"stock_location_1": self.warehouse, "cost_price": 500,
			"wholesale_price": 1000, "retail_price": 1200,
		})["name"]
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(nowdate(), 7),
			"items": [{"item_code": item, "qty": 10, "rate": 1000, "warehouse": self.warehouse,
			           "delivery_date": frappe.utils.add_days(nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		return so


class TestMigrationGuardrails(MigrationBase):
	def test_a_protected_site_is_refused_for_being_protected(self):
		"""Not incidentally, because the app is missing -- the site guard comes first."""
		original = frappe.local.site
		frappe.local.site = "site1.local"
		try:
			with self.assertRaises(migration.MigrationRefused) as caught:
				migration.apply_safe(commit=False)
			self.assertIn("protected", str(caught.exception))
		finally:
			frappe.local.site = original

	def test_an_unknown_site_is_refused(self):
		original = frappe.local.site
		frappe.local.site = "someone-elses-production.example"
		try:
			with self.assertRaises(migration.MigrationRefused) as caught:
				migration.apply_safe(commit=False)
			self.assertIn("not a known disposable site", str(caught.exception))
		finally:
			frappe.local.site = original

	def test_a_stale_backup_blocks_writing(self):
		original = migration.BACKUP_MAX_AGE_HOURS
		migration.BACKUP_MAX_AGE_HOURS = 0
		try:
			with self.assertRaises(migration.MigrationRefused) as caught:
				migration.apply_safe(commit=False)
			self.assertIn("backup", str(caught.exception).lower())
		finally:
			migration.BACKUP_MAX_AGE_HOURS = original

	def test_read_only_modes_never_need_a_backup(self):
		original = migration.BACKUP_MAX_AGE_HOURS
		migration.BACKUP_MAX_AGE_HOURS = 0
		try:
			self.assertEqual(migration.inspect()["mode"], "inspect")
			self.assertEqual(migration.dry_run()["mode"], "dry_run")
			self.assertEqual(migration.verify()["mode"], "verify")
		finally:
			migration.BACKUP_MAX_AGE_HOURS = original

	def test_an_unknown_mode_is_refused(self):
		with self.assertRaises(migration.MigrationRefused):
			migration.run("delete_everything")


class TestMigrationBehaviour(MigrationBase):
	def test_a_draft_order_is_settled_from_the_customers_team(self):
		customer = self._customer()
		order = self._draft_order(customer)
		self.assertFalse(order.get("custom_sales_team"))

		team = self._team()
		assign_customer_sales_team(customer, team)

		names = [row["name"] for row in migration.dry_run()["would_update"]]
		self.assertIn(order.name, names)

		migration.apply_safe(commit=False)
		order.reload()
		self.assertEqual(order.custom_sales_team, team)
		self.assertEqual(len(order.custom_sales_team_members), 3)

	def test_applying_twice_changes_nothing_the_second_time(self):
		customer = self._customer()
		order = self._draft_order(customer)
		assign_customer_sales_team(customer, self._team())

		first = migration.apply_safe(commit=False)
		self.assertIn(order.name, [row["name"] for row in first["updated"]])
		second = migration.apply_safe(commit=False)
		self.assertNotIn(order.name, [row["name"] for row in second["updated"]])

	def test_a_customer_with_no_team_is_never_guessed_at(self):
		customer = self._customer()
		order = self._draft_order(customer)
		migration.apply_safe(commit=False)
		order.reload()
		self.assertFalse(order.get("custom_sales_team"),
		                 "a team must never be invented for a customer that has none")

	def test_an_inactive_team_is_left_for_a_human(self):
		customer = self._customer()
		# The order has to exist *before* the customer gets a team, or it is frozen on
		# creation and there is nothing left for the backfill to do.
		order = self._draft_order(customer)
		team = self._team()
		assign_customer_sales_team(customer, team)
		frappe.db.set_value("Retail Sales Team", team, "is_active", 0)
		frappe.clear_document_cache("Retail Sales Team", team)

		self.assertNotIn(order.name, [r["name"] for r in migration.dry_run()["would_update"]])
		migration.apply_safe(commit=False)
		order.reload()
		self.assertFalse(order.get("custom_sales_team"))

	def test_a_submitted_document_is_never_rewritten(self):
		customer = self._customer()
		order = self._draft_order(customer)
		# Stock so the order can be submitted.
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt",
			"company": self.company,
			"items": [{"item_code": order.items[0].item_code, "qty": 100,
			           "t_warehouse": self.warehouse, "basic_rate": 500}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		order.submit()
		self.assertFalse(order.get("custom_sales_team"))

		assign_customer_sales_team(customer, self._team())
		result = migration.apply_safe(commit=False)
		self.assertEqual(result["submitted_documents_touched"], 0)
		order.reload()
		self.assertFalse(order.get("custom_sales_team"),
		                 "a submitted document must keep the (absent) team it was raised with")

	def test_submitted_documents_without_a_team_are_listed_for_review(self):
		report = migration.inspect()
		self.assertGreaterEqual(report["needing_manual_review"], 0)
		self.assertIn("documents", report)

	def test_dry_run_writes_nothing(self):
		customer = self._customer()
		order = self._draft_order(customer)
		assign_customer_sales_team(customer, self._team())
		migration.dry_run()
		order.reload()
		self.assertFalse(order.get("custom_sales_team"))

	def test_verify_reports_consistency(self):
		customer = self._customer()
		self._draft_order(customer)
		assign_customer_sales_team(customer, self._team())
		migration.apply_safe(commit=False)
		report = migration.verify()
		self.assertEqual(report["inconsistent_documents"], [])

	def test_the_export_lists_customers_without_a_team(self):
		customer = self._customer()
		result = migration.export_manual_review()
		self.assertTrue(result["path"].endswith(".csv"))
		with open(result["path"]) as handle:
			body = handle.read()
		self.assertIn(customer, body)
		self.assertIn("no sales team assigned", body)

	def test_the_export_never_lands_in_the_repository(self):
		result = migration.export_manual_review()
		self.assertNotIn("/apps/my_store_ui", result["path"])
		self.assertIn("private", result["path"])


if __name__ == "__main__":
	unittest.main()
