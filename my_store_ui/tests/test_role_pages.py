"""Role creation and page-driven permissions for the standalone Retail ERP."""

from __future__ import annotations

import unittest
import uuid
from pathlib import Path

import frappe

from my_store_ui.role_pages import create_role_with_page_access


class TestRolePages(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def setUp(self):
		self.savepoint = f"role_pages_{uuid.uuid4().hex[:8]}"
		self.role = f"SMJ Page Role {uuid.uuid4().hex[:8]}"
		frappe.db.savepoint(self.savepoint)

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.savepoint)
		frappe.clear_cache()

	def _permission(self, doctype):
		return frappe.db.get_value(
			"Custom DocPerm",
			{"parent": doctype, "role": self.role, "permlevel": 0, "if_owner": 0},
			["read", "write", "create", "submit"],
			as_dict=True,
		)

	def test_new_role_keeps_only_requested_core_values_and_page_selection(self):
		result = create_role_with_page_access(
			role_name=self.role,
			paths=["/sales/orders"],
			disabled=0,
			desk_access=1,
			is_custom=0,
			access_level="submit",
		)
		self.assertEqual(result["role"], self.role)
		role = frappe.get_doc("Role", self.role)
		self.assertFalse(role.disabled)
		self.assertTrue(role.desk_access)
		self.assertFalse(role.is_custom)
		self.assertEqual(
			frappe.get_all(
				"Retail Role Page", filters={"parent": self.role}, pluck="path"
			),
			["/sales/orders"],
		)

	def test_submit_level_grants_create_write_and_submit_to_submittable_records(self):
		create_role_with_page_access(
			role_name=self.role, paths=["/sales/orders"], access_level="submit",
		)
		permission = self._permission("Sales Order")
		self.assertEqual(
			{key: int(permission[key]) for key in ("read", "write", "create", "submit")},
			{"read": 1, "write": 1, "create": 1, "submit": 1},
		)

	def test_submit_level_does_not_add_invalid_submit_to_master_records(self):
		create_role_with_page_access(
			role_name=self.role, paths=["/sales/customers"], access_level="submit",
		)
		permission = self._permission("Customer")
		self.assertEqual(int(permission.read), 1)
		self.assertEqual(int(permission.write), 1)
		self.assertEqual(int(permission.create), 1)
		self.assertEqual(int(permission.submit), 0)

	def test_view_level_is_read_only(self):
		create_role_with_page_access(
			role_name=self.role, paths=["/sales/orders"], access_level="view",
		)
		permission = self._permission("Sales Order")
		self.assertEqual(int(permission.read), 1)
		self.assertEqual(int(permission.write), 0)
		self.assertEqual(int(permission.create), 0)
		self.assertEqual(int(permission.submit), 0)

	def test_empty_and_system_manager_only_page_selections_are_refused_before_insert(self):
		for paths in ([], ["/admin"], ["/admin/role-pages"]):
			with self.subTest(paths=paths), self.assertRaises((frappe.ValidationError, frappe.PermissionError)):
				create_role_with_page_access(role_name=self.role, paths=paths)
			self.assertFalse(frappe.db.exists("Role", self.role))

	def test_new_role_route_uses_the_dedicated_merged_form(self):
		frontend = Path(frappe.get_app_path("my_store_ui")).parent / "frontend" / "src"
		if not frontend.exists():
			self.skipTest("frontend sources are not present in this checkout")
		routes = (frontend / "router" / "routes.js").read_text(encoding="utf-8")
		page = (frontend / "pages" / "priority" / "NewRolePage.vue").read_text(encoding="utf-8")
		self.assertIn('path: "/admin/roles/new"', routes)
		self.assertIn('import("@/pages/priority/NewRolePage.vue")', routes)
		for label in ("Role Name", "Disabled", "Desk Access", "Is Custom", "Page access"):
			self.assertIn(label, page)
		for removed in ("Home Page", "Restrict To Domain", "Two Factor Authentication"):
			self.assertNotIn(removed, page)


if __name__ == "__main__":
	unittest.main()
