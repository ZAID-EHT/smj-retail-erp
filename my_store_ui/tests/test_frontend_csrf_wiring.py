"""Every write from the SPA must send a real CSRF token.

Frappe rejects a POST carrying a missing or wrong CSRF token with exactly
"Invalid Request" (`frappe/auth.py` -> `frappe.CSRFTokenError`). That is a
generic-looking message with no hint of a cause, which is why six call sites sent
an empty token for a long time without anybody tracing it: image upload, product
and customer quick entry, scheduled reports, the setup wizard and access
management all read `window.csrf_token`, a global nothing ever assigns.

The token is stored by `services/session.js` on `window.frappe.csrf_token`. These
tests read the frontend sources and fail if any file reaches for the wrong one, or
if the store that populates it moves.
"""

from __future__ import annotations

import pathlib
import re
import unittest

import frappe

FRONTEND = pathlib.Path(frappe.get_app_path("my_store_ui")).parent / "frontend" / "src"

CORRECT_GLOBAL = "window.frappe?.csrf_token"
# The global nothing assigns. Matched with a boundary so it does not also match
# the correct `window.frappe?.csrf_token`.
WRONG_GLOBAL = re.compile(r"window\.csrf_token")

CSRF_HEADER = "X-Frappe-CSRF-Token"


def _sources():
	if not FRONTEND.exists():
		return []
	return [p for p in FRONTEND.rglob("*")
	        if p.suffix in (".js", ".vue") and p.is_file()]


class TestCsrfWiring(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.sources = _sources()

	def setUp(self):
		if not self.sources:
			self.skipTest("frontend sources are not present in this checkout")

	def test_no_source_reads_the_unassigned_global(self):
		"""`window.csrf_token` is never assigned; reading it sends an empty token."""
		offenders = []
		for path in self.sources:
			text = path.read_text(encoding="utf-8")
			for line_no, line in enumerate(text.splitlines(), start=1):
				if WRONG_GLOBAL.search(line):
					offenders.append(f"{path.relative_to(FRONTEND)}:{line_no}")
		self.assertEqual(
			offenders, [],
			"these read window.csrf_token, which nothing assigns; every write "
			"through them fails with Frappe's 'Invalid Request': "
			+ ", ".join(offenders))

	def test_every_csrf_header_uses_a_populated_token(self):
		"""Either the global, or the session store's own copy of it.

		`session.js` owns the token and legitimately sends `state.csrfToken`,
		which is the same value it writes to the global.
		"""
		accepted = (CORRECT_GLOBAL, "state.csrfToken")
		wrong = []
		for path in self.sources:
			text = path.read_text(encoding="utf-8")
			for line_no, line in enumerate(text.splitlines(), start=1):
				if CSRF_HEADER not in line:
					continue
				if not any(source in line for source in accepted):
					wrong.append(f"{path.relative_to(FRONTEND)}:{line_no}")
		self.assertEqual(
			wrong, [],
			f"these send the {CSRF_HEADER} header without a populated token "
			f"({' or '.join(accepted)}): " + ", ".join(wrong))

	def test_the_session_store_still_populates_the_global(self):
		"""If this assignment moves, every write in the SPA breaks at once."""
		session = FRONTEND / "services" / "session.js"
		self.assertTrue(session.exists(), "services/session.js is missing")
		text = session.read_text(encoding="utf-8")
		self.assertIn(
			"window.frappe.csrf_token", text,
			"session.js no longer assigns window.frappe.csrf_token; nothing else "
			"populates it")

	def test_the_image_uploader_sends_a_csrf_header(self):
		"""The upload this was first reported against."""
		uploader = FRONTEND / "components" / "forms" / "ImageUpload.vue"
		self.assertTrue(uploader.exists())
		text = uploader.read_text(encoding="utf-8")
		self.assertIn(CSRF_HEADER, text)
		self.assertIn(CORRECT_GLOBAL, text)

	def test_the_bootstrap_endpoint_still_returns_a_token(self):
		"""The client can only send what the server hands it."""
		from my_store_ui.standalone import get_session_bootstrap

		bootstrap = get_session_bootstrap()
		self.assertTrue(bootstrap.get("authenticated"))
		self.assertIn("csrf_token", bootstrap)


if __name__ == "__main__":
	unittest.main()
