from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestGeneratedFeatureInventory(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.repo = Path(__file__).resolve().parents[2]
		cls.inventory = json.loads((cls.repo / "docs" / "erpnext-v15-complete-inventory.json").read_text())

	def test_every_feature_has_a_stable_unique_identifier_and_classification(self):
		features = self.inventory["features"]
		ids = [feature["feature_id"] for feature in features]
		self.assertEqual(len(ids), len(set(ids)))
		self.assertTrue(all(feature["classification"] in set("ABCDEFG") for feature in features))

	def test_every_user_facing_feature_has_a_documented_dependency(self):
		for feature in self.inventory["features"]:
			if feature["user_facing"]:
				self.assertTrue(feature["remaining_desk_dependency"])

	def test_inventory_contains_every_installed_application(self):
		apps = {entry["application"] for entry in self.inventory["applications"]}
		self.assertEqual(
			apps,
			{"frappe", "erpnext", "posawesome", "my_store_ui", "smj_theme", "erpnext_chatgpt", "erpnext_gemini_integration"},
		)

	def test_parity_audit_does_not_claim_false_completion(self):
		self.assertEqual(self.inventory["automated_audit"]["status"], "fail")
		self.assertGreater(self.inventory["automated_audit"]["failure_counts"]["unmapped_user_facing"], 0)


if __name__ == "__main__":
	unittest.main()
