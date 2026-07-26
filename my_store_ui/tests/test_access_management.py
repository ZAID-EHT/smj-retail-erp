"""Phase 8 regression: user, role and access administration.

The security-critical assertion in here is that effective access is evaluated by
the backend for the target user, and that a non-manager calling these endpoints
directly is rejected regardless of what the browser sends.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.access_management import (
	EFFECTIVE_ACCESS_DOCTYPES,
	HIGH_RISK_ROLES,
	PROTECTED_USERS,
	RESTRICTION_DOCTYPES,
	compare_role_profiles,
	count_user_sessions,
	get_email_configuration_status,
	get_restriction_options,
	get_role_overview,
	get_role_permission_summary,
	get_role_profile_change_impact,
	get_role_profile_overview,
	get_user_access_overview,
	revoke_user_sessions,
	set_user_restrictions,
)

SALES_USER = "smj-access-sales@example.com"
MANAGER_USER = "smj-access-manager@example.com"
PROFILE_A = "SMJ Test Profile A"
PROFILE_B = "SMJ Test Profile B"


class TestAccessManagement(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls._make_user(SALES_USER, ["Sales User"])
		cls._make_user(MANAGER_USER, ["System Manager"])
		cls._make_profile(PROFILE_A, ["Sales User", "Sales Manager"])
		cls._make_profile(PROFILE_B, ["Sales User", "Stock User"])
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for user in (SALES_USER, MANAGER_USER):
			for name in frappe.get_all("User Permission", filters={"user": user}, pluck="name"):
				frappe.delete_doc("User Permission", name, force=True, ignore_permissions=True)
		for profile in (PROFILE_A, PROFILE_B):
			if frappe.db.exists("Role Profile", profile):
				frappe.delete_doc("Role Profile", profile, force=True, ignore_permissions=True)
		for user in (SALES_USER, MANAGER_USER):
			if frappe.db.exists("User", user):
				frappe.delete_doc("User", user, force=True, ignore_permissions=True)
		frappe.db.commit()

	@classmethod
	def _make_user(cls, email: str, roles: list[str]) -> None:
		if frappe.db.exists("User", email):
			return
		doc = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": "SMJ Access Test",
			"send_welcome_email": 0, "enabled": 1,
		})
		doc.insert(ignore_permissions=True)
		for role in roles:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)

	@classmethod
	def _make_profile(cls, name: str, roles: list[str]) -> None:
		if frappe.db.exists("Role Profile", name):
			return
		doc = frappe.get_doc({"doctype": "Role Profile", "role_profile": name})
		for role in roles:
			doc.append("roles", {"role": role})
		doc.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.set_user("Administrator")

	# -- gating -------------------------------------------------------------

	def test_non_manager_cannot_reach_any_endpoint(self):
		"""Direct API calls must fail even if the browser sends anything it likes."""
		frappe.set_user(SALES_USER)
		self.assertNotIn("System Manager", frappe.get_roles())
		for call in (
			lambda: get_user_access_overview(user="Administrator"),
			lambda: get_role_overview(),
			lambda: get_role_profile_overview(),
			lambda: get_role_permission_summary(role="System Manager"),
			lambda: compare_role_profiles(first=PROFILE_A, second=PROFILE_B),
			lambda: get_restriction_options(doctype="Company"),
			lambda: set_user_restrictions(user=SALES_USER, doctype="Company", values=[]),
			lambda: revoke_user_sessions(user=SALES_USER),
			lambda: get_role_profile_change_impact(role_profile=PROFILE_A),
		):
			with self.subTest(call=call):
				with self.assertRaises(frappe.PermissionError):
					call()

	def test_restriction_doctype_is_allowlisted(self):
		"""An arbitrary DocType must never be accepted as a restriction."""
		with self.assertRaises(frappe.ValidationError):
			get_restriction_options(doctype="DocType")
		with self.assertRaises(frappe.ValidationError):
			set_user_restrictions(user=SALES_USER, doctype="Role", values=[])

	# -- effective access ---------------------------------------------------

	def test_effective_access_is_backend_evaluated_for_the_target_user(self):
		overview = get_user_access_overview(user=SALES_USER)
		self.assertEqual(overview["user"], SALES_USER)
		self.assertIn("Sales User", overview["effective_roles"])
		self.assertNotIn("System Manager", overview["effective_roles"])

		by_doctype = {row["doctype"]: row for row in overview["permissions"]}
		self.assertEqual(len(by_doctype), len([d for d in EFFECTIVE_ACCESS_DOCTYPES if frappe.db.exists("DocType", d)]))
		# A Sales User may raise a Sales Order but must not create purchasing
		# documents or administer users.
		self.assertTrue(by_doctype["Sales Order"]["create"])
		self.assertFalse(by_doctype["Purchase Order"]["create"])
		self.assertFalse(by_doctype["User"]["create"])
		# Non-submittable doctypes report submit/cancel/amend as False.
		self.assertFalse(by_doctype["Customer"]["submit"])
		self.assertTrue(by_doctype["Sales Order"]["is_submittable"])

	def test_effective_access_matches_frappe_has_permission(self):
		"""The report must not drift from the real permission engine."""
		overview = get_user_access_overview(user=SALES_USER)
		for row in overview["permissions"]:
			with self.subTest(doctype=row["doctype"]):
				self.assertEqual(
					row["read"],
					bool(frappe.has_permission(row["doctype"], "read", user=SALES_USER)),
				)

	def test_account_status_reports_enabled_and_sessions(self):
		overview = get_user_access_overview(user=SALES_USER)
		account = overview["account"]
		self.assertTrue(account["enabled"])
		self.assertFalse(account["protected"])
		self.assertEqual(account["active_sessions"], count_user_sessions(SALES_USER))
		self.assertIn("last_login", account)

		admin = get_user_access_overview(user="Administrator")
		self.assertTrue(admin["account"]["protected"])

	# -- restrictions -------------------------------------------------------

	def test_restrictions_use_standard_user_permission_documents(self):
		company = frappe.get_all("Company", pluck="name")[0]
		result = set_user_restrictions(user=SALES_USER, doctype="Company", values=[company])
		self.assertEqual(result["values"], [company])
		self.assertTrue(frappe.db.exists("User Permission", {
			"user": SALES_USER, "allow": "Company", "for_value": company,
		}))
		restrictions = {row["doctype"]: row for row in result["restrictions"]}
		self.assertEqual(set(restrictions), set(RESTRICTION_DOCTYPES))
		self.assertTrue(restrictions["Company"]["restricted"])
		self.assertEqual(restrictions["Company"]["values"], [company])

		# Replacing with an empty list clears the restriction.
		cleared = set_user_restrictions(user=SALES_USER, doctype="Company", values=[])
		self.assertEqual(cleared["values"], [])
		self.assertFalse(frappe.db.exists("User Permission", {"user": SALES_USER, "allow": "Company"}))

	def test_restriction_rejects_a_value_that_does_not_exist(self):
		with self.assertRaises(frappe.ValidationError):
			set_user_restrictions(user=SALES_USER, doctype="Company", values=["No Such Company"])

	def test_restriction_options_are_permission_filtered(self):
		options = get_restriction_options(doctype="Company")
		self.assertEqual(options["doctype"], "Company")
		self.assertEqual(set(options["options"]), set(frappe.get_all("Company", pluck="name")))

	# -- sessions -----------------------------------------------------------

	def test_protected_accounts_cannot_have_sessions_revoked(self):
		for user in PROTECTED_USERS:
			with self.subTest(user=user):
				with self.assertRaises(frappe.PermissionError):
					revoke_user_sessions(user=user)

	def test_revoking_sessions_reports_a_zeroed_count(self):
		result = revoke_user_sessions(user=SALES_USER)
		self.assertEqual(result["user"], SALES_USER)
		self.assertEqual(result["active_sessions"], 0)

	# -- roles --------------------------------------------------------------

	def test_role_overview_reports_real_counts_and_risk(self):
		roles = {row["role"]: row for row in get_role_overview()["roles"]}
		self.assertIn("Sales User", roles)
		self.assertIn("System Manager", roles)
		self.assertTrue(roles["System Manager"]["high_risk"])
		self.assertFalse(roles["Sales User"]["high_risk"])
		self.assertTrue(roles["All"]["protected"])
		# Our fixture user holds Sales User, and both fixture profiles include it.
		self.assertGreaterEqual(roles["Sales User"]["assigned_users"], 1)
		self.assertGreaterEqual(roles["Sales User"]["role_profiles"], 2)
		self.assertEqual(
			roles["Sales User"]["assigned_users"],
			frappe.db.count("Has Role", {"role": "Sales User", "parenttype": "User"}),
		)

	def test_role_permission_summary_comes_from_docperm(self):
		summary = get_role_permission_summary(role="Sales User")
		self.assertEqual(summary["role"], "Sales User")
		granted = {row["doctype"]: row["granted"] for row in summary["doctype_permissions"]}
		self.assertIn("Sales Order", granted)
		self.assertIn("create", granted["Sales Order"])
		self.assertNotIn("Purchase Order", granted)

	def test_role_permission_summary_rejects_unknown_role(self):
		with self.assertRaises(frappe.DoesNotExistError):
			get_role_permission_summary(role="No Such Role")

	def test_high_risk_roles_are_declared(self):
		self.assertIn("System Manager", HIGH_RISK_ROLES)

	# -- role profiles ------------------------------------------------------

	def test_role_profile_overview_lists_roles_and_assignments(self):
		profiles = {row["role_profile"]: row for row in get_role_profile_overview()["profiles"]}
		self.assertIn(PROFILE_A, profiles)
		self.assertEqual(profiles[PROFILE_A]["roles"], ["Sales Manager", "Sales User"])
		self.assertEqual(profiles[PROFILE_A]["role_count"], 2)

	def test_compare_role_profiles_reports_the_difference(self):
		result = compare_role_profiles(first=PROFILE_A, second=PROFILE_B)
		self.assertEqual(result["shared"], ["Sales User"])
		self.assertEqual(result["only_in_first"], ["Sales Manager"])
		self.assertEqual(result["only_in_second"], ["Stock User"])

	def test_compare_role_profiles_rejects_unknown_profile(self):
		with self.assertRaises(frappe.DoesNotExistError):
			compare_role_profiles(first=PROFILE_A, second="No Such Profile")

	def test_change_impact_counts_affected_users(self):
		impact = get_role_profile_change_impact(role_profile=PROFILE_A)
		self.assertEqual(impact["role_profile"], PROFILE_A)
		self.assertEqual(impact["affected_user_count"], len(impact["affected_users"]))
		self.assertEqual(
			impact["affected_user_count"],
			frappe.db.count("User", {"role_profile_name": PROFILE_A}),
		)

	# -- self-lockout -------------------------------------------------------

	def test_a_manager_cannot_disable_their_own_account(self):
		"""Frappe only protects Administrator/Guest, so this guard is ours."""
		from my_store_ui.universal.api import update_document

		savepoint = "self_disable"
		frappe.db.savepoint(savepoint)
		try:
			frappe.set_user(MANAGER_USER)
			with self.assertRaises(frappe.PermissionError) as caught:
				update_document(feature="user", name=MANAGER_USER, values={"enabled": 0})
			self.assertIn("your own account", str(caught.exception))
		finally:
			frappe.set_user("Administrator")
			frappe.db.rollback(save_point=savepoint)
		self.assertTrue(frappe.db.get_value("User", MANAGER_USER, "enabled"))

	def test_a_manager_cannot_remove_their_own_system_manager_role(self):
		from my_store_ui.universal.api import update_document

		savepoint = "self_derole"
		frappe.db.savepoint(savepoint)
		try:
			frappe.set_user(MANAGER_USER)
			with self.assertRaises(frappe.PermissionError) as caught:
				update_document(
					feature="user", name=MANAGER_USER,
					values={"enabled": 1, "roles": [{"role": "Sales User"}]},
				)
			self.assertIn("System Manager", str(caught.exception))
		finally:
			frappe.set_user("Administrator")
			frappe.db.rollback(save_point=savepoint)
		self.assertIn("System Manager", frappe.get_roles(MANAGER_USER))

	def test_a_manager_may_still_disable_a_different_user(self):
		"""The guard must protect only the caller, not block real administration."""
		from my_store_ui.universal.api import update_document

		savepoint = "disable_other"
		frappe.db.savepoint(savepoint)
		try:
			frappe.set_user(MANAGER_USER)
			update_document(feature="user", name=SALES_USER, values={"enabled": 0})
			self.assertFalse(frappe.db.get_value("User", SALES_USER, "enabled"))
		finally:
			frappe.set_user("Administrator")
			frappe.db.rollback(save_point=savepoint)

	# -- email --------------------------------------------------------------

	def test_email_status_is_truthful_and_actionable(self):
		"""`Email Account` has no `disabled` field -- outgoing is driven by
		`enable_outgoing`, and `awaiting_password` means it cannot actually send."""
		status = get_email_configuration_status()
		accounts = frappe.get_all(
			"Email Account", filters={"enable_outgoing": 1},
			fields=["name", "default_outgoing", "awaiting_password"],
		)
		usable = [row for row in accounts if not row.awaiting_password]
		fallback = bool(frappe.conf.get("mail_server") or frappe.conf.get("mail_login"))

		self.assertEqual(status["outgoing_configured"], bool(accounts) or fallback)
		self.assertEqual(status["outgoing_enabled"], bool(usable) or fallback)
		self.assertEqual(status["can_send_welcome_email"], bool(usable) or fallback)
		self.assertEqual(len(status["accounts"]), len(accounts))
		if status["can_send_welcome_email"]:
			self.assertIsNone(status["message"])
		else:
			self.assertIn("temporary password", status["message"])

	def test_email_status_never_returns_credentials(self):
		status = get_email_configuration_status()
		leaked = {"password", "smtp_server", "api_key", "api_secret", "access_token", "auth_token"}
		self.assertEqual(set(status) & leaked, set())
		for account in status["accounts"]:
			self.assertEqual(set(account) & leaked, set())

	def test_email_status_is_not_readable_by_a_non_manager(self):
		frappe.set_user(SALES_USER)
		with self.assertRaises(frappe.PermissionError):
			get_email_configuration_status()


if __name__ == "__main__":
	unittest.main()
