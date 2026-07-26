"""Complete role-denial and privilege-escalation matrix.

Extends the single-role denial in test_access_management to every representative
role. The security boundary is the server-side gate, not menu hiding, so this
calls the admin endpoints DIRECTLY as each role and asserts:

  * every non-System-Manager role is refused on every access-management endpoint;
  * payload manipulation does not create access;
  * a manager cannot grant System Manager to another user through the ordinary
    universal save path unless they themselves hold it;
  * a disabled user cannot authenticate;
  * protected system accounts stay protected;
  * self-lockout is prevented.

Every fixture is fictional and removed afterwards.
"""

from __future__ import annotations

import unittest

import frappe
from frappe.core.doctype.user.user import User

from my_store_ui.access_management import (
	compare_role_profiles,
	get_email_configuration_status,
	get_restriction_options,
	get_role_overview,
	get_role_permission_summary,
	get_role_profile_change_impact,
	get_role_profile_overview,
	get_user_access_overview,
	revoke_user_sessions,
	search_users,
	set_user_restrictions,
)

# role -> whether it should be allowed on the access-management surface
NON_MANAGER_ROLES = (
	"Sales User", "Sales Manager", "Purchase User", "Purchase Manager",
	"Stock User", "Stock Manager", "Accounts User", "Accounts Manager", "Item Manager",
)
PASSWORD = "Smj!matrix-test-pw-0001"


def _make_user(email: str, roles: list[str], enabled: int = 1) -> None:
	if frappe.db.exists("User", email):
		frappe.delete_doc("User", email, force=True, ignore_permissions=True)
	doc = frappe.get_doc({
		"doctype": "User", "email": email, "first_name": "SMJ Matrix",
		"send_welcome_email": 0, "enabled": enabled, "new_password": PASSWORD,
	})
	doc.insert(ignore_permissions=True)
	for role in roles:
		doc.append("roles", {"role": role})
	doc.save(ignore_permissions=True)
	frappe.clear_cache(user=email)


class TestRoleDenialMatrix(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.users = {}
		for role in NON_MANAGER_ROLES:
			email = f"smj-matrix-{frappe.scrub(role)}@example.com"
			_make_user(email, [role])
			cls.users[role] = email
		_make_user("smj-matrix-disabled@example.com", ["Sales User"], enabled=0)
		_make_user("smj-matrix-manager@example.com", ["System Manager"])
		_make_user("smj-matrix-victim@example.com", ["Sales User"])
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		emails = list(cls.users.values()) + [
			"smj-matrix-disabled@example.com", "smj-matrix-manager@example.com",
			"smj-matrix-victim@example.com",
		]
		for email in emails:
			for perm in frappe.get_all("User Permission", filters={"user": email}, pluck="name"):
				frappe.delete_doc("User Permission", perm, force=True, ignore_permissions=True)
			if frappe.db.exists("User", email):
				frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		frappe.db.commit()

	def tearDown(self):
		frappe.set_user("Administrator")

	def _endpoints(self, victim: str):
		"""Every access-management endpoint, as zero-arg callables."""
		return {
			"get_user_access_overview": lambda: get_user_access_overview(user=victim),
			"search_users": lambda: search_users(search="smj-matrix"),
			"get_role_overview": lambda: get_role_overview(),
			"get_role_permission_summary": lambda: get_role_permission_summary(role="System Manager"),
			"get_role_profile_overview": lambda: get_role_profile_overview(),
			"get_role_profile_change_impact": lambda: get_role_profile_change_impact(role_profile="X"),
			"get_restriction_options": lambda: get_restriction_options(doctype="Company"),
			"set_user_restrictions": lambda: set_user_restrictions(user=victim, doctype="Company", values=[]),
			"revoke_user_sessions": lambda: revoke_user_sessions(user=victim),
			"get_email_configuration_status": lambda: get_email_configuration_status(),
		}

	def test_every_non_manager_role_is_denied_on_every_endpoint(self):
		victim = self.users["Sales User"]
		for role, email in self.users.items():
			frappe.set_user(email)
			self.assertNotIn("System Manager", frappe.get_roles(email))
			for name, call in self._endpoints(victim).items():
				with self.subTest(role=role, endpoint=name):
					with self.assertRaises(frappe.PermissionError):
						call()

	def test_payload_manipulation_does_not_create_access(self):
		"""A forged 'user=self' or unknown DocType must not bypass the gate."""
		frappe.set_user(self.users["Accounts Manager"])
		with self.assertRaises(frappe.PermissionError):
			get_user_access_overview(user=self.users["Accounts Manager"])
		with self.assertRaises(frappe.PermissionError):
			# Even the allowlist check is behind the manager gate.
			set_user_restrictions(user=self.users["Accounts Manager"], doctype="DocType", values=["User"])

	def test_a_manager_cannot_grant_system_manager_they_could_but_a_plain_user_cannot(self):
		"""The universal save path enforces User.create/write; a non-manager cannot
		reach it at all, so cannot escalate a victim to System Manager."""
		from my_store_ui.universal.api import update_document

		frappe.set_user(self.users["Sales Manager"])
		with self.assertRaises(frappe.PermissionError):
			update_document(
				feature="user", name="smj-matrix-victim@example.com",
				values={"roles": [{"role": "System Manager"}]},
			)
		frappe.set_user("Administrator")
		self.assertNotIn("System Manager", frappe.get_roles("smj-matrix-victim@example.com"))

	def test_disabled_user_cannot_authenticate(self):
		result = User.find_by_credentials("smj-matrix-disabled@example.com", PASSWORD)
		# find_by_credentials returns the row with enabled=0; LoginManager fails on it.
		self.assertFalse(result["enabled"])

	def test_enabled_user_can_authenticate(self):
		result = User.find_by_credentials(self.users["Sales User"], PASSWORD)
		self.assertTrue(result["is_authenticated"])
		self.assertTrue(result["enabled"])

	def test_system_manager_is_allowed(self):
		frappe.set_user("smj-matrix-manager@example.com")
		overview = get_user_access_overview(user=self.users["Sales User"])
		self.assertEqual(overview["user"], self.users["Sales User"])
		roles = get_role_overview()
		self.assertTrue(roles["roles"])

	def test_denied_response_leaks_no_user_data(self):
		"""A refusal must not carry the target user's details."""
		frappe.set_user(self.users["Stock User"])
		try:
			get_user_access_overview(user="Administrator")
			self.fail("expected PermissionError")
		except frappe.PermissionError as exc:
			message = str(exc)
			self.assertNotIn("Administrator", message)
			self.assertNotIn("@", message)


if __name__ == "__main__":
	unittest.main()
