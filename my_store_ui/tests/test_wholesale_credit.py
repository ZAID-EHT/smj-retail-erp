"""Pure unit tests for the customer credit delivery-gate rules.

These need no site data and run standalone, so the approved business rules are
verified now (before the staging site exists).
"""
import unittest

from my_store_ui.wholesale.credit import decide_delivery_gate, CREDIT_CUSTOMER, NON_CREDIT_CUSTOMER


class TestDeliveryGate(unittest.TestCase):
    def test_unset_type_requires_manager_classification(self):
        d = decide_delivery_gate(None, False, 0, 0, 0, field_present=False)
        self.assertFalse(d["allowed"])
        self.assertTrue(d["requires_manager_approval"])

    def test_non_credit_requires_full_payment(self):
        d = decide_delivery_gate(NON_CREDIT_CUSTOMER, False, 0, 0, 5000)
        self.assertFalse(d["allowed"])
        self.assertFalse(d["requires_manager_approval"])

    def test_credit_within_limit_allowed(self):
        d = decide_delivery_gate(CREDIT_CUSTOMER, False, 100000, 20000, 5000)
        self.assertTrue(d["allowed"])
        self.assertFalse(d["requires_manager_approval"])

    def test_credit_over_limit_requires_manager(self):
        # 20000 outstanding + 90000 new = 110000 > 100000 limit
        d = decide_delivery_gate(CREDIT_CUSTOMER, False, 100000, 20000, 90000)
        self.assertFalse(d["allowed"])
        self.assertTrue(d["requires_manager_approval"])

    def test_credit_exactly_at_limit_allowed(self):
        d = decide_delivery_gate(CREDIT_CUSTOMER, False, 100000, 20000, 80000)
        self.assertTrue(d["allowed"])

    def test_overdue_credit_requires_manager(self):
        d = decide_delivery_gate(CREDIT_CUSTOMER, True, 100000, 20000, 1000)
        self.assertFalse(d["allowed"])
        self.assertTrue(d["requires_manager_approval"])

    def test_credit_no_limit_set_allowed_when_not_overdue(self):
        # credit_limit 0 means no explicit cap -> not blocked by limit
        d = decide_delivery_gate(CREDIT_CUSTOMER, False, 0, 500000, 100000)
        self.assertTrue(d["allowed"])


if __name__ == "__main__":
    unittest.main()
