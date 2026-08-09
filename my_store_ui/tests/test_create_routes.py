"""Phase 6 regression: every required create route exists, resolves and works.

Covers the two gaps found in the Phase 6 audit:
  * Role Profile had no create route at all (implementation_type "unavailable").
  * Payment Entry had one generic entry point instead of Receive / Pay /
    Internal Transfer.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

BENCH_PATH = Path(__file__).resolve().parents[4]

from my_store_ui.priority_pages import get_priority_route_definition
from my_store_ui.services.frontend_routes import (
	QUICK_CREATE_GROUPS,
	get_quick_create_actions,
	resolve_frontend_route,
	route_is_permitted,
)
from my_store_ui.universal.api import (
	SIMPLE_CREATE_FIELDS,
	SIMPLE_CREATE_REQUIRED,
	SPECIAL_WRITABLE_FIELDS,
	create_document,
	get_doctype_metadata,
	get_document_detail,
)

# Every DocType the requirement says must have a working custom create route.
REQUIRED_CREATE_DOCTYPES = (
	# Master data
	"Customer", "Supplier", "Item", "Contact", "Address", "Warehouse",
	# Sales
	"Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
	# Purchasing
	"Purchase Order", "Purchase Receipt", "Purchase Invoice",
	# Stock
	"Stock Entry", "Stock Reconciliation",
	# Administration
	"User", "Role", "Role Profile",
	# Accounts
	"Journal Entry",
)

PAYMENT_VARIANTS = {
	"/finance/payments/receive/new": "Receive",
	"/finance/payments/pay/new": "Pay",
	"/finance/payments/internal-transfer/new": "Internal Transfer",
}


class TestCreateRoutes(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def test_every_required_doctype_has_a_real_create_route(self):
		from my_store_ui.universal.registry import get_registry_records

		by_doctype = {}
		for record in get_registry_records():
			doctype = record.get("doctype")
			if doctype and record.get("create_route") and doctype not in by_doctype:
				by_doctype[doctype] = record

		for doctype in REQUIRED_CREATE_DOCTYPES:
			with self.subTest(doctype=doctype):
				record = by_doctype.get(doctype)
				self.assertIsNotNone(record, f"{doctype} has no registry record with a create route")
				self.assertNotEqual(record["implementation_type"], "unavailable")
				route = record["create_route"]
				self.assertTrue(route.startswith("/"))
				self.assertNotIn("/app/", route, "must never route staff into ERPNext Desk")
				definition, _params = resolve_frontend_route(route)
				self.assertIsNotNone(definition, f"{doctype} create route {route} does not resolve")
				self.assertEqual(definition["permission"], "create")
				# Handcrafted ROUTE_REGISTRY entries carry no "mode"; registry- and
				# variant-derived ones do, and it must say "new".
				self.assertEqual(definition.get("mode", "new"), "new")
				self.assertEqual(definition["doctype"], doctype)
				self.assertTrue(route_is_permitted(definition))

	def test_role_profile_create_route_is_registered_and_admin_gated(self):
		from my_store_ui.universal.registry import ADMIN_FEATURE_ROLES

		definition = get_priority_route_definition("/retail-erp/admin/role-profiles/new")
		self.assertEqual(definition["doctype"], "Role Profile")
		self.assertEqual(definition["mode"], "new")
		self.assertEqual(definition["component"], "entity")
		# Bundling roles is at least as sensitive as editing Role itself.
		self.assertEqual(ADMIN_FEATURE_ROLES.get("Role Profile"), {"System Manager"})

	def test_role_profile_roles_table_is_writable_through_the_engine(self):
		"""Desk hides this table behind a JS RoleEditor; without the adapter a
		Role Profile could be created but never given any roles."""
		self.assertIn("roles", SPECIAL_WRITABLE_FIELDS.get("Role Profile", set()))
		metadata = get_doctype_metadata("role-profile")
		roles = next((f for f in metadata["fields"] if f["fieldname"] == "roles"), None)
		self.assertIsNotNone(roles, "roles table is not exposed on Role Profile")
		self.assertFalse(roles["read_only"], "roles table must be editable for user managers")
		self.assertIn("role", [child["fieldname"] for child in roles.get("child_fields", [])])

	def test_role_profile_can_be_created_with_roles(self):
		name = "SMJ Test Role Profile"
		savepoint = "test_role_profile"
		frappe.db.savepoint(savepoint)
		try:
			result = create_document("role-profile", json.dumps({
				"role_profile": name,
				"roles": [{"role": "Sales User"}],
			}))
			self.assertEqual(result["name"], name)
			detail = get_document_detail("role-profile", result["name"])
			assigned = [row.get("role") for row in (detail["document"].get("roles") or [])]
			self.assertIn("Sales User", assigned)
		finally:
			frappe.db.rollback(save_point=savepoint)
		self.assertFalse(frappe.db.exists("Role Profile", name))

	def test_role_profile_add_form_is_curated(self):
		self.assertEqual(SIMPLE_CREATE_FIELDS["Role Profile"], ("role_profile", "roles"))
		self.assertEqual(SIMPLE_CREATE_REQUIRED["Role Profile"], ("role_profile", "roles"))

	def test_payment_entry_variants_preset_payment_type(self):
		options = [
			line for line in (frappe.get_meta("Payment Entry").get_field("payment_type").options or "").splitlines()
			if line
		]
		for path, payment_type in PAYMENT_VARIANTS.items():
			with self.subTest(path=path):
				self.assertIn(payment_type, options, "preset must be a real Select option")
				definition = get_priority_route_definition(f"/retail-erp{path}")
				self.assertEqual(definition["doctype"], "Payment Entry")
				self.assertEqual(definition["mode"], "new")
				self.assertEqual(definition["defaults"], {"payment_type": payment_type})
				self.assertEqual(definition["base_path"], "/finance/payments")

	def test_quick_create_offers_the_required_grouped_actions(self):
		groups = {group["group"]: group["items"] for group in get_quick_create_actions()["groups"]}
		expected = {
			"Sales": {"Customer", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice", "Receive Payment"},
			"Purchasing": {"Supplier", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Pay Supplier"},
			"Inventory": {"Product", "Stock Entry", "Stock Reconciliation", "Warehouse"},
			"Administration": {"User", "Role", "Role Profile"},
			"More": {"Journal Entry", "Contact", "Address", "Internal Transfer"},
		}
		for group, labels in expected.items():
			with self.subTest(group=group):
				self.assertIn(group, groups)
				self.assertEqual(labels, {item["label"] for item in groups[group]})

	def test_no_quick_create_action_is_dead(self):
		for group in get_quick_create_actions()["groups"]:
			for item in group["items"]:
				with self.subTest(label=item["label"]):
					definition, _params = resolve_frontend_route(item["path"])
					self.assertIsNotNone(definition, f"{item['label']} -> {item['path']} does not resolve")
					self.assertEqual(definition.get("mode", "new"), "new")
					self.assertEqual(definition["permission"], "create")
					self.assertTrue(route_is_permitted(definition))
					self.assertTrue(frappe.has_permission(item["doctype"], "create"))

	def test_quick_create_groups_only_reference_installed_doctypes(self):
		for _group, entries in QUICK_CREATE_GROUPS:
			for entry in entries:
				doctype = entry if isinstance(entry, str) else entry["doctype"]
				with self.subTest(doctype=doctype):
					self.assertTrue(frappe.db.exists("DocType", doctype))

	def test_quick_create_paths_are_unique_and_keyed_by_path_in_the_menu(self):
		"""Payment Entry now appears three times, so doctype is no longer a unique
		key. Keying the menu on doctype would duplicate Vue keys and highlight all
		three Payment Entry rows at once during keyboard navigation."""
		paths = [
			item["path"]
			for group in get_quick_create_actions()["groups"]
			for item in group["items"]
		]
		self.assertEqual(len(paths), len(set(paths)), "quick create paths must be unique")

		doctypes = [
			item["doctype"]
			for group in get_quick_create_actions()["groups"]
			for item in group["items"]
		]
		self.assertEqual(doctypes.count("Payment Entry"), 3)

		source = (BENCH_PATH / "apps/my_store_ui/frontend/src/components/shell/QuickCreateMenu.vue").read_text()
		self.assertIn(':key="item.path"', source)
		self.assertIn("flatItems[activeIndex]?.path === item.path", source)
		self.assertNotIn(':key="item.doctype"', source)

	def test_quick_create_is_permission_filtered(self):
		"""A user with no create rights must be offered nothing."""
		with patch("my_store_ui.services.frontend_routes.frappe.has_permission", return_value=False):
			self.assertEqual(get_quick_create_actions()["groups"], [])


if __name__ == "__main__":
	unittest.main()
