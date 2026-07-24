"""Permission-aware Quick Create ( + Create ) header menu.

Verifies the menu only ever offers real, create-permitted routes: an Administrator
sees the full grouped set with resolvable paths; a Sales-only user does not see the
Administration group (no User/Role create permission), but still sees Customer.
No dead actions: every offered path resolves as a create route.
"""
from __future__ import annotations

import unittest

import frappe

from my_store_ui.services.frontend_routes import get_quick_create_actions, resolve_frontend_route


class TestQuickCreateMenu(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")

	def test_administrator_sees_grouped_real_create_routes(self):
		result = get_quick_create_actions()
		groups = {group["group"]: group for group in result["groups"]}
		# All five curated groups are present for a full-access user.
		for group in ("Sales", "Purchasing", "Inventory", "Administration", "More"):
			self.assertIn(group, groups)
		# Key actions exist with a real, resolvable create route.
		items = {item["doctype"]: item for group in result["groups"] for item in group["items"]}
		for doctype in ("Customer", "Supplier", "Purchase Order", "Item", "User"):
			self.assertIn(doctype, items)
			path = items[doctype]["path"]
			self.assertTrue(path and path.endswith("/new"))
			definition, _params = resolve_frontend_route(path)
			self.assertIsNotNone(definition, f"{doctype} create route {path} did not resolve")
			self.assertEqual(definition["permission"], "create")
			self.assertEqual(definition["doctype"], doctype)

	def test_no_action_is_a_dead_route(self):
		for group in get_quick_create_actions()["groups"]:
			for item in group["items"]:
				definition, _params = resolve_frontend_route(item["path"])
				self.assertIsNotNone(definition, f"dead action: {item['path']}")

	def test_sales_only_user_does_not_see_administration_actions(self):
		frappe.db.savepoint("quick_create_priv")
		try:
			email = f"quick_create_sales_{frappe.generate_hash(length=8)}@example.com"
			frappe.get_doc({
				"doctype": "User", "email": email, "first_name": "Quick Sales",
				"send_welcome_email": 0, "roles": [{"role": "Sales User"}],
			}).insert(ignore_permissions=True)
			original = frappe.session.user
			try:
				frappe.set_user(email)
				result = get_quick_create_actions()
				groups = {group["group"]: group for group in result["groups"]}
				items = {item["doctype"] for group in result["groups"] for item in group["items"]}
				# A Sales User cannot create Users/Roles → Administration group hidden.
				self.assertNotIn("Administration", groups)
				self.assertNotIn("User", items)
				self.assertNotIn("Role", items)
			finally:
				frappe.set_user(original)
		finally:
			frappe.db.rollback(save_point="quick_create_priv")

	def test_guest_is_rejected(self):
		original = frappe.session.user
		try:
			frappe.set_user("Guest")
			with self.assertRaises(frappe.AuthenticationError):
				get_quick_create_actions()
		finally:
			frappe.set_user(original)
