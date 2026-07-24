"""Reservation concurrency UX: bounded retry-on-deadlock + friendly message.

Deterministically exercises the retry path in reserve_sales_order by simulating a
MariaDB lock conflict (error 1213) from the standard reservation engine, without a
flaky live two-process run. Confirms:
  * a persistent conflict is retried RESERVE_MAX_ATTEMPTS times then surfaced as a
    friendly ValidationError (not a raw 500 deadlock traceback);
  * a transient conflict that clears is retried and then succeeds.
"""
from __future__ import annotations

import unittest

import frappe

from my_store_ui.wholesale import reservation
from my_store_ui.wholesale.reservation import RESERVE_MAX_ATTEMPTS, _is_lock_conflict, reserve_sales_order


class _Deadlock(Exception):
	def __init__(self):
		super().__init__(1213, "Deadlock found when trying to get lock")


class _FakeSO:
	def __init__(self, fail_times: int):
		self.docstatus = 1
		self.items = []
		self._fail_times = fail_times
		self.attempts = 0

	def reload(self):
		pass

	def create_stock_reservation_entries(self):
		self.attempts += 1
		if self.attempts <= self._fail_times:
			raise _Deadlock()


class TestReservationRetry(unittest.TestCase):
	def setUp(self):
		self._orig = {
			"get_doc": reservation.frappe.get_doc,
			"has_permission": reservation.frappe.has_permission,
			"enabled": reservation._reservation_enabled,
			"lock": reservation._lock_bins,
			"commit": reservation.frappe.db.commit,
			"rollback": reservation.frappe.db.rollback,
			"sleep": reservation.time.sleep,
			"reservations_for": reservation._reservations_for,
			"log_error": reservation.frappe.log_error,
		}
		reservation.frappe.log_error = lambda *a, **k: None
		reservation.frappe.has_permission = lambda *a, **k: True
		reservation._reservation_enabled = lambda: True
		reservation._lock_bins = lambda bins: None
		reservation.frappe.db.commit = lambda: None
		reservation.frappe.db.rollback = lambda: None
		reservation.time.sleep = lambda *_a, **_k: None
		reservation._reservations_for = lambda so: []

	def tearDown(self):
		reservation.frappe.get_doc = self._orig["get_doc"]
		reservation.frappe.has_permission = self._orig["has_permission"]
		reservation._reservation_enabled = self._orig["enabled"]
		reservation._lock_bins = self._orig["lock"]
		reservation.frappe.db.commit = self._orig["commit"]
		reservation.frappe.db.rollback = self._orig["rollback"]
		reservation.time.sleep = self._orig["sleep"]
		reservation._reservations_for = self._orig["reservations_for"]
		reservation.frappe.log_error = self._orig["log_error"]

	def test_is_lock_conflict_classifies_deadlock(self):
		self.assertTrue(_is_lock_conflict(_Deadlock()))
		self.assertFalse(_is_lock_conflict(ValueError("nope")))

	def _patch_get_doc(self, fake):
		# Only intercept the Sales Order fetch; delegate everything else to the real
		# frappe.get_doc so frappe internals (e.g. System Settings) keep working.
		original = self._orig["get_doc"]

		def fake_get_doc(doctype, *args, **kwargs):
			if doctype == "Sales Order":
				return fake
			return original(doctype, *args, **kwargs)

		reservation.frappe.get_doc = fake_get_doc

	def test_persistent_conflict_returns_friendly_error_after_bounded_retries(self):
		fake = _FakeSO(fail_times=RESERVE_MAX_ATTEMPTS + 5)
		self._patch_get_doc(fake)
		with self.assertRaises(frappe.ValidationError) as ctx:
			reserve_sales_order("SO-TEST")
		self.assertIn("another order", str(ctx.exception).lower())
		# Bounded: it did not loop forever.
		self.assertEqual(fake.attempts, RESERVE_MAX_ATTEMPTS)

	def test_transient_conflict_retries_then_succeeds(self):
		fake = _FakeSO(fail_times=1)
		self._patch_get_doc(fake)
		result = reserve_sales_order("SO-TEST")
		self.assertTrue(result["reserved"])
		self.assertEqual(result["attempts"], 2)
