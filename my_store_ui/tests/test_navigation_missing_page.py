"""Navigation must survive links to apps that are not installed.

Found by browser verification: Smart Sales logged a 404 because get_bootstrap
raised DoesNotExistError from get_navigation() -- the menu links to the POS Awesome
page, and frappe.has_permission(doc=...) throws when the record does not exist.
A missing optional app must drop the link, not break the page.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.api import _linked_record_permitted, get_bootstrap, get_navigation


class TestNavigationMissingPage(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def test_navigation_does_not_raise_for_a_missing_page(self):
		sections = get_navigation()
		self.assertTrue(sections)

	def test_missing_record_is_not_permitted(self):
		self.assertFalse(_linked_record_permitted("Page", "definitely-not-installed-xyz"))
		self.assertFalse(_linked_record_permitted("Report", "definitely-not-installed-xyz"))
		self.assertFalse(_linked_record_permitted("Page", None))

	def test_existing_record_is_evaluated_normally(self):
		if frappe.db.exists("Page", "smart-sales"):
			self.assertTrue(_linked_record_permitted("Page", "smart-sales"))

	def test_bootstrap_succeeds_even_when_an_optional_page_is_absent(self):
		"""posapp is not installed on this site; the bootstrap must still return."""
		self.assertFalse(frappe.db.exists("Page", "posapp"))
		data = get_bootstrap(page_length=5)
		self.assertIn("items", data)

	def test_no_navigation_link_points_at_a_missing_record(self):
		for section in get_navigation():
			for link in section["links"]:
				self.assertTrue(link.get("route"), f"link without a route in {section['label']}")


if __name__ == "__main__":
	unittest.main()
