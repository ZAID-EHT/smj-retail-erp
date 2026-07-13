from pathlib import Path
import unittest


class TestRetailERPScrolling(unittest.TestCase):
	def test_shared_shell_keeps_browser_page_scrolling_enabled(self):
		css = (Path(__file__).resolve().parents[2] / "frontend" / "src" / "design" / "base.css").read_text()
		self.assertNotIn("body.retail-erp-active { overflow: hidden", css)
		self.assertIn("overflow-y: auto", css)
		self.assertIn(".retail-erp-page .retail-erp-mount { min-height: 100vh; overflow: visible; }", css)
		self.assertIn(".ref-app-shell { min-height: 100vh; overflow: visible;", css)
		self.assertIn("overflow-y: visible", css)

	def test_dialogs_scroll_internally_without_body_scroll_lock(self):
		css = (Path(__file__).resolve().parents[2] / "frontend" / "src" / "design" / "base.css").read_text()
		self.assertIn("max-height: min(760px,calc(100vh - 40px)); overflow: auto", css)
		self.assertNotIn("body.modal-open", css)
		self.assertNotIn("body.scroll-lock", css)
