"""Regression tests for generated clean-route coverage and the universal list
engine robustness fix (KeyError on text/hidden default columns).

Runs under the Frappe test runner (needs a site + allow_tests). Verified
manually via `bench execute my_store_ui.audit.route_coverage.verify_generated_routes`
on 2026-07-14: served=170, failed=0.
"""
import frappe
from frappe.tests.utils import FrappeTestCase

from my_store_ui import priority_pages
from my_store_ui.audit import route_coverage
from my_store_ui.services.priority_registry import ENTITY_ROUTES, _GENERATED_ENTITY_ROUTES
from my_store_ui.universal import api as universal_api


class TestGeneratedRouteCoverage(FrappeTestCase):
    def test_every_entity_route_resolves_and_serves(self):
        # As Administrator every ENTITY_ROUTES base must resolve and serve.
        frappe.set_user("Administrator")
        result = route_coverage.verify_generated_routes()
        self.assertEqual(result["failed"], 0, msg=str(result["failures"]))
        self.assertGreaterEqual(result["served"], len(_GENERATED_ENTITY_ROUTES))

    def test_list_engine_handles_text_and_hidden_default_columns(self):
        # Timesheet/Contract previously raised KeyError because default columns
        # (title/status) were excluded from all_columns. They must serve now.
        frappe.set_user("Administrator")
        for doctype in ("Timesheet", "Contract", "Address Template"):
            if doctype not in {spec["doctype"] for spec in ENTITY_ROUTES.values()}:
                continue
            feature = frappe.scrub(doctype).replace("_", "-")
            listing = universal_api.get_document_list(feature, page=1, page_size=2)
            self.assertIn("columns", listing)
            for column in listing["columns"]:
                self.assertIn("fieldname", column)
                self.assertIn("label", column)

    def test_ledger_tables_are_not_routed(self):
        # System/ledger tables must never get an editable generic route.
        routed = {spec["doctype"] for spec in ENTITY_ROUTES.values()}
        for doctype in ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry", "Bin"):
            self.assertNotIn(doctype, routed)

    def test_every_grouped_report_definition_loads(self):
        # Every REPORT_GROUPS report must resolve and load its viewer definition.
        frappe.set_user("Administrator")
        result = route_coverage.verify_generated_reports()
        self.assertEqual(result["failed"], 0, msg=str(result["failures"]))
