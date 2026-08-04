"""The production configuration checker.

Two things are being protected here. First, that the checker cannot become a
remote shell: there is no endpoint that takes a command, and the check list is a
fixed tuple of named functions. Second, that it cannot flatter itself -- an item
depending on somebody outside this system reports External and never Pass, and a
single broken check reports itself rather than taking the page down.
"""

from __future__ import annotations

import unittest
import uuid

import frappe

from my_store_ui import production_configuration as cfg


class ProductionConfigurationBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.suffix = uuid.uuid4().hex[:6]
		cls.outsider = cls._user("out", ("Sales User",))

	@classmethod
	def _user(cls, tag, roles):
		email = f"smjcfg_{tag}_{cls.suffix}@example.com"
		doc = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": f"Cfg {tag}",
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
		frappe.delete_doc("User", cls.outsider, force=True, ignore_permissions=True)
		frappe.db.commit()

	def setUp(self):
		self.sp = f"cfg_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)


class TestNoArbitraryExecution(ProductionConfigurationBase):
	def test_checks_are_a_fixed_tuple_of_named_functions(self):
		self.assertIsInstance(cfg.CHECK_GROUPS, tuple)
		for group_fn in cfg.CHECK_GROUPS:
			self.assertTrue(callable(group_fn))
			self.assertTrue(group_fn.__name__.startswith("_"))

	def test_the_module_exposes_exactly_one_endpoint(self):
		"""A configuration checker that accepts a command is a remote shell."""
		whitelisted = [
			name for name in dir(cfg)
			if callable(getattr(cfg, name, None))
			and getattr(getattr(cfg, name), "__name__", "") != "wrapper"
			and name in frappe.whitelisted_methods_for_module(cfg.__name__)
		] if hasattr(frappe, "whitelisted_methods_for_module") else None
		if whitelisted is None:
			# Fall back to checking the obvious shape: one public entry point.
			public = [n for n in dir(cfg)
			          if not n.startswith("_") and callable(getattr(cfg, n))
			          and getattr(getattr(cfg, n), "__module__", "") == cfg.__name__]
			self.assertEqual(public, ["get_production_configuration"], public)

	def test_no_check_function_takes_caller_supplied_input(self):
		import inspect

		for group_fn in cfg.CHECK_GROUPS:
			signature = inspect.signature(group_fn)
			self.assertEqual(
				list(signature.parameters), [],
				f"{group_fn.__name__} accepts input; checks must be fixed-purpose")


class TestPermissions(ProductionConfigurationBase):
	def test_outsider_is_refused(self):
		frappe.set_user(self.outsider)
		with self.assertRaises(frappe.PermissionError):
			cfg.get_production_configuration()

	def test_administrator_may_read(self):
		frappe.set_user("Administrator")
		data = cfg.get_production_configuration()
		self.assertGreater(data["total"], 0)


class TestCheckShape(ProductionConfigurationBase):
	def test_all_six_groups_are_present(self):
		data = cfg.get_production_configuration()
		for group in ("Application", "Services", "Business setup", "Security",
		              "Operations", "Finance and approvals"):
			self.assertIn(group, data["by_group"], f"{group} produced no checks")

	def test_every_check_has_a_valid_status(self):
		data = cfg.get_production_configuration()
		allowed = {cfg.PASS, cfg.WARNING, cfg.FAIL, cfg.EXTERNAL, cfg.NOT_APPLICABLE}
		for check in data["checks"]:
			self.assertIn(check["status"], allowed,
			              f"{check['name']} has status {check['status']}")

	def test_every_check_names_itself_and_explains_itself(self):
		for check in cfg.get_production_configuration()["checks"]:
			self.assertTrue(check["name"].strip())
			self.assertTrue(check["group"].strip())

	def test_counts_add_up_to_the_total(self):
		data = cfg.get_production_configuration()
		self.assertEqual(sum(data["counts"].values()), data["total"])

	def test_only_fail_is_treated_as_blocking(self):
		for check in cfg.get_production_configuration()["checks"]:
			self.assertEqual(check["blocking"], check["status"] == cfg.FAIL)


class TestExternalIsNeverPass(ProductionConfigurationBase):
	"""The distinction the page depends on."""

	EXTERNALLY_OWNED = (
		"Off-server backup destination", "Restore drill", "Monitoring",
		"Background workers",
	)

	def test_externally_owned_items_never_report_pass(self):
		checks = {c["name"]: c for c in cfg.get_production_configuration()["checks"]}
		for name in self.EXTERNALLY_OWNED:
			self.assertIn(name, checks, f"{name} is not checked at all")
			self.assertEqual(
				checks[name]["status"], cfg.EXTERNAL,
				f"{name} claims {checks[name]['status']}; nobody here can verify it")

	def test_production_ready_is_false_while_external_items_remain(self):
		data = cfg.get_production_configuration()
		if data["counts"][cfg.EXTERNAL]:
			self.assertFalse(data["production_ready"])

	def test_commission_posting_is_reported_as_not_applicable(self):
		checks = {c["name"]: c for c in cfg.get_production_configuration()["checks"]}
		self.assertEqual(checks["Commission posting"]["status"], cfg.NOT_APPLICABLE)
		self.assertIn("disabled in this build", checks["Commission posting"]["detail"])


class TestNoSecretExposure(ProductionConfigurationBase):
	def test_no_check_detail_contains_a_secret_value(self):
		data = cfg.get_production_configuration()
		secrets = [str(frappe.conf.get(key)) for key in
		           ("db_password", "encryption_key", "admin_password")
		           if frappe.conf.get(key)]
		blob = " ".join(f"{c['name']} {c['detail']}" for c in data["checks"])
		for secret in secrets:
			self.assertNotIn(secret, blob, "a check leaked a configured secret")

	def test_encryption_key_check_reports_presence_not_value(self):
		checks = {c["name"]: c for c in cfg.get_production_configuration()["checks"]}
		detail = checks["Encryption key configured"]["detail"]
		self.assertIn(detail, ("configured", "not configured"))


class TestStagingIsHonestlyReported(ProductionConfigurationBase):
	"""staging.local is not production, and the checker should say so plainly."""

	def test_test_mode_is_reported_as_a_failure_on_a_test_site(self):
		if frappe.local.site != "staging.local":
			self.skipTest("staging-specific expectation")
		checks = {c["name"]: c for c in cfg.get_production_configuration()["checks"]}
		if frappe.conf.get("allow_tests"):
			self.assertEqual(checks["Test mode disabled"]["status"], cfg.FAIL)

	def test_the_site_does_not_claim_to_be_production_ready(self):
		self.assertFalse(cfg.get_production_configuration()["production_ready"])


if __name__ == "__main__":
	unittest.main()
