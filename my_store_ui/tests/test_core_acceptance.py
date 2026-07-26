"""Reproducible acceptance scenarios for the SMJ core wholesale workflow.

Scenarios 1-9 are asserted by the focused modules listed in
`docs/workflows/SMJ_CORE_ACCEPTANCE_SCENARIOS.md`; this module covers the two
that had no end-to-end coverage -- simplified entry forms (10) and the full user
lifecycle (11) -- and asserts the cross-cutting claims those scenarios make.

All fixtures are fictional and removed afterwards. Credentials are generated per
run and never written to any document.
"""

from __future__ import annotations

import json
import unittest
import uuid

import frappe
from frappe.core.doctype.user.user import User
from frappe.utils import flt

from my_store_ui.access_management import get_user_access_overview, set_user_restrictions
from my_store_ui.form_api import save_entity_form

LIFECYCLE_USER = "smj-acceptance-lifecycle@example.com"
PROFILE = "SMJ Acceptance Profile"
CUSTOMER = "SMJ Acceptance Customer"
SUPPLIER = "SMJ Acceptance Supplier"
PRODUCT = "SMJ-ACCEPTANCE-PRODUCT"


def _password() -> str:
	"""A fresh throwaway password per run -- never persisted to any doc or doc file."""
	return f"Smj!{uuid.uuid4().hex[:16]}"


