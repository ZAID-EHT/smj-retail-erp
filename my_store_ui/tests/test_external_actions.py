"""The external action tracker, and the ways it declines to be ticked off.

A go-live checklist that can be marked done without proof is worse than no
checklist: it converts "nobody has done this" into "somebody says this is fine"
without anything changing in the world. These tests are mostly about that.

The seeded catalogue is shared site state rather than per-test fixture data, so
tests here read it and restore anything they change.
"""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui import external_actions as ext

ACTION = ext.ACTION


class ExternalActionBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.suffix = uuid.uuid4().hex[:6]
		cls.manager = cls._user("mgr", ("System Manager",))
		cls.verifier = cls._user("ver", ("Retail Finance Verifier",))
		cls.outsider = cls._user("out", ("Sales User",))
		ext.seed_actions()
		frappe.db.commit()

	@classmethod
	def _user(cls, tag, roles):
		email = f"smjext_{tag}_{cls.suffix}@example.com"
		doc = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": f"Ext {tag}",
			"send_welcome_email": 0, "enabled": 1,
		}).insert(ignore_permissions=True)
		for role in roles:
			if frappe.db.exists("Role", role):
				doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)
		return email

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		for email in (cls.manager, cls.verifier, cls.outsider):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		frappe.db.commit()

	def setUp(self):
		self.sp = f"ext_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)


class TestCatalogue(ExternalActionBase):
	def test_every_catalogue_entry_is_complete(self):
		for entry in ext.CATALOGUE:
			for key in ("action_id", "category", "owner", "title", "required_action",
			            "risk", "verification", "default_status"):
				self.assertTrue(str(entry.get(key) or "").strip(),
				                f"{entry.get('action_id')} is missing {key}")

	def test_action_ids_are_unique(self):
		ids = [e["action_id"] for e in ext.CATALOGUE]
		self.assertEqual(len(ids), len(set(ids)))

	def test_nothing_ships_pre_verified(self):
		"""Nobody has done any of these yet, and the catalogue must say so."""
		for entry in ext.CATALOGUE:
			self.assertNotEqual(entry["default_status"], "Verified",
			                    f"{entry['action_id']} ships claiming to be verified")

	def test_the_expected_external_categories_are_covered(self):
		categories = {e["category"] for e in ext.CATALOGUE}
		for required in ("Accounting", "Database", "Email", "Infrastructure",
		                 "Operations", "UAT", "Approval"):
			self.assertIn(required, categories)

	def test_seeding_is_idempotent(self):
		before = frappe.db.count(ACTION)
		result = ext.seed_actions()
		self.assertEqual(result["created"], [])
		self.assertEqual(frappe.db.count(ACTION), before)

	def test_every_action_states_how_it_would_be_verified(self):
		for entry in ext.CATALOGUE:
			self.assertTrue(len(entry["verification"]) > 10,
			                f"{entry['action_id']} has no real verification procedure")


