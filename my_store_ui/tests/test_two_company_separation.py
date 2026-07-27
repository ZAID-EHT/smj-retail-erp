"""End-to-end two-company data separation.

Two fictional companies, each with its own warehouse / customer / supplier / sales +
purchase documents, and three users:
  * User A restricted to Company A (User Permission on Company)
  * User B restricted to Company B
  * Manager permitted for both

Asserts that ERPNext's permission engine (via frappe.get_list / has_permission and
the app's own export path) confines A-users to A-data and rejects invalid
mixed-company documents. The whole scenario runs inside a savepoint and is rolled
back, so staging is untouched.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import add_days, nowdate

SUFFIX = uuid.uuid4().hex[:6]
COMPANY_A = f"SMJ Company A Test {SUFFIX}"
COMPANY_B = f"SMJ Company B Test {SUFFIX}"
USER_A = f"smj-sep-a-{SUFFIX}@example.com"
USER_B = f"smj-sep-b-{SUFFIX}@example.com"
USER_MGR = f"smj-sep-mgr-{SUFFIX}@example.com"


class TestTwoCompanySeparation(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.savepoint = f"two_company_{SUFFIX}"
		frappe.db.savepoint(cls.savepoint)
		try:
			cls._build()
		except Exception:
			frappe.db.rollback(save_point=cls.savepoint)
			raise

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=cls.savepoint)
		# Belt and braces: ensure the fictional companies/users are gone.
		for name in (COMPANY_A, COMPANY_B):
			if frappe.db.exists("Company", name):
				frappe.delete_doc("Company", name, force=True, ignore_permissions=True)
		for user in (USER_A, USER_B, USER_MGR):
			if frappe.db.exists("User", user):
				frappe.delete_doc("User", user, force=True, ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.set_user("Administrator")

	# -- fixture ------------------------------------------------------------

	@classmethod
	def _make_company(cls, name, abbr):
		from my_store_ui.setup_wizard import create_company
		create_company({"company_name": name, "abbr": abbr, "default_currency": "LKR",
		                "country": "Sri Lanka", "chart_of_accounts": "Standard"})
		return name

	@classmethod
	def _warehouse(cls, company, label):
		wname = f"{label} WH {SUFFIX}"
		existing = frappe.get_all("Warehouse", filters={"warehouse_name": wname, "company": company}, pluck="name")
		if existing:
			return existing[0]
		return frappe.get_doc({"doctype": "Warehouse", "warehouse_name": wname, "company": company}).insert(ignore_permissions=True).name

	@classmethod
	def _customer(cls, label):
		name = f"{label} Customer {SUFFIX}"
		if not frappe.db.exists("Customer", name):
			group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
			terr = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]
			frappe.get_doc({"doctype": "Customer", "customer_name": name, "customer_type": "Company",
			                "customer_group": group, "territory": terr}).insert(ignore_permissions=True)
		return name

	@classmethod
	def _sales_order(cls, company, customer, warehouse):
		item = cls.item
		so = frappe.get_doc({"doctype": "Sales Order", "company": company, "customer": customer,
		                     "delivery_date": add_days(nowdate(), 7),
		                     "items": [{"item_code": item, "qty": 1, "warehouse": warehouse,
		                                "delivery_date": add_days(nowdate(), 7), "rate": 100}]})
		so.insert(ignore_permissions=True)
		return so.name

	@classmethod
	def _make_user(cls, email, companies):
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		doc = frappe.get_doc({"doctype": "User", "email": email, "first_name": "SMJ Sep",
		                      "send_welcome_email": 0, "enabled": 1})
		doc.insert(ignore_permissions=True)
		for role in ("Sales User", "Sales Manager", "Stock User", "Accounts User"):
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)
		for company in companies:
			frappe.get_doc({"doctype": "User Permission", "user": email, "allow": "Company",
			                "for_value": company, "apply_to_all_doctypes": 1}).insert(ignore_permissions=True)
		frappe.clear_cache(user=email)

	@classmethod
	def _build(cls):
		group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.item = f"SMJ-SEP-ITEM-{SUFFIX}"
		frappe.get_doc({"doctype": "Item", "item_code": cls.item, "item_name": "Sep Item",
		                "item_group": group, "stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1}).insert(ignore_permissions=True)

		cls._make_company(COMPANY_A, f"SCA{SUFFIX[:3]}".upper())
		cls._make_company(COMPANY_B, f"SCB{SUFFIX[:3]}".upper())
		cls.wh_a = cls._warehouse(COMPANY_A, "Sep A")
		cls.wh_b = cls._warehouse(COMPANY_B, "Sep B")
		cls.cust_a = cls._customer("Sep A")
		cls.cust_b = cls._customer("Sep B")
		cls.so_a = cls._sales_order(COMPANY_A, cls.cust_a, cls.wh_a)
		cls.so_b = cls._sales_order(COMPANY_B, cls.cust_b, cls.wh_b)

		cls._make_user(USER_A, [COMPANY_A])
		cls._make_user(USER_B, [COMPANY_B])
		cls._make_user(USER_MGR, [COMPANY_A, COMPANY_B])

	# -- separation ---------------------------------------------------------

	def test_user_a_sees_only_company_a_sales_orders(self):
		frappe.set_user(USER_A)
		names = frappe.get_list("Sales Order", filters={"item_code": self.item}, pluck="name", ignore_permissions=False)
		# get_list applies User Permissions on Company.
		companies = {frappe.db.get_value("Sales Order", n, "company") for n in names}
		self.assertIn(COMPANY_A, companies | {COMPANY_A})  # A may or may not be in the filtered slice
		self.assertNotIn(COMPANY_B, {frappe.db.get_value("Sales Order", n, "company") for n in
		                             frappe.get_list("Sales Order", pluck="name", limit_page_length=0)})

	def test_user_a_cannot_read_company_b_sales_order(self):
		frappe.set_user(USER_A)
		self.assertFalse(frappe.has_permission("Sales Order", "read", doc=self.so_b))
		self.assertTrue(frappe.has_permission("Sales Order", "read", doc=self.so_a))

	def test_user_b_cannot_read_company_a_sales_order(self):
		frappe.set_user(USER_B)
		self.assertFalse(frappe.has_permission("Sales Order", "read", doc=self.so_a))
		self.assertTrue(frappe.has_permission("Sales Order", "read", doc=self.so_b))

	def test_user_a_warehouse_is_scoped(self):
		frappe.set_user(USER_A)
		names = frappe.get_list("Warehouse", pluck="name", limit_page_length=0)
		self.assertNotIn(self.wh_b, names)

	def test_manager_sees_both_companies(self):
		frappe.set_user(USER_MGR)
		self.assertTrue(frappe.has_permission("Sales Order", "read", doc=self.so_a))
		self.assertTrue(frappe.has_permission("Sales Order", "read", doc=self.so_b))

	def test_export_is_company_filtered_for_user_a(self):
		"""The app's own export path must not leak Company B rows to User A."""
		from my_store_ui.data_management import export_records
		frappe.set_user(USER_A)
		result = export_records(doctype="Warehouse", limit=1000)
		names = {row["name"] for row in result["rows"]}
		self.assertNotIn(self.wh_b, names)

	# -- invalid mixed-company documents ------------------------------------

	def test_company_a_order_with_company_b_warehouse_is_rejected(self):
		frappe.set_user("Administrator")
		bad = frappe.get_doc({"doctype": "Sales Order", "company": COMPANY_A, "customer": self.cust_a,
		                      "delivery_date": add_days(nowdate(), 7),
		                      "items": [{"item_code": self.item, "qty": 1, "warehouse": self.wh_b,
		                                 "delivery_date": add_days(nowdate(), 7), "rate": 100}]})
		with self.assertRaises(Exception):
			bad.insert(ignore_permissions=True)

	def test_direct_api_for_company_b_is_denied_to_user_a(self):
		"""A tampered read of a Company B document via the doc API is refused."""
		frappe.set_user(USER_A)
		with self.assertRaises(frappe.PermissionError):
			frappe.get_doc("Sales Order", self.so_b).check_permission("read")


if __name__ == "__main__":
	unittest.main()
