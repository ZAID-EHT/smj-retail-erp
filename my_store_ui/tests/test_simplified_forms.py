"""Every Retail ERP create form must be simplified, not the raw ERPNext form.

ACCOUNT CREATION.docx repeatedly asks for "only the important stuff, no corporate
level stuff". This pins the curated add-form field set for each document and proves
the business fields the document names are present.
"""

from __future__ import annotations

import unittest

import frappe

from my_store_ui.universal.api import (
	SIMPLE_CREATE_FIELDS,
	SIMPLE_CREATE_REQUIRED,
	get_doctype_metadata,
)
from my_store_ui.universal.registry import get_registry_records

# The forms the document lists that flow through the generated engine.
CURATED = (
	"Supplier", "Lead", "Quotation", "Purchase Order", "Purchase Receipt",
	"Purchase Invoice", "Stock Entry", "Warehouse",
)

# Forms served by dedicated curated pages instead of the generated engine.
CUSTOM_FORM_DOCTYPES = ("Customer", "Item", "Sales Order", "Delivery Note",
                        "Sales Invoice", "Payment Entry")

# Corporate-level fields that must never sit on a simplified add form.
CORPORATE_NOISE = {
	"amended_from", "letter_head", "select_print_heading", "group_same_items",
	"auto_repeat", "update_auto_repeat_reference", "inter_company_reference",
	"inter_company_order_reference", "inter_company_invoice_reference",
	"represents_company", "is_internal_supplier", "base_grand_total",
	"base_net_total", "base_total", "base_in_words", "in_words",
	"rounding_adjustment", "base_rounding_adjustment", "other_charges_calculation",
	"plc_conversion_rate", "price_list_currency", "ignore_pricing_rule",
	"disable_rounded_total", "base_rounded_total",
}


class TestSimplifiedForms(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.local.session = frappe._dict(user="Administrator", data={})
		frappe.set_user("Administrator")
		cls.by_doctype = {}
		for rec in get_registry_records():
			dt = rec.get("doctype")
			if dt and dt not in cls.by_doctype:
				cls.by_doctype[dt] = rec

	def _metadata(self, doctype):
		record = self.by_doctype.get(doctype)
		self.assertIsNotNone(record, f"{doctype} has no registry record")
		return get_doctype_metadata(record["route_key"])

	def test_every_named_form_has_a_curated_field_set(self):
		for doctype in CURATED:
			self.assertIn(
				doctype, SIMPLE_CREATE_FIELDS,
				f"{doctype} still presents the raw ERPNext form",
			)
			self.assertTrue(SIMPLE_CREATE_FIELDS[doctype], f"{doctype} curated set is empty")

	def test_curated_forms_are_materially_smaller_than_the_raw_form(self):
		for doctype in CURATED:
			data = self._metadata(doctype)
			simple = data["simple_create_fields"]
			full = [
				f for f in data["fields"]
				if f.get("fieldtype") not in ("Section Break", "Column Break", "Tab Break")
			]
			self.assertTrue(simple, f"{doctype} produced no simple_create_fields")
			self.assertLess(
				len(simple), len(full),
				f"{doctype} add form is not simplified ({len(simple)} of {len(full)})",
			)

	def test_curated_forms_exclude_corporate_noise(self):
		for doctype in CURATED:
			leaked = set(SIMPLE_CREATE_FIELDS[doctype]) & CORPORATE_NOISE
			self.assertFalse(leaked, f"{doctype} add form still exposes {sorted(leaked)}")

	def test_curated_fields_all_exist_on_the_doctype(self):
		"""A curated name that does not exist would silently vanish from the form."""
		for doctype in CURATED:
			meta = frappe.get_meta(doctype)
			for fieldname in SIMPLE_CREATE_FIELDS[doctype]:
				self.assertTrue(
					meta.get_field(fieldname),
					f"{doctype}.{fieldname} does not exist on the DocType",
				)

	def test_required_add_fields_exist_and_are_a_subset(self):
		for doctype in CURATED:
			required = SIMPLE_CREATE_REQUIRED.get(doctype, ())
			self.assertTrue(required, f"{doctype} declares no required add fields")
			self.assertTrue(
				set(required) <= set(SIMPLE_CREATE_FIELDS[doctype]),
				f"{doctype} requires a field that is not on its add form",
			)

	# --- the specific business fields the document lists ---------------------

	def test_purchase_order_keeps_the_requested_business_fields(self):
		fields = set(SIMPLE_CREATE_FIELDS["Purchase Order"])
		for expected in ("supplier", "company", "items", "set_warehouse",
		                 "schedule_date", "taxes", "buying_price_list"):
			self.assertIn(expected, fields, f"Purchase Order is missing {expected}")

	def test_quotation_keeps_the_requested_business_fields(self):
		fields = set(SIMPLE_CREATE_FIELDS["Quotation"])
		for expected in ("quotation_to", "party_name", "company", "transaction_date",
		                 "valid_till", "items", "selling_price_list", "terms"):
			self.assertIn(expected, fields, f"Quotation is missing {expected}")

	def test_stock_transfer_keeps_source_and_target_warehouse(self):
		fields = set(SIMPLE_CREATE_FIELDS["Stock Entry"])
		self.assertIn("from_warehouse", fields)
		self.assertIn("to_warehouse", fields)

	def test_customer_form_carries_the_documented_business_fields(self):
		"""Customer uses the dedicated curated form, not the generated engine."""
		meta = frappe.get_meta("Customer")
		for fieldname in ("default_price_list", "custom_credit_type", "custom_credit_days",
		                  "custom_br_no", "custom_business_nature",
		                  "custom_transport_method", "custom_transport_detail",
		                  "custom_whatsapp_no"):
			self.assertTrue(meta.get_field(fieldname), f"Customer.{fieldname} is missing")

	def test_product_form_carries_the_documented_business_fields(self):
		meta = frappe.get_meta("Item")
		for fieldname in ("custom_sku", "custom_image_2", "custom_carton_qty",
		                  "custom_margin", "custom_stock_location_1",
		                  "custom_stock_location_2", "custom_stock_location_3"):
			self.assertTrue(meta.get_field(fieldname), f"Item.{fieldname} is missing")

	def test_custom_form_doctypes_are_not_routed_through_the_generated_engine(self):
		"""These have dedicated curated pages; the generated engine must refuse them."""
		for doctype in CUSTOM_FORM_DOCTYPES:
			record = self.by_doctype.get(doctype)
			if not record:
				continue
			with self.assertRaises(frappe.PermissionError, msg=f"{doctype} leaked to the engine"):
				get_doctype_metadata(record["route_key"])


if __name__ == "__main__":
	unittest.main()