class TestPermissions(ExternalActionBase):
	def test_outsider_cannot_read_the_tracker(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(frappe.PermissionError):
			ext.get_external_actions()

	def test_outsider_cannot_change_an_action(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(frappe.PermissionError):
			ext.set_action_status("EXT-01", "In Progress")

	def test_outsider_cannot_verify_an_action(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(frappe.PermissionError):
			ext.verify_action("EXT-01")

	def test_manager_can_read(self):
		frappe.set_user(self.manager)
		data = ext.get_external_actions()
		self.assertEqual(data["total"], len(ext.CATALOGUE))


class TestStatusRules(ExternalActionBase):
	def test_verified_cannot_be_reached_by_setting_the_status(self):
		"""The whole point: you cannot tick this box."""
		frappe.set_user(self.manager)
		with self.assertRaises(frappe.ValidationError):
			ext.set_action_status("EXT-01", "Verified")

	def test_rejection_requires_a_reason(self):
		frappe.set_user(self.manager)
		with self.assertRaises(frappe.ValidationError):
			ext.set_action_status("EXT-01", "Rejected", note="")

	def test_rejection_with_a_reason_is_recorded(self):
		frappe.set_user(self.manager)
		ext.set_action_status("EXT-01", "Rejected", note="accountant unavailable")
		self.assertEqual(frappe.db.get_value(ACTION, "EXT-01", "status"), "Rejected")

	def test_verification_requires_ready_for_verification_first(self):
		frappe.set_user(self.verifier)
		with self.assertRaises(frappe.ValidationError):
			ext.verify_action("EXT-01", evidence_reference="something")

	def test_verification_without_evidence_is_refused(self):
		frappe.set_user(self.manager)
		ext.mark_action_complete("EXT-13", evidence_reference="")
		frappe.set_user(self.verifier)
		with self.assertRaises(frappe.ValidationError):
			ext.verify_action("EXT-13", evidence_reference="")

	def test_the_person_who_completed_it_cannot_verify_it(self):
		frappe.set_user(self.manager)
		ext.mark_action_complete("EXT-13", evidence_reference="monitor screenshot")
		with self.assertRaises((frappe.ValidationError, frappe.PermissionError)):
			ext.verify_action("EXT-13", evidence_reference="monitor screenshot")

	def test_a_different_verifier_with_evidence_succeeds(self):
		frappe.set_user(self.manager)
		ext.mark_action_complete("EXT-13", evidence_reference="monitor screenshot")
		frappe.set_user(self.verifier)
		result = ext.verify_action("EXT-13", evidence_reference="monitor screenshot",
		                           verification_note="alert received")
		self.assertEqual(result["status"], "Verified")

	def test_marking_complete_is_a_claim_not_a_verification(self):
		frappe.set_user(self.manager)
		result = ext.mark_action_complete("EXT-13", evidence_reference="x")
		self.assertEqual(result["status"], "Ready for Verification")
		self.assertIn("not as done", result["message"])


class TestViewAndFilters(ExternalActionBase):
	def test_blocking_actions_are_reported(self):
		frappe.set_user(self.manager)
		data = ext.get_external_actions()
		self.assertGreater(data["blocking_outstanding"], 0)
		self.assertFalse(data["go_live_ready"])

	def test_blocking_filter_narrows_to_blocking_work(self):
		frappe.set_user(self.manager)
		data = ext.get_external_actions(blocking_only=1)
		self.assertTrue(data["items"])
		for item in data["items"]:
			self.assertTrue(item["blocking_go_live"])

	def test_a_blocking_action_cannot_be_hidden_by_filtering(self):
		"""Filters narrow the view; the blocking count is computed from all rows."""
		frappe.set_user(self.manager)
		unfiltered = ext.get_external_actions()
		filtered = ext.get_external_actions(category="Email")
		self.assertEqual(filtered["blocking_outstanding"],
		                 unfiltered["blocking_outstanding"])
		self.assertEqual(filtered["total"], unfiltered["total"])

	def test_category_filter_works(self):
		frappe.set_user(self.manager)
		data = ext.get_external_actions(category="Infrastructure")
		self.assertTrue(data["items"])
		for item in data["items"]:
			self.assertEqual(item["category"], "Infrastructure")

	def test_ready_filter_shows_only_ready_actions(self):
		frappe.set_user(self.manager)
		ext.mark_action_complete("EXT-13", evidence_reference="x")
		data = ext.get_external_actions(ready_only=1)
		self.assertTrue(any(i["action_id"] == "EXT-13" for i in data["items"]))
		for item in data["items"]:
			self.assertEqual(item["status"], "Ready for Verification")

	def test_go_live_blockers_names_them(self):
		frappe.set_user(self.manager)
		result = ext.go_live_blockers()
		self.assertFalse(result["ready"])
		self.assertGreater(result["count"], 0)
		self.assertIn("None of them can be completed by changing this software",
		              result["statement"])

	def test_evidence_is_reported_per_action(self):
		frappe.set_user(self.manager)
		for item in ext.get_external_actions()["items"]:
			if item["status"] == "Verified":
				self.assertTrue(item["evidence"],
				                f"{item['action_id']} is Verified with no evidence")


class TestRouteIsReal(ExternalActionBase):
	def test_route_resolves(self):
		from my_store_ui.standalone import resolve_frontend_route

		definition, params = resolve_frontend_route(
			"/retail-erp/admin/readiness/external-actions")
		self.assertIsNotNone(definition)
		self.assertEqual(definition["name"], "external-actions")

	def test_route_is_role_gated(self):
		from my_store_ui.services.frontend_routes import ROUTE_REGISTRY

		entry = next(r for r in ROUTE_REGISTRY if r["name"] == "external-actions")
		self.assertTrue(entry.get("roles"))
		self.assertNotIn("Sales User", entry["roles"])


if __name__ == "__main__":
	unittest.main()
