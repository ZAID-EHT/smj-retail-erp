"""Delivery preparation: FIFO batch allocation, payment gate and partial delivery.

Every document is created through standard ERPNext controllers and mappings; the
Stock Ledger is never written directly. Savepoint + rollback, no residue.
"""

from __future__ import annotations

import unittest
import uuid

import frappe
from frappe.utils import flt

from my_store_ui.quick_entry.product import create_product
from my_store_ui.wholesale.credit import (
	CREDIT_CUSTOMER,
	NON_CREDIT_CUSTOMER,
	decide_delivery_gate,
	sales_order_paid_amount,
)
from my_store_ui.wholesale.delivery import (
	create_delivery_note,
	fifo_batches,
	get_fifo_allocation,
	prepare_delivery,
)

RATE_A = 1000.0
RATE_B = 1200.0


class TestDeliveryFifo(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.company = frappe.get_all("Company", pluck="name")[0]
		cls.group = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name")[0]
		cls.wh = frappe.get_all(
			"Warehouse", filters={"is_group": 0, "company": cls.company, "disabled": 0}, pluck="name"
		)[0]
		cls.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		cls.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]

	def setUp(self):
		self.sp = f"deliv_{uuid.uuid4().hex[:6]}"
		frappe.db.savepoint(self.sp)
		self.item = create_product({
			"product_name": f"Deliv {uuid.uuid4().hex[:5]}", "category": self.group,
			"stock_location_1": self.wh, "cost_price": RATE_A, "wholesale_price": 1200,
			"retail_price": 1500,
		})["name"]
		self.customer = self._customer(NON_CREDIT_CUSTOMER)

	def tearDown(self):
		frappe.db.rollback(save_point=self.sp)

	def _customer(self, credit_type, limit=0):
		doc = frappe.get_doc({
			"doctype": "Customer", "customer_name": f"DelivCust {uuid.uuid4().hex[:6]}",
			"custom_credit_type": credit_type, "customer_group": self.customer_group,
			"territory": self.territory,
		})
		if limit:
			doc.append("credit_limits", {"company": self.company, "credit_limit": limit})
		doc.insert(ignore_permissions=True)
		return doc.name

	def _receive(self, qty, rate):
		se = frappe.get_doc({
			"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": self.company,
			"items": [{"item_code": self.item, "qty": qty, "t_warehouse": self.wh, "basic_rate": rate}],
		})
		se.insert(ignore_permissions=True)
		se.submit()
		return se

	def _order(self, qty=5, customer=None, submit=True):
		so = frappe.get_doc({
			"doctype": "Sales Order", "customer": customer or self.customer, "company": self.company,
			"delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
			"items": [{"item_code": self.item, "qty": qty, "rate": 1200, "warehouse": self.wh,
			           "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7)}],
		})
		so.insert(ignore_permissions=True)
		if submit:
			so.submit()
		return so

	def _pay(self, so, amount):
		pe = frappe.get_doc({
			"doctype": "Payment Entry", "payment_type": "Receive", "company": self.company,
			"party_type": "Customer", "party": so.customer, "paid_amount": amount,
			"received_amount": amount, "reference_no": uuid.uuid4().hex[:8],
			"reference_date": frappe.utils.nowdate(),
			"paid_to": frappe.get_all("Account", filters={
				"company": self.company, "account_type": "Bank", "is_group": 0}, pluck="name")[0],
			"references": [{"reference_doctype": "Sales Order", "reference_name": so.name,
			                "allocated_amount": amount}],
		})
		pe.insert(ignore_permissions=True)
		pe.submit()
		return pe

	# --- FIFO allocation ---

	def test_fifo_allocation_spans_two_batches_oldest_first(self):
		self._receive(10, RATE_A)
		self._receive(10, RATE_B)
		batches = fifo_batches(self.item, self.wh, 12)
		self.assertEqual(len(batches), 2)
		self.assertEqual(flt(batches[0]["qty"]), 10.0)
		self.assertEqual(flt(batches[1]["qty"]), 2.0)
		# Oldest batch first.
		older = frappe.db.get_value("Batch", batches[0]["batch_no"], "creation")
		newer = frappe.db.get_value("Batch", batches[1]["batch_no"], "creation")
		self.assertLess(older, newer)

	def test_get_fifo_allocation_reports_shortfall(self):
		self._receive(5, RATE_A)
		res = get_fifo_allocation(self.item, self.wh, 9)
		self.assertEqual(flt(res["allocated_qty"]), 5.0)
		self.assertEqual(flt(res["shortfall"]), 4.0)
		self.assertFalse(res["fully_allocated"])

	def test_non_batch_item_has_no_batch_allocation(self):
		plain = frappe.get_doc({
			"doctype": "Item", "item_code": f"PLAIN-{uuid.uuid4().hex[:6]}",
			"item_name": "Plain", "item_group": self.group, "stock_uom": "Nos", "is_stock_item": 1,
		})
		plain.insert(ignore_permissions=True)
		self.assertEqual(fifo_batches(plain.name, self.wh, 5), [])

	# --- payment gate ---

	def test_non_credit_delivery_blocked_without_payment(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		prep = prepare_delivery(so.name)
		self.assertFalse(prep["gate"]["allowed"])
		with self.assertRaises(frappe.ValidationError):
			create_delivery_note(so.name)

	def test_non_credit_delivery_allowed_after_full_payment(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		self.assertEqual(flt(sales_order_paid_amount(so.name)), flt(so.grand_total))
		gate = prepare_delivery(so.name)["gate"]
		self.assertTrue(gate["allowed"], gate.get("reason"))
		res = create_delivery_note(so.name, submit=1)
		self.assertEqual(frappe.get_doc("Delivery Note", res["name"]).docstatus, 1)

	def test_partial_payment_still_blocks_and_reports_shortfall(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, flt(so.grand_total) / 2)
		gate = prepare_delivery(so.name)["gate"]
		self.assertFalse(gate["allowed"])
		self.assertTrue(gate["requires_manager_approval"])
		self.assertAlmostEqual(flt(gate["shortfall"]), flt(so.grand_total) / 2, places=2)

	def test_override_requires_a_reason(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		with self.assertRaises(frappe.ValidationError):
			create_delivery_note(so.name, override_reason="   ")

	def test_override_with_reason_is_audited(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		res = create_delivery_note(so.name, override_reason="Owner approved on call")
		self.assertTrue(res["overridden"])
		comment = frappe.db.get_value(
			"Comment", {"reference_doctype": "Delivery Note", "reference_name": res["name"]}, "content"
		)
		self.assertIn("Owner approved on call", comment)

	def test_gate_decision_unpaid_non_credit_is_overridable(self):
		d = decide_delivery_gate(NON_CREDIT_CUSTOMER, False, 0, 0, 0, paid_amount=0, order_total=5000)
		self.assertFalse(d["allowed"])
		self.assertTrue(d["requires_manager_approval"])
		self.assertEqual(flt(d["shortfall"]), 5000.0)

	def test_gate_decision_paid_non_credit_is_allowed(self):
		d = decide_delivery_gate(NON_CREDIT_CUSTOMER, False, 0, 0, 0, paid_amount=5000, order_total=5000)
		self.assertTrue(d["allowed"])
		self.assertFalse(d["requires_manager_approval"])

	# --- delivery mechanics ---

	def test_delivery_reduces_physical_stock_via_standard_ledger(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		before = flt(frappe.db.get_value("Bin", {"item_code": self.item, "warehouse": self.wh}, "actual_qty"))
		create_delivery_note(so.name, submit=1)
		after = flt(frappe.db.get_value("Bin", {"item_code": self.item, "warehouse": self.wh}, "actual_qty"))
		self.assertEqual(before - after, 5.0)

	def test_partial_delivery_leaves_the_order_open(self):
		self._receive(20, RATE_A)
		so = self._order(10)
		self._pay(so, so.grand_total)
		create_delivery_note(so.name, lines=[{"idx": 1, "qty": 4}], submit=1)
		so.reload()
		self.assertEqual(flt(so.items[0].delivered_qty), 4.0)
		self.assertLess(flt(so.per_delivered), 100.0)
		prep = prepare_delivery(so.name)
		self.assertEqual(flt(prep["lines"][0]["remaining_qty"]), 6.0)
		self.assertFalse(prep["fully_delivered"])

	def test_second_delivery_completes_the_order(self):
		self._receive(20, RATE_A)
		so = self._order(10)
		self._pay(so, so.grand_total)
		create_delivery_note(so.name, lines=[{"idx": 1, "qty": 4}], submit=1)
		create_delivery_note(so.name, lines=[{"idx": 1, "qty": 6}], submit=1)
		so.reload()
		self.assertEqual(flt(so.items[0].delivered_qty), 10.0)
		self.assertGreaterEqual(flt(so.per_delivered), 100.0)

	def test_over_delivery_is_refused(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		with self.assertRaises(frappe.ValidationError):
			create_delivery_note(so.name, lines=[{"idx": 1, "qty": 9}])

	def test_fully_delivered_order_cannot_be_delivered_again(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		create_delivery_note(so.name, submit=1)
		with self.assertRaises(frappe.ValidationError):
			create_delivery_note(so.name)

	def test_duplicate_request_id_returns_the_same_delivery(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		rid = uuid.uuid4().hex
		first = create_delivery_note(so.name, request_id=rid)
		second = create_delivery_note(so.name, request_id=rid)
		self.assertEqual(first["name"], second["name"])
		self.assertTrue(second["duplicate"])

	def test_idempotency_survives_cache_loss(self):
		"""A Redis restart must not let a retried request dispatch goods twice."""
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		rid = uuid.uuid4().hex
		first = create_delivery_note(so.name, request_id=rid)
		# Simulate the cache going away entirely.
		frappe.cache.delete_value(f"my_store_ui:idem:Delivery Note:{frappe.session.user}:{rid}")
		second = create_delivery_note(so.name, request_id=rid)
		self.assertEqual(first["name"], second["name"])
		self.assertTrue(second["duplicate"])
		self.assertEqual(
			frappe.db.count("Delivery Note", {"custom_request_id": rid}), 1,
			"a retried request must not create a second Delivery Note",
		)

	def test_request_id_is_recorded_on_the_delivery(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		rid = uuid.uuid4().hex
		res = create_delivery_note(so.name, request_id=rid)
		self.assertEqual(frappe.db.get_value("Delivery Note", res["name"], "custom_request_id"), rid)

	def test_delivery_note_carries_the_fifo_batch(self):
		self._receive(10, RATE_A)
		so = self._order(4)
		self._pay(so, so.grand_total)
		res = create_delivery_note(so.name, submit=1)
		row = frappe.get_doc("Delivery Note", res["name"]).items[0]
		self.assertTrue(row.batch_no or row.serial_and_batch_bundle)

	def test_transport_details_are_recorded(self):
		self._receive(20, RATE_A)
		so = self._order(5)
		self._pay(so, so.grand_total)
		res = create_delivery_note(so.name, transport_method="Courier", transport_detail="Blue van")
		note = frappe.get_doc("Delivery Note", res["name"])
		self.assertEqual(note.custom_transport_method, "Courier")
		self.assertEqual(note.custom_transport_detail, "Blue van")

	def test_draft_order_cannot_be_delivered(self):
		self._receive(20, RATE_A)
		so = self._order(5, submit=False)
		with self.assertRaises(frappe.ValidationError):
			prepare_delivery(so.name)

	def test_credit_customer_within_limit_delivers_without_payment(self):
		self._receive(20, RATE_A)
		customer = self._customer(CREDIT_CUSTOMER, limit=1000000)
		so = self._order(5, customer=customer)
		gate = prepare_delivery(so.name)["gate"]
		self.assertTrue(gate["allowed"], gate.get("reason"))
		res = create_delivery_note(so.name, submit=1)
		self.assertEqual(frappe.get_doc("Delivery Note", res["name"]).docstatus, 1)


if __name__ == "__main__":
	unittest.main()