class TestCoreAcceptance(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.item_group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.supplier_group = frappe.get_all("Supplier Group", filters={"is_group": 0}, pluck="name")[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
		cls._cleanup()
		if not frappe.db.exists("Role Profile", PROFILE):
			profile = frappe.get_doc({"doctype": "Role Profile", "role_profile": PROFILE})
			profile.append("roles", {"role": "Sales User"})
			profile.insert(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		cls._cleanup()
		frappe.db.commit()

	@classmethod
	def _cleanup(cls):
		for name in frappe.get_all("User Permission", filters={"user": LIFECYCLE_USER}, pluck="name"):
			frappe.delete_doc("User Permission", name, force=True, ignore_permissions=True)
		for name in frappe.get_all("Item Price", filters={"item_code": PRODUCT}, pluck="name"):
			frappe.delete_doc("Item Price", name, force=True, ignore_permissions=True)
		for doctype, name in (
			("User", LIFECYCLE_USER), ("Item", PRODUCT),
			("Customer", CUSTOMER), ("Supplier", SUPPLIER), ("Role Profile", PROFILE),
		):
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)

	def tearDown(self):
		frappe.set_user("Administrator")
		# Each scenario creates the lifecycle user from scratch, so remove it
		# between tests rather than letting one scenario collide with the next.
		for name in frappe.get_all("User Permission", filters={"user": LIFECYCLE_USER}, pluck="name"):
			frappe.delete_doc("User Permission", name, force=True, ignore_permissions=True)
		if frappe.db.exists("User", LIFECYCLE_USER):
			frappe.delete_doc("User", LIFECYCLE_USER, force=True, ignore_permissions=True)
		frappe.db.commit()

	# -- Scenario 10 --------------------------------------------------------

	def test_scenario_10_simplified_forms_create_valid_master_records(self):
		"""Customer, Supplier and Product all save through the curated forms."""
		customer = save_entity_form("customers", json.dumps({
			"customer_name": CUSTOMER, "customer_type": "Company",
			"customer_group": self.customer_group, "territory": self.territory,
		}))
		self.assertTrue(frappe.db.exists("Customer", customer["name"]))

		from my_store_ui.universal.api import create_document

		supplier = create_document(feature="supplier", values={
			"supplier_name": SUPPLIER, "supplier_group": self.supplier_group,
		})
		self.assertTrue(frappe.db.exists("Supplier", supplier["name"]))

		product = save_entity_form("items", json.dumps({
			"item_code": PRODUCT, "item_name": "SMJ Acceptance Product",
			"item_group": self.item_group, "stock_uom": "Nos", "is_stock_item": 1,
			"custom_purchase_price": 500.0, "custom_additional_cost": 100.0,
			"custom_retail_profit_percentage": 40.0, "custom_wholesale_profit_percentage": 20.0,
		}))
		self.assertEqual(product["name"], PRODUCT)

		# The scenario's real requirement: prices reach the pricing engine.
		prices = {
			row.price_list: flt(row.price_list_rate)
			for row in frappe.get_all(
				"Item Price", filters={"item_code": PRODUCT}, fields=["price_list", "price_list_rate"]
			)
		}
		self.assertEqual(prices.get("Standard Buying"), 500.0)
		self.assertEqual(prices.get("Retail Price List"), 600.0 * 1.4)
		self.assertEqual(prices.get("Wholesale Price List"), 600.0 * 1.2)

	# -- Scenario 11 --------------------------------------------------------

	def test_scenario_11_user_lifecycle_end_to_end(self):
		"""Create, password, profile, direct role, restrict, log in, disable, reactivate."""
		from my_store_ui.universal.api import create_document, update_document

		password = _password()

		# 1. Create with an initial password and a role, through the real form engine.
		created = create_document(feature="user", values={
			"email": LIFECYCLE_USER, "first_name": "SMJ Acceptance",
			"new_password": password, "enabled": 1,
			"roles": [{"role": "Sales User"}],
		})
		self.assertEqual(created["name"], LIFECYCLE_USER)

		# 2. The password must work and must never be readable back.
		authenticated = User.find_by_credentials(LIFECYCLE_USER, password)
		self.assertTrue(authenticated and authenticated["is_authenticated"])
		self.assertTrue(authenticated["enabled"])
		from my_store_ui.universal.api import get_document_detail

		detail = get_document_detail(feature="user", name=LIFECYCLE_USER)
		serialised = json.dumps(detail, default=str)
		self.assertNotIn(password, serialised, "a password must never be returned to the browser")

		# 3. Assign a Role Profile. In Frappe v15 the profile is authoritative:
		#    User.validate calls populate_role_profile_roles() on *every* save, which
		#    clears `roles` and re-applies the profile's. A direct role therefore
		#    cannot coexist with an assigned profile -- asserted rather than assumed,
		#    because the admin UI has to reflect it.
		update_document(feature="user", name=LIFECYCLE_USER, values={
			"role_profile_name": PROFILE,
			"roles": [{"role": "Sales User"}, {"role": "Stock User"}],
		})
		roles = frappe.get_roles(LIFECYCLE_USER)
		self.assertIn("Sales User", roles, "the profile's roles apply")
		self.assertNotIn("Stock User", roles, "an assigned Role Profile overrides direct roles")

		# 4. Remove the profile, and direct roles apply again.
		update_document(feature="user", name=LIFECYCLE_USER, values={
			"role_profile_name": None,
			"roles": [{"role": "Sales User"}, {"role": "Stock User"}],
		})
		roles = frappe.get_roles(LIFECYCLE_USER)
		self.assertIn("Sales User", roles)
		self.assertIn("Stock User", roles, "direct roles apply once no profile is assigned")

		# 5. Restrict to one company and one warehouse.
		warehouse = frappe.get_all(
			"Warehouse", filters={"company": self.company, "is_group": 0}, pluck="name", limit_page_length=1
		)
		set_user_restrictions(user=LIFECYCLE_USER, doctype="Company", values=[self.company])
		if warehouse:
			set_user_restrictions(user=LIFECYCLE_USER, doctype="Warehouse", values=warehouse)

		overview = get_user_access_overview(user=LIFECYCLE_USER)
		restrictions = {row["doctype"]: row for row in overview["restrictions"]}
		self.assertTrue(restrictions["Company"]["restricted"])
		self.assertEqual(restrictions["Company"]["values"], [self.company])

		# 6/7. Allowed vs denied routes, evaluated by the backend for this user.
		permissions = {row["doctype"]: row for row in overview["permissions"]}
		self.assertTrue(permissions["Sales Order"]["create"], "a Sales User may raise a Sales Order")
		self.assertFalse(permissions["Purchase Order"]["create"], "and may not raise a Purchase Order")
		self.assertFalse(permissions["User"]["create"], "and may not administer users")

		# 8. Disable -- Frappe's own login path must then refuse the account.
		update_document(feature="user", name=LIFECYCLE_USER, values={"enabled": 0})
		disabled = User.find_by_credentials(LIFECYCLE_USER, password)
		self.assertFalse(disabled["enabled"], "a disabled account must be refused at login")

		# 9. Reactivate -- the same credentials work again.
		update_document(feature="user", name=LIFECYCLE_USER, values={"enabled": 1})
		reactivated = User.find_by_credentials(LIFECYCLE_USER, password)
		self.assertTrue(reactivated["enabled"])
		self.assertTrue(reactivated["is_authenticated"])

	def test_scenario_11_a_wrong_password_is_refused(self):
		"""The credential check must actually be a credential check."""
		from my_store_ui.universal.api import create_document

		password = _password()
		create_document(feature="user", values={
			"email": LIFECYCLE_USER, "first_name": "SMJ Acceptance",
			"new_password": password, "enabled": 1, "roles": [{"role": "Sales User"}],
		})
		self.assertTrue(User.find_by_credentials(LIFECYCLE_USER, password)["is_authenticated"])
		wrong = User.find_by_credentials(LIFECYCLE_USER, _password())
		self.assertFalse(wrong and wrong.get("is_authenticated"))


if __name__ == "__main__":
	unittest.main()
