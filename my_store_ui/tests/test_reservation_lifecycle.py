"""One continuous reservation lifecycle trace, asserted end to end.

Drives the same item/warehouse/customer through receipt -> Sales Order -> reserve
-> release -> re-reserve -> partial delivery -> full delivery -> return, using only
standard ERPNext controllers, and asserts the invariant
Available-to-Sell = Actual - Reserved at every step, plus the physical-vs-reserved
distinctions. The reusable trace lives in
dev_scripts/reservation_lifecycle_trace.py and is documented in
docs/verification/SMJ_RESERVATION_LIFECYCLE_TRACE.md.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.dev_scripts import reservation_lifecycle_trace as trace


class TestReservationLifecycle(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.enabled = bool(frappe.db.get_single_value("Stock Settings", "enable_stock_reservation"))
		cls.on_staging = frappe.local.site == "staging.local"

	def test_continuous_lifecycle_holds_all_invariants(self):
		if not self.enabled or not self.on_staging:
			self.skipTest("needs staging.local with stock reservation enabled")
		result = trace.execute()
		steps = {row["step"]: row for row in result["trace"]}

		# Every step satisfies Available = Actual - Reserved and never goes negative.
		self.assertTrue(result["all_invariants_ok"])
		self.assertTrue(result["no_negative_available"])

		# Reserving does not touch physical Actual, only Available.
		self.assertEqual(steps["3_reserved_12"]["actual"], 20.0)
		self.assertEqual(steps["3_reserved_12"]["reserved"], 12.0)
		self.assertEqual(steps["3_reserved_12"]["available"], 8.0)

		# Releasing restores Available fully.
		self.assertEqual(steps["4_unreserved_released"]["reserved"], 0.0)
		self.assertEqual(steps["4_unreserved_released"]["available"], 20.0)

		# Delivery reduces physical Actual and consumes the reservation.
		self.assertEqual(steps["8_delivered_5"]["actual"], 15.0)
		self.assertEqual(steps["8_delivered_5"]["reserved"], 7.0)

		# Full delivery consumes the reservation entirely.
		self.assertEqual(steps["9_delivered_remaining_7"]["actual"], 8.0)
		self.assertEqual(steps["9_delivered_remaining_7"]["reserved"], 0.0)

		# Return increases physical stock and does not recreate a reservation.
		self.assertEqual(steps["12_returned_2"]["actual"], 10.0)
		self.assertEqual(steps["12_returned_2"]["reserved"], 0.0)

		# No abandoned open reservation remains after full delivery.
		self.assertEqual(result["open_reservations_after_full_delivery"], [])
		self.assertTrue(result["teardown_ok"])


if __name__ == "__main__":
	unittest.main()
