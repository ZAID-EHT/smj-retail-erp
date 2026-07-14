"""Validation tests for the authoritative parity registry (Stage 2).

These enforce the honesty contract described in
`my_store_ui/audit/parity_registry.py`. They read the committed canonical
inventory, so they run under the Frappe test runner (when `allow_tests` is
enabled) and also standalone via plain Python.
"""
import unittest

from my_store_ui.audit import parity_registry as pr


class TestParityRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = pr.build_parity_registry()

    def test_validation_passes(self):
        result = pr.validate_parity_registry(self.registry)
        self.assertEqual(result["status"], "pass", msg=str(result["errors"]))

    def test_no_duplicate_keys(self):
        keys = [e["feature_key"] for e in self.registry["entries"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_entry_has_known_status_priority_strategy(self):
        for e in self.registry["entries"]:
            self.assertIn(e["status"], pr.STATUSES, e["feature_key"])
            self.assertIn(e["business_priority"], pr.PRIORITIES, e["feature_key"])
            self.assertIn(e["implementation_strategy"], pr.STRATEGIES, e["feature_key"])

    def test_verified_complete_requires_evidence(self):
        for e in self.registry["entries"]:
            if e["status"] == "verified_complete":
                self.assertTrue(e.get("evidence"), e["feature_key"])
                self.assertNotIn(e.get("verification_level"), {None, "route_only", "n/a"}, e["feature_key"])

    def test_route_is_never_alone_treated_as_complete(self):
        # No entry may be verified_complete solely on the basis of a route.
        for e in self.registry["entries"]:
            if e["retail_erp_route"] and e["status"] == "verified_complete":
                self.assertNotIn(e.get("verification_level"), {"route_only", None, "n/a"}, e["feature_key"])

    def test_unavailable_and_not_required_have_no_route(self):
        for e in self.registry["entries"]:
            if e["status"] in {"unavailable_with_reason", "not_required"}:
                self.assertIsNone(e["retail_erp_route"], e["feature_key"])

    def test_covers_every_user_facing_feature(self):
        result = pr.validate_parity_registry(self.registry)
        self.assertNotIn("no registry entry", " ".join(result["errors"]))


if __name__ == "__main__":
    unittest.main()
