"""Customer quick-entry: address/contact, pricing, credit, atomicity, security."""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import cint, flt

from my_store_ui.quick_entry.customer import create_customer, find_duplicate_customers, get_customer

SUFFIX = uuid.uuid4().hex[:6]
SALES_USER = f"smj-cqe-sales-{SUFFIX}@example.com"
MADE: list[str] = []


class TestCustomerQuickEntry(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		if not frappe.db.exists("User", SALES_USER):
			d = frappe.get_doc({"doctype": "User", "email": SALES_USER, "first_name": "CQE",
			                    "send_welcome_email": 0, "enabled": 1})
			d.insert(ignore_permissions=True)
			d.append("roles", {"role": "Sales User"})
			d.save(ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for cust in MADE:
			for dt in ("Address", "Contact"):
				for parent in frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": cust, "parenttype": dt}, pluck="parent"):
					if frappe.db.exists(dt, parent):
						frappe.delete_doc(dt, parent, force=True, ignore_permissions=True)
			if frappe.db.exists("Customer", cust):
				frappe.delete_doc("Customer", cust, force=True, ignore_permissions=True)
		if frappe.db.exists("User", SALES_USER):
			frappe.delete_doc("User", SALES_USER, force=True, ignore_permissions=True)
		frappe.db.commit()

	def _create(self, **over):
		v = {"customer_name": f"CQE Test {uuid.uuid4().hex[:6]}", "address": "1 Test Rd", "city": "Colombo",
		     "contact_no": "0771234567", "price_category": "Retail Price List", "payment_type": "Non-Credit"}
		v.update(over)
		res = create_customer(v)
		MADE.append(res["name"])
		return res

	def test_customer_required(self):
		with self.assertRaises(frappe.ValidationError):
			create_customer({"customer_name": "", "price_category": "Retail Price List"})

	def test_address_and_contact_created_and_linked(self):
		res = self._create()
		addrs = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": res["name"], "parenttype": "Address"}, pluck="parent")
		contacts = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": res["name"], "parenttype": "Contact"}, pluck="parent")
		self.assertEqual(len(addrs), 1)
		self.assertEqual(len(contacts), 1)

	def test_edit_does_not_duplicate_address_or_contact(self):
		res = self._create()
		create_customer({"customer_name": get_customer(res["name"])["customer_name"], "address": "2 New Rd",
		                 "contact_no": "0777654321", "price_category": "Retail Price List", "payment_type": "Non-Credit"}, name=res["name"])
		addrs = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": res["name"], "parenttype": "Address"}, pluck="parent")
		self.assertEqual(len(addrs), 1)
		self.assertEqual(get_customer(res["name"])["address"], "2 New Rd")

	def test_same_whatsapp_defaults_from_contact(self):
		res = self._create(whatsapp_no="", same_whatsapp=1, contact_no="0759999999")
		self.assertEqual(get_customer(res["name"])["whatsapp_no"], "0759999999")

	def test_default_price_category_is_retail(self):
		res = create_customer({"customer_name": f"CQE Def {uuid.uuid4().hex[:6]}", "payment_type": "Non-Credit"})
		MADE.append(res["name"])
		self.assertEqual(get_customer(res["name"])["price_category"], "Retail Price List")

	def test_wholesale_and_department_price_categories(self):
		for pl in ("Wholesale Price List", "Department Price List"):
			res = self._create(price_category=pl)
			self.assertEqual(get_customer(res["name"])["price_category"], pl)

	def test_buying_price_list_rejected_as_category(self):
		with self.assertRaises(frappe.ValidationError):
			self._create(price_category="Standard Buying")

	def test_non_credit_defaults_zero(self):
		res = self._create(payment_type="Non-Credit")
		g = get_customer(res["name"])
		self.assertEqual(g["payment_type"], "Non-Credit")
		self.assertEqual(flt(g["credit_limit"]), 0.0)
		self.assertEqual(cint(g["credit_days"]), 0)

	def test_credit_requires_limit(self):
		with self.assertRaises(frappe.ValidationError):
			self._create(payment_type="Credit", credit_limit=0, credit_days=30)

	def test_credit_customer_stores_limit_and_days(self):
		res = self._create(payment_type="Credit", credit_limit=250000, credit_days=45)
		g = get_customer(res["name"])
		self.assertEqual(g["payment_type"], "Credit")
		self.assertEqual(flt(g["credit_limit"]), 250000.0)
		self.assertEqual(cint(g["credit_days"]), 45)

	def test_all_business_fields_persist(self):
		res = self._create(accounts_department_no="0112345678", transport_method="Courier",
		                   transport_detail="Gate", br_no="BR-1", business_nature="Wholesaler")
		g = get_customer(res["name"])
		self.assertEqual(g["accounts_department_no"], "0112345678")
		self.assertEqual(g["transport_method"], "Courier")
		self.assertEqual(g["transport_detail"], "Gate")
		self.assertEqual(g["br_no"], "BR-1")
		self.assertEqual(g["business_nature"], "Wholesaler")

	def test_created_date_present(self):
		res = self._create()
		self.assertTrue(get_customer(res["name"])["created"])

	def test_duplicate_warning(self):
		res = self._create(customer_name="CQE Duplicate Probe")
		found = find_duplicate_customers("CQE Duplicate Probe")
		self.assertTrue(any(c["name"] == res["name"] for c in found["candidates"]))

	def test_arbitrary_field_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			create_customer({"customer_name": "x", "price_category": "Retail Price List", "evil": 1})

	def test_atomic_rollback_on_failure(self):
		before = frappe.db.count("Customer")
		with self.assertRaises(frappe.ValidationError):
			create_customer({"customer_name": "CQE Rollback", "price_category": "Standard Buying"})
		self.assertEqual(frappe.db.count("Customer"), before)


if __name__ == "__main__":
	unittest.main()
