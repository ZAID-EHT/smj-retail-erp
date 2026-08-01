"""Henderson analysis, Accounts workspace and Print Format administration.

Covers permission behaviour on every endpoint, because a frontend guard is never
the only control. Savepoint + rollback; no residue.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt, nowdate

from my_store_ui.accounts_workspace import get_accounts_workspace
from my_store_ui.henderson import get_henderson_analysis, save_henderson_analysis
from my_store_ui.my_store_ui.doctype.henderson_assessment.henderson_assessment import DOMAINS
from my_store_ui.print_format_admin import (
	MANAGED_DOCTYPES,
	create_custom_print_format,
	get_print_format_admin,
	preview_print_format,
	resolve_print_format,
	set_default_print_format,
	set_print_format_disabled,
)
from my_store_ui.standalone import authorize_frontend_route

SALES_USER = "mgmt-pages-sales@example.invalid"
ACCOUNTS_USER = "mgmt-pages-accounts@example.invalid"


class ManagementPagesBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]

	def setUp(self):
		self.sp = f"mgmt_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _user(self, email, roles):
		if not frappe.db.exists("User", email):
			doc = frappe.get_doc({
				"doctype": "User", "email": email, "first_name": email.split("@")[0],
				"send_welcome_email": 0,
			})
			doc.insert(ignore_permissions=True)
			doc.add_roles(*roles)
		return email


class TestHendersonAnalysis(ManagementPagesBase):
	def _payload(self, current=2, target=4):
		return [
			{"domain": d, "current_score": current, "target_score": target,
			 "priority": "High", "notes": f"{d} note"}
			for d in DOMAINS
		]

	def test_route_resolves(self):
		self.assertEqual(
			authorize_frontend_route("/reports/henderson-analysis")["outcome"], "allowed"
		)

	def test_empty_state_before_any_assessment(self):
		data = get_henderson_analysis(company=self.company)
		self.assertIn("domains", data)
		self.assertIn("summary", data)
		self.assertTrue(data["can_edit"])

	def test_save_and_read_back_an_assessment(self):
		res = save_henderson_analysis(
			company=self.company, assessment_date=nowdate(), domains=self._payload(),
			summary_notes="Alignment review", status="Active",
		)
		self.assertTrue(res["name"])
		data = get_henderson_analysis(company=self.company)
		self.assertEqual(data["assessment"]["summary_notes"], "Alignment review")
		self.assertEqual(len(data["domains"]), len(DOMAINS))

	def test_gaps_and_priority_areas_are_derived(self):
		save_henderson_analysis(
			company=self.company, assessment_date=nowdate(), domains=self._payload(1, 5),
		)
		data = get_henderson_analysis(company=self.company)
		self.assertTrue(all(d["gap"] == 4 for d in data["domains"]))
		self.assertEqual(flt(data["summary"]["total_gap"]), 4.0 * len(DOMAINS))
		self.assertTrue(data["summary"]["priority_areas"])

	def test_every_domain_is_reported_even_when_unassessed(self):
		save_henderson_analysis(
			company=self.company, assessment_date=nowdate(),
			domains=[{"domain": "IT Strategy", "current_score": 3, "target_score": 4}],
		)
		data = get_henderson_analysis(company=self.company)
		self.assertEqual(len(data["domains"]), len(DOMAINS))
		self.assertEqual(sum(1 for d in data["domains"] if d["assessed"]), 1)

	def test_last_updated_and_updater_are_reported(self):
		save_henderson_analysis(
			company=self.company, assessment_date=nowdate(), domains=self._payload(),
		)
		assessment = get_henderson_analysis(company=self.company)["assessment"]
		self.assertTrue(assessment["modified"])
		self.assertEqual(assessment["modified_by"], "Administrator")

	def test_unknown_domain_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			save_henderson_analysis(
				company=self.company, assessment_date=nowdate(),
				domains=[{"domain": "Marketing Strategy", "current_score": 1, "target_score": 2}],
			)

	def test_score_out_of_range_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			save_henderson_analysis(
				company=self.company, assessment_date=nowdate(),
				domains=[{"domain": "IT Systems", "current_score": 9, "target_score": 2}],
			)

	def test_duplicate_domain_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			save_henderson_analysis(
				company=self.company, assessment_date=nowdate(),
				domains=[
					{"domain": "Infrastructure", "current_score": 1, "target_score": 2},
					{"domain": "Infrastructure", "current_score": 3, "target_score": 4},
				],
			)

	def test_a_sales_user_cannot_edit_the_analysis(self):
		user = self._user(SALES_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				save_henderson_analysis(
					company=self.company, assessment_date=nowdate(), domains=self._payload(),
				)
		finally:
			frappe.set_user("Administrator")

	def test_a_manager_gets_read_only_access(self):
		save_henderson_analysis(
			company=self.company, assessment_date=nowdate(), domains=self._payload(),
		)
		user = self._user("mgmt-pages-salesmgr@example.invalid", ["Sales Manager"])
		frappe.set_user(user)
		try:
			data = get_henderson_analysis(company=self.company)
			self.assertFalse(data["can_edit"], "Sales Manager is read-only here")
			self.assertIsNotNone(data["assessment"])
			with self.assertRaises(frappe.PermissionError):
				save_henderson_analysis(
					company=self.company, assessment_date=nowdate(), domains=self._payload(),
				)
		finally:
			frappe.set_user("Administrator")

	def test_henderson_never_touches_operational_modules(self):
		"""Separation requirement: no stock, price or order side effects."""
		before_items = frappe.db.count("Item Price")
		before_orders = frappe.db.count("Sales Order")
		save_henderson_analysis(
			company=self.company, assessment_date=nowdate(), domains=self._payload(),
		)
		self.assertEqual(frappe.db.count("Item Price"), before_items)
		self.assertEqual(frappe.db.count("Sales Order"), before_orders)


class TestAccountsWorkspace(ManagementPagesBase):
	def test_route_resolves(self):
		self.assertEqual(authorize_frontend_route("/finance/accounts")["outcome"], "allowed")

	def test_administrator_sees_sections_and_money(self):
		data = get_accounts_workspace(self.company)
		self.assertTrue(data["has_access"])
		self.assertTrue(data["shows_financials"])
		keys = {s["key"] for s in data["sections"]}
		self.assertIn("receivables", keys)
		self.assertIn("reports", keys)

	def test_figures_are_real_erpnext_values(self):
		data = get_accounts_workspace(self.company)
		receivables = next(s for s in data["sections"] if s["key"] == "receivables")
		card = next(c for c in receivables["cards"] if c["kind"] == "currency")
		expected = sum(
			flt(r.outstanding_amount)
			for r in frappe.get_all(
				"Sales Invoice",
				filters={"company": self.company, "docstatus": 1,
				         "outstanding_amount": [">", 0.01]},
				fields=["outstanding_amount"],
			)
		)
		self.assertAlmostEqual(flt(card["value"]), flt(expected), places=2)

	def test_a_sales_user_receives_no_money_totals(self):
		user = self._user(SALES_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			data = get_accounts_workspace(self.company)
			self.assertFalse(data["shows_financials"])
			for section in data["sections"]:
				for card in section.get("cards") or []:
					self.assertNotEqual(
						card["kind"], "currency",
						f"{card['label']} leaked a monetary total to a Sales User",
					)
		finally:
			frappe.set_user("Administrator")

	def test_an_accounts_user_sees_money(self):
		user = self._user(ACCOUNTS_USER, ["Accounts User"])
		frappe.set_user(user)
		try:
			self.assertTrue(get_accounts_workspace(self.company)["shows_financials"])
		finally:
			frappe.set_user("Administrator")

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.AuthenticationError):
				get_accounts_workspace(self.company)
		finally:
			frappe.set_user("Administrator")


class TestPrintFormatAdmin(ManagementPagesBase):
	def test_route_resolves(self):
		self.assertEqual(authorize_frontend_route("/admin/print-formats")["outcome"], "allowed")

	def test_all_required_document_types_are_managed(self):
		data = get_print_format_admin()
		managed = {d["doctype"] for d in data["documents"]}
		for doctype, _label in MANAGED_DOCTYPES:
			if frappe.db.exists("DocType", doctype):
				self.assertIn(doctype, managed)
		labels = {d["label"] for d in data["documents"]}
		self.assertIn("Stock Transfer", labels, "Stock Entry must be presented as Stock Transfer")

	def test_set_and_resolve_a_default_format(self):
		data = get_print_format_admin()
		doc = next(d for d in data["documents"] if d["formats"])
		fmt = doc["formats"][0]["name"]
		set_default_print_format(doc["doctype"], fmt)
		self.assertEqual(resolve_print_format(doc["doctype"]), fmt)

	def test_clearing_a_default_is_supported(self):
		data = get_print_format_admin()
		doc = next(d for d in data["documents"] if d["formats"])
		set_default_print_format(doc["doctype"], doc["formats"][0]["name"])
		set_default_print_format(doc["doctype"], None)
		self.assertIsNone(resolve_print_format(doc["doctype"]))

	def test_a_format_from_another_doctype_is_refused(self):
		data = get_print_format_admin()
		docs = [d for d in data["documents"] if d["formats"]]
		first, second = docs[0], docs[1]
		with self.assertRaises(frappe.ValidationError):
			set_default_print_format(first["doctype"], second["formats"][0]["name"])

	def test_unmanaged_doctype_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			set_default_print_format("User", None)

	def test_create_a_custom_format_from_a_standard_one(self):
		data = get_print_format_admin()
		doc = next(d for d in data["documents"]
		           if any(f["is_standard"] for f in d["formats"]))
		standard = next(f for f in doc["formats"] if f["is_standard"])
		name = f"Retail ERP Test {uuid.uuid4().hex[:6]}"
		res = create_custom_print_format(doc["doctype"], name, standard["name"])
		self.assertFalse(res["is_standard"])
		self.assertEqual(
			frappe.db.get_value("Print Format", name, "standard"), "No",
			"a copy must be custom, never standard",
		)
		# The source standard format must be untouched.
		self.assertEqual(frappe.db.get_value("Print Format", standard["name"], "standard"), "Yes")

	def test_duplicate_format_name_is_refused(self):
		data = get_print_format_admin()
		doc = next(d for d in data["documents"] if d["formats"])
		name = f"Retail ERP Dup {uuid.uuid4().hex[:6]}"
		create_custom_print_format(doc["doctype"], name)
		with self.assertRaises(frappe.ValidationError):
			create_custom_print_format(doc["doctype"], name)

	def test_a_standard_format_cannot_be_disabled(self):
		data = get_print_format_admin()
		doc = next(d for d in data["documents"]
		           if any(f["is_standard"] for f in d["formats"]))
		standard = next(f for f in doc["formats"] if f["is_standard"])
		with self.assertRaises(frappe.ValidationError):
			set_print_format_disabled(standard["name"], 1)

	def test_disabling_a_custom_format_clears_it_as_default(self):
		data = get_print_format_admin()
		doc = next(d for d in data["documents"] if d["formats"])
		name = f"Retail ERP Dis {uuid.uuid4().hex[:6]}"
		create_custom_print_format(doc["doctype"], name)
		set_default_print_format(doc["doctype"], name)
		self.assertEqual(resolve_print_format(doc["doctype"]), name)
		set_print_format_disabled(name, 1)
		self.assertIsNone(
			resolve_print_format(doc["doctype"]),
			"a disabled format must not remain the Retail ERP default",
		)

	def test_a_sales_user_cannot_administer_print_formats(self):
		user = self._user(SALES_USER, ["Sales User"])
		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_print_format_admin()
			with self.assertRaises(frappe.PermissionError):
				set_default_print_format("Sales Order", None)
		finally:
			frappe.set_user("Administrator")

	def test_preview_renders_for_every_document_type_that_has_data(self):
		checked = 0
		for doctype, _label in MANAGED_DOCTYPES:
			if not frappe.db.exists("DocType", doctype):
				continue
			rows = frappe.get_all(doctype, fields=["name"], limit=1)
			if not rows:
				continue
			result = preview_print_format(doctype=doctype)
			self.assertIn("<", result["html"], f"{doctype} preview produced no HTML")
			checked += 1
		self.assertGreater(checked, 0, "no printable documents existed to preview")

	def test_preview_of_an_unmanaged_doctype_is_refused(self):
		with self.assertRaises(frappe.ValidationError):
			preview_print_format(doctype="User")


if __name__ == "__main__":
	unittest.main()
