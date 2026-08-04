"""Home dashboard KPIs, and the two ways they were silently reading zero.

Both defects produced the same symptom -- a confident `LKR 0` on a tile -- from
completely different causes, which is why they survived: a dashboard that renders
0 for "no margin this month", "the report crashed" and "I read the wrong column"
gives you no way to tell them apart.

- Gross Profit called ERPNext's report without `group_by`. That report treats it
  as required-with-a-default and raised `'NoneType' object is not iterable`; the
  bare `except` swallowed it and left the tile at 0. It had logged 308 times.
- Reserved Stock Value summed `reserved_stock`, which only carries a value when
  Stock Reservation Entries are in play. Ordinary Sales Order reservation lands in
  `reserved_qty`, so the tile read 0 while stock really was reserved -- and
  Available-to-Sell was overstated by exactly the same amount.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui import dashboard_analytics as da


class HomeKpiBase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")

	def setUp(self):
		self.sp = f"kpi_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point=self.sp)

	def _kpi(self, key):
		return next(k for k in da.get_home_kpis()["kpis"] if k["key"] == key)


class TestGrossProfit(HomeKpiBase):
	def test_the_report_is_called_with_a_group_by(self):
		"""Without it the report raises and the tile silently reads zero."""
		captured = {}
		import frappe.desk.query_report as qr

		original = qr.run

		def spy(report_name, filters=None, **kwargs):
			captured["filters"] = dict(filters or {})
			return original(report_name, filters=filters, **kwargs)

		qr.run = spy
		try:
			da._gross_profit("2026-08-01", "2026-08-31", None)
		finally:
			qr.run = original
		self.assertIn("group_by", captured.get("filters", {}),
		              "Gross Profit was called without group_by; it will raise")

	def test_gross_profit_computes_without_error(self):
		value, error = da._gross_profit("2026-08-01", "2026-08-31", None)
		self.assertIsNone(error, f"gross profit could not be computed: {error}")
		self.assertIsInstance(value, float)

	def test_only_invoice_level_rows_are_summed(self):
		"""Grouping by Invoice returns a tree; summing every row double-counts."""
		from frappe.desk.query_report import run as run_report

		company = da._company()
		filters = {"from_date": "2026-08-01", "to_date": "2026-08-31",
		           "group_by": da.GROSS_PROFIT_GROUP_BY}
		if company:
			filters["company"] = company
		result = run_report("Gross Profit", filters=filters, ignore_prepared_report=True)

		parents = 0.0
		children = 0.0
		for row in result.get("result") or []:
			if not isinstance(row, dict):
				continue
			if flt(row.get("indent")) == 0:
				parents += flt(row.get("gross_profit"))
			else:
				children += flt(row.get("gross_profit"))

		value, error = da._gross_profit("2026-08-01", "2026-08-31", company)
		self.assertIsNone(error)
		self.assertAlmostEqual(value, parents, places=2)
		if children:
			self.assertNotAlmostEqual(
				value, parents + children, places=2,
				msg="the KPI is summing child rows as well; that double-counts")

	def test_a_failing_report_is_not_reported_as_zero_profit(self):
		"""A crash and a flat month must not look the same on the tile."""
		import frappe.desk.query_report as qr

		original = qr.run

		def boom(*args, **kwargs):
			raise TypeError("'NoneType' object is not iterable")

		qr.run = boom
		try:
			value, error = da._gross_profit("2026-08-01", "2026-08-31", None)
			tile = self._kpi("gross_profit")
		finally:
			qr.run = original

		self.assertEqual(value, 0.0)
		self.assertIsNotNone(error, "a failed report reported success")
		self.assertTrue(tile["unavailable"], "the tile claims a real zero")
		self.assertTrue(tile["unavailable_reason"])

	def test_a_working_report_is_not_flagged_unavailable(self):
		tile = self._kpi("gross_profit")
		self.assertFalse(tile["unavailable"])
		self.assertIsNone(tile["unavailable_reason"])


class TestReservedStock(HomeKpiBase):
	def _bin_totals(self):
		return frappe.db.sql(
			"""select ifnull(sum(reserved_stock * valuation_rate), 0),
			          ifnull(sum(reserved_qty * valuation_rate), 0),
			          ifnull(sum(actual_qty * valuation_rate), 0)
			   from tabBin""")[0]

	def test_reserved_value_falls_back_to_reserved_qty(self):
		"""reserved_stock is only populated by Stock Reservation Entries."""
		reserved_stock_value, reserved_qty_value, _actual = self._bin_totals()
		expected = flt(reserved_stock_value) or flt(reserved_qty_value)
		self.assertAlmostEqual(self._kpi("reserved_stock")["value"], expected, places=2)

	def test_reserved_value_is_not_zero_while_stock_is_reserved(self):
		reserved_stock_value, reserved_qty_value, _actual = self._bin_totals()
		if not (flt(reserved_stock_value) or flt(reserved_qty_value)):
			self.skipTest("nothing is reserved on this site")
		self.assertGreater(
			self._kpi("reserved_stock")["value"], 0,
			"stock is reserved but the tile reads zero")

	def test_available_to_sell_is_actual_less_reserved(self):
		reserved_stock_value, reserved_qty_value, actual = self._bin_totals()
		reserved = flt(reserved_stock_value) or flt(reserved_qty_value)
		self.assertAlmostEqual(
			self._kpi("available_to_sell")["value"], flt(actual) - reserved, places=2)

	def test_available_to_sell_is_not_overstated(self):
		"""Reading the wrong reserved column inflates this tile silently."""
		_rs, _rq, actual = self._bin_totals()
		available = self._kpi("available_to_sell")["value"]
		reserved = self._kpi("reserved_stock")["value"]
		if reserved:
			self.assertLess(available, flt(actual))


class TestKpiShape(HomeKpiBase):
	def test_every_expected_tile_is_present(self):
		keys = {k["key"] for k in da.get_home_kpis()["kpis"]}
		self.assertEqual(
			keys,
			{"total_sales", "receivables", "gross_profit", "reserved_stock",
			 "available_to_sell", "pending_deliveries"})

	def test_every_tile_has_a_numeric_value(self):
		for tile in da.get_home_kpis()["kpis"]:
			self.assertIsInstance(tile["value"], (int, float),
			                      f"{tile['key']} is not numeric")


if __name__ == "__main__":
	unittest.main()
