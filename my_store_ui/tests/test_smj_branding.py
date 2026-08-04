"""The SMJ mark is the brand everywhere, including the pages the SPA does not own.

Branding breaks in a particular way: it looks right on the screen someone checked
and wrong on the login page, the desk, or a browser tab. So these tests cover the
three separate places an icon has to be declared -- the SPA's own `<head>`, the
shell component, and Website/Navbar Settings, which is what every non-SPA page
reads -- rather than assuming one implies the others.
"""

from __future__ import annotations

import pathlib
import unittest

import frappe

APP = pathlib.Path(frappe.get_app_path("my_store_ui"))
IMAGES = APP / "public" / "images"
FRONTEND = APP.parent / "frontend" / "src"

LOGO_URL = "/assets/my_store_ui/images/smj-logo.png"
FAVICON_URL = "/assets/my_store_ui/images/favicon.ico"

# Every icon the head declares. A link to a file that is not shipped is a broken
# icon in the tab, which nobody notices until it is in front of a client.
EXPECTED_FILES = (
	"smj-logo.png", "favicon.ico", "favicon-16.png", "favicon-32.png",
	"favicon-48.png", "favicon-64.png", "favicon-192.png", "favicon-512.png",
	"apple-touch-icon.png",
)


class TestBrandAssets(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def test_every_declared_icon_file_ships(self):
		missing = [name for name in EXPECTED_FILES if not (IMAGES / name).is_file()]
		self.assertEqual(missing, [], f"declared but not shipped: {missing}")

	def test_icons_are_not_empty(self):
		for name in EXPECTED_FILES:
			self.assertGreater((IMAGES / name).stat().st_size, 100,
			                   f"{name} looks like a placeholder")

	def test_favicons_are_square(self):
		"""A non-square favicon is letterboxed or stretched by the browser."""
		try:
			from PIL import Image
		except ImportError:
			self.skipTest("Pillow is not available")
		for name in ("favicon-16.png", "favicon-32.png", "favicon-48.png",
		             "favicon-64.png", "favicon-192.png", "apple-touch-icon.png"):
			with Image.open(IMAGES / name) as img:
				self.assertEqual(img.size[0], img.size[1], f"{name} is {img.size}")

	def test_favicon_ico_carries_multiple_sizes(self):
		try:
			from PIL import Image
		except ImportError:
			self.skipTest("Pillow is not available")
		with Image.open(IMAGES / "favicon.ico") as img:
			self.assertGreaterEqual(len(getattr(img, "ico", img).sizes()), 2)


class TestSpaBranding(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def test_page_context_serves_the_smj_logo_by_default(self):
		from my_store_ui.www.retail_erp import get_context

		context = frappe._dict()
		get_context(context)
		company_logo = None
		company = frappe.defaults.get_global_default("company")
		if company:
			company_logo = frappe.db.get_value("Company", company, "company_logo")
		if company_logo:
			self.skipTest("this site has its own company logo, which takes priority")
		self.assertEqual(context.retail_logo, LOGO_URL)
		self.assertEqual(context.retail_bootstrap["logo"], LOGO_URL)

	def test_the_page_head_declares_the_icons(self):
		head = (APP / "www" / "retail_erp.html").read_text(encoding="utf-8")
		for fragment in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
			self.assertIn(fragment, head, f"{fragment} is not linked in the head")
		self.assertIn('rel="apple-touch-icon"', head)

	def test_the_shell_no_longer_falls_back_to_a_stock_icon(self):
		"""The house icon is what used to show when no company logo was set."""
		brand = FRONTEND / "components" / "shell" / "CompanyBrand.vue"
		if not brand.exists():
			self.skipTest("frontend sources are not present in this checkout")
		text = brand.read_text(encoding="utf-8")
		self.assertIn(LOGO_URL, text, "the shell does not reference the SMJ mark")
		self.assertNotIn("SmjHomeBuilding", text,
		                 "the shell still falls back to the stock house icon")


class TestSiteWideBranding(unittest.TestCase):
	"""Website and Navbar Settings drive every page the SPA does not render."""

	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def test_website_favicon_is_set(self):
		self.assertEqual(
			frappe.db.get_single_value("Website Settings", "favicon"), FAVICON_URL,
			"non-SPA pages would show the Frappe default icon")

	def test_website_app_logo_is_set(self):
		self.assertEqual(
			frappe.db.get_single_value("Website Settings", "app_logo"), LOGO_URL)

	def test_navbar_logo_is_set(self):
		if not frappe.db.exists("DocType", "Navbar Settings"):
			self.skipTest("Navbar Settings is not installed")
		self.assertEqual(
			frappe.db.get_single_value("Navbar Settings", "app_logo"), LOGO_URL)

	def test_the_patch_does_not_overwrite_a_deliberate_choice(self):
		"""A site that picked its own icon must keep it."""
		from my_store_ui.patches.install_smj_branding import REPLACEABLE, execute

		original = frappe.db.get_single_value("Website Settings", "favicon")
		chosen = "/files/a-client-chose-this.png"
		try:
			frappe.db.set_single_value("Website Settings", "favicon", chosen)
			self.assertNotIn(chosen, REPLACEABLE)
			execute()
			self.assertEqual(
				frappe.db.get_single_value("Website Settings", "favicon"), chosen,
				"the patch overwrote a favicon somebody deliberately set")
		finally:
			frappe.db.set_single_value("Website Settings", "favicon", original)

	def test_the_patch_is_idempotent(self):
		from my_store_ui.patches.install_smj_branding import execute

		execute()
		execute()
		self.assertEqual(
			frappe.db.get_single_value("Website Settings", "favicon"), FAVICON_URL)


if __name__ == "__main__":
	unittest.main()
